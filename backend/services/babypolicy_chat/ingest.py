from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from supabase import Client

from .service import BabyPolicyChatService


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


def _build_data_policy_identity(pdf_path: Path, data_root: Path) -> tuple[str, str, Dict[str, Any]]:
    relative = pdf_path.relative_to(data_root)
    id_parts = [part.replace(" ", "_") for part in relative.with_suffix("").parts]
    policy_id = f"data-{'-'.join(id_parts)}".lower()
    policy_title = pdf_path.stem
    metadata = {
        "relative_path": str(relative),
        "source": "data_directory",
    }
    return policy_id, policy_title, metadata


def ingest_pdf_files(
    supabase: Client,
    service: BabyPolicyChatService,
    *,
    limit: Optional[int] = None,
    policy_id: Optional[str] = None,
) -> List[IngestionResult]:
    module_path = Path(__file__).resolve()
    project_root = module_path.parents[3]
    data_root = project_root / "data"

    if not data_root.exists():
        return [
            IngestionResult(
                path=str(data_root),
                policy_id="",
                chunks=0,
                status="error",
                message="data 폴더를 찾을 수 없습니다.",
            )
        ]

    pdf_candidates = sorted(data_root.rglob("*.pdf"))
    if not pdf_candidates:
        return [
            IngestionResult(
                path=str(data_root),
                policy_id="",
                chunks=0,
                status="error",
                message="data 폴더에 PDF 파일이 없습니다.",
            )
        ]

    results: List[IngestionResult] = []

    for pdf_path in pdf_candidates:
        if limit is not None and len(results) >= limit:
            break

        derived_policy_id, policy_title, metadata = _build_data_policy_identity(
            pdf_path, data_root
        )

        if policy_id and derived_policy_id != policy_id:
            continue

        try:
            ingest_result = service.ingest_pdf(
                path=pdf_path,
                policy_id=derived_policy_id,
                policy_title=policy_title,
                metadata=metadata,
            )
            results.append(
                IngestionResult(
                    path=str(pdf_path),
                    policy_id=derived_policy_id,
                    chunks=len(ingest_result.chunks),
                    status="success",
                )
            )
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
    return results


# ---------------------------------------------------------------------------
# Below is the previous Supabase-based ingestion flow preserved for reference.
# Uncomment and adjust if you need to restore database-driven ingestion.
# ---------------------------------------------------------------------------

# def ingest_pdf_files(
#     supabase: Client,
#     service: BabyPolicyChatService,
#     *,
#     limit: Optional[int] = None,
#     policy_id: Optional[str] = None,
# ) -> List[IngestionResult]:
#     response = supabase.table("pdf_files").select("*").execute()
#     records = response.data or []
#     results: List[IngestionResult] = []
#
#     for idx, record in enumerate(records):
#         if limit is not None and idx >= limit:
#             break
#
#         path_value = record.get("path")
#         if not path_value:
#             results.append(
#                 IngestionResult(
#                     path="",
#                     policy_id="",
#                     chunks=0,
#                     status="skipped",
#                     message="path 필드가 비어 있습니다.",
#                 )
#             )
#             continue
#
#         path = _resolve_ingest_path(path_value)
#         category_payload = _load_category(record.get("category"))
#         derived_policy_id = _derive_policy_id(path, category_payload)
#         policy_title = str(category_payload.get("title") or derived_policy_id)
#
#         if policy_id and derived_policy_id != policy_id:
#             continue
#
#         if not path.exists():
#             results.append(
#                 IngestionResult(
#                     path=str(path),
#                     policy_id=derived_policy_id,
#                     chunks=0,
#                     status="missing",
#                     message="경로를 찾을 수 없습니다.",
#                 )
#             )
#             continue
#
#         if path.is_dir():
#             results.append(
#                 IngestionResult(
#                     path=str(path),
#                     policy_id=derived_policy_id,
#                     chunks=0,
#                     status="skipped",
#                     message="PDF 파일 경로 대신 디렉터리가 제공되었습니다.",
#                 )
#             )
#             continue
#
#         try:
#             ingest_result = service.ingest_pdf(
#                 path=path,
#                 policy_id=derived_policy_id,
#                 policy_title=policy_title,
#                 metadata=category_payload,
#             )
#             results.append(
#                 IngestionResult(
#                     path=str(path),
#                     policy_id=derived_policy_id,
#                     chunks=len(ingest_result.chunks),
#                     status="success",
#                 )
#             )
#         except FileNotFoundError as exc:
#             results.append(
#                 IngestionResult(
#                     path=str(path),
#                     policy_id=derived_policy_id,
#                     chunks=0,
#                     status="missing",
#                     message=str(exc),
#                 )
#             )
#         except Exception as exc:  # pragma: no cover - defensive logging
#             results.append(
#                 IngestionResult(
#                     path=str(path),
#                     policy_id=derived_policy_id,
#                     chunks=0,
#                     status="error",
#                     message=str(exc),
#                 )
#             )
#     return results
