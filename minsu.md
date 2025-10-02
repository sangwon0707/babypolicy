# Change Log
- 2025-10-01 13:51:38 KST | file: minsu.md | section: file creation | reason: set up edit log as requested
- 2025-10-01 13:54:28 KST | file: backend/init_supabase.sql | section: vector search setup | reason: update RAG index/function to enforce 1024-dim embeddings and matching ivfflat config
- 2025-10-01 14:40:26 KST | file: backend/init_supabase.sql | section: policy pdf storage table | reason: add pdf_files table for tracking local pdf paths with categories and timestamps
- 2025-10-01 14:44:01 KST | file: backend/init_supabase.sql | section: pdf_files table | reason: switch pdf_files.category to JSONB so each path can hold structured category data
- 2025-10-01 14:53:02 KST | file: minsu.md | section: chatbot migration plan | reason: documented integration roadmap for replacing existing RAG chatbot with PREC service
- 2025-10-01 14:58:07 KST | file: minsu.md | section: chatbot migration plan | reason: revised plan to use PREC service with pdf_files ingestion trigger and score removal
- 2025-10-01 14:59:34 KST | file: minsu.md | section: chatbot migration plan | reason: updated plan to minimize non-chatbot backend changes during PREC integration
- 2025-10-01 15:01:27 KST | file: minsu.md | section: chatbot migration plan | reason: added naming alignment step to replace temporary PREC branding with project-specific naming
- 2025-10-01 15:10:49 KST | file: minsu.md | section: chatbot migration plan | reason: outlined manual pdf_files seeding and LLM-triggered embedding workflow prior to frontend integration
- 2025-10-01 15:13:49 KST | file: backend/init_supabase.sql | section: match_policy_chunks | reason: removed similarity score output to align with new chatbot design
- 2025-10-01 15:15:41 KST | file: backend/init_supabase.sql | section: pdf_files table | reason: set updated_at to NOT NULL with default timestamp for consistency
- 2025-10-01 15:16:54 KST | file: backend/init_supabase.sql | section: pdf_files table | reason: revert updated_at to nullable since manual updates may omit timestamp
- 2025-10-01 15:32:54 KST | file: backend/services/babypolicy_chat/* | section: chatbot backend rewrite | reason: ported PREC-based chat service, vector store, pdf loader, and ingestion utilities with baby policy naming
- 2025-10-01 15:33:09 KST | file: backend/routers/chat.py; backend/schemas.py | section: chatbot integration | reason: switched chat endpoint to new service and aligned RagSource schema without score field
- 2025-10-01 15:35:17 KST | file: backend/routers/admin.py; backend/services/babypolicy_chat/ingest.py; backend/services/scraper_service.py | section: admin ingestion flow | reason: rerouted RAG processing endpoint to new ingestion pipeline and removed legacy rag_service dependency
- 2025-10-01 15:38:13 KST | file: README.md; SETUP_GUIDE.md | section: docs | reason: documented new babypolicy chat modules and ingestion workflow
- 2025-10-01 15:40:21 KST | file: backend/services/babypolicy_chat/service.py | section: prompts | reason: reformatted system prompt text for clarity
- 2025-10-02 11:00:24 KST | file: backend/services/rag_system/*; backend/services/rag_system_ingest.py; README.md; SETUP_GUIDE.md; backend/routers/* | section: rename alignment | reason: renamed babypolicy_chat modules to rag_system and updated imports/docs
- 2025-10-02 11:15:24 KST | file: backend/services/rag_system/ingest.py | section: directory ingestion | reason: update ingest workflow to process all PDFs inside provided folders


## Chatbot Migration Plan

| 단계 | 목표 | 주요 수정 파일 | 메모 |
| --- | --- | --- | --- |
| 1 | PREC 챗봇 코드 자산 분석 및 재사용 범위 확정 | `prec/service.py`, `prec/vector_store.py`, `prec/openai_client.py`, `prec/settings.py` | 비챗봇 백엔드 기능과 분리할 경계를 먼저 정의하고, 최종 브랜드명에 맞춰 모듈명 변경 범위를 계획 |
| 2 | 독립적인 PREC 어댑터 서비스 작성 | `backend/services/rag_system/service.py` | 기존 `rag_service`를 대체하되 동일한 인터페이스를 유지해 라우터·CRUD 수정 범위를 축소하고, 서비스 명칭도 프로젝트 컨벤션에 맞춰 통일 |
| 3 | pdf_files 기반 단발성 인제스트 유틸 추가 | `backend/services/rag_system/ingest.py`, `backend/services/rag_system_ingest.py` | 프론트 기능이 준비될 때까지 `pdf_files`에 경로/태그를 수동 하드코딩해 채우고, 새 유틸을 LLM 호출(예: 관리용 스크립트)과 연계해 한 번만 임베딩 실행 |
| 4 | FastAPI 라우터에서 서비스 교체 | `backend/routers/chat.py`, `backend/main.py` | 엔드포인트·응답 스키마는 유지하고 내부 서비스 인스턴스만 새 어댑터로 교체, 라우터 내 PREC 명칭을 프로젝트 명칭으로 정리 |
| 5 | score 필드 제거 및 최소 범위 수정 | `backend/schemas.py`, `backend/crud.py` | 메시지 저장 시 `score` 관련 처리만 삭제하고 나머지 로직은 변경하지 않음 |
| 6 | 환경 변수·의존성 업데이트 | `backend/requirements.txt`, `.env` 문서 | 추가 패키지 반영 시 기존 구성 영향 최소화를 위해 새 변수는 선택값으로 문서화 |
| 7 | 인제스트 절차·회귀 테스트 문서화 | `README.md`, `SETUP_GUIDE.md`, 테스트 스크립트 | 신규 유틸 실행 방법과 챗봇 기능 검사만 추가 기록하여 다른 백엔드 기능 변경을 피한 채 검증, 문서에서도 PREC 명칭을 새 이름으로 교체 |

## Detailed Update Notes (2025-10-01)
- `backend/services/rag_system/` 전체를 신설해 PREC 챗봇 로직(OpenAI 클라이언트, PDF 청크 생성, 벡터스토어, 단발성 인제스트 도구)을 프로젝트 네이밍에 맞춰 이식했습니다.
- `backend/services/rag_system_ingest.py` CLI를 추가해 `pdf_files` 테이블을 한 번 호출해 임베딩하도록 구성하고, 요약 출력 기능을 넣었습니다.
- `/api/chat` 라우터(`backend/routers/chat.py`)는 새 서비스로 교체하고, `backend/schemas.py`의 `RagSource`에 `chunk_id` 필드를 추가해 score 없이도 추적 가능하도록 했습니다.
- 관리자용 `/api/admin/process-rag`가 새 인제스트 파이프라인을 호출하도록 `backend/routers/admin.py` 및 `backend/services/scraper_service.py`를 정리했습니다.
- `backend/init_supabase.sql`의 `match_policy_chunks` 함수에서 similarity 컬럼을 제거하고, `backend/requirements.txt` 등 환경 설정을 새 구조에 맞춰 조정했습니다.
- README와 SETUP_GUIDE에 rag_system 모듈과 인제스트 절차를 문서화하고, 모든 변경 사항을 `minsu.md` 변경 로그에 반영했습니다.
