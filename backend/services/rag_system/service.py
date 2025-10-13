from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter
from typing import Iterable, List, Optional

from supabase import Client

from .openai_client import OpenAIChatClient, OpenAIEmbeddingClient
from .pdf_loader import build_chunks
from .reranker import CrossEncoderReranker
from .types import ChunkInput, DocumentChunk, IngestedDocument
from .vector_store import RankedChunk, SupabaseVectorStore

SYSTEM_PROMPT = (
    "당신은 임산부·임신 예정자·영유아 관련 정책과 복지 혜택을 안내하는 한국어 전문가입니다."
    "제공된 문맥을 꼼꼼히 읽고 질문에 직접 답하며, 문맥에서 찾은 지원 내용·금액·조건을 명확히 요약하세요."
    "문서 이름과 페이지를 괄호로 인용해 근거를 제시하세요. 문맥에 일부 정보라도 있으면 그 부분은 요약하고, 없는 항목은 '문서에 명시 없음/확인 필요'로 표시하세요. 관련 문맥이 전혀 없을 때만 '정보를 찾을 수 없습니다.'라고 답하세요."
    "추측이나 문맥 밖 정보는 추가하지 마세요."
    "\n\n중요: 캘린더 추가는 '정책 관련 일정'에 한정합니다."
    "사용자 개인 일정(예: 출산 예정일)은 사용자가 명시적으로 추가해달라고 요청한 경우에만 제안하세요."
    "정책 문맥에 날짜가 있거나, 사용자가 '언제/언제까지/날짜/일정/예약' 같이 시점·스케줄을 묻는 경우에는 add_calendar_event 함수를 호출해 정책 일정을 제안하세요."
    "\n항상 텍스트 답변과 function call(필요할 때만)을 함께 제공하세요."
    "\n\n반드시 모든 답변은 한국어로만 작성하세요."
)


def _default(value: Optional[str], fallback: str) -> str:
    return value if value else fallback


class RagService:
    def __init__(
        self,
        *,
        supabase: Client,
        openai_api_key: str,
        embedding_model: str,
        chat_model: str,
        vector_table: str,
        match_function: str,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        embedding_batch_size: int = 64,
        reranker: CrossEncoderReranker | None = None,
        rerank_top_n: Optional[int] = None,
    ) -> None:
        self._supabase = supabase
        self._vector_store = SupabaseVectorStore(
            supabase, table=vector_table, query_function=match_function
        )
        self._embedding_client = OpenAIEmbeddingClient(
            api_key=openai_api_key, model=embedding_model
        )
        self._chat_client = OpenAIChatClient(api_key=openai_api_key, model=chat_model)
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._embedding_batch_size = max(1, embedding_batch_size)
        self._reranker = reranker
        self._rerank_top_n = rerank_top_n

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------
    def ingest_pdf(
        self,
        *,
        path: Path,
        policy_id: str,
        policy_title: str,
        metadata: dict | None = None,
    ) -> IngestedDocument:
        """Ingest a single PDF file using the provided policy metadata."""
        chunks = build_chunks(
            path, chunk_size=self._chunk_size, overlap=self._chunk_overlap
        )
        if not chunks:
            return IngestedDocument(path=path, chunks=[])

        normalized_chunks = self._prepare_chunks(
            chunks, policy_id=policy_id, file_path=path
        )
        embeddings = self._embed_chunks(normalized_chunks)
        stored_chunks = [
            DocumentChunk(
                id=chunk.id,
                text=chunk.text,
                metadata=chunk.metadata,
                embedding=embedding,
            )
            for chunk, embedding in zip(normalized_chunks, embeddings, strict=True)
        ]

        # Persist to Supabase
        self._vector_store.add_chunks(stored_chunks)

        # Ensure policy row exists/upserts
        policy_payload = {
            "id": policy_id,
            "title": _default(policy_title, policy_id),
            "description": _default((metadata or {}).get("description"), ""),
            "category": (metadata or {}).get("category"),
            "region": (metadata or {}).get("region"),
            "eligibility": (metadata or {}).get("eligibility", {}),
        }
        self._supabase.table("policies").upsert(policy_payload).execute()

        return IngestedDocument(path=path, chunks=stored_chunks)

    def _prepare_chunks(
        self, chunks: Iterable[ChunkInput], *, policy_id: str, file_path: Path
    ) -> List[ChunkInput]:
        prepared: List[ChunkInput] = []
        for chunk in chunks:
            page = chunk.metadata.page
            chunk_index = chunk.metadata.extra.get("chunk_index", 0)
            chunk.metadata.source = policy_id
            chunk.metadata.extra = {
                **chunk.metadata.extra,
                "file_path": str(file_path),
            }
            chunk.id = f"{policy_id}-p{page}-c{chunk_index}"
            prepared.append(chunk)
        return prepared

    def _embed_chunks(self, chunks: Iterable[ChunkInput]) -> List[List[float]]:
        texts = [chunk.text for chunk in chunks]
        if not texts:
            return []
        embeddings: List[List[float]] = []
        batch_size = self._embedding_batch_size
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            embeddings.extend(self._embedding_client.embed(batch))
        return embeddings

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def answer(
        self,
        question: str,
        *,
        top_k: int = 50,
        conversation_history: Optional[List[dict]] = None,
        enable_function_calling: bool = True,
    ) -> dict:
        if not question.strip():
            raise ValueError("Question must not be empty")
        if self._vector_store.is_empty():
            raise RuntimeError("Vector store is empty. 먼저 PDF를 임베딩하세요.")

        query_embedding = self._embedding_client.embed([question])[0]
        ranked = self._vector_store.top_k(query_embedding, k=top_k)
        print(
            "[DEBUG Retrieval] "
            f"{len(ranked)} hits; "
            f"scores={[item.score for item in ranked[:3]]}"
        )
        ranked_for_answer = ranked

        if self._reranker is not None and ranked:
            try:
                ranked_for_answer = self._reranker.rerank(
                    question,
                    ranked,
                    top_n=self._rerank_top_n or top_k,
                )
            except Exception:
                ranked_for_answer = ranked

        sections, context_text = self._build_context(ranked_for_answer)
        messages = self._build_prompt(question, context_text, conversation_history)

        # Define calendar function tool
        tools = None
        if enable_function_calling:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_calendar_event",
                        "description": "사용자가 언급한 특정 날짜(예: 출산 예정일, 신청 마감일, 검진 일정 등)를 캘린더에 자동으로 추가합니다. 사용자 질문에 구체적인 날짜(YYYY년 MM월 DD일 형식)가 포함되어 있으면 반드시 이 함수를 호출하여 일정을 제안하세요.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "일정 제목 (예: '첫만남이용권 신청 마감', '출산 예정일')",
                                },
                                "date": {
                                    "type": "string",
                                    "description": "일정 날짜 (ISO 8601 형식: YYYY-MM-DDTHH:MM:SS)",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "일정에 대한 상세 설명 (선택사항)",
                                },
                            },
                            "required": ["title", "date"],
                        },
                    },
                }
            ]

        start = perf_counter()
        # Use "auto" to let GPT decide whether to call functions while still providing an answer
        # The system prompt instructs GPT to provide BOTH answer and function call when needed
        tool_choice = "auto" if tools else None
        print(
            f"[DEBUG Service] tools enabled: {bool(tools)}, tool_choice: {tool_choice}"
        )

        response = self._chat_client.complete(
            messages, tools=tools, tool_choice=tool_choice
        )
        latency = perf_counter() - start

        sources = [
            {
                "id": item.chunk.id,
                "source": item.chunk.metadata.source,
                "page": item.chunk.metadata.page,
                "text": item.chunk.text,
            }
            for item in ranked_for_answer
        ]

        # Handle function call response
        if isinstance(response, dict) and "function_call" in response:
            # Get the text answer from GPT
            answer_text = response.get("content", "").strip()

            # Parse and sanitize function call arguments (avoid past dates, handle '상시')
            import json
            import re
            from datetime import datetime, timedelta

            def parse_iso(dt_str: str) -> datetime | None:
                try:
                    s = dt_str.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(s)
                    if dt.tzinfo is not None:
                        # Convert to local naive for comparison
                        dt = dt.astimezone().replace(tzinfo=None)
                    return dt
                except Exception:
                    return None

            def next_9am(dt: datetime) -> datetime:
                candidate = dt.replace(hour=9, minute=0, second=0, microsecond=0)
                if candidate <= dt:
                    candidate = (dt + timedelta(days=1)).replace(
                        hour=9, minute=0, second=0, microsecond=0
                    )
                return candidate

            func_call = response["function_call"] or {}
            func_args = func_call.get("arguments", {})
            if isinstance(func_args, str):
                try:
                    func_args = json.loads(func_args)
                except Exception:
                    func_args = {}

            proposed_title = func_args.get("title") or "정책 일정"
            proposed_date_str = func_args.get("date")
            now_local = datetime.now()

            # Detect 'always-available' from sources or title
            always_keywords = ["상시", "연중", "수시", "항시"]
            sources_text = (
                "\n".join(item["text"] for item in sources[:5]) if sources else ""
            )
            is_always = any(kw in sources_text for kw in always_keywords) or any(
                kw in proposed_title for kw in always_keywords
            )

            sanitized_fc = None
            if proposed_date_str:
                parsed_dt = parse_iso(proposed_date_str)
                if parsed_dt is None:
                    # Invalid date; drop function call
                    sanitized_fc = None
                elif parsed_dt < now_local and not is_always:
                    # Past date and not an always-available policy → drop
                    sanitized_fc = None
                elif parsed_dt < now_local and is_always:
                    # Adjust to the next 9AM in the near future
                    adjusted = next_9am(now_local + timedelta(days=1))
                    sanitized_fc = {
                        "name": func_call.get("name", "add_calendar_event"),
                        "arguments": {
                            "title": (
                                proposed_title if proposed_title else "상시 신청 알림"
                            ),
                            "date": adjusted.isoformat(),
                            "description": f"정책 관련 일정 제안 (상시/연중 문구 감지)",
                        },
                    }
                else:
                    # Future date is acceptable
                    sanitized_fc = {
                        "name": func_call.get("name", "add_calendar_event"),
                        "arguments": {
                            "title": proposed_title,
                            "date": parsed_dt.isoformat(),
                            "description": func_args.get("description")
                            or "정책 관련 일정 제안",
                        },
                    }
            else:
                # No date provided; if sources indicate 'always' and user showed time intent, set next 9AM
                time_intent = bool(
                    re.search(
                        r"(언제|언제까지|날짜|일정|예약|시기|시한|기한)", question
                    )
                )
                if is_always and time_intent:
                    adjusted = next_9am(now_local + timedelta(days=1))
                    sanitized_fc = {
                        "name": func_call.get("name", "add_calendar_event"),
                        "arguments": {
                            "title": "상시 신청 알림",
                            "date": adjusted.isoformat(),
                            "description": "정책 관련 일정 제안 (상시/연중 문구 감지)",
                        },
                    }

            def format_korean_datetime(dt: datetime) -> str:
                ampm = "오전" if dt.hour < 12 else "오후"
                hour12 = (
                    dt.hour
                    if 1 <= dt.hour <= 12
                    else (dt.hour - 12 if dt.hour > 12 else 12)
                )
                return f"{dt.year}년 {dt.month}월 {dt.day}일 {ampm} {hour12:02d}:{dt.minute:02d}"

            # Build a more helpful fallback when the model declines to answer
            def build_helpful_fallback_text(default_title: str) -> str:
                prefix = "질문과 관련된 정책 정보를 일부 확인했습니다."
                if sanitized_fc and sanitized_fc.get("arguments", {}).get("date"):
                    try:
                        dt = datetime.fromisoformat(sanitized_fc["arguments"]["date"])
                    except Exception:
                        dt = None
                    if dt:
                        when = format_korean_datetime(dt)
                        return f"{prefix} 아래 일정 정보를 기준으로 안내드립니다.\n- {default_title}: {when}"
                # No date available; point to sources
                return f"{prefix} 아래 참고 정책을 확인해 주세요. 필요한 항목은 '문서에 명시 없음/확인 필요'로 표시됩니다."

            # If GPT didn't provide a text answer, or returned a too-strong refusal, craft a fallback
            if not answer_text or answer_text.strip().startswith(
                "정보를 찾을 수 없습니다"
            ):
                title_for_text = proposed_title or "정책 일정"
                answer_text = build_helpful_fallback_text(title_for_text)

            # If sanitized function_call is None, attempt synthesis from sources
            if sanitized_fc is None:
                try:
                    import re
                    from datetime import datetime, timedelta
                    import calendar as _cal

                    def next_9am(dt: datetime) -> datetime:
                        candidate = dt.replace(
                            hour=9, minute=0, second=0, microsecond=0
                        )
                        if candidate <= dt:
                            candidate = (dt + timedelta(days=1)).replace(
                                hour=9, minute=0, second=0, microsecond=0
                            )
                        return candidate

                    now_local = datetime.now()
                    time_intent = bool(
                        re.search(
                            r"(언제|언제까지|날짜|일정|예약|시기|시한|기한)", question
                        )
                    )

                    # Combine top source texts
                    sources_text = (
                        "\n".join(item["text"] for item in sources[:5])
                        if sources
                        else ""
                    )

                    # Quarter detection in sources
                    q_pat1 = re.compile(
                        r"제\s*(\d)분기\s*:\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일부터\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일까지"
                    )
                    q_pat2 = re.compile(
                        r"제\s*(\d)분기\s*:\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일부터\s*그\s*다음해의\s*(\d{1,2})\s*월\s*말일까지"
                    )

                    quarter_ends: list[datetime] = []
                    for mq in q_pat1.finditer(sources_text):
                        q, sm, sd, em, ed = mq.groups()
                        y = now_local.year
                        try:
                            end_dt = datetime(y, int(em), int(ed), 18, 0, 0)
                            if end_dt < now_local:
                                end_dt = datetime(y + 1, int(em), int(ed), 18, 0, 0)
                            quarter_ends.append(end_dt)
                        except Exception:
                            pass
                    for mq in q_pat2.finditer(sources_text):
                        q, sm, sd, em = mq.groups()
                        y = now_local.year
                        try:
                            last_day = _cal.monthrange(y + 1, int(em))[1]
                            end_dt = datetime(y + 1, int(em), last_day, 18, 0, 0)
                            if end_dt < now_local:
                                last_day = _cal.monthrange(y + 2, int(em))[1]
                                end_dt = datetime(y + 2, int(em), last_day, 18, 0, 0)
                            quarter_ends.append(end_dt)
                        except Exception:
                            pass

                    if time_intent and quarter_ends:
                        selected = min(
                            [dt for dt in quarter_ends if dt >= now_local], default=None
                        )
                        if selected is not None:
                            sanitized_fc = {
                                "name": func_call.get("name", "add_calendar_event"),
                                "arguments": {
                                    "title": "분기 마감",
                                    "date": selected.isoformat(),
                                    "description": "정책 관련 일정 제안 (분기 일정 추론)",
                                },
                            }
                except Exception:
                    pass

            return {
                "answer": answer_text,
                "sources": sources,
                "latency_seconds": latency,
                "sections": sections,
                "function_call": sanitized_fc,
            }

        # No function_call from model. As a safety net, detect policy-related
        # dates in retrieved sources (NOT from the user's personal question)
        # and synthesize a function call so the UI can offer "캘린더에 추가".
        if enable_function_calling and isinstance(response, str):
            try:
                import re
                from datetime import datetime, timedelta

                # If the user asks implicitly about timing, we can be generous
                # when accepting dates from sources (even without explicit policy keywords)
                time_intent = bool(
                    re.search(
                        r"(언제|언제까지|날짜|일정|예약|시기|시한|기한)", question
                    )
                )

                def next_9am(dt: datetime) -> datetime:
                    candidate = dt.replace(hour=9, minute=0, second=0, microsecond=0)
                    if candidate <= dt:
                        candidate = (dt + timedelta(days=1)).replace(
                            hour=9, minute=0, second=0, microsecond=0
                        )
                    return candidate

                def find_policy_date_and_title(
                    source_text: str,
                ) -> tuple[str | None, str | None, bool]:
                    # Look for Korean and ISO-like dates
                    date_patterns = [
                        r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일",
                        r"(\d{4})[\./-](\d{1,2})[\./-](\d{1,2})",
                    ]
                    # Ranges like 2025.01.10 ~ 2025.02.20 or 2025년 1월 10일 ~ 2025년 2월 20일
                    range_patterns = [
                        r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*[~\-–]\s*(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일",
                        r"(\d{4})[\./-](\d{1,2})[\./-](\d{1,2})\s*[~\-–]\s*(\d{4})[\./-](\d{1,2})[\./-](\d{1,2})",
                    ]
                    # Policy-related keywords
                    keywords = [
                        "신청",
                        "접수",
                        "마감",
                        "기간",
                        "시작",
                        "종료",
                        "지급",
                        "공고",
                    ]
                    always_keywords = ["상시", "연중", "수시", "항시"]
                    now = datetime.now()

                    # Search window: if a date occurs near a keyword, consider it relevant
                    # Prefer end date of ranges if present
                    for pat in range_patterns:
                        for m in re.finditer(pat, source_text):
                            span_start, span_end = m.span()
                            window_start = max(0, span_start - 60)
                            window_end = min(len(source_text), span_end + 60)
                            window = source_text[window_start:window_end]

                            y1, mo1, d1, y2, mo2, d2 = map(int, m.groups())
                            start_dt = datetime(y1, mo1, d1, 9, 0, 0)
                            end_dt = datetime(y2, mo2, d2, 18, 0, 0)

                            # Choose end if still future, else start if future
                            chosen_dt = (
                                end_dt
                                if end_dt >= now
                                else (start_dt if start_dt >= now else None)
                            )
                            if not chosen_dt:
                                continue

                            title = None
                            if any(kw in window for kw in keywords):
                                if "마감" in window or chosen_dt == end_dt:
                                    title = "신청 마감"
                                elif "접수" in window and (
                                    "시작" in window
                                    or "개시" in window
                                    or chosen_dt == start_dt
                                ):
                                    title = "접수 시작"
                                elif "지급" in window:
                                    title = "지급일"
                                elif "종료" in window:
                                    title = "지원 종료"
                                else:
                                    title = "정책 신청 일정"
                            elif time_intent:
                                title = "정책 일정"

                            if title:
                                return chosen_dt.isoformat(), title, False

                    for pat in date_patterns:
                        for m in re.finditer(pat, source_text):
                            span_start, span_end = m.span()
                            window_start = max(0, span_start - 40)
                            window_end = min(len(source_text), span_end + 40)
                            window = source_text[window_start:window_end]

                            y, mo, d = map(int, m.groups())
                            dt = datetime(y, mo, d, 9, 0, 0)

                            if any(kw in window for kw in keywords):
                                # Title heuristic with keywords nearby
                                if "마감" in window:
                                    return dt.isoformat(), "신청 마감", False
                                if "접수" in window and (
                                    "시작" in window or "개시" in window
                                ):
                                    return dt.isoformat(), "접수 시작", False
                                if "지급" in window:
                                    return dt.isoformat(), "지급일", False
                                if "종료" in window:
                                    return dt.isoformat(), "지원 종료", False
                                if (
                                    "기간" in window
                                    or "공고" in window
                                    or "신청" in window
                                    or "접수" in window
                                ):
                                    return dt.isoformat(), "정책 신청 일정", False

                            # If user shows time intent, accept a date even without nearby keywords
                            if time_intent:
                                return dt.isoformat(), "정책 일정", False

                    # No explicit date, but always-available policy in text and time intent
                    if time_intent and any(kw in source_text for kw in always_keywords):
                        return (
                            next_9am(now + timedelta(days=1)).isoformat(),
                            "상시 신청 알림",
                            True,
                        )

                    # Quarter schedule detection (e.g., 제1분기: 3월 1일부터 5월 31일까지 ...)
                    import calendar as _cal

                    q_pat1 = re.compile(
                        r"제\s*(\d)분기\s*:\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일부터\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일까지"
                    )
                    q_pat2 = re.compile(
                        r"제\s*(\d)분기\s*:\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일부터\s*그\s*다음해의\s*(\d{1,2})\s*월\s*말일까지"
                    )

                    quarter_ends: list[datetime] = []
                    for mq in q_pat1.finditer(source_text):
                        q, sm, sd, em, ed = mq.groups()
                        y = now.year
                        try:
                            end_dt = datetime(y, int(em), int(ed), 18, 0, 0)
                            # If end is still past, try next year
                            if end_dt < now:
                                end_dt = datetime(y + 1, int(em), int(ed), 18, 0, 0)
                            quarter_ends.append(end_dt)
                        except Exception:
                            continue

                    for mq in q_pat2.finditer(source_text):
                        q, sm, sd, em = mq.groups()
                        y = now.year
                        try:
                            last_day = _cal.monthrange(y + 1, int(em))[1]
                            end_dt = datetime(y + 1, int(em), last_day, 18, 0, 0)
                            if end_dt < now:
                                # Roll one more year if needed
                                last_day = _cal.monthrange(y + 2, int(em))[1]
                                end_dt = datetime(y + 2, int(em), last_day, 18, 0, 0)
                            quarter_ends.append(end_dt)
                        except Exception:
                            continue

                    if quarter_ends:
                        selected = min(
                            [dt for dt in quarter_ends if dt >= now], default=None
                        )
                        if selected is not None:
                            # If user has timing intent, synthesize a quarter deadline event
                            if time_intent:
                                return selected.isoformat(), "분기 마감", False

                    return None, None, False

                # Scan top-ranked chunks' text for a policy-related date
                chosen_date: str | None = None
                chosen_title: str | None = None
                chosen_always: bool = False
                chosen_source_id: str | None = None
                for item in ranked_for_answer:
                    dt, title, is_always = find_policy_date_and_title(item.chunk.text)
                    if dt and title:
                        chosen_date, chosen_title, chosen_always = dt, title, is_always
                        chosen_source_id = item.chunk.metadata.source
                        break

                if chosen_date and chosen_title:
                    # Avoid scheduling in the past unless it's an always-available policy
                    try:
                        parsed = datetime.fromisoformat(chosen_date)
                    except Exception:
                        parsed = None

                    if parsed is not None:
                        now = datetime.now()
                        if parsed < now and not chosen_always:
                            # Skip emitting function_call for past-due schedules
                            raise RuntimeError(
                                "Detected past policy date without 'always' flag; skipping function_call"
                            )
                        if parsed < now and chosen_always:
                            parsed = next_9am(now + timedelta(days=1))
                            chosen_date = parsed.isoformat()
                            if chosen_title in (None, "정책 일정"):
                                chosen_title = "상시 신청 알림"

                    synthesized_fc = {
                        "name": "add_calendar_event",
                        "arguments": {
                            "title": chosen_title,
                            "date": chosen_date,
                            "description": f"정책 관련 일정 제안 (출처: {chosen_source_id or ''})",
                        },
                    }
                    return {
                        "answer": response,
                        "sources": sources,
                        "latency_seconds": latency,
                        "sections": sections,
                        "function_call": synthesized_fc,
                    }
            except Exception:
                # Best-effort only; ignore any parsing errors
                pass

        # If the model declined despite having sources, provide a minimal helpful answer
        if (
            isinstance(response, str)
            and response.strip().startswith("정보를 찾을 수 없습니다")
            and sources
        ):
            minimal = "질문과 관련된 정책 정보를 일부 확인했습니다. 다만 문서에 정확한 표현이 없거나 확인이 더 필요합니다. 아래 참고 정책을 확인해 주세요."
            return {
                "answer": minimal,
                "sources": sources,
                "latency_seconds": latency,
                "sections": sections,
            }

        return {
            "answer": response,
            "sources": sources,
            "latency_seconds": latency,
            "sections": sections,
        }

    def _build_context(
        self, ranked_chunks: Iterable[RankedChunk]
    ) -> tuple[List[str], str]:
        sections: List[str] = []
        for item in ranked_chunks:
            metadata = item.chunk.metadata
            header = metadata.source
            if metadata.page is not None:
                header = f"{header} (page {metadata.page})"
            section = f"Source: {header}\\n{item.chunk.text}"
            sections.append(section)
        context_text = "\\n\\n".join(sections) if sections else "No context available."
        return sections, context_text

    def _build_prompt(
        self,
        question: str,
        context_text: str,
        conversation_history: Optional[List[dict]] = None,
    ) -> List[dict]:
        """
        Build the prompt with system message, conversation history, and current question.
        conversation_history should be a list of dicts with 'role' and 'content' keys.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current question with context
        user_message = (
            "Answer the user question using ONLY the context below. Quote relevant "
            "sections when helpful. If the context does not contain enough information, "
            "respond with '정보를 찾을 수 없습니다.'.\\n\\n"
            f"Context:\\n{context_text}\\n\\n"
            f"Question: {question}"
        )
        messages.append({"role": "user", "content": user_message})

        return messages


_SERVICE_INSTANCE: RagService | None = None


def get_rag_service(*, supabase: Client) -> RagService:
    """Create/reuse a singleton chat service instance using environment configuration."""
    global _SERVICE_INSTANCE
    if _SERVICE_INSTANCE is not None:
        return _SERVICE_INSTANCE

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY 환경 변수가 설정되어야 합니다.")

    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "upskyy/bge-m3-korean")
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-nano")
    vector_table = os.getenv("SUPABASE_POLICY_CHUNK_TABLE", "policy_chunks")
    match_function = os.getenv("SUPABASE_MATCH_FUNCTION", "match_policy_chunks")
    chunk_size = int(os.getenv("CHAT_CHUNK_SIZE", "1200"))
    chunk_overlap = int(os.getenv("CHAT_CHUNK_OVERLAP", "200"))
    embedding_batch_size = int(os.getenv("CHAT_EMBED_BATCH_SIZE", "64"))

    rerank_enabled = os.getenv("CHAT_ENABLE_RERANKING", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    reranker: CrossEncoderReranker | None = None
    rerank_top_n_value = os.getenv("CHAT_RERANK_TOP_N")
    rerank_top_n = int(rerank_top_n_value) if rerank_top_n_value else None

    if rerank_enabled:
        reranker_model = os.getenv("CHAT_RERANKER_MODEL", "BAAI/bge-reranker-base")
        device = os.getenv("CHAT_RERANKER_DEVICE")
        try:
            reranker = CrossEncoderReranker(reranker_model, device=device)
        except ImportError as exc:
            raise RuntimeError(
                "CHAT_ENABLE_RERANKING이 true이지만 sentence-transformers 패키지가 설치되어 있지 않습니다."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"리랭커 초기화 실패: {exc}") from exc

    _SERVICE_INSTANCE = RagService(
        supabase=supabase,
        openai_api_key=openai_api_key,
        embedding_model=embedding_model,
        chat_model=chat_model,
        vector_table=vector_table,
        match_function=match_function,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_batch_size=embedding_batch_size,
        reranker=reranker,
        rerank_top_n=rerank_top_n,
    )
    return _SERVICE_INSTANCE
