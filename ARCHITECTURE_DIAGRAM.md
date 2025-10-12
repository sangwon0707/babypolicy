# BabyPolicy - 기술 스택 아키텍처 다이어그램

## 📋 프로젝트 개요
BabyPolicy는 AI 기반 육아 정책 추천 시스템으로, RAG(Retrieval-Augmented Generation)와 OpenAI Function Calling을 활용하여 맞춤형 정책 정보를 제공합니다.

---

## 🏗️ 전체 아키텍처 구조 (상세 연결도)

```
                    ┌──────────────────────────────┐
                    │   🔄 Version Control         │
                    │      GitHub Repository       │
                    │   - Source Code              │
                    │   - CI/CD Workflows          │
                    │   - Issue Tracking           │
                    └──────────┬───────────────────┘
                               │ Git Push/Pull
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
    ┌────────────────────┐      ┌────────────────────┐
    │   개발자 (Dev)      │      │  배포 환경 (Deploy) │
    │   - Local Dev      │      │  - Vercel (FE)     │
    │   - Code Review    │      │  - Cloud (BE)      │
    └────────────────────┘      └────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                          사용자 레이어 (User)                          │
│                   💻 Desktop / 📱 Mobile / 🖥️ Tablet                 │
└───────────────────────────┬───────────────────────────────────────────┘
                            │ HTTPS (TLS 1.3)
                            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    프론트엔드 레이어 (Frontend)                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Next.js 15 + React 19 + TypeScript                             │ │
│  │  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │ │
│  │  │  App Router  │  UI/UX       │  State Mgmt  │  API Client  │ │ │
│  │  │  (RSC)       │  Tailwind    │  Context API │  Fetch/Axios │ │ │
│  │  │              │  Radix UI    │              │              │ │ │
│  │  └──────────────┴──────────────┴──────────────┴──────────────┘ │ │
│  │                                                                  │ │
│  │  페이지 구조:                                                     │ │
│  │  / → 홈 (배너, 인기글)                                           │ │
│  │  /chat → AI 정책 상담                                            │ │
│  │  /community → 커뮤니티                                           │ │
│  │  /me/calendar → 캘린더                                           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────┬────────────┬─────────────┬───────────────┬──────────────────┘
        │            │             │               │
        │ REST API   │ REST API    │ REST API      │ REST API
        │ /auth      │ /chat       │ /community    │ /calendar
        ▼            ▼             ▼               ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     백엔드 레이어 (Backend)                            │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  FastAPI + Python 3.13 + Uvicorn (ASGI)                         │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │  라우터 계층 (Router Layer)                               │  │ │
│  │  │  /auth /chat /community /calendar /user /admin /policy   │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  │                            ▼                                     │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │  비즈니스 로직 계층 (Business Logic)                      │  │ │
│  │  │  ┌──────────┬──────────┬──────────┬───────────────────┐  │  │ │
│  │  │  │  Auth    │   RAG    │ Function │   Scraper         │  │  │ │
│  │  │  │  Service │  System  │ Calling  │   Service         │  │  │ │
│  │  │  ├──────────┼──────────┼──────────┼───────────────────┤  │  │ │
│  │  │  │ JWT      │ Vector   │ Calendar │   Selenium        │  │  │ │
│  │  │  │ Passlib  │ Embed    │ Auto     │   WebDriver       │  │  │ │
│  │  │  │ Token    │ Rerank   │ Schedule │   PDF Parser      │  │  │ │
│  │  │  └──────────┴──────────┴──────────┴───────────────────┘  │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  │                            ▼                                     │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │  데이터 접근 계층 (Data Access Layer)                     │  │ │
│  │  │  CRUD 함수 (crud.py) + Supabase Client                   │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────┬────────┬──────────┬──────────┬────────────┬──────────────────┘
       │        │          │          │            │
       │        │          │          │            │ Web Scraping
       │        │          │          │            ▼
       │        │          │          │   ┌────────────────────────┐
       │        │          │          │   │  정책 데이터 소스       │
       │        │          │          │   │  - bokjiro.go.kr      │
       │        │          │          │   │  - 정책브리핑          │
       │        │          │          │   │  - 정부24             │
       │        │          │          │   └────────────────────────┘
       │        │          │          │
       │ SQL    │ SQL      │ API Call │ API Call
       │ Query  │ Vector   │ Chat     │ Embedding
       ▼        ▼          ▼          ▼
┌────────────────────────────────────────────────────────────────────┐
│              데이터베이스 & 외부 서비스 레이어                       │
│                                                                     │
│  ┌─────────────────────────────────┐  ┌────────────────────────┐  │
│  │   Supabase (PostgreSQL)         │  │   OpenAI API          │  │
│  │   ┌───────────────────────────┐ │  │   ┌────────────────┐  │  │
│  │   │  Database                 │ │  │   │  GPT-4o-mini   │  │  │
│  │   │  - PostgreSQL 15          │ │  │   │  - Chat API    │  │  │
│  │   │  - pgvector Extension     │ │  │   │  - Streaming   │  │  │
│  │   │                           │ │  │   │  - Function    │  │  │
│  │   │  Tables:                  │ │  │   │    Calling     │  │  │
│  │   │  ├─ users                 │ │  │   └────────────────┘  │  │
│  │   │  ├─ user_profiles         │ │  │                       │  │
│  │   │  ├─ policies              │ │  │   ┌────────────────┐  │  │
│  │   │  ├─ policy_chunks         │ │  │   │  Embedding     │  │  │
│  │   │  │  (+ vector embeddings)│ │  │   │  BGE-M3-Korean │  │  │
│  │   │  ├─ conversations         │ │  │   │  512 dim       │  │  │
│  │   │  ├─ messages              │ │  │   └────────────────┘  │  │
│  │   │  ├─ categories            │ │  └────────────────────────┘  │
│  │   │  ├─ posts                 │ │                              │
│  │   │  ├─ comments              │ │                              │
│  │   │  ├─ post_likes            │ │                              │
│  │   │  └─ calendar_events       │ │                              │
│  │   │                           │ │                              │
│  │   │  RPC Functions:           │ │                              │
│  │   │  - match_policy_chunks    │ │                              │
│  │   │  - increment_views_count  │ │                              │
│  │   │  - increment_likes_count  │ │                              │
│  │   └───────────────────────────┘ │                              │
│  │                                 │                              │
│  │   ┌───────────────────────────┐ │                              │
│  │   │  Auth                     │ │                              │
│  │   │  - JWT Validation         │ │                              │
│  │   │  - Row Level Security     │ │                              │
│  │   └───────────────────────────┘ │                              │
│  └─────────────────────────────────┘                              │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 계층별 상세 기술 스택

### 1️⃣ 프론트엔드 레이어 (Frontend Layer)

#### 핵심 프레임워크
- **Next.js 15.5.4** - React 메타 프레임워크, App Router
- **React 19.1.0** - UI 라이브러리
- **TypeScript 5** - 정적 타입 시스템

#### UI/UX 라이브러리
- **Tailwind CSS 4** - 유틸리티 우선 CSS 프레임워크
- **Lucide React** - 아이콘 라이브러리
- **Radix UI** - 접근성 중심 컴포넌트 라이브러리
  - @radix-ui/react-label
  - @radix-ui/react-slot
- **Class Variance Authority** - 조건부 클래스 관리
- **Tailwind Merge** - Tailwind 클래스 병합
- **Tailwind Animate** - 애니메이션 유틸리티

#### 주요 페이지 구조
```
/                    - 홈 (배너, 인기글)
/chat               - AI 정책 상담
/community          - 육아 커뮤니티
/community/[id]     - 게시글 상세
/me                 - 마이페이지
/me/calendar        - 일정 관리
/login              - 로그인
/signup             - 회원가입
```

---

### 2️⃣ 백엔드 레이어 (Backend Layer)

#### 핵심 프레임워크
- **FastAPI** - 현대적인 Python 웹 프레임워크
- **Uvicorn** - ASGI 서버
- **Python-dotenv** - 환경 변수 관리

#### 데이터베이스 & ORM
- **Supabase Client** - PostgreSQL 클라이언트
- **SQLAlchemy** - Python ORM
- **psycopg2-binary** - PostgreSQL 어댑터
- **pgvector** - 벡터 검색 확장

#### RAG & AI 시스템
- **OpenAI Python SDK** - GPT-4 API 클라이언트
- **Sentence Transformers** - 임베딩 모델
- **BGE-M3-Korean** - 한국어 임베딩 모델
- **pypdf** - PDF 파싱

#### 인증 시스템
- **python-jose** - JWT 토큰 생성/검증
- **passlib[bcrypt]** - 비밀번호 해싱

#### 스크래퍼 시스템
- **Selenium** - 웹 자동화
- **Webdriver Manager** - 드라이버 관리

#### 기타 유틸리티
- **python-multipart** - 파일 업로드
- **httpx** - 비동기 HTTP 클라이언트

#### API 엔드포인트 구조
```
/api/auth           - 인증 (로그인, 회원가입, 프로필)
/api/chat           - RAG 기반 정책 상담
/api/chat/execute-function - Function Calling 실행
/api/conversations  - 대화 내역 관리
/api/community      - 커뮤니티 게시판
/api/community/posts/popular - 인기글
/api/calendar       - 일정 관리 CRUD
/api/policies       - 정책 조회
/api/user           - 사용자 정보 관리
/api/admin          - 관리자 기능
```

---

### 3️⃣ 데이터베이스 레이어 (Database Layer)

#### Supabase PostgreSQL
- **pgvector 확장** - 벡터 유사도 검색
- **RPC 함수** - 벡터 검색, 조회수/좋아요 카운터

#### 주요 테이블
```sql
-- 사용자 관련
users              (id, email, password, created_at)
user_profiles      (user_id, name, gender, region, children_info)
user_settings      (user_id, notify_policy, language, theme)

-- 정책 관련
policies           (id, title, description, category, region, eligibility)
policy_chunks      (id, policy_id, content, embedding, metadata)
user_policies      (user_id, policy_id, is_checked)

-- 대화 관련
conversations      (id, user_id, title, created_at, last_message_at)
messages           (id, conversation_id, role, content, rag_sources)

-- 커뮤니티 관련
categories         (id, name, description, sort_order)
posts              (id, author_id, category_id, title, content, views_count, likes_count)
comments           (id, post_id, author_id, content, parent_id)
post_likes         (post_id, user_id)

-- 캘린더 관련
calendar_events    (id, user_id, title, description, event_date, is_policy_related)
```

---

### 4️⃣ 외부 서비스 (External Services)

#### OpenAI API
- **GPT-4 Chat Completion** - 자연어 대화 생성
- **Embeddings API** - 텍스트 벡터화
- **Function Calling** - 구조화된 함수 호출
  - `add_calendar_event` - 날짜 감지 시 자동 일정 추가

#### 정책 데이터 소스
- **복지로 (bokjiro.go.kr)** - 정부 복지 정책
- **정책브리핑** - 최신 정책 뉴스

---

## 🔄 데이터 흐름 (Data Flow)

### 1. 사용자 질문 → AI 답변 → 캘린더 자동 추가 흐름
```
┌─────────────────────────────────────────────────────────────────┐
│ User: "2025년 12월 25일에 출산 예정인데 받을 수 있는 지원금은?" │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Frontend (Next.js)                                              │
│ - 사용자 입력 수집                                               │
│ - POST /api/chat { message, conversation_id }                  │
│ - Authorization: Bearer {JWT_TOKEN}                            │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTPS
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Backend - Auth Middleware                                       │
│ 1. JWT 토큰 검증                                                │
│ 2. user_id 추출                                                 │
│ 3. 권한 확인                                                    │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Backend - Chat Router (/api/chat)                              │
│ 1. 대화 내역 조회 (최근 10개)                                    │
│    SELECT * FROM messages WHERE conversation_id = ?            │
│ 2. RAG Service 호출                                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ RAG Service - Step 1: Vector Search                            │
│ 1. 질문 임베딩 생성                                              │
│    OpenAI Embedding API (BGE-M3-Korean)                        │
│    Input: "2025년 12월 25일에 출산 예정인데..."                 │
│    Output: [0.123, -0.456, ..., 0.789] (512 dim)              │
│                                                                 │
│ 2. pgvector 유사도 검색                                          │
│    SELECT * FROM policy_chunks                                 │
│    ORDER BY embedding <=> $1 LIMIT 50                          │
│    (코사인 유사도 계산)                                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ RAG Service - Step 2: Reranking                                │
│ - Top 50개 청크를 Top 8개로 정밀 필터링                          │
│ - 의미적 관련성 점수 재계산                                      │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ RAG Service - Step 3: Context Building                         │
│ - 8개 청크를 텍스트로 조합                                        │
│ - 시스템 프롬프트 + 컨텍스트 + 사용자 질문 결합                   │
│ - Function Tool 정의 추가 (add_calendar_event)                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ OpenAI API Call                                                 │
│ POST https://api.openai.com/v1/chat/completions                │
│ {                                                               │
│   "model": "gpt-4o-mini",                                       │
│   "messages": [...],                                            │
│   "tools": [{                                                   │
│     "type": "function",                                         │
│     "function": {                                               │
│       "name": "add_calendar_event",                             │
│       "description": "날짜를 캘린더에 추가",                      │
│       "parameters": {...}                                       │
│     }                                                           │
│   }],                                                           │
│   "tool_choice": "required"  // 날짜 감지 시                     │
│ }                                                               │
│                                                                 │
│ Response:                                                       │
│ - content: "출산 시 첫만남이용권 200만원..."                     │
│ - tool_calls: [{                                                │
│     function: {                                                 │
│       name: "add_calendar_event",                               │
│       arguments: {                                              │
│         title: "출산 예정일",                                    │
│         date: "2025-12-25T09:00:00",                            │
│         description: "첫만남이용권 신청 가능"                    │
│       }                                                         │
│     }                                                           │
│   }]                                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Backend - Save Messages                                         │
│ 1. INSERT INTO messages (conversation_id, role='user', ...)    │
│ 2. INSERT INTO messages (conversation_id, role='assistant'...) │
│ 3. UPDATE conversations SET last_message_at = NOW()            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Backend → Frontend Response                                     │
│ {                                                               │
│   "answer": "출산 시 첫만남이용권 200만원...",                  │
│   "sources": [{...}, {...}],                                    │
│   "function_call": {                                            │
│     "name": "add_calendar_event",                               │
│     "arguments": {...}                                          │
│   }                                                             │
│ }                                                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Frontend - Render UI                                            │
│ 1. 답변 표시                                                     │
│ 2. 출처 카드 표시 (접을 수 있음)                                 │
│ 3. "📅 캘린더 일정 제안" 카드 표시                               │
│    - 제목: "출산 예정일"                                         │
│    - 날짜: 2025년 12월 25일                                      │
│    - 버튼: "✅ 캘린더에 추가"                                    │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼ (User clicks "캘린더에 추가")
┌────────────────────────────────────────────────────────────────┐
│ Frontend                                                        │
│ POST /api/chat/execute-function                                 │
│ {                                                               │
│   "function_name": "add_calendar_event",                        │
│   "arguments": {...},                                           │
│   "conversation_id": "..."                                      │
│ }                                                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Backend - Execute Function                                      │
│ 1. 인자 검증 (title, date 필수)                                 │
│ 2. 날짜 파싱 (ISO 8601)                                          │
│ 3. INSERT INTO calendar_events (user_id, title, date, ...)     │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│ Frontend - Success Message                                      │
│ "✅ '출산 예정일' 일정이 캘린더에 추가되었습니다."               │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 커뮤니티 인기글 표시 흐름
```
┌─────────────────────────────────────────────────────────┐
│ Frontend - Home Page Load                                │
│ useEffect(() => { fetchPopularPosts() })                 │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend API Call                                        │
│ GET /api/community/posts/popular?limit=2                │
│ Authorization: Bearer {JWT_TOKEN}                       │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Backend - Community Router                               │
│ def get_popular_posts(limit, supabase):                 │
│     return crud.get_popular_posts(supabase, limit)      │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Database Query                                           │
│ SELECT posts.*,                                          │
│        users.id, users.email,                            │
│        user_profiles.name                                │
│ FROM posts                                               │
│ JOIN users ON posts.author_id = users.id                │
│ LEFT JOIN user_profiles ON users.id = user_profiles.id  │
│ ORDER BY posts.views_count DESC                         │
│ LIMIT 2                                                  │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Backend - Data Transform                                 │
│ - user_profiles 중첩 구조를 평탄화                        │
│ - author.name으로 변환                                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend - Render UI                                     │
│ <div className="space-y-3">                             │
│   {popularPosts.map(post => (                           │
│     <Link href={`/community/${post.id}`}>              │
│       <div className="bg-white rounded-xl...">         │
│         🔥 인기 - 조회수 {post.views_count}             │
│         {post.title}                                    │
│       </div>                                            │
│     </Link>                                             │
│   ))}                                                   │
│ </div>                                                  │
└─────────────────────────────────────────────────────────┘
```

### 3. 정책 스크래핑 → 벡터 저장 → RAG 준비 흐름
```
┌─────────────────────────────────────────────────────────┐
│ Scraper Service (Selenium)                               │
│ 1. Chrome WebDriver 초기화                               │
│ 2. bokjiro.go.kr 접속                                    │
│ 3. 정책 목록 페이지 순회                                  │
│ 4. 각 정책 상세 페이지 방문                               │
│ 5. PDF 다운로드 링크 추출                                 │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ PDF Download                                             │
│ - 파일 저장: data/pdfs/bokjiro/{policy_id}.pdf          │
│ - 메타데이터 저장: {title, url, date}                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ PDF Parsing (pypdf)                                      │
│ 1. PDF 파일 열기                                         │
│ 2. 페이지별 텍스트 추출                                   │
│ 3. 텍스트 정제 (공백, 특수문자 제거)                      │
│ 4. 전체 텍스트 결합                                       │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Text Chunking                                            │
│ - 512 토큰 단위로 분할 (overlap 50 토큰)                 │
│ - 각 청크에 메타데이터 추가                               │
│   {                                                      │
│     policy_id, doc_id, page_num,                        │
│     chunk_index, total_chunks                           │
│   }                                                      │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Embedding Generation (BGE-M3-Korean)                    │
│ FOR EACH chunk:                                          │
│   1. 텍스트 → 임베딩 벡터 (512 dim)                      │
│   2. Batch size: 64 (성능 최적화)                        │
│   3. 벡터 정규화 (L2 norm)                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Database Insert                                          │
│ BEGIN TRANSACTION;                                       │
│                                                          │
│ 1. INSERT INTO policies (id, title, category, ...)      │
│                                                          │
│ 2. INSERT INTO policy_chunks (                          │
│      policy_id,                                          │
│      content,                                            │
│      embedding,  -- pgvector type                       │
│      metadata                                            │
│    ) VALUES (?, ?, ?, ?)                                 │
│    (배치로 1000개씩 삽입)                                 │
│                                                          │
│ 3. CREATE INDEX IF NOT EXISTS                           │
│    idx_policy_chunks_embedding                          │
│    ON policy_chunks                                     │
│    USING ivfflat (embedding vector_cosine_ops)          │
│    WITH (lists = 100);                                  │
│                                                          │
│ COMMIT;                                                  │
└─────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ RAG System Ready                                         │
│ ✅ 정책 데이터 인덱싱 완료                                │
│ ✅ 벡터 검색 가능                                         │
│ ✅ 사용자 질문 응답 준비                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 보안 & 인증

### JWT 인증 플로우
```
1. User: 로그인 (email, password)
2. Backend:
   a. 비밀번호 검증 (bcrypt)
   b. JWT 토큰 생성 (python-jose)
3. Frontend: 토큰을 localStorage에 저장
4. 이후 모든 요청: Authorization: Bearer <token>
5. Backend: JWT 검증 후 user_id 추출
```

---

## 🚀 배포 & 운영

### 개발 환경
- Frontend: `npm run dev` (포트 3000)
- Backend: `uvicorn backend.main:app --reload` (포트 8000)

### 환경 변수
```env
# Backend (.env)
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-proj-...
SECRET_KEY=...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=upskyy/bge-m3-korean
PDF_DIRECTORIES=data/pdfs/bokjiro,data/pdfs/auto_scraper

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 📊 주요 기능

### ✅ 구현 완료
- [x] 회원가입/로그인 (JWT)
- [x] RAG 기반 정책 상담
- [x] OpenAI Function Calling (자동 일정 추가)
- [x] 캘린더 시스템 (CRUD)
- [x] 커뮤니티 (게시판, 댓글, 좋아요)
- [x] 홈 배너 (자동 슬라이드)
- [x] 인기글 시스템
- [x] 정책 스크래퍼 (Selenium)
- [x] 벡터 검색 (pgvector + Reranking)

---

## 🎨 Draw.io 다이어그램 작성 가이드

### 필요한 아이콘 목록
1. **프론트엔드**: Next.js, React, TypeScript, Tailwind CSS
2. **백엔드**: FastAPI, Python
3. **데이터베이스**: PostgreSQL, Supabase
4. **AI**: OpenAI, GPT-4
5. **기타**: Selenium, JWT, REST API

### 레이어 구성 (상단 → 하단)
1. **User Layer** (파란색)
2. **Frontend Layer** (초록색)
3. **Backend Layer** (주황색)
4. **Database Layer** (보라색)
5. **External Services Layer** (회색)

### 화살표 방향
- User → Frontend: HTTPS
- Frontend → Backend: REST API
- Backend → Database: PostgreSQL Connection
- Backend → OpenAI: API Calls
- Backend → Scraper Sites: Web Scraping

---

## 📝 기술 선택 이유

### Next.js 15
- App Router로 서버 컴포넌트 활용
- 빠른 페이지 로딩
- SEO 최적화

### FastAPI
- 비동기 지원으로 높은 성능
- 자동 API 문서 생성
- Python 생태계 활용

### Supabase
- PostgreSQL 기반 오픈소스
- pgvector로 벡터 검색 지원
- 실시간 데이터 동기화

### OpenAI GPT-4
- 높은 정확도의 자연어 이해
- Function Calling으로 구조화된 출력
- RAG와의 완벽한 통합

---

## 📈 향후 개선 계획

1. **캐싱 시스템**: Redis 도입으로 성능 향상
2. **검색 고도화**: Elasticsearch 통합
3. **실시간 알림**: WebSocket 적용
4. **모바일 앱**: React Native 개발
5. **관리자 대시보드**: 정책 관리 UI

---

## 📚 참고 문서

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)

---

**작성일**: 2025-10-12
**버전**: 1.0.0
**작성자**: BabyPolicy Team
