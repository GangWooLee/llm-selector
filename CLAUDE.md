# LLM Selector

## Project Overview
- **Project**: LLM Selector — 실시간 데이터 기반 AI 모델 선택 어드바이저
- **핵심 가치**: 정보의 신선도 — 항상 최신 모델 데이터 반영
- **MVP 범위**: 용도 분석 → 모델 매칭 → 근거 기반 비교 리포트 (2주)

---

## 🔴 불변 설계 원칙 (절대 위반 금지)

코드를 작성하거나 구조를 변경할 때, 아래 원칙은 어떤 상황에서도 지켜야 한다.
위반이 감지되면 즉시 중단하고 수정한다.

1. **LLM은 자체 지식으로 모델 정보를 답하지 않는다**
   → 에이전트는 반드시 도구(Tools)를 호출하여 DB/웹에서 데이터를 조회한 후에만 답변
   → 시스템 프롬프트에 이 제약을 명시 (상세: `docs/02-agent-workflow.md`)

2. **사용자 API 키를 서버에 저장하지 않는다**
   → 요청마다 전달받아 사용 후 폐기, 로그에 키 출력 금지
   → 프론트엔드: sessionStorage만 사용 (상세: `docs/04-feature-spec.md` F1)

3. **모든 추천에는 데이터 근거를 제시한다**
   → "이 모델이 좋습니다" 결론만 던지지 않음
   → 벤치마크 점수, 가격 비교, 적합도 평가 등 구체적 데이터 첨부 (상세: `docs/02-agent-workflow.md`)

4. **계층 분리를 지킨다**
   → Backend: Routes(얇게) → Services → Agent → DB Queries
   → Frontend: Server Components 기본, `"use client"`는 필요할 때만
   → 상위 계층이 하위를 호출, 역방향 의존 금지 (상세: `docs/01-architecture.md`)

5. **사전 구축된 DB에서 조회한다 (매 요청마다 크롤링하지 않음)**
   → 빠른 응답 속도를 보장하기 위해 모델 데이터는 DB에 미리 동기화
   → 동기화는 Cron Job(매일 1회)으로 별도 수행 (상세: `docs/03-data-model.md`)

---

## Architecture

**프론트엔드/백엔드 분리형**:
- **Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind 4 + shadcn/ui → **Vercel**
- **Backend**: FastAPI + Pydantic AI + SQLAlchemy → **Render** (Docker)
- **DB**: PostgreSQL (Render)
- **통신**: REST + SSE (Server-Sent Events)

---

## 📚 기획 문서 라우팅 (반드시 따를 것)

작업 유형에 따라 해당 문서를 **먼저 읽고** 작업을 시작한다.
문서를 읽지 않고 구현하면 기획 의도와 어긋날 위험이 있다.

| 이런 작업을 할 때 | 반드시 먼저 읽을 문서 | 핵심 확인 사항 |
|------------------|---------------------|---------------|
| 프로젝트 맥락 파악, 새 세션 시작 | `docs/00-overview.md` | 문제 정의, 타겟 사용자, MVP 범위 |
| 디렉토리 생성, 배포 설정, 인프라 | `docs/01-architecture.md` | 디렉토리 구조, 배포 구조, 환경변수 |
| 에이전트 구현, 도구 추가/수정, SSE | `docs/02-agent-workflow.md` | 시스템 프롬프트, 도구 6개 스펙, SSE 이벤트 타입, 출력 스키마 |
| DB 모델, 마이그레이션, 동기화 | `docs/03-data-model.md` | 3개 테이블 스키마, 인덱스, OpenRouter 필드 매핑 |
| UI 컴포넌트, 사용자 플로우, 기능 구현 | `docs/04-feature-spec.md` | F1~F5 상세 동작, UI 상태 전이 |
| API 엔드포인트 추가/수정 | `docs/05-api-spec.md` | 요청/응답 스키마, 에러 코드, CORS |
| Phase 완료 확인, 다음 작업 결정 | `docs/06-dev-plan.md` | Phase별 체크리스트, 검증 계획 |

### 복합 작업 시 읽기 순서
- **에이전트 도구 추가**: `02-agent-workflow.md` → `03-data-model.md` → `05-api-spec.md`
- **새 UI 기능 구현**: `04-feature-spec.md` → `02-agent-workflow.md` (출력 스키마) → `05-api-spec.md`
- **DB 스키마 변경**: `03-data-model.md` → `02-agent-workflow.md` (도구 영향) → `05-api-spec.md` (응답 영향)

---

## Tech Stack Quick Reference

| 영역 | 기술 |
|------|------|
| Frontend Framework | Next.js 15 (App Router) |
| Frontend Language | TypeScript |
| Frontend Styling | Tailwind CSS 4 |
| Frontend Components | shadcn/ui |
| Backend Framework | FastAPI |
| Agent Framework | Pydantic AI |
| Backend Language | Python 3.12+ |
| Database | PostgreSQL |
| ORM | SQLAlchemy + Alembic |
| LLM API | OpenRouter API (사용자 키) |
| Web Search | Tavily API |
| Frontend Deploy | Vercel |
| Backend Deploy | Render (Docker) |

---

## Agent Tools (6개)

| 도구 | 목적 | 관련 DB 테이블 |
|------|------|---------------|
| `search_models` | 요구사항 기반 모델 DB 검색 | models, model_tags |
| `compare_pricing` | 후보 모델 가격 비교 + 월 비용 시뮬레이션 | models |
| `get_benchmarks` | 벤치마크 데이터 조회 | model_benchmarks |
| `assess_model_fit` | 용도 적합도 평가 (스코어링) | models, model_tags, model_benchmarks |
| `web_search` | 최신 모델 정보 웹 검색 | (외부 API: Tavily) |
| `get_model_details` | 모델 전체 상세 조회 | models + benchmarks + tags JOIN |

---

## Project Status

### 현재 Phase
> **Phase 2 — 에이전트 워크플로우 핵심 구현** 🔜 다음

### Phase 진행 상황
| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 0 | 기획 확정 + Claude Code 환경 세팅 | ✅ 완료 |
| Phase 1 | 프로젝트 셋업 & 인프라 | ✅ 완료 |
| Phase 2 | 에이전트 워크플로우 핵심 구현 (Day 4-8) | 🔜 다음 |
| Phase 3 | 대시보드 UI (Day 9-11) | ⬜ 대기 |
| Phase 4 | 마무리 & 배포 (Day 12-14) | ⬜ 대기 |

상세 체크리스트: `docs/06-dev-plan.md` 참조

---

## Codebase Inventory

### Backend (12 modules)
| 영역 | 파일 | 내용 |
|------|------|------|
| DB Models | `app/db/models.py` | Model, ModelBenchmark, ModelTag (3 테이블) |
| DB Session | `app/db/session.py` | async engine + sessionmaker |
| DB Queries | `app/db/queries.py` | 6개 쿼리 함수 |
| API Routes | `app/api/routes/models.py` | GET /models, GET /models/{id} |
| API Routes | `app/api/routes/sync.py` | POST /sync |
| Schemas | `app/schemas/model.py` | 7개 Pydantic 모델 |
| Schemas | `app/schemas/sync.py` | SyncResponse |
| Services | `app/services/openrouter.py` | OpenRouter API 클라이언트 + 필드 매핑 |
| Services | `app/services/sync_service.py` | DB 동기화 오케스트레이션 |
| Config | `app/config.py` | pydantic-settings |
| App | `app/main.py` | FastAPI 앱 + CORS + 라우터 |
| Migration | `alembic/versions/c2ac3ba0363d_initial_tables.py` | 3 테이블 초기 마이그레이션 |

### Frontend (4 컴포넌트 + 2 페이지)
| 영역 | 파일 | 내용 |
|------|------|------|
| Component | `components/ApiKeyInput.tsx` | F1: API 키 관리 (5상태) |
| Component | `components/layout/Header.tsx` | 사이트 헤더 |
| Page | `app/page.tsx` | 랜딩 페이지 |
| API Route | `app/api/validate-key/route.ts` | OpenRouter 키 검증 프록시 |
| Lib | `lib/api.ts` | 백엔드 API 클라이언트 |
| Types | `types/model.ts`, `types/api.ts` | TypeScript 타입 |

### Tests (36 total)
| 영역 | 파일 | 테스트 수 |
|------|------|----------|
| Backend DB | `tests/test_db/test_queries.py` | 10 |
| Backend API | `tests/test_api/test_models.py` | 4 |
| Backend Sync | `tests/test_services/test_sync.py` | 4 |
| Frontend | `components/__tests__/ApiKeyInput.test.tsx` | 16 |
| Frontend | `components/__tests__/Header.test.tsx` | 2 |

### Design (4 문서)
| 파일 | 내용 |
|------|------|
| `docs/design/tokens/design-system.md` | 컬러, 타이포, 스페이싱 토큰 |
| `docs/design/components/ApiKeyInput.md` | F1 컴포넌트 스펙 (5상태, 접근성) |
| `docs/design/layouts/advisor.md` | 어드바이저 페이지 와이어프레임 |
| `docs/design/layouts/model-list.md` | 모델 탐색 페이지 와이어프레임 |

---

## Project-Specific Notes

### Lessons Learned (Phase 1)

1. **SQLite JSONB 호환**: 테스트에서 SQLite 사용 시 `JSON` 타입 폴백 필요. conftest.py에서 event listener로 `engine.connect` 시 `pragma` 설정.

2. **Next.js Google Fonts**: 오프라인/샌드박스 환경에서 `next/font/google` fetch 실패. `next/font/local` 또는 Tailwind 기본 폰트로 대체.

3. **Agent Team 파일 소유권**: 독점 파일 경계가 명확할수록 병렬 작업 효율 극대화. 7명 에이전트가 충돌 0건으로 동시 작업 완료.

4. **OpenRouter 가격 정밀도**: `pricing.prompt`가 문자열("0.000015")로 반환됨. `Decimal(str)` 변환 필수, `float()` 사용 시 서브센트 손실.

### OpenRouter API
- 모델 목록: `GET https://openrouter.ai/api/v1/models`
- 키 검증: `GET https://openrouter.ai/api/v1/key`
- Chat Completion: `POST https://openrouter.ai/api/v1/chat/completions`
- Structured Output, Function Calling 지원

### 개발 워크플로우
- `/plan` → `/verify` → `/wrap-up` 사이클
- Phase 완료마다 검증 실행 (빌드 + 테스트 + 린트)
- 검증 없이 완료 선언 금지 (`.claude/rules/common/verification-discipline.md`)
