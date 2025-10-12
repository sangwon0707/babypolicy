# 기술 스택 아이콘 모음

이 디렉토리에는 BabyPolicy 프로젝트의 아키텍처 다이어그램 작성에 필요한 기술 스택 아이콘들이 포함되어 있습니다.

## 📦 포함된 아이콘 목록 (총 17개)

### 프론트엔드
- **nextjs.svg** - Next.js (검정색 #000000)
- **react.svg** - React (파란색 #61DAFB)
- **typescript.svg** - TypeScript (파란색 #3178C6)
- **tailwindcss.svg** - Tailwind CSS (청록색 #06B6D4)
- **lucide.svg** - Lucide Icons (빨간색 #F56565)

### 백엔드
- **fastapi.svg** - FastAPI (청록색 #009688)
- **python.svg** - Python (파란색 #3776AB)

### 데이터베이스
- **postgresql.svg** - PostgreSQL (파란색 #4169E1)
- **supabase.svg** - Supabase (초록색 #3FCF8E)

### AI & 외부 서비스
- **openai.svg** - OpenAI (보라색 #412991)
- **selenium.svg** - Selenium (초록색 #43B02A)

### 버전 관리 & DevOps
- **git.svg** - Git (주황색 #F05032)
- **github.svg** - GitHub (검정색 #181717)
- **docker.svg** - Docker (파란색 #2496ED)
- **vercel.svg** - Vercel (검정색 #000000)
- **render.svg** - Render (청록색 #46E3B7)

### 인증
- **jwt.svg** - JSON Web Tokens (검정색)

## 🎨 Draw.io에서 사용하기

### 1. 아이콘 가져오기
1. Draw.io 열기
2. `File` → `Import` → `From Device...`
3. SVG 파일 선택하여 가져오기

### 2. 아이콘 크기 권장사항 (시각적 명확성)
- **주요 기술 스택**: **80 × 80px** (Next.js, FastAPI, Supabase 등)
- **보조 기술**: **64 × 64px** (Git, Docker 등)
- **아이콘 간 간격**: **32px** (명확한 시각적 분리)
- **여백**: 컨테이너 가장자리에서 **24px**

### 3. 아이콘 배치 예시
```
┌─────────────────────────────────────────────┐
│  프론트엔드 레이어 (Frontend)                │
│                                              │
│    ┌────────┐  ┌────────┐  ┌────────┐      │
│    │  Next  │  │ React  │  │   TS   │      │
│    │ 80×80  │  │ 80×80  │  │ 80×80  │      │
│    └────────┘  └────────┘  └────────┘      │
│        ↑ 32px 간격 ↑    ↑ 32px 간격 ↑      │
└─────────────────────────────────────────────┘
```

### 4. 색상 구성 추천
- **사용자 레이어**: 파란색 (#3B82F6)
- **프론트엔드 레이어**: 초록색 (#10B981)
- **백엔드 레이어**: 주황색 (#F97316)
- **데이터베이스 레이어**: 보라색 (#8B5CF6)
- **외부 서비스 레이어**: 회색 (#6B7280)

## 📐 레이아웃 가이드

### 권장 다이어그램 크기
- **캔버스**: 1200px × 1600px
- **아이콘 크기**: 64px × 64px
- **여백**: 20px

### 레이어 순서 (상단 → 하단)
1. 사용자 (User)
2. 프론트엔드 (Frontend)
3. 백엔드 (Backend)
4. 데이터베이스 (Database)
5. 외부 서비스 (External Services)

### 화살표 스타일
- **HTTPS**: 실선 (Solid) + 파란색
- **REST API**: 실선 (Solid) + 초록색
- **DB Connection**: 실선 (Solid) + 보라색
- **API Call**: 점선 (Dashed) + 주황색

## 🔗 아이콘 출처
모든 아이콘은 [Simple Icons](https://simpleicons.org/)에서 제공됩니다.
- 라이선스: CC0 1.0 Universal (Public Domain)
- 사용 제한: 없음 (자유롭게 사용 가능)

## 💡 추가 아이콘 다운로드 방법

필요한 아이콘이 더 있다면 다음 명령어로 다운로드할 수 있습니다:

```bash
# 예시: Redis 아이콘 다운로드
curl -sL "https://cdn.simpleicons.org/redis/DC382D" -o redis.svg

# 형식: https://cdn.simpleicons.org/{아이콘이름}/{색상코드}
```

## 📚 참고 자료
- [Simple Icons 웹사이트](https://simpleicons.org/)
- [Draw.io 공식 문서](https://www.diagrams.net/doc/)
- [BabyPolicy 아키텍처 문서](../ARCHITECTURE_DIAGRAM.md)

---

**마지막 업데이트**: 2025-10-12
