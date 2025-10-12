from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List

from .. import crud, schemas
from ..database import get_supabase
from ..auth.utils import get_current_user

router = APIRouter()

@router.get("/categories")
def get_categories(supabase: Client = Depends(get_supabase)):
    return crud.get_categories(supabase)

@router.get("/posts/popular")
def get_popular_posts(
    limit: int = 2,
    supabase: Client = Depends(get_supabase)
):
    """Get most popular posts by views count."""
    return crud.get_popular_posts(supabase, limit=limit)

@router.get("/posts")
def get_posts(
    skip: int = 0,
    limit: int = 10,
    category_id: str = None,
    supabase: Client = Depends(get_supabase)
):
    return crud.get_posts(supabase, skip=skip, limit=limit, category_id=category_id)

@router.post("/posts")
def create_post(
    post: schemas.PostCreate,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    return crud.create_post(supabase=supabase, post=post, author_id=user_id)

@router.get("/posts/{post_id}")
def get_post(post_id: str, supabase: Client = Depends(get_supabase)):
    db_post = crud.get_post(supabase, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.get("/posts/{post_id}/comments")
def get_comments_for_post(post_id: str, supabase: Client = Depends(get_supabase)):
    return crud.get_comments_for_post(supabase, post_id=post_id)

@router.post("/posts/{post_id}/comments")
def create_comment_for_post(
    post_id: str,
    comment: schemas.CommentCreate,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    return crud.create_comment(supabase=supabase, comment=comment, post_id=post_id, author_id=user_id)

@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Toggle like on a post. Returns liked status."""
    user_id = current_user["user_id"]
    is_liked = crud.toggle_post_like(supabase, post_id=post_id, user_id=user_id)
    return {"liked": is_liked}

@router.get("/posts/{post_id}/liked")
def check_liked(
    post_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Check if current user has liked the post."""
    user_id = current_user["user_id"]
    is_liked = crud.check_post_liked(supabase, post_id=post_id, user_id=user_id)
    return {"liked": is_liked}
