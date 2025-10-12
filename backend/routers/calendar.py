from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List

from ..database import get_supabase
from ..auth.utils import get_current_user
from .. import schemas, crud

router = APIRouter()

# ========================
# Calendar Event Endpoints
# ========================

@router.get("/events", response_model=List[schemas.CalendarEvent])
async def get_calendar_events(
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all calendar events for the current user"""
    try:
        events = crud.get_user_calendar_events(supabase, user["user_id"])
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")

@router.post("/events", response_model=schemas.CalendarEvent)
async def create_calendar_event(
    event: schemas.CalendarEventCreate,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Create a new calendar event"""
    try:
        new_event = crud.create_calendar_event(supabase, event, user["user_id"])
        if not new_event:
            raise HTTPException(status_code=500, detail="Failed to create calendar event")
        return new_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")

@router.get("/events/{event_id}", response_model=schemas.CalendarEvent)
async def get_calendar_event(
    event_id: int,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get a specific calendar event"""
    try:
        event = crud.get_calendar_event(supabase, event_id, user["user_id"])
        if not event:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar event: {str(e)}")

@router.put("/events/{event_id}", response_model=schemas.CalendarEvent)
async def update_calendar_event(
    event_id: int,
    event: schemas.CalendarEventCreate,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update a calendar event"""
    try:
        updated_event = crud.update_calendar_event(supabase, event_id, user["user_id"], event)
        if not updated_event:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        return updated_event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update calendar event: {str(e)}")

@router.delete("/events/{event_id}")
async def delete_calendar_event(
    event_id: int,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete a calendar event"""
    try:
        crud.delete_calendar_event(supabase, event_id, user["user_id"])
        return {"message": "Calendar event deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete calendar event: {str(e)}")
