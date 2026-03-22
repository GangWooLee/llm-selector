# 서비스 아키텍처

## 전체 구조: 프론트엔드/백엔드 분리형

Next.js 프론트엔드(Vercel)와 FastAPI+Pydantic AI 에이전트 백엔드(Render)를 분리 배포하는 구조. 2025-2026 AI 에이전트 앱의 업계 표준 패턴.

```
┌─────────────────────────────────────────┐
│           사용자 브라우저                   │
│  Next.js (Vercel)                       │
│  ┌─────────┐  ┌──────────────────────┐  │
│  │ 용도 입력 │→│  에이전트 추론 과정     │  │
│  │   폼    │  │  (SSE 스트리밍 표시)   │  │
│  └─────────┘  └──────────────────────┘  │
│       │              ▲                   │
└───────┼──────────────┼───────────────────┘
        │ POST         │ SSE
        ▼              │
┌───────────────────────────────────────────┐
│       FastAPI + Pydantic AI (Render)       │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │     Model Advisor Agent             │  │
│  │                                     │  │
│  │  [1] 용도 분석 (LLM 추론)            │  │
│  │       │                             │  │
│  │  [2] 도구 호출 결정                   │  │
│  │       ├── search_models()           │  │
│  │       ├── compare_pricing()         │  │
│  │       ├── get_benchmarks()          │  │
│  │       ├── assess_model_fit()        │  │
│  │       ├── web_search()              │  │
│  │       └── get_model_details()       │  │
│  │       │                             │  │
│  │  [3] 결과 종합 + 비교 리포트 생성      │  │
│  └─────────────────────────────────────┘  │
│       │                                   │
│  ┌────▼────┐  ┌───────────┐              │
│  │ 모델 DB  │  │ 웹 검색 API │              │
│  │(Postgres)│  │(Tavily 등) │              │
│  └─────────┘  └───────────┘              │
└───────────────────────────────────────────┘
```

---

## 기술 스택

### 프론트엔드 (Next.js → Vercel)

| 영역 | 기술 | 선정 이유 |
|------|------|----------|
| Framework | Next.js 15 (App Router) | Vercel 네이티브 배포, SSR/SSG 지원 |
| Language | TypeScript | 타입 안정성 |
| Styling | Tailwind CSS 4 | 빠른 UI 개발, 유틸리티 퍼스트 |
| UI 컴포넌트 | shadcn/ui | 접근성, 커스터마이징 용이, 소유권 |

### 백엔드 — 에이전트 서버 (FastAPI + Pydantic AI → Render)

| 영역 | 기술 | 선정 이유 |
|------|------|----------|
| Framework | FastAPI | Python 비동기, SSE 네이티브 지원 |
| Agent Framework | Pydantic AI | 타입세이프, 간결, 모델 비교 에이전트에 적합 |
| DB | PostgreSQL (Render) | 관계형, JSONB 지원, Render 네이티브 통합 |
| ORM | SQLAlchemy + Alembic | 마이그레이션 관리, 성숙한 생태계 |
| LLM API | OpenRouter API | 사용자 키 경유, 400+ 모델 접근 |
| 웹 검색 | Tavily API 또는 DuckDuckGo | 최신 모델 정보/리뷰 수집 |
| 배포 | Render (Docker) | 무료 티어, 100분 타임아웃, Rails/FastAPI 친화적 |

### 프론트↔백엔드 통신

| 방식 | 용도 | 선정 이유 |
|------|------|----------|
| REST (POST) | 에이전트 태스크 시작 | 단순, 표준 |
| SSE (Server-Sent Events) | 에이전트 추론 과정 실시간 스트리밍 | WebSocket보다 단순, 단방향 스트리밍에 최적 |

---

## 배포 구조

### Vercel (프론트엔드)
- Next.js 15 자동 배포 (Git push → 자동 빌드/배포)
- Edge Functions로 빠른 응답
- 무료 티어: Hobby Plan

### Render (백엔드)
- Docker 기반 FastAPI 배포
- PostgreSQL 데이터베이스 (무료 티어: 256MB)
- Cron Job: 모델 DB 자동 동기화 (매일 1회)
- 무료 티어: 서비스 비활성 시 자동 일시 중지, 요청 시 즉시 기동

### 환경변수

**프론트엔드 (Vercel)**:
- `NEXT_PUBLIC_API_URL`: 백엔드 API URL (Render)

**백엔드 (Render)**:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `TAVILY_API_KEY`: 웹 검색 API 키 (선택)
- `ALLOWED_ORIGINS`: CORS 허용 도메인 (Vercel URL)

---

## 데이터 흐름

### 1. 모델 DB 동기화 (백그라운드)
```
Render Cron Job (매일 1회)
  → OpenRouter GET /api/v1/models
  → 응답 파싱 (400+ 모델)
  → PostgreSQL upsert (신규 추가, 가격 변동 업데이트)
```

### 2. 사용자 요청 처리
```
사용자 (브라우저)
  → [자연어 용도 입력]
  → POST /api/v1/advise (SSE)
  → FastAPI: ModelAdvisorAgent 실행
    → 에이전트가 자율적으로 도구 호출 (DB 조회, 벤치마크, 웹 검색)
    → 각 단계를 SSE로 실시간 스트리밍
  → 최종 ComparisonReport 반환
  → 프론트엔드 대시보드에 비교 결과 표시
```

---

## Rails 템플릿 자산 활용

`/Users/igangu/repos/claude-rails-template`에서 Next.js/FastAPI 프로젝트에 적응 가능한 자산:

| 자산 | 활용 방법 |
|------|----------|
| 개발 워크플로우 (/plan → /tdd → /verify) | Phase별 개발 프로세스에 적용 |
| 품질 게이트 | Phase 간 체크포인트 개념 차용 |
| 코드 표준 (메서드 길이, 복잡도 제한) | TypeScript/Python 코드에 범용 적용 |
| 에이전트 시스템 (code-review, security) | Claude Code 에이전트로 코드 리뷰 활용 |
| 디자인 지식 베이스 | UI 컴포넌트 설계 시 참조 |

---

## 프로젝트 디렉토리 구조

```
llm_selector/
├── docs/                              # 기획 문서
├── frontend/                          # Next.js (Vercel)
│   ├── src/
│   │   ├── app/                       # App Router 페이지
│   │   ├── components/                # UI 컴포넌트
│   │   ├── lib/                       # 유틸리티, API 클라이언트
│   │   └── types/                     # 타입 정의
│   ├── next.config.ts
│   └── package.json
│
├── backend/                           # FastAPI + Pydantic AI (Render)
│   ├── app/
│   │   ├── agent/                     # 에이전트 정의, 도구, 프롬프트
│   │   ├── api/routes/                # API 라우트
│   │   ├── db/                        # DB 모델, 세션, 쿼리
│   │   └── services/                  # 외부 서비스 (OpenRouter, 웹 검색)
│   ├── alembic/                       # DB 마이그레이션
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml
│
├── CLAUDE.md                          # Claude Code 프로젝트 컨텍스트
└── README.md
```
