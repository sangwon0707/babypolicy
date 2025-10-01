# 🍼 BabyPolicy - AI육아정책 도우미

> 육아 정책을 쉽고 빠르게 찾아주는 AI 챗봇 서비스

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai)](https://openai.com/)

## 📋 목차
- [기능 소개](#-features)
- [기술 스택](#️-tech-stack)
- [초보자를 위한 설치 가이드](#-초보자를-위한-설치-가이드)
- [파일별 기능 설명](#-파일별-기능-설명-어디를-수정하면-될까요)
- [API 엔드포인트](#-api-endpoints)
- [프로젝트 구조](#-project-structure)
- [문제 해결](#-자주-발생하는-문제와-해결-방법)

---

## 🌟 Features

- 🤖 **AI 챗봇** - GPT 기반 RAG로 정확한 정책 정보 제공
- 👨‍👩‍👧‍👦 **커뮤니티** - 육아 경험 공유 및 소통
- 📋 **정책 검색** - 지역, 소득, 가족 구성별 맞춤 정책
- 💬 **실시간 대화** - 자연어로 편하게 질문
- 🎨 **Baby-Friendly UI** - 귀엽고 편안한 디자인

---

## 🏗️ Tech Stack

### Frontend
- **Next.js 15.5** - React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 스타일링
- **Lucide Icons** - 아이콘

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **Supabase Client** - PostgreSQL + 실시간 DB
- **OpenAI API** - GPT-4 기반 RAG
- **pgvector** - 벡터 검색

### Database
- **Supabase (PostgreSQL)** - 메인 데이터베이스
- **pgvector Extension** - 벡터 임베딩 저장

---

## 🚀 초보자를 위한 설치 가이드

### 사전 준비물

다음 프로그램들을 먼저 설치해주세요:

1. **Python 3.13 이상**
   - 다운로드: https://www.python.org/downloads/
   - 설치 시 "Add Python to PATH" 체크 필수!

2. **Node.js 18 이상**
   - 다운로드: https://nodejs.org/
   - LTS 버전 설치 권장

3. **Git**
   - 다운로드: https://git-scm.com/downloads

4. **VS Code** (코드 에디터, 선택사항)
   - 다운로드: https://code.visualstudio.com/

5. **Supabase 계정**
   - 회원가입: https://supabase.com/
   - 무료 계정으로 시작 가능

6. **OpenAI API Key**
   - 발급: https://platform.openai.com/api-keys
   - 결제 수단 등록 필요 (사용한 만큼만 과금)

---

### Step 1: 프로젝트 다운로드

터미널(Mac/Linux) 또는 명령 프롬프트(Windows)를 열고 다음을 입력하세요:

```bash
# 프로젝트를 다운로드할 폴더로 이동 (예: 바탕화면)
cd Desktop

# 프로젝트 복사
git clone https://github.com/sangwon0707/babypolicy.git

# 프로젝트 폴더로 이동
cd babypolicy
```

---

### Step 2: 데이터베이스 설정 (Supabase)

1. **Supabase 대시보드 접속**
   - https://supabase.com/dashboard 로 이동
   - 새 프로젝트 만들기 (Create new project)

2. **데이터베이스 비밀번호 설정**
   - 프로젝트 생성 시 입력한 비밀번호를 꼭 기억하세요!

3. **SQL 에디터에서 테이블 생성**
   - 왼쪽 메뉴에서 `SQL Editor` 클릭
   - `New query` 클릭
   - `backend/init_supabase.sql` 파일의 내용을 전체 복사해서 붙여넣기
   - `Run` 버튼 클릭

4. **API 키 복사**
   - 왼쪽 메뉴에서 `Settings` > `API` 클릭
   - 다음 값들을 메모장에 복사해두기:
     - `Project URL` (예: https://xxx.supabase.co)
     - `anon public` 키
     - `service_role secret` 키 (Show 버튼 클릭해야 보임)

---

### Step 3: 백엔드 환경 설정

터미널에서 다음 명령어를 **한 줄씩** 입력하세요:

```bash
# 백엔드 폴더로 이동
cd backend

# 가상환경 생성 (처음 한 번만 실행)
python -m venv venv

# 가상환경 활성화
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 환경변수 파일 복사
cp .env.example .env
```

**중요!** 이제 `.env` 파일을 텍스트 에디터로 열어서 다음 값들을 입력하세요:

```bash
# backend/.env 파일 내용

# OpenAI API Key (https://platform.openai.com/api-keys 에서 발급)
OPENAI_API_KEY="sk-proj-여기에_실제_키_입력"

# Supabase 정보 (Supabase Dashboard > Settings > API 에서 복사)
SUPABASE_URL="https://여기에_프로젝트_URL_입력.supabase.co"
SUPABASE_ANON_KEY="여기에_anon_키_입력"
SUPABASE_SERVICE_ROLE_KEY="여기에_service_role_키_입력"

# 데이터베이스 연결 (Supabase Dashboard > Settings > Database > Connection String)
DATABASE_URL="postgresql://postgres.xxx:[비밀번호]@xxx.supabase.com:6543/postgres"

# JWT 비밀키 (아무 긴 문자열이나 입력하세요, 예: asdfghjkl1234567890)
SECRET_KEY="여기에_랜덤한_긴_문자열_입력"

# 프론트엔드 주소 (그대로 두세요)
FRONTEND_URL="http://localhost:3000"
```

저장하고 닫기!

---

### Step 4: 백엔드 실행

같은 터미널에서 계속:

```bash
# 필요한 라이브러리 설치 (처음 한 번만 실행, 시간 좀 걸림)
pip install -r requirements.txt

# 서버 실행!
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ **성공하면** 다음과 같이 표시됩니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

이 터미널 창은 **그냥 두세요** (서버가 실행 중입니다!)

브라우저에서 http://localhost:8000/docs 를 열어보세요. API 문서가 보이면 성공!

---

### Step 5: 프론트엔드 환경 설정

**새 터미널 창**을 하나 더 열고:

```bash
# 프로젝트 폴더로 이동
cd Desktop/babypolicy

# 프론트엔드 폴더로 이동
cd frontend

# 환경변수 파일 복사
cp .env.local.example .env.local
```

`.env.local` 파일을 열어보세요. 기본값이 이미 설정되어 있습니다:

```bash
# frontend/.env.local 파일 내용
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

그대로 두고 저장!

---

### Step 6: 프론트엔드 실행

같은 터미널에서:

```bash
# 필요한 라이브러리 설치 (처음 한 번만 실행, 시간 좀 걸림)
npm install

# 개발 서버 실행!
npm run dev
```

✅ **성공하면** 다음과 같이 표시됩니다:
```
✓ Ready in 2s
- Local:        http://localhost:3000
```

브라우저에서 **http://localhost:3000** 를 열어보세요!

---

### Step 7: 회원가입 & 로그인

1. 브라우저에서 `http://localhost:3000` 접속
2. **회원가입** 버튼 클릭
3. 이메일과 비밀번호 입력 (테스트용으로 아무거나)
4. 회원가입 완료되면 자동 로그인!

---

### Step 8: (선택사항) PDF 정책 데이터 다운로드

AI 챗봇이 실제 정책 정보를 답변하려면 PDF 데이터가 필요합니다.

**새 터미널 창**을 열고:

```bash
# 1. 복지로 사이트에서 PDF 다운로드 (5개 정책, 약 1-2분 소요)
curl -X POST http://localhost:8000/api/admin/run-scraper \
  -H "Content-Type: application/json" \
  -d '{"max_policies": 5, "skip_rag": true}'

# 2. PDF를 AI가 읽을 수 있게 처리 (약 2-3분 소요)
curl -X POST http://localhost:8000/api/admin/process-rag \
  -H "Content-Type: application/json" \
  -d '{}'
```

✅ 완료되면 AI 챗봇이 정책 질문에 답변할 수 있습니다!

---

### 🎉 완료!

이제 다음 URL들을 사용할 수 있습니다:

- **프론트엔드**: http://localhost:3000 (사용자가 보는 화면)
- **백엔드 API 문서**: http://localhost:8000/docs (개발자용)
- **데이터베이스**: Supabase Dashboard에서 확인

---

### 서버 종료 방법

- 터미널에서 `Ctrl + C` 누르기

### 다음에 다시 실행하는 방법

**백엔드 터미널:**
```bash
cd Desktop/babypolicy/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**프론트엔드 터미널:**
```bash
cd Desktop/babypolicy/frontend
npm run dev
```

---

## 📝 파일별 기능 설명 (어디를 수정하면 될까요?)

### 🎨 프론트엔드 (화면 디자인 & 기능)

#### **메인 페이지 (첫 화면)**
- **파일**: `frontend/app/page.tsx`
- **수정하면 바뀌는 것**:
  - 로고, 제목, 설명 문구
  - 로그인/회원가입 버튼 디자인
  - 배경 색상, 애니메이션
  - 로그인 전/후 보이는 내용

#### **로그인 페이지**
- **파일**: `frontend/app/(auth)/login/page.tsx`
- **수정하면 바뀌는 것**:
  - 로그인 폼 디자인 (이메일/비밀번호 입력창)
  - 에러 메시지 문구
  - "회원가입" 링크 위치

#### **회원가입 페이지**
- **파일**: `frontend/app/(auth)/register/page.tsx`
- **수정하면 바뀌는 것**:
  - 회원가입 폼 (이메일/비밀번호/이름 입력창)
  - 비밀번호 유효성 검사 규칙
  - 가입 완료 후 이동 경로

#### **AI 챗봇 페이지**
- **파일**: `frontend/app/chat/page.tsx`
- **수정하면 바뀌는 것**:
  - 채팅창 UI (말풍선 색상, 크기)
  - 메시지 입력창 디자인
  - AI 답변 표시 방식
  - 출처 정보 표시

#### **커뮤니티 페이지**
- **파일**: `frontend/app/community/page.tsx`
- **수정하면 바뀌는 것**:
  - 게시글 목록 레이아웃
  - 카테고리 필터
  - 게시글 카드 디자인
  - 좋아요/댓글 개수 표시

#### **마이페이지 (내 정보)**
- **파일**: `frontend/app/me/page.tsx`
- **수정하면 바뀌는 것**:
  - 프로필 정보 표시
  - 로그아웃 버튼 위치
  - 설정 메뉴 항목
  - 내가 쓴 글, 관심 정책 링크

#### **하단 네비게이션 바**
- **파일**: `frontend/components/BottomNav.tsx`
- **수정하면 바뀌는 것**:
  - 메뉴 아이콘 (챗봇/커뮤니티/마이)
  - 메뉴 개수 추가/삭제
  - 활성화된 메뉴 색상
  - 로그인 전/후 메뉴 동작

#### **인증 로직 (로그인 상태 관리)**
- **파일**: `frontend/contexts/AuthContext.tsx`
- **수정하면 바뀌는 것**:
  - 로그인/로그아웃 동작
  - 토큰 저장 방식
  - 자동 로그인 유지 시간
  - 사용자 정보 불러오기

#### **API 통신 (서버와 대화)**
- **파일**: `frontend/lib/api.ts`
- **수정하면 바뀌는 것**:
  - 백엔드 서버 주소
  - API 요청 형식 (JSON)
  - 에러 처리 방법
  - 헤더 설정 (인증 토큰)

---

### ⚙️ 백엔드 (서버 & 데이터 처리)

#### **메인 서버 설정**
- **파일**: `backend/main.py`
- **수정하면 바뀌는 것**:
  - API 엔드포인트 경로 (라우터 연결)
  - CORS 설정 (어떤 도메인에서 접속 허용할지)
  - 서버 시작 메시지
  - 전역 에러 처리

#### **회원가입 & 로그인**
- **파일**: `backend/routers/auth.py`
- **수정하면 바뀌는 것**:
  - 회원가입 규칙 (비밀번호 길이 등)
  - 로그인 성공 시 응답 데이터
  - JWT 토큰 발급 방식
  - 이메일 중복 체크

#### **AI 챗봇 답변 생성**
- **파일**: `backend/routers/chat.py`
- **수정하면 바뀌는 것**:
  - 사용자 질문 처리
  - AI 답변 요청
  - 대화 기록 저장 방식

#### **커뮤니티 게시글**
- **파일**: `backend/routers/community.py`
- **수정하면 바뀌는 것**:
  - 게시글 작성/조회/삭제
  - 댓글 기능
  - 좋아요 기능
  - 카테고리 관리
  - 페이지네이션 (한 페이지에 몇 개씩 보여줄지)

#### **사용자 프로필**
- **파일**: `backend/routers/user.py`
- **수정하면 바뀌는 것**:
  - 내 정보 조회
  - 프로필 수정
  - 관심 정책 관리

#### **관리자 기능 (PDF 다운로드/RAG)**
- **파일**: `backend/routers/admin.py`
- **수정하면 바뀌는 것**:
  - PDF 스크래핑 설정
  - RAG 처리 시작

#### **RAG (AI 학습 & 답변)**
- **파일**: `backend/services/rag_service.py`
- **수정하면 바뀌는 것**:
  - PDF 텍스트 추출 방식
  - 텍스트 청크(조각) 크기
  - OpenAI 임베딩 모델
  - AI 답변 생성 프롬프트 (한국어 답변 강제 등)
  - 유사도 검색 개수 (top_k)

#### **PDF 스크래핑 (복지로 사이트)**
- **파일**: `backend/services/scraper_service.py`
- **수정하면 바뀌는 것**:
  - 다운로드할 PDF 개수
  - 스크래핑 대상 웹사이트
  - PDF 저장 위치
  - 중복 다운로드 방지

#### **데이터베이스 연결**
- **파일**: `backend/database.py`
- **수정하면 바뀌는 것**:
  - Supabase 연결 설정
  - 환경변수 불러오기

#### **데이터베이스 작업 (CRUD)**
- **파일**: `backend/crud.py`
- **수정하면 바뀌는 것**:
  - 사용자 생성/조회/수정/삭제
  - 게시글 생성/조회/수정/삭제
  - 댓글, 좋아요 처리
  - 벡터 검색 (RAG)
  - SQL 쿼리 로직

#### **데이터 모델 (Pydantic)**
- **파일**: `backend/schemas.py`
- **수정하면 바뀌는 것**:
  - API 요청/응답 데이터 형식
  - 필수/선택 필드
  - 데이터 유효성 검사 규칙

#### **비밀번호 & JWT 토큰**
- **파일**: `backend/auth/utils.py`
- **수정하면 바뀌는 것**:
  - 비밀번호 해싱 방식 (bcrypt)
  - JWT 토큰 생성/검증
  - 토큰 만료 시간
  - 비밀번호 확인 로직

---

### 🗄️ 데이터베이스 (Supabase)

#### **테이블 생성 SQL**
- **파일**: `backend/init_supabase.sql`
- **수정하면 바뀌는 것**:
  - 테이블 구조 (users, posts, comments 등)
  - 컬럼 추가/삭제
  - 인덱스, 외래키 관계
  - Row Level Security (RLS) 정책
  - 벡터 검색 함수

---

### 🔧 환경 설정 파일

#### **백엔드 환경변수**
- **파일**: `backend/.env`
- **수정하면 바뀌는 것**:
  - OpenAI API 키
  - Supabase 연결 정보
  - JWT 비밀키
  - 데이터베이스 비밀번호

#### **프론트엔드 환경변수**
- **파일**: `frontend/.env.local`
- **수정하면 바뀌는 것**:
  - 백엔드 API 서버 주소

#### **Python 라이브러리 목록**
- **파일**: `backend/requirements.txt`
- **수정하면 바뀌는 것**:
  - 설치할 Python 패키지 버전
  - 새로운 라이브러리 추가

#### **Node.js 라이브러리 목록**
- **파일**: `frontend/package.json`
- **수정하면 바뀌는 것**:
  - 설치할 npm 패키지 버전
  - 새로운 라이브러리 추가
  - 빌드 스크립트

---

### 🎨 디자인 시스템

#### **글로벌 스타일**
- **파일**: `frontend/app/globals.css`
- **수정하면 바뀌는 것**:
  - 전체 앱 색상 테마
  - 폰트 설정
  - 애니메이션 정의
  - Tailwind CSS 커스터마이징

---

## 🔍 자주 발생하는 문제와 해결 방법

### ❌ "Python을 찾을 수 없습니다"
**원인**: Python이 설치되지 않았거나 PATH에 추가되지 않음
**해결**:
1. Python 재설치 시 "Add Python to PATH" 체크
2. 터미널 재시작
3. `python --version` 으로 확인

### ❌ "Node를 찾을 수 없습니다"
**원인**: Node.js가 설치되지 않음
**해결**:
1. https://nodejs.org/ 에서 LTS 버전 다운로드
2. 설치 후 터미널 재시작
3. `node --version` 으로 확인

### ❌ "venv\Scripts\activate를 실행할 수 없습니다" (Windows)
**원인**: PowerShell 실행 정책
**해결**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "Failed to fetch user" 또는 "401 Unauthorized"
**원인**: JWT 토큰이 만료되었거나 잘못됨
**해결**:
1. 브라우저에서 F12 (개발자 도구)
2. Application > Local Storage > `auth_token` 삭제
3. 다시 로그인

### ❌ "CORS policy error"
**원인**: 백엔드 CORS 설정 문제
**해결**:
1. `backend/main.py` 에서 CORS 설정 확인
2. `FRONTEND_URL` 환경변수가 `http://localhost:3000` 인지 확인

### ❌ "Supabase connection failed"
**원인**: 환경변수가 잘못 입력됨
**해결**:
1. `backend/.env` 파일 확인
2. Supabase Dashboard에서 키 다시 복사
3. 따옴표 없이 입력했는지 확인

### ❌ "OpenAI API error"
**원인**: API 키가 잘못되었거나 크레딧 부족
**해결**:
1. https://platform.openai.com/account/billing 에서 잔액 확인
2. API 키 재발급
3. `backend/.env` 에서 새 키로 교체

### ❌ "Port 8000 is already in use"
**원인**: 백엔드 서버가 이미 실행 중
**해결**:
```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID [프로세스번호] /F
```

### ❌ "Module not found" (Python)
**원인**: 라이브러리가 설치되지 않음
**해결**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ "Module not found" (Node.js)
**원인**: npm 패키지가 설치되지 않음
**해결**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Documentation

- **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** - Modern Supabase integration guide
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Detailed setup instructions
- **[COMPLETE_VERIFICATION.md](./COMPLETE_VERIFICATION.md)** - Full system verification

---

## 🎨 Design

### Color Palette
- **Primary**: `#FF9ECD` (Soft Pink)
- **Secondary**: `#B4E4FF` (Baby Blue)
- **Accent**: `#F0E6FF` (Lavender)
- **Background**: Gradient (Pink → Blue → Purple)

### UI Features
- ✨ Floating animations
- 🎭 Glassmorphism effects
- 🌈 Gradient buttons
- 🔘 Rounded corners (1rem)
- 💫 Smooth transitions

---

## 📁 Project Structure

```
babypolicy/
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── table-ref.md                 # Database schema reference
├── data/
│   └── pdfs/bokjiro/           # Downloaded policy PDFs (auto-generated)
│
├── backend/
│   ├── .env.example            # Backend environment template
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # Supabase client setup
│   ├── crud.py                 # Database CRUD operations
│   ├── schemas.py              # Pydantic schemas
│   ├── init_supabase.sql       # Database initialization SQL
│   ├── auth/
│   │   └── utils.py           # JWT & password hashing
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat.py            # AI chatbot endpoints
│   │   ├── community.py       # Community endpoints
│   │   ├── user.py            # User profile endpoints
│   │   └── admin.py           # Admin endpoints (scraper, RAG)
│   └── services/
│       ├── rag_service.py     # RAG processing & Q&A
│       └── scraper_service.py # PDF scraping from Bokjiro
│
└── frontend/
    ├── .env.local.example      # Frontend environment template
    ├── package.json            # Node dependencies
    ├── app/
    │   ├── layout.tsx         # Root layout with AuthProvider
    │   ├── page.tsx           # Home page (auth-aware)
    │   ├── (auth)/
    │   │   ├── login/         # Login page
    │   │   └── register/      # Registration page
    │   ├── chat/page.tsx      # AI chatbot interface
    │   ├── community/         # Community pages
    │   └── me/page.tsx        # User profile page
    ├── components/
    │   ├── BottomNav.tsx      # Bottom navigation (auth-aware)
    │   └── ui/                # shadcn/ui components
    ├── contexts/
    │   └── AuthContext.tsx    # Global authentication state
    └── lib/
        └── api.ts             # API client functions
```

---

## 🗄️ Database Schema

### Core Tables (15 total)

#### User Management
- `users` - User accounts
- `user_profiles` - User details (name, region, family info)
- `user_settings` - Preferences

#### Policy & RAG
- `policies` - Policy documents
- `policy_chunks` - Text chunks with vector embeddings
- `user_policies` - Saved policies

#### Community
- `categories` - Post categories (6 default)
- `posts` - Community posts
- `comments` - Post comments
- `post_likes` / `comment_likes` - Like tracking

#### Chat
- `conversations` - Chat sessions
- `messages` - Chat messages with RAG sources

#### Other
- `calendar_events` - Policy deadlines
- `notifications` - User notifications

---

## 🔧 API Endpoints

### Authentication (`/api/auth`)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)
- `GET /auth/me` - Get current user (requires authentication)

### Chat (`/api/chat`)
- `POST /chat` - Send message to AI chatbot (RAG-powered)

### Community (`/api/community`)
- `GET /community/categories` - Get all categories
- `GET /community/posts` - Get posts (with pagination)
- `POST /community/posts` - Create new post (requires auth)
- `GET /community/posts/{id}` - Get single post with details
- `GET /community/posts/{id}/comments` - Get comments for a post
- `POST /community/posts/{id}/comments` - Create comment (requires auth)

### User (`/api/user`)
- `GET /user/profile` - Get user profile (requires auth)

### Admin (`/api/admin`) - For development/maintenance
- `POST /admin/run-scraper` - Download policy PDFs from Bokjiro
- `POST /admin/process-rag` - Process PDFs into vector embeddings

---

## 🧪 Testing

### Backend API Testing
Visit http://localhost:8000/docs for interactive API documentation

### Frontend Testing
```bash
npm run dev
# Visit http://localhost:3000
```

### Database Testing
```python
# Test Supabase connection
from backend.database import supabase
result = supabase.table('categories').select('*').execute()
print(f'Found {len(result.data)} categories')
```

---

## 🚢 Deployment

### Frontend (Vercel)
```bash
# Connect to Vercel
vercel --prod

# Set environment variable
NEXT_PUBLIC_API_URL=https://your-backend.com/api
```

### Backend (Railway / Fly.io)
```bash
# Deploy backend
# Set all environment variables from .env
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Team

Built with ❤️ for parents and babies

---

## 🙏 Acknowledgments

- [Supabase](https://supabase.com/) - Database & Backend
- [OpenAI](https://openai.com/) - AI/GPT Integration
- [Next.js](https://nextjs.org/) - React Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web Framework

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in `/docs`
- Contact: [support@babypolicy.com]

---

**Made with 🍼 by BabyPolicy Team**