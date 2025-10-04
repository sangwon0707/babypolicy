from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..database import get_supabase
from ..auth.utils import get_current_user

router = APIRouter()

# Pydantic models
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    income: Optional[int] = None
    family_size: Optional[int] = None

class PolicyCheckUpdate(BaseModel):
    is_checked: bool

# ========================
# User Profile Endpoints
# ========================

@router.get("/profile")
async def get_user_profile(
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get user profile information"""
    try:
        response = supabase.table("user_profiles").select("*").eq("user_id", user["id"]).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            # Return empty profile if doesn't exist
            return {
                "user_id": user["id"],
                "name": None,
                "gender": None,
                "region": None,
                "income": None,
                "family_size": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update user profile information"""
    try:
        update_data = profile_data.dict(exclude_unset=True)
        update_data["user_id"] = user["id"]
        update_data["updated_at"] = datetime.now().isoformat()

        # Upsert (insert or update)
        response = supabase.table("user_profiles").upsert(update_data).execute()

        return {"message": "Profile updated successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

# ========================
# User Policies Endpoints
# ========================

@router.get("/policies")
async def get_user_policies(
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all policies saved by the user"""
    try:
        # Get user_policies with joined policy data
        response = supabase.table("user_policies")\
            .select("*, policy:policies(id, title, description, category, region)")\
            .eq("user_id", user["id"])\
            .order("created_at", desc=True)\
            .execute()

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch policies: {str(e)}")

@router.post("/policies/{policy_id}")
async def save_policy(
    policy_id: str,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Save a policy to user's favorites"""
    try:
        insert_data = {
            "user_id": user["id"],
            "policy_id": policy_id,
            "is_checked": False,
            "created_at": datetime.now().isoformat()
        }

        response = supabase.table("user_policies").insert(insert_data).execute()

        return {"message": "Policy saved successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save policy: {str(e)}")

@router.patch("/policies/{policy_id}/check")
async def toggle_policy_check(
    policy_id: str,
    is_checked: bool,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Toggle the checked status of a saved policy"""
    try:
        response = supabase.table("user_policies")\
            .update({"is_checked": is_checked})\
            .eq("user_id", user["id"])\
            .eq("policy_id", policy_id)\
            .execute()

        return {"message": "Policy status updated", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update policy status: {str(e)}")

@router.delete("/policies/{policy_id}")
async def remove_policy(
    policy_id: str,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Remove a policy from user's favorites"""
    try:
        response = supabase.table("user_policies")\
            .delete()\
            .eq("user_id", user["id"])\
            .eq("policy_id", policy_id)\
            .execute()

        return {"message": "Policy removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove policy: {str(e)}")

# ========================
# Dashboard Stats Endpoint
# ========================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get dashboard statistics for the user"""
    try:
        # Count total saved policies
        saved_policies = supabase.table("user_policies")\
            .select("*", count="exact")\
            .eq("user_id", user["id"])\
            .execute()
        total_saved = saved_policies.count or 0

        # Count checked (applied) policies
        applied_policies = supabase.table("user_policies")\
            .select("*", count="exact")\
            .eq("user_id", user["id"])\
            .eq("is_checked", True)\
            .execute()
        total_applied = applied_policies.count or 0

        # Count AI consultations (conversations)
        conversations = supabase.table("conversations")\
            .select("*", count="exact")\
            .eq("user_id", user["id"])\
            .execute()
        total_consultations = conversations.count or 0

        # Count upcoming deadlines (calendar events in the future)
        # For now, return 0 as calendar_events needs proper schema
        upcoming_deadlines = 0

        return {
            "recommended_policies": total_saved,  # Using saved policies as "recommended"
            "applied_policies": total_applied,
            "upcoming_deadlines": upcoming_deadlines,
            "ai_consultations": total_consultations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")

# ========================
# User Settings Endpoints
# ========================

@router.get("/settings")
async def get_user_settings(
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get user settings"""
    try:
        response = supabase.table("user_settings").select("*").eq("user_id", user["id"]).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            # Return default settings if doesn't exist
            return {
                "user_id": user["id"],
                "notify_policy": True,
                "notify_event": True,
                "language": "ko",
                "theme": "light"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")

@router.patch("/settings")
async def update_user_settings(
    settings_data: dict,
    user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update user settings"""
    try:
        settings_data["user_id"] = user["id"]

        # Upsert settings
        response = supabase.table("user_settings").upsert(settings_data).execute()

        return {"message": "Settings updated successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
