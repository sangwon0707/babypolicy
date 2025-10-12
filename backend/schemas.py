from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime
import uuid

# ========================
# Base & Generic
# ========================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# ========================
# User Schemas
# ========================

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: uuid.UUID
    provider: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    income: Optional[int] = None
    family_size: Optional[int] = None

    class Config:
        orm_mode = True

class UserResponse(User):
    profile: Optional[UserProfile] = None

# ========================
# Policy & RAG Schemas
# ========================

class Policy(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    eligibility: Optional[Any] = None

    class Config:
        orm_mode = True

class PolicyChunkBase(BaseModel):
    id: str
    doc_id: str
    chunk_index: int
    content: str
    metadata: Optional[dict] = None
    embedding: List[float]

class PolicyChunkCreate(PolicyChunkBase):
    pass

class PolicyChunk(PolicyChunkBase):
    class Config:
        orm_mode = True

# ========================
# Community Schemas
# ========================

class Category(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    color_code: Optional[str] = None
    icon_emoji: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str
    category_id: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    views_count: int
    likes_count: int
    comments_count: int
    author: User

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: uuid.UUID
    author_id: uuid.UUID
    post_id: uuid.UUID
    created_at: datetime
    likes_count: int
    author: User

    class Config:
        orm_mode = True

# ========================
# Chat Schemas
# ========================

class FunctionCall(BaseModel):
    name: str
    arguments: dict

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[uuid.UUID] = None

class RagSource(BaseModel):
    chunk_id: Optional[str] = None
    doc_id: str
    page: Optional[int] = None
    content: str

class ChatResponse(BaseModel):
    answer: str
    conversation_id: uuid.UUID
    sources: List[RagSource]
    function_call: Optional[FunctionCall] = None

class Conversation(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str] = None
    created_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Message(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    rag_sources: Optional[Any] = None

    class Config:
        orm_mode = True

# ========================
# Calendar Schemas
# ========================

class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    is_policy_related: bool = False

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEvent(CalendarEventBase):
    id: int
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True

# ========================
# Function Calling Schemas
# ========================

class ExecuteFunctionRequest(BaseModel):
    function_name: str
    arguments: dict
    conversation_id: Optional[uuid.UUID] = None
