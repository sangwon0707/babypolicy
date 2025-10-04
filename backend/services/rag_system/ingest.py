from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from supabase import Client

from .service import RagService


@dataclass
class IngestionResult:
    path: str
    policy_id: str
    chunks: int
    status: str
    message: Optional[str] = None


def _load_category(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {"raw": payload}
    return {}


def _derive_policy_id(path: Path, category: Dict[str, Any]) -> str:
    value = category.get("policy_id") if category else None
    if value:
        return str(value)
    return path.stem


def _get_pdf_directories() -> List[Path]:
    """
    .env에서 지정한 PDF 디렉토리 경로들을 반환합니다.
    환경변수가 설정되지 않은 경우 빈 리스트를 반환합니다.

    Returns:
        PDF 디렉토리 경로 리스트

    Raises:
        EnvironmentError: PDF_DIRECTORIES 환경변수가 설정되지 않은 경우
    """
    # 프로젝트 루트 경로 계산 (backend/services/babypolicy_chat -> 루트)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent

    # .env에서 PDF 디렉토리 경로 읽기 (쉼표로 구분된 여러 경로 지원)
    pdf_dirs_env = os.getenv("PDF_DIRECTORIES")

    if not pdf_dirs_env:
        raise EnvironmentError(
            "PDF_DIRECTORIES 환경변수가 설정되어야 합니다. "
            ".env 파일에 PDF_DIRECTORIES를 설정해주세요. "
            '예: PDF_DIRECTORIES="data/pdfs/bokjiro,data/pdfs/auto_scraper"'
        )

    pdf_directories = []
    for dir_path in pdf_dirs_env.split(","):
        dir_path = dir_path.strip()
        if dir_path:
            # 상대 경로를 절대 경로로 변환
            if not Path(dir_path).is_absolute():
                abs_path = project_root / dir_path
            else:
                abs_path = Path(dir_path)
            pdf_directories.append(abs_path)

    return pdf_directories


def ingest_pdf_files(
    supabase: Client,
    service: RagService,
    *,
    limit: Optional[int] = None,
    policy_id: Optional[str] = None,
) -> List[IngestionResult]:
    """
    환경변수로 지정된 PDF 디렉토리들을 스캔하여 모든 PDF 파일을 임베딩합니다.
    pdf_files 테이블 대신 파일시스템을 직접 읽습니다.

    Args:
        supabase: Supabase 클라이언트
        service: RagService 인스턴스
        limit: 처리할 최대 PDF 수 (None이면 전체)
        policy_id: 특정 policy_id만 처리 (None이면 전체)

    Returns:
        IngestionResult 리스트
    """
    results: List[IngestionResult] = []
    pdf_directories = _get_pdf_directories()

    total_processed = 0

    for pdf_dir in pdf_directories:
        if not pdf_dir.exists():
            results.append(
                IngestionResult(
                    path=str(pdf_dir),
                    policy_id="",
                    chunks=0,
                    status="skipped",
                    message=f"디렉토리가 존재하지 않습니다: {pdf_dir}",
                )
            )
            continue

        if not pdf_dir.is_dir():
            results.append(
                IngestionResult(
                    path=str(pdf_dir),
                    policy_id="",
                    chunks=0,
                    status="skipped",
                    message=f"폴더가 아닙니다: {pdf_dir}",
                )
            )
            continue

        # 디렉토리 이름을 카테고리로 사용 (bokjiro, auto_scraper 등)
        category_name = pdf_dir.name

        # 모든 PDF 파일 찾기
        pdf_candidates = sorted(pdf_dir.glob("**/*.pdf"))

        if not pdf_candidates:
            results.append(
                IngestionResult(
                    path=str(pdf_dir),
                    policy_id="",
                    chunks=0,
                    status="skipped",
                    message=f"PDF 파일이 없습니다: {pdf_dir}",
                )
            )
            continue

        # 각 PDF 파일 처리
        for pdf_path in pdf_candidates:
            # limit 체크
            if limit is not None and total_processed >= limit:
                break

            # policy_id 생성: category-filename
            file_stem = pdf_path.stem
            derived_policy_id = f"{category_name}-{file_stem}"

            # 특정 policy_id 필터링
            if policy_id and derived_policy_id != policy_id:
                continue

            # 정책 제목은 파일명 사용
            policy_title = file_stem.replace("_", " ").replace("-", " ")

            try:
                ingest_result = service.ingest_pdf(
                    path=pdf_path,
                    policy_id=derived_policy_id,
                    policy_title=policy_title,
                    metadata={
                        "category": category_name,
                        "source": "filesystem",
                        "directory": str(pdf_dir),
                    },
                )
                results.append(
                    IngestionResult(
                        path=str(pdf_path),
                        policy_id=derived_policy_id,
                        chunks=len(ingest_result.chunks),
                        status="success",
                    )
                )
                total_processed += 1

            except FileNotFoundError as exc:
                results.append(
                    IngestionResult(
                        path=str(pdf_path),
                        policy_id=derived_policy_id,
                        chunks=0,
                        status="missing",
                        message=str(exc),
                    )
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                results.append(
                    IngestionResult(
                        path=str(pdf_path),
                        policy_id=derived_policy_id,
                        chunks=0,
                        status="error",
                        message=str(exc),
                    )
                )

            # limit 체크
            if limit is not None and total_processed >= limit:
                break

    return results
