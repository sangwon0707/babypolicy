from supabase import Client
import uuid
from datetime import datetime
from typing import List, Optional

from . import schemas

# =======================
# User CRUD
# =======================

def get_user(supabase: Client, user_id: str):
    response = supabase.table("users").select("*, user_profiles(*)").eq("id", user_id).execute()
    return response.data[0] if response.data else None

def get_user_by_email(supabase: Client, email: str):
    response = supabase.table("users").select("*, user_profiles(*)").eq("email", email).execute()
    return response.data[0] if response.data else None

def create_user(supabase: Client, user: schemas.UserCreate, hashed_password: str):
    # Create user
    user_data = {
        "email": user.email,
        "password": hashed_password,
    }
    response = supabase.table("users").insert(user_data).execute()
    user_id = response.data[0]["id"]

    # Create default profile
    profile_data = {
        "user_id": user_id,
        "name": user.name or user.email.split('@')[0]
    }
    supabase.table("user_profiles").insert(profile_data).execute()

    return get_user(supabase, user_id)

# =======================
# Policy CRUD
# =======================

def create_policy(supabase: Client, policy_id: str, title: str, description: str, category: str, region: str, eligibility: dict):
    policy_data = {
        "id": policy_id,
        "title": title,
        "description": description,
        "category": category,
        "region": region,
        "eligibility": eligibility
    }
    response = supabase.table("policies").insert(policy_data).execute()
    return response.data[0] if response.data else None

def create_policy_chunks(supabase: Client, chunks: list[schemas.PolicyChunkCreate]):
    chunks_data = [chunk.dict() for chunk in chunks]
    response = supabase.table("policy_chunks").insert(chunks_data).execute()
    return response.data if response.data else []

def search_relevant_chunks(supabase: Client, query_embedding: list[float], top_k: int = 5):
    """
    Performs vector similarity search on policy_chunks table.
    Requires the `pgvector` extension to be enabled in PostgreSQL.
    Uses Supabase RPC for vector search.
    """
    # Call Supabase RPC function for vector similarity search
    response = supabase.rpc('match_policy_chunks', {
        'query_embedding': query_embedding,
        'match_count': top_k
    }).execute()

    return response.data if response.data else []

# =======================
# Conversation CRUD
# =======================

def create_conversation(supabase: Client, user_id: str, title: str = "New Conversation"):
    conversation_data = {
        "user_id": user_id,
        "title": title
    }
    response = supabase.table("conversations").insert(conversation_data).execute()
    return response.data[0] if response.data else None

def create_message(supabase: Client, conversation_id: str, role: str, content: str, rag_sources: dict = None):
    message_data = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "rag_sources": rag_sources
    }
    response = supabase.table("messages").insert(message_data).execute()

    # Update conversation's last_message_at
    supabase.table("conversations").update({
        "last_message_at": datetime.now().isoformat()
    }).eq("id", conversation_id).execute()

    return response.data[0] if response.data else None

def get_conversation(supabase: Client, conversation_id: str):
    response = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    return response.data[0] if response.data else None

# =======================
# Community CRUD
# =======================

def get_posts(supabase: Client, skip: int = 0, limit: int = 10, category_id: str = None):
    query = supabase.table("posts").select("*, author:users(id, email, user_profiles(name))").order("created_at", desc=True).range(skip, skip + limit - 1)

    if category_id:
        query = query.eq("category_id", category_id)

    response = query.execute()
    return response.data if response.data else []

def create_post(supabase: Client, post: schemas.PostCreate, author_id: str):
    post_data = {
        **post.dict(),
        "author_id": author_id
    }
    response = supabase.table("posts").insert(post_data).execute()
    return response.data[0] if response.data else None

def get_post(supabase: Client, post_id: str):
    response = supabase.table("posts").select("*, author:users(id, email, user_profiles(name))").eq("id", post_id).execute()
    return response.data[0] if response.data else None

def get_comments_for_post(supabase: Client, post_id: str):
    response = supabase.table("comments").select("*, author:users(id, email, user_profiles(name))").eq("post_id", post_id).order("created_at").execute()
    return response.data if response.data else []

def create_comment(supabase: Client, comment: schemas.CommentCreate, post_id: str, author_id: str):
    comment_data = {
        **comment.dict(),
        "post_id": post_id,
        "author_id": author_id
    }
    response = supabase.table("comments").insert(comment_data).execute()

    # Update comments_count on the post
    supabase.rpc("increment_comments_count", {"post_id": post_id}).execute()

    return response.data[0] if response.data else None

def get_categories(supabase: Client):
    response = supabase.table("categories").select("*").order("sort_order").execute()
    return response.data if response.data else []
