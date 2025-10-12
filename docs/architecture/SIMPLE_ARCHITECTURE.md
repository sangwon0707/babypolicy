# BabyPolicy 아키텍처 (간단 버전)

> 📌 **아이콘 중심의 시각적 다이어그램** - 주요 기술 스택 한눈에 보기

---

## 🏗️ 시스템 구조도

```
┌─────────────────────────────────────────────────────────────────┐
│                         🔄 Version Control                       │
│                                                                  │
│                    [github.svg]  GitHub                          │
│                     ↓         ↓         ↓                        │
│     [git.svg] Dev   [vercel.svg] FE   [render.svg] BE           │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                         👤 사용자 (User)                         │
│                                                                  │
│              💻 Desktop  📱 Mobile  🖥️ Tablet                   │
└─────────────────────────────────────────────────────────────────┘
                                 ↓ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                    🌐 Frontend (웹 인터페이스)                    │
│                                                                  │
│   [nextjs.svg]     [react.svg]     [typescript.svg]             │
│     Next.js          React 19        TypeScript                 │
│                                                                  │
│   [tailwindcss.svg]  [lucide.svg]                               │
│    Tailwind CSS      Lucide Icons                               │
└─────────────────────────────────────────────────────────────────┘
                                 ↓ REST API
┌─────────────────────────────────────────────────────────────────┐
│                    ⚙️ Backend (비즈니스 로직)                     │
│                                                                  │
│       [fastapi.svg]              [python.svg]                   │
│         FastAPI                   Python 3.13                   │
│                                                                  │
│                     주요 기능:                                    │
│   [jwt.svg] 인증   [selenium.svg] 스크래핑                       │
│     JWT              정책 수집                                   │
└─────────────────────────────────────────────────────────────────┘
                  ↓                              ↓
┌─────────────────────────────────┐  ┌─────────────────────────────┐
│    💾 Database                  │  │    🤖 AI Service            │
│                                  │  │                             │
│  [supabase.svg]  [postgresql.svg]│  │    [openai.svg]             │
│    Supabase       PostgreSQL     │  │     OpenAI API              │
│                                  │  │                             │
│  - users (사용자)                │  │  - GPT-4o-mini (채팅)       │
│  - policies (정책)               │  │  - BGE-M3 (임베딩)          │
│  - messages (대화)               │  │  - Function Calling         │
│  - calendar (일정)               │  │    (캘린더 자동 추가)        │
└─────────────────────────────────┘  └─────────────────────────────┘
```

---

## 🎯 주요 기술 스택 (아이콘 17개)

### Frontend (5개)
| 아이콘 | 기술 | 역할 |
|--------|------|------|
| ![Next.js](../../architecture-icons/nextjs.svg) | **Next.js 15** | React 프레임워크, 서버 사이드 렌더링 |
| ![React](../../architecture-icons/react.svg) | **React 19** | UI 컴포넌트 라이브러리 |
| ![TypeScript](../../architecture-icons/typescript.svg) | **TypeScript** | 타입 안전성, 개발 생산성 |
| ![Tailwind](../../architecture-icons/tailwindcss.svg) | **Tailwind CSS** | 유틸리티 기반 스타일링 |
| ![Lucide](../../architecture-icons/lucide.svg) | **Lucide Icons** | 아이콘 라이브러리 |

### Backend (2개)
| 아이콘 | 기술 | 역할 |
|--------|------|------|
| ![FastAPI](../../architecture-icons/fastapi.svg) | **FastAPI** | Python 웹 프레임워크 |
| ![Python](../../architecture-icons/python.svg) | **Python 3.13** | 백엔드 언어 |

### Database (2개)
| 아이콘 | 기술 | 역할 |
|--------|------|------|
| ![Supabase](../../architecture-icons/supabase.svg) | **Supabase** | BaaS, 인증, 실시간 DB |
| ![PostgreSQL](../../architecture-icons/postgresql.svg) | **PostgreSQL** | 관계형 데이터베이스 + pgvector |

### AI & External (2개)
| 아이콘 | 기술 | 역할 |
|--------|------|------|
| ![OpenAI](../../architecture-icons/openai.svg) | **OpenAI API** | GPT-4o-mini, 임베딩, Function Calling |
| ![Selenium](../../architecture-icons/selenium.svg) | **Selenium** | 정책 스크래핑 |

### DevOps (5개)
| 아이콘 | 기술 | 역할 |
|--------|------|------|
| ![Git](../../architecture-icons/git.svg) | **Git** | 버전 관리 |
| ![GitHub](../../architecture-icons/github.svg) | **GitHub** | 소스 코드 저장소 |
| ![Docker](../../architecture-icons/docker.svg) | **Docker** | 컨테이너화 (예정) |
| ![Vercel](../../architecture-icons/vercel.svg) | **Vercel** | 프론트엔드 배포 |
| ![Render](../../architecture-icons/render.svg) | **Render** | 백엔드 배포 |

### Auth (1개)
| 아이콘 | 기술 | 역할 |
|--------|------|------|
| ![JWT](../../architecture-icons/jwt.svg) | **JWT** | 토큰 기반 인증 |

---

## 🔄 데이터 흐름 (3가지 주요 시나리오)

### 1️⃣ 사용자 질문 → AI 답변 → 캘린더 자동 추가
```
[User] → [Frontend] → [Backend/FastAPI] → [OpenAI Function Calling]
                            ↓
                      [Backend/Calendar API]
                            ↓
                      [Supabase/calendar 테이블]
                            ↓
                      [Frontend/캘린더 UI 업데이트]
```

### 2️⃣ 정책 검색 (RAG)
```
[User 질문] → [Frontend] → [Backend/RAG System]
                                  ↓
                           [Supabase/pgvector 검색]
                                  ↓
                           [OpenAI GPT-4o-mini]
                                  ↓
                           [Frontend/답변 표시]
```

### 3️⃣ 정책 스크래핑
```
[Backend/Selenium] → [정부 사이트 크롤링]
         ↓
   [OpenAI BGE-M3 임베딩]
         ↓
   [Supabase/policy_chunks 저장]
```

---

## 📊 Draw.io 다이어그램 만들기

### 1단계: 아이콘 가져오기
```bash
# Draw.io에서 아이콘 임포트
File → Import → Device → docs/architecture-icons/
```

### 2단계: 레이아웃 (5개 레이어)
1. **Version Control** (회색 #F3F4F6) - GitHub, Git, Vercel
2. **User** (파란색 #DBEAFE) - 사용자 디바이스
3. **Frontend** (초록색 #D1FAE5) - Next.js, React, TypeScript, Tailwind, Lucide
4. **Backend** (주황색 #FED7AA) - FastAPI, Python, JWT, Selenium
5. **Database & AI** (보라색 #E9D5FF) - Supabase, PostgreSQL, OpenAI

### 3단계: 아이콘 크기
- **주요 아이콘**: 80×80px (Next.js, FastAPI, Supabase, OpenAI)
- **보조 아이콘**: 64×64px (Git, Docker, Lucide 등)
- **간격**: 32px (아이콘 간)
- **여백**: 24px (컨테이너 가장자리)

---

## 🎨 색상 팔레트 (Tailwind CSS)

| 레이어 | 배경색 | 테두리 | 텍스트 |
|--------|--------|--------|--------|
| Version Control | #F3F4F6 | #6B7280 | #374151 |
| User | #DBEAFE | #3B82F6 | #1E40AF |
| Frontend | #D1FAE5 | #10B981 | #065F46 |
| Backend | #FED7AA | #F97316 | #9A3412 |
| Database & AI | #E9D5FF | #8B5CF6 | #6B21A8 |

---

## ✅ 주요 기능 요약

1. **🔐 인증**: JWT 기반 사용자 인증
2. **💬 AI 채팅**: OpenAI GPT-4o-mini로 정책 상담
3. **🔍 RAG 검색**: pgvector + 임베딩으로 정책 검색
4. **📅 일정 자동 추가**: Function Calling으로 캘린더 이벤트 생성
5. **📰 정책 스크래핑**: Selenium으로 정부 사이트 크롤링
6. **👥 커뮤니티**: 게시판, 좋아요, 댓글 기능

---

**작성일**: 2025-10-12
**버전**: 1.0.0 (간단 버전)
**아이콘**: 17개 SVG (Simple Icons)

> 💡 **Tip**: 이 문서를 참고하여 Draw.io에서 시각적 다이어그램을 만드세요!
> 상세 가이드: [DRAWIO_GUIDE.md](./DRAWIO_GUIDE.md)
