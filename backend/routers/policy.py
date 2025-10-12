from fastapi import APIRouter, Depends
from supabase import Client

from .. import crud
from ..database import get_supabase

router = APIRouter()

@router.get("/policies")
def get_policies(
    limit: int = 5,
    supabase: Client = Depends(get_supabase)
):
    """Get policies for banner display."""
    return crud.get_policies(supabase, limit=limit)
