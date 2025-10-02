from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from pydantic import BaseModel
from typing import Optional

from ..database import get_supabase
from ..services import scraper_service
from ..services.babypolicy_chat import get_chat_service
from ..services.babypolicy_chat.ingest import ingest_pdf_files
from ..auth.utils import get_current_user

router = APIRouter()

class ScraperRequest(BaseModel):
    max_policies: Optional[int] = 5
    skip_rag: bool = True  # By default, only scrape PDFs without RAG processing

class RagProcessRequest(BaseModel):
    policy_id: Optional[str] = None  # If None, process all unprocessed PDFs

@router.post("/run-scraper", status_code=status.HTTP_202_ACCEPTED)
def run_scraper_endpoint(
    request: ScraperRequest,
    supabase: Client = Depends(get_supabase),
    # Placeholder for admin user check
    # current_user: dict = Depends(get_current_user)
):
    """
    Triggers the web scraping process to download PDFs only.
    RAG processing should be done separately via /process-rag endpoint.
    """
    # Admin check placeholder
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=403, detail="Not authorized")

    # For now, running synchronously. In production, use background tasks.
    result = scraper_service.run_scraping(supabase, max_policies=request.max_policies, skip_rag=request.skip_rag)

    return {"message": "Scraping process started.", "details": result}

@router.post("/process-rag", status_code=status.HTTP_202_ACCEPTED)
def process_rag_endpoint(
    request: RagProcessRequest,
    supabase: Client = Depends(get_supabase),
):
    """
    Process downloaded PDFs with RAG (embedding and vector storage).
    Can process a specific policy or all unprocessed PDFs.
    """
    chat_service = get_chat_service(supabase=supabase)
    results = ingest_pdf_files(supabase, chat_service, policy_id=request.policy_id)
    payload = [result.__dict__ for result in results]
    return {"message": "PDF ingestion completed.", "details": payload}
