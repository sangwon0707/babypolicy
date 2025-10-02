# 🍼 BabyPolicy Setup Guide

## 📋 Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- OpenAI API key

---

## 🗄️ Step 1: Setup Supabase Database

### 1.1 Get Your Supabase Credentials
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `orccihzuolbrzkobhkgm`
3. Get your database password from **Settings** → **Database** → **Database Password**

### 1.2 Initialize Database Tables
1. In Supabase Dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the entire content from `backend/init_supabase.sql`
4. Click **Run** to create all tables
5. Verify tables were created in **Table Editor**

✅ You should see tables: users, user_profiles, policies, posts, categories, conversations, messages, etc.

---

## ⚙️ Step 2: Configure Backend

### 2.1 Update Backend Environment Variables
Open `/Users/sangwon/Project/babypolicy/backend/.env` and update:

```bash
DATABASE_URL="postgresql://postgres.orccihzuolbrzkobhkgm:[YOUR-DB-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
```

Replace `[YOUR-DB-PASSWORD]` with your actual Supabase database password.

### 2.2 Install Backend Dependencies
```bash
cd /Users/sangwon/Project/babypolicy/backend
pip install -r requirements.txt
```

### 2.3 Start Backend Server
```bash
# Make sure you're in the backend directory
cd /Users/sangwon/Project/babypolicy/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

---

## 🎨 Step 3: Configure Frontend

### 3.1 Install Frontend Dependencies
```bash
cd /Users/sangwon/Project/babypolicy/frontend
npm install
```

### 3.2 Start Frontend Development Server
```bash
cd /Users/sangwon/Project/babypolicy/frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

---

## 🧪 Step 4: Test the Application

### 4.1 Test Backend API
Visit: `http://localhost:8000/docs`
- Try the `/api/community/categories` endpoint
- Should return 6 default categories

### 4.2 Test Frontend
1. Open browser: `http://localhost:3000`
2. You should see a cute welcome page with:
   - 👶 Baby icon
   - Pink/purple/blue gradients
   - Floating emoji decorations
   - Korean text

### 4.3 Test Full Stack Integration

**Without Login (Browse Mode):**
- ✅ Home page works
- ✅ Community page loads (shows "로딩 중..." then posts)
- ✅ Chat page shows welcome message
- ⚠️ Sending chat messages requires login

**With Login:**
1. Register a new account at `/register`
2. Login at `/login`
3. Try sending a chat message
4. Create a community post
5. View your profile at `/me`

---

## 📁 Project Structure

```
babypolicy/
├── frontend/                    # Next.js frontend
│   ├── app/
│   │   ├── page.tsx            # 🏠 Home (cute welcome)
│   │   ├── chat/page.tsx       # 💬 Chat with AI
│   │   ├── community/page.tsx  # 👨‍👩‍👧‍👦 Community
│   │   └── me/page.tsx         # 👤 Profile
│   ├── components/
│   │   └── BottomNav.tsx       # 🧭 Navigation
│   ├── lib/
│   │   └── api.ts              # 🔌 API client
│   └── .env.local              # Frontend config
│
├── backend/                     # FastAPI backend
│   ├── main.py                 # Main app
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── crud.py                 # Database operations
│   ├── database.py             # DB connection
│   ├── routers/
│   │   ├── chat.py            # Chat endpoints
│   │   └── community.py       # Community endpoints
│   ├── services/
│   │   ├── rag_system/       # PREC 기반 챗봇 서비스 모듈
│   │   └── rag_system_ingest.py # pdf_files → 벡터스토어 인제스트 스크립트
│   ├── init_supabase.sql      # DB initialization
│   └── .env                    # Backend config
│
└── table-ref.md                # Database schema reference
```

---

## 🎨 Design Features

### Color Theme
- **Primary**: Pink (#FF9ECD)
- **Secondary**: Blue (#B4E4FF)
- **Accent**: Purple (#F0E6FF)
- **Background**: Gradient (Pink → Blue → Purple)

### UI Elements
- ✨ Floating emoji animations
- 🎭 Glassmorphism effects
- 🌈 Gradient buttons
- 🔘 Rounded corners (1rem radius)
- 💫 Smooth transitions
- 👶 Baby-friendly emojis everywhere

### Pages
1. **Home** - Welcome screen with floating decorations
2. **Chat** - AI chatbot with cute bubbles
3. **Community** - Post feed with categories
4. **Profile** - User info and settings

---

## 🔧 Troubleshooting

### Backend won't start
- ✅ Check DATABASE_URL has correct password
- ✅ Run `pip install -r requirements.txt`
- ✅ Check Supabase tables exist

### Frontend API errors
- ✅ Backend must be running on port 8000
- ✅ Check `.env.local` has correct API URL
- ✅ Check browser console for errors

### Chat not working
- ✅ OpenAI API key must be set in backend/.env
- ✅ User must be logged in
- ✅ Check backend logs for errors

### Community page shows no posts
- ✅ This is normal for new database
- ✅ Create a test post via API docs or app
- ✅ Check categories were inserted

---

## 🚀 Next Steps

1. **Authentication**: Implement login/register pages
2. **RAG Service**: Configure vector embeddings for policy search
3. **Deploy**: Deploy to Vercel (frontend) + Railway/Fly.io (backend)
4. **Add Features**:
   - Calendar for policy deadlines
   - Push notifications
   - More community features
   - Policy bookmarking

---

## 📞 Support

For issues or questions:
1. Check backend logs: `uvicorn` console output
2. Check frontend logs: Browser console (F12)
3. Test API endpoints: `http://localhost:8000/docs`

---

**Happy coding! 👶💕**
