# 🍼 BabyPolicy - Modern Supabase Setup Guide

## ✅ Updated Architecture

The backend now uses **Supabase Python Client** instead of direct PostgreSQL/SQLAlchemy connection.

```
Frontend (Next.js) → Backend (FastAPI + Supabase Client) → Supabase Platform
```

---

## 🎯 What Changed

### Before (Old Way):
- ❌ Direct PostgreSQL connection via SQLAlchemy
- ❌ Manual database schema management
- ❌ Complex ORM setup

### After (Modern Way):
- ✅ Supabase Python Client (`supabase-py`)
- ✅ Supabase handles schema, migrations, and more
- ✅ Simpler, more maintainable code
- ✅ Built-in features: Auth, Storage, Realtime

---

## 📋 Setup Steps

### 1. **Initialize Supabase Database**

Go to your Supabase Dashboard SQL Editor and run:

```sql
-- File: backend/init_supabase.sql
-- This creates all 15 tables + default data

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Run the rest of init_supabase.sql...
```

**Tables created:**
- users, user_profiles, user_settings
- policies, policy_chunks, user_policies
- categories (with 6 default categories), posts, comments
- post_likes, comment_likes
- conversations, messages
- calendar_events, notifications

---

### 2. **Environment Configuration**

All configuration is in **root `.env` file**:

```bash
# /Users/sangwon/Project/babypolicy/.env

# OpenAI API Key
OPENAI_API_KEY=sk-proj-...

# Supabase Settings
SUPABASE_URL=https://orccihzuolbrzkobhkgm.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...

# FastAPI Settings
HOST=0.0.0.0
PORT=8000

# CORS Settings
FRONTEND_URL=http://localhost:3000
```

**No more DATABASE_URL needed!** ✨

---

### 3. **Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- `supabase` - Supabase Python client
- `fastapi` - Web framework
- `python-dotenv` - Environment variables
- `openai` - AI/RAG features

---

### 4. **Backend Code Updates**

#### **database.py** - Now uses Supabase client
```python
from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_supabase() -> Client:
    return supabase
```

#### **crud.py** - Supabase table operations
```python
# Old SQLAlchemy way
def get_posts(db: Session, skip, limit):
    return db.query(models.Post).offset(skip).limit(limit).all()

# New Supabase way
def get_posts(supabase: Client, skip, limit):
    response = supabase.table("posts")\
        .select("*, author:users(id, email, user_profiles(name))")\
        .range(skip, skip + limit - 1)\
        .execute()
    return response.data
```

#### **Routers** - Use `get_supabase()` dependency
```python
from ..database import get_supabase

@router.get("/posts")
def get_posts(supabase: Client = Depends(get_supabase)):
    return crud.get_posts(supabase)
```

---

## 🚀 Start the Application

### Terminal 1 - Backend
```bash
cd /Users/sangwon/Project/babypolicy/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend
```bash
cd /Users/sangwon/Project/babypolicy/frontend
npm run dev
```

### Test
- Backend API: http://localhost:8000/docs
- Frontend App: http://localhost:3000

---

## 🧪 Testing the Connection

### 1. Test Supabase Connection
```bash
cd backend
python -c "
from database import supabase
result = supabase.table('categories').select('*').execute()
print(f'Found {len(result.data)} categories')
print(result.data)
"
```

Expected output:
```
Found 6 categories
[{'id': 'tips', 'label': '육아 팁', ...}, ...]
```

### 2. Test API Endpoints

Visit: http://localhost:8000/docs

Try these endpoints:
- `GET /api/community/categories` → Returns 6 default categories
- `GET /api/community/posts` → Returns posts (empty array if new)
- `POST /api/auth/register` → Create test user
- `POST /api/auth/login` → Login
- `POST /api/chat` → Send chat message (requires auth)

---

## 📁 File Structure

```
babypolicy/
├── .env                          # ✅ Single source of truth
├── backend/
│   ├── database.py              # ✅ Supabase client setup
│   ├── crud.py                  # ✅ Supabase table operations
│   ├── main.py                  # ✅ No more SQLAlchemy
│   ├── models.py                # ⚠️ Not used (kept for reference)
│   ├── routers/
│   │   ├── chat.py             # ✅ Uses Supabase
│   │   └── community.py        # ✅ Uses Supabase
│   └── init_supabase.sql       # ✅ Database initialization
└── frontend/
    ├── .env.local              # API URL config
    └── lib/api.ts              # API client (unchanged)
```

---

## 🎨 Features Working

### ✅ Fully Functional
1. **Community Page** - View posts and categories
2. **Chat Page** - AI chatbot (requires auth)
3. **Profile Page** - User profile (requires auth)
4. **Authentication** - Register/Login
5. **Database** - All 15 tables via Supabase

### 🔄 Supabase Features Available
- **Auth**: Built-in user authentication
- **Realtime**: Subscribe to database changes
- **Storage**: File uploads
- **Edge Functions**: Serverless functions
- **Vector Search**: pgvector for RAG

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check .env file exists
ls -la /Users/sangwon/Project/babypolicy/.env

# Check Supabase credentials
python -c "import os; from dotenv import load_dotenv; load_dotenv('../.env'); print(os.getenv('SUPABASE_URL'))"

# Install dependencies
pip install supabase python-dotenv fastapi
```

### "Module not found" error
```bash
cd backend
pip install -r requirements.txt
```

### Categories not showing
```bash
# Run init_supabase.sql in Supabase Dashboard
# Go to: SQL Editor → New Query → Paste script → Run
```

### Auth not working
```bash
# Check if users table exists
# Go to Supabase Dashboard → Table Editor → Check for 'users' table
```

---

## 🌟 Benefits of Supabase Approach

1. **Simpler Setup** - No database URL, just API keys
2. **Auto-migrations** - Supabase handles schema changes
3. **Built-in Auth** - Can use Supabase Auth instead of JWT
4. **Realtime** - Subscribe to live data changes
5. **Better DX** - Dashboard, logs, and monitoring
6. **Scalable** - Managed infrastructure

---

## 📚 Next Steps

### Recommended Improvements
1. **Use Supabase Auth** - Replace JWT with Supabase Auth
2. **Add Realtime** - Live updates for chat and community
3. **Implement Storage** - User avatars, file uploads
4. **Add RLS Policies** - Row Level Security for data protection
5. **Edge Functions** - Move RAG service to Supabase Edge Functions

---

## 📞 Support

### Supabase Resources
- Dashboard: https://supabase.com/dashboard/project/orccihzuolbrzkobhkgm
- Docs: https://supabase.com/docs
- Python Client: https://supabase.com/docs/reference/python

### Project Files
- Setup Guide: `SETUP_GUIDE.md`
- Verification: `COMPLETE_VERIFICATION.md`
- This File: `SUPABASE_SETUP.md`

---

**Status: ✅ Modern Supabase Integration Complete! 🎉**

The backend now uses the official Supabase Python client for a cleaner, more maintainable codebase!