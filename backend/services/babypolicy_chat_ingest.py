from __future__ import annotations

import argparse
import json
from typing import Optional, List

from supabase import Client

from backend.database import get_supabase
from backend.services.babypolicy_chat import get_chat_service
from backend.services.babypolicy_chat.ingest import IngestionResult, ingest_pdf_files


def _print_summary(results: List[IngestionResult]) -> None:
    totals = {}
    for item in results:
        totals[item.status] = totals.get(item.status, 0) + 1
    print()
    print("Ingestion summary:")
    for status, count in totals.items():
        print(f"  {status}: {count}")
    total_chunks = sum(item.chunks for item in results)
    print(f"  total chunks: {total_chunks}")


def run(limit: Optional[int] = None, echo: bool = False) -> List[IngestionResult]:
    supabase: Client = get_supabase()
    service = get_chat_service(supabase=supabase)
    results = ingest_pdf_files(supabase, service, limit=limit)
    if echo:
        print(json.dumps([item.__dict__ for item in results], ensure_ascii=False, indent=2))
    return results


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Ingest pdf_files into Supabase vector store.")
    parser.add_argument("--limit", type=int, default=None, help="최대 처리할 레코드 수")
    parser.add_argument("--echo", action="store_true", help="결과를 JSON 형식으로 출력")
    args = parser.parse_args(argv)

    results = run(limit=args.limit, echo=args.echo)
    _print_summary(results)


if __name__ == "__main__":
    main()
