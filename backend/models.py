from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    BigInteger,
    Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid
from pgvector.sqlalchemy import Vector

# ========================
# 1. 사용자 관리
# ========================

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text) # Added for authentication
    provider = Column(Text) # google, github, kakao 등
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    settings = relationship("UserSetting", back_populates="user", uselist=False, cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    conversations = relationship("Conversation", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    name = Column(Text)
    gender = Column(Text)
    region = Column(Text)
    income = Column(Integer)
    family_size = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    user = relationship("User", back_populates="profile")

class UserSetting(Base):
    __tablename__ = "user_settings"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    notify_policy = Column(Boolean, default=True)
    notify_event = Column(Boolean, default=True)
    language = Column(Text, default='ko')
    theme = Column(Text, default='light')

    user = relationship("User", back_populates="settings")

# ========================
# 2. 정책 + RAG
# ========================

class Policy(Base):
    __tablename__ = "policies"
    id = Column(Text, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(Text)
    region = Column(Text)
    eligibility = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("PolicyChunk", back_populates="policy", cascade="all, delete-orphan")

class PolicyChunk(Base):
    __tablename__ = "policy_chunks"
    id = Column(Text, primary_key=True)
    doc_id = Column(Text, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text)
    metadata = Column(JSON)
    embedding = Column(Vector(1024))

    policy = relationship("Policy", back_populates="chunks")

class UserPolicy(Base):
    __tablename__ = "user_policies"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    policy_id = Column(Text, ForeignKey("policies.id", ondelete="CASCADE"), primary_key=True)
    is_checked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ========================
# 3. 커뮤니티
# ========================

class Category(Base):
    __tablename__ = "categories"
    id = Column(String(50), primary_key=True)
    label = Column(String(100), nullable=False)
    description = Column(Text)
    color_code = Column(String(7))
    icon_emoji = Column(String(10))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    status = Column(String(20), default='published')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    published_at = Column(DateTime(timezone=True))

    author = relationship("User", back_populates="posts")
    category = relationship("Category")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id])

class PostLike(Base):
    __tablename__ = "post_likes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CommentLike(Base):
    __tablename__ = "comment_likes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ========================
# 4. 대화 & 메시지
# ========================

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200))
    conversation_type = Column(String(30), default='general')
    is_archived = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    topics_discussed = Column(JSON) # Using JSON for TEXT[]
    user_context = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(30), default='text')
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    rag_sources = Column(JSON)
    extracted_entities = Column(JSON)
    confidence_score = Column(Float)
    action_buttons = Column(JSON)

    conversation = relationship("Conversation", back_populates="messages")

# ========================
# 5. 캘린더 & 알림
# ========================

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(Text)
    description = Column(Text)
    event_date = Column(DateTime(timezone=True))
    is_policy_related = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(BigInteger, ForeignKey("calendar_events.id", ondelete="CASCADE"))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
