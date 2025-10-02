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


def ingest_pdf_files(
    supabase: Client,
    service: BabyPolicyChatService,
    *,
    limit: Optional[int] = None,
    policy_id: Optional[str] = None,
) -> List[IngestionResult]:
    response = supabase.table("pdf_files").select("*").execute()
    records = response.data or []
    results: List[IngestionResult] = []

    for idx, record in enumerate(records):
        if limit is not None and idx >= limit:
            break

        path_value = record.get("path")
        if not path_value:
            results.append(
                IngestionResult(
                    path="",
                    policy_id="",
                    chunks=0,
                    status="skipped",
                    message="path 필드가 비어 있습니다.",
                )
            )
            continue

        path = Path(path_value).expanduser()
        category_payload = _load_category(record.get("category"))
        derived_policy_id = _derive_policy_id(path, category_payload)
        policy_title = str(category_payload.get("title") or derived_policy_id)

        if policy_id and derived_policy_id != policy_id:
            continue

        try:
            ingest_result = service.ingest_pdf(
                path=path,
                policy_id=derived_policy_id,
                policy_title=policy_title,
                metadata=category_payload,
            )
            results.append(
                IngestionResult(
                    path=str(path),
                    policy_id=derived_policy_id,
                    chunks=len(ingest_result.chunks),
                    status="success",
                )
            )
        except FileNotFoundError as exc:
            results.append(
                IngestionResult(
                    path=str(path),
                    policy_id=derived_policy_id,
                    chunks=0,
                    status="missing",
                    message=str(exc),
                )
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            results.append(
                IngestionResult(
                    path=str(path),
                    policy_id=derived_policy_id,
                    chunks=0,
                    status="error",
                    message=str(exc),
                )
            )
    return results
