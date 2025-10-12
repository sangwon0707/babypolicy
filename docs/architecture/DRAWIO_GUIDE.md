# BabyPolicy - Draw.io 아키텍처 다이어그램 제작 가이드

이 문서는 Draw.io에서 **BabyPolicy 시스템 아키텍처 다이어그램**을 제작하는 실용적인 단계별 가이드입니다.

> 📘 **참고 문서**: 전체 아키텍처 설명은 [ARCHITECTURE_DIAGRAM.md](../../ARCHITECTURE_DIAGRAM.md) 참조

---

## 🎯 디자인 철학: 아이콘 중심의 시각적 명확성

이 다이어그램은 **아이콘 위주의 시각적 설계**를 기본 원칙으로 합니다.

### 핵심 원칙
1. **아이콘이 주인공**: 기술 스택을 한눈에 파악할 수 있도록 아이콘을 크고 명확하게 배치
2. **시각적 계층**: 색상 구분된 레이어로 시스템 구조를 즉각적으로 이해
3. **최소한의 텍스트**: 필수 정보만 표기, 아이콘이 스스로 말하도록
4. **깔끔한 여백**: 충분한 공간으로 시각적 피로 최소화

### 시각적 우선순위
```
🥇 1순위: 아이콘 (크기 80×80px 이상)
🥈 2순위: 계층 구분 (배경색 + 여백)
🥉 3순위: 주요 연결선 (굵고 명확한 화살표)
4순위: 텍스트 라벨 (보조 설명)
```

---

## 🚀 빠른 시작 가이드 (아이콘 중심 레이아웃)

시각적으로 임팩트 있는 다이어그램을 빠르게 만들고 싶다면 이 가이드를 따르세요.

### 5분 퀵 스타트
1. **캔버스 설정**: A3 크기 (297×420mm), Grid 10px
2. **5개 레이어 생성**: 각 색상별 Swimlane 컨테이너
3. **아이콘 임포트**: 17개 SVG 파일 한 번에 가져오기
4. **아이콘 배치**: 80×80px 크기로 각 레이어에 배치
5. **연결선 추가**: 굵은 실선(주요)과 점선(보조) 구분

### 시각적 임팩트를 위한 황금 비율
```
아이콘 크기:간격:여백 = 80:32:24 (px)
  │        │      └─ 컨테이너 여백 (넉넉한 공간)
  │        └─ 아이콘 간 간격 (명확한 분리)
  └─ 주요 아이콘 크기 (한눈에 보임)
```

### 3단계 시각적 최적화
1. **아이콘 먼저**: 모든 아이콘을 80×80px로 크게 배치
2. **색상 레이어**: 5가지 명확한 배경색으로 구분
3. **최소 텍스트**: 기술명만 표기, 설명은 최소화

---

## 📋 사전 준비

### 1. 필요한 도구
- **Draw.io**: [https://app.diagrams.net/](https://app.diagrams.net/) 또는 데스크톱 앱
- **아이콘**: `docs/architecture-icons/` 폴더의 16개 SVG 파일

### 2. 아이콘 목록 확인
```bash
ls -1 docs/architecture-icons/*.svg
```

**사용 가능한 아이콘 (16개)**:
- nextjs.svg, react.svg, typescript.svg, tailwindcss.svg, lucide.svg
- fastapi.svg, python.svg
- postgresql.svg, supabase.svg
- openai.svg, selenium.svg
- git.svg, github.svg, docker.svg, vercel.svg
- jwt.svg

---

## 🎨 다이어그램 레이아웃 구조

### 전체 구조 (5개 계층)
```
┌─────────────────────────────────────────────────────────┐
│  1️⃣ VERSION CONTROL LAYER (회색 #6B7280)             │
│     GitHub Repository                                    │
│       ├─ Developer (Local Dev, Code Review)             │
│       └─ Deploy (Vercel FE, Cloud BE)                   │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2️⃣ USER LAYER (파란색 #3B82F6)                       │
│     Desktop / Mobile / Tablet                            │
└─────────────────────────────────────────────────────────┘
                    ▼ HTTPS (TLS 1.3)
┌─────────────────────────────────────────────────────────┐
│  3️⃣ FRONTEND LAYER (초록색 #10B981)                   │
│     Next.js 15 + React 19 + TypeScript                  │
│     ┌───────────┬───────────┬───────────┬──────────┐   │
│     │App Router │  UI/UX    │State Mgmt │API Client│   │
│     │   (RSC)   │ Tailwind  │Context API│  Fetch   │   │
│     └───────────┴───────────┴───────────┴──────────┘   │
└─────────────────────────────────────────────────────────┘
      │         │          │           │
      │ REST API endpoints (4개)      │
      ▼         ▼          ▼           ▼
┌─────────────────────────────────────────────────────────┐
│  4️⃣ BACKEND LAYER (주황색 #F97316)                    │
│     FastAPI + Python 3.13 + Uvicorn                     │
│     ┌─────────────────────────────────────────────┐    │
│     │ Router Layer                                 │    │
│     │ /auth /chat /community /calendar /user       │    │
│     └─────────────────────────────────────────────┘    │
│                      ▼                                   │
│     ┌─────────────────────────────────────────────┐    │
│     │ Business Logic Layer                         │    │
│     │ ┌──────┬──────┬──────────┬────────────┐    │    │
│     │ │Auth  │ RAG  │Function  │  Scraper   │    │    │
│     │ │JWT   │Vector│Calling   │  Selenium  │    │    │
│     │ └──────┴──────┴──────────┴────────────┘    │    │
│     └─────────────────────────────────────────────┘    │
│                      ▼                                   │
│     ┌─────────────────────────────────────────────┐    │
│     │ Data Access Layer                            │    │
│     │ CRUD Functions + Supabase Client             │    │
│     └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
      │        │          │          │           │
      ▼        ▼          ▼          ▼           ▼
┌─────────────────────────────────────────────────────────┐
│  5️⃣ DATABASE & EXTERNAL SERVICES (보라색 #8B5CF6)    │
│  ┌────────────────┐    ┌──────────────────────────┐   │
│  │Supabase        │    │ OpenAI API               │   │
│  │ PostgreSQL     │    │ - GPT-4o-mini (Chat)     │   │
│  │ + pgvector     │    │ - BGE-M3 (Embedding)     │   │
│  │                │    │ - Function Calling       │   │
│  │ Tables:        │    └──────────────────────────┘   │
│  │ - users        │                                    │
│  │ - policies     │    ┌──────────────────────────┐   │
│  │ - policy_chunks│    │ 정부 사이트               │   │
│  │ - messages     │    │ - bokjiro.go.kr          │   │
│  │ - posts        │    │ - 정책브리핑              │   │
│  │ - calendar     │    └──────────────────────────┘   │
│  └────────────────┘                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Draw.io 제작 단계 (6단계)

### Step 1: 캔버스 설정

1. **Draw.io 열기**: [https://app.diagrams.net/](https://app.diagrams.net/)
2. **새 다이어그램 생성**: `Blank Diagram` 선택
3. **페이지 설정**:
   - Format → Canvas → Size: `A3` (297mm × 420mm)
   - Grid: **10px** (View → Grid 체크)
   - Background: `#FFFFFF` (흰색)

### Step 2: 컨테이너 배치 (5개 계층)

#### 2.1. 컨테이너 생성
1. 좌측 패널에서 `Containers` 선택
2. `Rectangle` 도형을 캔버스에 5개 배치

#### 2.2. 계층별 설정

| 계층 | 배경색 | 텍스트 색상 | 높이 |
|------|--------|------------|------|
| 1️⃣ Version Control | `#F3F4F6` | `#374151` | 120px |
| 2️⃣ User | `#DBEAFE` | `#1E40AF` | 100px |
| 3️⃣ Frontend | `#D1FAE5` | `#065F46` | 200px |
| 4️⃣ Backend | `#FED7AA` | `#9A3412` | 280px |
| 5️⃣ Database & External | `#E9D5FF` | `#6B21A8` | 220px |

**설정 방법**:
- 도형 우클릭 → `Edit Style` → `fillColor=#DBEAFE;strokeColor=#3B82F6;fontColor=#1E40AF`

### Step 3: 아이콘 가져오기

#### 3.1. 아이콘 임포트
```
File → Import → Device → docs/architecture-icons/ 폴더 선택
```

**한 번에 가져오기**:
- 16개 SVG 파일 모두 선택 (Cmd/Ctrl + A)
- `Import` 클릭

#### 3.2. 아이콘 크기 조정 (시각적 명확성 중요!)

**권장 크기** (시각적 우선순위에 따라):
- **주요 기술 스택**: **80 × 80px** (Next.js, FastAPI, Supabase 등)
- **보조 기술**: **64 × 64px** (Git, Docker 등)
- **세부 요소**: **48 × 48px** (작은 라이브러리, 유틸리티)

**크기 조정 팁**:
- 균일하게 조정: `Shift` 누른 채 모서리 드래그
- 정확한 크기 입력: 우클릭 → `Edit Style` → `width=80;height=80`
- 일괄 조정: 여러 아이콘 선택 → Format → Arrange → Same Size

### Step 4: 계층별 내용 배치

#### 4.1. Version Control Layer
```
┌────────────────────────────────────┐
│  [github.svg]  GitHub Repository    │
│     ├─ [git.svg] Developer          │
│     └─ [vercel.svg] Deploy          │
└────────────────────────────────────┘
```

**배치**:
1. GitHub 아이콘을 중앙에 배치
2. 텍스트 추가: "GitHub Repository" (24pt, Bold)
3. Git, Vercel 아이콘을 하위에 배치
4. 화살표로 연결 (점선)

#### 4.2. User Layer
```
┌────────────────────────────────────┐
│  💻 Desktop / 📱 Mobile / 🖥️ Tablet│
└────────────────────────────────────┘
```

**배치**:
- 텍스트만 배치 (아이콘 없음)
- 이모지 사용: 💻 📱 🖥️

#### 4.3. Frontend Layer
```
┌────────────────────────────────────┐
│  Next.js 15 + React 19 + TypeScript│
│  ┌──────┬──────┬──────┬──────┐    │
│  │Router│UI/UX │State │ API  │    │
│  └──────┴──────┴──────┴──────┘    │
└────────────────────────────────────┘
```

**배치**:
1. 상단에 아이콘 3개 나란히 배치:
   - `nextjs.svg` + `react.svg` + `typescript.svg`
2. 하단에 4개 박스 생성 (작은 Rectangle):
   - App Router (RSC)
   - UI/UX (Tailwind, Radix)
   - State Mgmt (Context API)
   - API Client (Fetch)
3. Tailwind, Lucide 아이콘을 UI/UX 박스 안에 배치

#### 4.4. Backend Layer
```
┌────────────────────────────────────┐
│  FastAPI + Python 3.13              │
│  ┌──────────────────────────────┐  │
│  │  Router Layer                 │  │
│  │  /auth /chat /community...    │  │
│  └──────────────────────────────┘  │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  Business Logic Layer         │  │
│  │  ┌───┬───┬───┬───┐           │  │
│  │  │JWT│RAG│Fn │Scr│           │  │
│  │  └───┴───┴───┴───┘           │  │
│  └──────────────────────────────┘  │
│             ▼                       │
│  ┌──────────────────────────────┐  │
│  │  Data Access Layer            │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

**배치**:
1. 상단에 `fastapi.svg` + `python.svg` 배치
2. 3개 하위 박스 생성 (수직 배치):
   - Router Layer
   - Business Logic Layer (내부에 4개 작은 박스)
   - Data Access Layer
3. JWT 아이콘을 Auth 박스에 배치
4. Selenium 아이콘을 Scraper 박스에 배치

#### 4.5. Database & External Services Layer
```
┌────────────────────────────────────┐
│  [supabase.svg] Supabase           │
│  [postgresql.svg] PostgreSQL       │
│  - Tables: users, policies...      │
│                                     │
│  [openai.svg] OpenAI API           │
│  - GPT-4o-mini, Embeddings...      │
└────────────────────────────────────┘
```

**배치**:
1. 좌측에 Supabase + PostgreSQL 아이콘
2. 우측에 OpenAI 아이콘
3. 테이블 목록 텍스트 추가

### Step 5: 연결선 및 화살표

#### 5.1. 화살표 스타일

| 연결 유형 | 스타일 | 색상 | 텍스트 |
|----------|--------|------|--------|
| Git Push/Pull | 점선 | `#6B7280` | "Git Push/Pull" |
| HTTPS | 실선 | `#3B82F6` | "HTTPS (TLS 1.3)" |
| REST API | 실선 | `#10B981` | "/auth, /chat, /community, /calendar" |
| SQL Query | 실선 | `#8B5CF6` | "SQL Query" |
| Vector Search | 실선 | `#8B5CF6` | "pgvector search" |
| API Call (Chat) | 점선 | `#F97316` | "Chat API" |
| API Call (Embed) | 점선 | `#F97316` | "Embedding API" |
| Web Scraping | 점선 | `#EF4444` | "Selenium scraping" |

#### 5.2. 화살표 추가 방법
1. 좌측 패널에서 `Arrows` 선택
2. 도형 간 연결
3. 우클릭 → `Edit Style` → `strokeColor=#3B82F6;strokeWidth=2;dashed=0`

**점선 설정**: `dashed=1`

#### 5.3. 주요 연결선

**User → Frontend**:
```
strokeColor=#3B82F6;strokeWidth=3;dashed=0
텍스트: "HTTPS (TLS 1.3)"
```

**Frontend → Backend** (4개 분기):
```
strokeColor=#10B981;strokeWidth=2;dashed=0
텍스트:
- "/api/auth"
- "/api/chat"
- "/api/community"
- "/api/calendar"
```

**Backend → Database** (2개 분기):
```
strokeColor=#8B5CF6;strokeWidth=2;dashed=0
텍스트:
- "SQL Query"
- "Vector Search (pgvector)"
```

**Backend → OpenAI** (2개 분기):
```
strokeColor=#F97316;strokeWidth=2;dashed=1
텍스트:
- "Chat API (GPT-4o-mini)"
- "Embedding API (BGE-M3)"
```

### Step 6: 범례 및 마무리

#### 6.1. 범례 추가
```
┌─────────────────────────────────┐
│  범례 (Legend)                   │
│  ─────  실선: 동기 호출          │
│  ─ ─ ─  점선: 비동기/배치 작업   │
│  ──→   데이터 흐름               │
└─────────────────────────────────┘
```

**배치**: 우측 하단

#### 6.2. 제목 및 메타데이터
```
┌─────────────────────────────────────────┐
│  BabyPolicy - 시스템 아키텍처           │
│  AI 기반 육아 정책 추천 서비스          │
│                                         │
│  버전: 1.0.0                            │
│  작성일: 2025-10-12                     │
│  작성자: BabyPolicy Team                │
└─────────────────────────────────────────┘
```

**배치**: 최상단 중앙
**스타일**:
- 제목: 32pt, Bold
- 부제: 18pt, Regular
- 메타: 12pt, Gray

#### 6.3. 최종 체크리스트

- [ ] 5개 계층 컨테이너 배치 완료
- [ ] 16개 아이콘 모두 배치 (크기 64×64px)
- [ ] 계층별 배경색 적용
- [ ] 주요 연결선 8개 추가 (4개 실선, 4개 점선)
- [ ] 텍스트 라벨 명확히 표기
- [ ] 범례 추가
- [ ] 제목 및 메타데이터 추가
- [ ] Grid 정렬 확인 (Ctrl+Shift+A)

---

## 🎨 스타일 가이드

### 색상 팔레트

**계층별 배경색**:
```css
Version Control:  #F3F4F6 (Gray 100)
User:             #DBEAFE (Blue 100)
Frontend:         #D1FAE5 (Green 100)
Backend:          #FED7AA (Orange 100)
Database:         #E9D5FF (Purple 100)
```

**텍스트 색상**:
```css
Headings:     #111827 (Gray 900) - Bold 20pt
Subheadings:  #374151 (Gray 700) - Semibold 16pt
Body:         #6B7280 (Gray 500) - Regular 14pt
Labels:       #9CA3AF (Gray 400) - Regular 12pt
```

**화살표 색상**:
```css
HTTPS:        #3B82F6 (Blue 500)
REST API:     #10B981 (Green 500)
SQL:          #8B5CF6 (Purple 500)
API Call:     #F97316 (Orange 500)
Scraping:     #EF4444 (Red 500)
Git:          #6B7280 (Gray 500)
```

### 폰트

**권장 폰트**:
- 영문: `Inter`, `Roboto`, `Arial`
- 한글: `Noto Sans KR`, `Pretendard`, `맑은 고딕`

**폰트 크기**:
- 제목 (Title): 32pt, Bold
- 부제 (Subtitle): 20pt, Semibold
- 헤딩 (Heading): 16pt, Semibold
- 본문 (Body): 14pt, Regular
- 라벨 (Label): 12pt, Regular

---

## 💡 프로 팁

### 정렬 단축키
- **수평 정렬**: `Ctrl + Shift + H`
- **수직 정렬**: `Ctrl + Shift + V`
- **균등 분포 (수평)**: `Ctrl + Shift + E`
- **균등 분포 (수직)**: `Ctrl + Shift + D`
- **그리드 정렬**: `Ctrl + Shift + A`

### 효율적인 작업 흐름
1. **레이어 사용**: View → Layers → 계층별 레이어 생성
2. **그룹화**: 관련 도형 선택 → `Ctrl + G`
3. **복제**: `Ctrl + D` (같은 크기의 박스 여러 개 만들 때)
4. **스타일 복사**: 도형 선택 → `Ctrl + C` → 다른 도형 선택 → `Ctrl + Shift + V`

### 아이콘 배치 팁 (시각적 임팩트 극대화)

**간격 및 여백** (넉넉하게!):
- **아이콘 간 간격**: **32px** (시각적 분리 명확)
- **컨테이너 상단 여백**: **24px** (숨통 트이는 공간)
- **컨테이너 좌우 여백**: **24px**
- **아이콘 그룹 간 간격**: **48px** (계층 구분)

**정렬 및 배치**:
- **수평 정렬**: 항상 Grid에 맞춰 정렬 (`Snap to Grid` 활성화)
- **아이콘 크기 통일**: 같은 레벨의 아이콘은 동일 크기
- **시각적 그룹핑**: 관련된 아이콘끼리 가까이 배치

**시각적 균형**:
- **중앙 정렬**: 주요 아이콘은 레이어 중앙에 배치
- **좌우 대칭**: 가능하면 좌우 균형 유지
- **시선 흐름**: 위에서 아래로 자연스럽게 흐르도록

### 연결선 팁
- **시작점**: 도형 중앙이 아닌 가장자리에서 시작
- **직각**: Waypoints 사용하여 깔끔한 직각 연결
- **교차 방지**: 가능한 선이 교차하지 않도록 배치
- **라벨 위치**: 연결선 중간에 배치, 배경색 흰색

---

## ✨ 시각적 명확성 체크리스트

이 섹션은 **한눈에 보기 좋은 다이어그램**을 만들기 위한 최종 점검 가이드입니다.

### 1. 아이콘 가독성 체크
- [ ] **주요 아이콘 크기**: 80×80px 이상으로 충분히 크게
- [ ] **아이콘 간 간격**: 최소 32px 이상 (겹치지 않고 명확하게)
- [ ] **아이콘 정렬**: Grid에 정확히 맞춤 (지저분해 보이지 않도록)
- [ ] **색상 대비**: 배경색과 아이콘이 명확히 구분되는지 확인

### 2. 계층 구분 체크
- [ ] **배경색 대비**: 5개 레이어가 색상으로 명확히 구분
- [ ] **레이어 높이**: 내용물에 비해 충분한 높이 (여백 24px 이상)
- [ ] **레이어 순서**: 위에서 아래로 논리적 흐름 (Version Control → User → Frontend → Backend → Database)

### 3. 연결선 명확성 체크
- [ ] **선 굵기**: 주요 연결선은 2~3px (너무 가늘지 않게)
- [ ] **색상 대비**: 배경과 선이 명확히 구분
- [ ] **교차 최소화**: 선끼리 교차하는 부분 최소화
- [ ] **라벨 위치**: 연결선 중간, 배경 흰색으로 가독성 확보

### 4. 텍스트 가독성 체크
- [ ] **제목 크기**: 32pt 이상 (한눈에 들어오는 크기)
- [ ] **본문 크기**: 14pt 이상 (너무 작지 않게)
- [ ] **폰트 색상**: 배경과 명확한 대비
- [ ] **줄바꿈**: 긴 텍스트는 적절히 줄바꿈

### 5. 전체 균형 체크
- [ ] **좌우 대칭**: 가능하면 시각적 균형 유지
- [ ] **여백 충분**: 답답하지 않게 넉넉한 공간
- [ ] **시선 흐름**: 위→아래, 좌→우 자연스러운 흐름
- [ ] **정보 밀도**: 한 레이어에 너무 많은 정보 집중 방지

### 6. 3미터 테스트 (가장 중요!)
- [ ] **3미터 거리에서 테스트**: 화면에서 3미터 떨어져서 봤을 때도 주요 아이콘과 구조가 보이는가?
- [ ] **5초 규칙**: 처음 보는 사람이 5초 안에 시스템 구조를 파악할 수 있는가?
- [ ] **색상 구분**: 각 레이어가 색상만으로도 즉시 구분되는가?

### 빠른 개선 팁
```
❌ 피해야 할 것:
- 아이콘이 너무 작음 (48px 이하)
- 텍스트가 너무 많음
- 선이 복잡하게 얽힘
- 여백이 부족함
- 색상이 비슷해서 구분 안 됨

✅ 해야 할 것:
- 아이콘을 크고 명확하게 (80px+)
- 필수 정보만 표기
- 직선/직각 연결 우선
- 넉넉한 공간 확보
- 명확한 색상 대비
```

---

## 📤 내보내기

### 권장 포맷

1. **PNG (프레젠테이션)**:
   - File → Export as → PNG
   - Resolution: `300 DPI`
   - Size: `3000 × 4000px`
   - Background: Transparent 체크 해제

2. **SVG (웹사이트)**:
   - File → Export as → SVG
   - Text Settings: Convert labels to SVG
   - Include a copy of my diagram: 체크

3. **PDF (문서)**:
   - File → Export as → PDF
   - Page Size: A3
   - Fit to: 1 page wide, 1 page tall

### 파일명 규칙
```
babypolicy-architecture-v1.0-20251012.png
babypolicy-architecture-v1.0-20251012.svg
babypolicy-architecture-v1.0-20251012.pdf
```

---

## 🔗 참고 자료

### 내부 문서
- [전체 아키텍처 문서](../../ARCHITECTURE_DIAGRAM.md) - 기술 스택 상세 설명
- [아이콘 README](../architecture-icons/README.md) - 아이콘 목록 및 사용법

### 외부 링크
- [Draw.io 공식 문서](https://www.diagrams.net/doc/)
- [Simple Icons](https://simpleicons.org/) - 추가 아이콘 다운로드
- [Tailwind CSS 색상 팔레트](https://tailwindcss.com/docs/customizing-colors)

---

## 🆘 문제 해결

### Q1: 아이콘이 흐릿하게 보여요
**A**: SVG 파일을 PNG로 변환하지 말고, Draw.io에 직접 SVG로 임포트하세요.

### Q2: 연결선이 도형을 관통해요
**A**: 우클릭 → `To Back` 또는 레이어 순서 조정

### Q3: 텍스트가 박스 밖으로 나가요
**A**: 텍스트 박스 크기 조정 또는 `Word Wrap` 활성화

### Q4: 저장이 안돼요
**A**: 브라우저 버전은 자동 저장, 데스크톱 앱은 `Ctrl + S`

### Q5: 아이콘 색상을 변경하고 싶어요
**A**: SVG를 텍스트 에디터로 열어 `fill` 속성 변경 후 재임포트

---

**작성일**: 2025-10-12
**버전**: 1.0.0
**작성자**: BabyPolicy Team

이 가이드를 따라 전문적이고 일관된 아키텍처 다이어그램을 제작할 수 있습니다! 🚀
