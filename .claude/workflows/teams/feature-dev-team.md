# Feature Development Team — 11역할 전문 구현 팀

## 사용 시점
Phase 1-3 구현, 전체 스택 병렬 작업 시

## 구성 (11명 + lead)

### 🎨 디자인
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **ui-ux-designer** | opus | default | 컴포넌트 스펙, 레이아웃 설계, 접근성, 반응형, shadcn/ui 활용 |

### 🖥️ 프론트엔드
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **frontend-dev** | opus | default | Next.js App Router 페이지, React 컴포넌트 구현, 상태 관리 |
| **frontend-qa** | opus | default | Vitest, @testing-library/react, 컴포넌트 테스트, 접근성 감사 |

### 🔗 통합
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **sse-specialist** | opus | default | FastAPI StreamingResponse + 프론트 SSE 클라이언트 + 이벤트 파서 |

### ⚙️ 백엔드 API
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **api-dev** | opus | default | FastAPI 라우트, Pydantic 요청/응답 스키마, 에러 처리, CORS |

### 🤖 AI 에이전트 (3명)
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **agent-architect** | opus | default | Pydantic AI 에이전트 설계, 오케스트레이션, 실행 흐름 |
| **tool-dev** | opus | default | 6개 에이전트 도구 함수 구현 (search_models, compare_pricing 등) |
| **prompt-engineer** | opus | default | 시스템 프롬프트 설계, 출력 스키마(ComparisonReport) 설계 |

### 🗄️ 데이터 (2명)
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **db-engineer** | opus | default | SQLAlchemy 모델, Alembic 마이그레이션, queries.py, 인덱스 |
| **sync-engineer** | opus | default | OpenRouter API 동기화 서비스, upsert 로직, Cron Job |

### ✅ 백엔드 QA
| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| **backend-qa** | opus | default | pytest, 에이전트 도구 테스트, API 엔드포인트 테스트, DB 쿼리 테스트 |

---

## 파일 소유권 (독점 — 동시 수정 금지)

| 소유자 | 독점 파일 |
|--------|----------|
| **ui-ux-designer** | `docs/design/` (신규), 디자인 스펙 문서 |
| **frontend-dev** | `frontend/src/app/`, `frontend/src/components/`, `frontend/src/lib/`, `frontend/src/types/` |
| **frontend-qa** | `frontend/src/**/__tests__/`, `frontend/src/**/*.test.*` |
| **sse-specialist** | `frontend/src/lib/sse-client.ts`, `backend/app/api/routes/advise.py`, `backend/app/utils/sse.py` (SSE 헬퍼) |
| **api-dev** | `backend/app/api/routes/models.py`, `backend/app/api/routes/sync.py`, `backend/app/api/deps.py`, `backend/app/schemas/` |
| **agent-architect** | `backend/app/agent/advisor.py`, `backend/app/agent/__init__.py` |
| **tool-dev** | `backend/app/agent/tools/` (모든 도구 파일) |
| **prompt-engineer** | `backend/app/agent/prompts.py`, `backend/app/agent/schemas.py` (출력 스키마) |
| **db-engineer** | `backend/app/db/models.py`, `backend/app/db/session.py`, `backend/app/db/queries.py`, `backend/alembic/` |
| **sync-engineer** | `backend/app/services/sync_service.py`, `backend/app/services/openrouter.py` |
| **backend-qa** | `backend/tests/` (모든 테스트 파일), `backend/tests/conftest.py` |
| **lead** | `docs/`, `CLAUDE.md`, `.claude/`, `backend/app/main.py`, `backend/app/config.py` |

### 공유 파일 규칙
- **읽기**: 모든 멤버가 모든 파일 읽기 가능
- **쓰기**: 위 독점 파일만 해당 소유자가 수정
- **경계 파일** (2명 이상 관련): lead가 조정
  - `backend/app/main.py` (라우터 등록): lead가 관리, api-dev가 요청
  - `frontend/package.json`: lead가 관리, frontend-dev가 요청

---

## Phase/Wave 구조

### Phase 1: 인프라 셋업 (Day 1-3)

**Wave 1A (순차 — DB가 먼저)**:
| 순서 | 멤버 | 작업 |
|------|------|------|
| 1 | db-engineer | SQLAlchemy 모델 3개 테이블 정의 |
| 2 | db-engineer | Alembic 초기 마이그레이션 |
| 3 | db-engineer | queries.py 기본 CRUD |

**Wave 1B (병렬 — DB 완료 후)**:
| 멤버 | 작업 |
|------|------|
| sync-engineer | OpenRouter API 클라이언트 + 동기화 서비스 + 초기 데이터 로드 |
| api-dev | FastAPI 앱 스켈레톤, CORS, 모델 목록/상세 엔드포인트 |
| ui-ux-designer | 전체 페이지 레이아웃 설계, 컴포넌트 스펙 문서 작성 |
| frontend-dev | Next.js 초기화, Tailwind 4, shadcn/ui, 기본 레이아웃 |
| backend-qa | conftest.py, DB fixture, 모델 테스트 |
| lead | Dockerfile, render.yaml, 환경변수, Vercel 설정 |

**Gate 1**: `backend build OK` + `pytest pass` + `frontend build OK` + `동기화 1회 성공`

### Phase 2: 에이전트 코어 (Day 4-8)

**Wave 2A (순차 — 에이전트 설계가 먼저)**:
| 순서 | 멤버 | 작업 |
|------|------|------|
| 1 | prompt-engineer | 시스템 프롬프트 작성 + ComparisonReport 출력 스키마 |
| 2 | agent-architect | Pydantic AI 에이전트 정의 + 실행 흐름 설계 |
| 3 | tool-dev | 6개 도구 함수 구현 (db-engineer의 queries.py 사용) |

**Wave 2B (병렬 — 에이전트 동작 후)**:
| 멤버 | 작업 |
|------|------|
| sse-specialist | SSE 엔드포인트 (`POST /api/v1/advise`) + 프론트 SSE 클라이언트 |
| api-dev | 요청/응답 스키마 정비, 에러 코드 통일 |
| frontend-dev | UsageForm, AgentStream 컴포넌트 (sse-specialist와 협력) |
| ui-ux-designer | 비교 대시보드 UI 스펙, 모델 카드 디자인 |
| backend-qa | 에이전트 도구 단위 테스트, API 엔드포인트 테스트 |
| frontend-qa | SSE 클라이언트 테스트, 폼 컴포넌트 테스트 |
| db-engineer | 쿼리 최적화 (N+1 방지, 인덱스 확인) |

**Gate 2**: `pytest -v pass` + `npm run build` + `tsc --noEmit` + `SSE E2E 동작`

### Phase 3: 대시보드 UI (Day 9-11)

**Wave 3 (병렬)**:
| 멤버 | 작업 |
|------|------|
| ui-ux-designer | 모델 탐색 페이지 설계, 반응형 레이아웃, 접근성 감사 |
| frontend-dev | TopPickCard, ComparisonTable, ModelCard, ReportDashboard, 모델 탐색 |
| sse-specialist | 스트리밍 진행 UI 상태머신 (idle→streaming→complete→error) |
| api-dev | 에지 케이스 에러 처리, 동기화 Cron 엔드포인트 |
| prompt-engineer | 추천 품질 개선 (프롬프트 튜닝) |
| frontend-qa | 대시보드 컴포넌트 테스트, 반응형 테스트, 접근성 |
| backend-qa | 통합 테스트, 에러 시나리오 테스트 |

**Gate 3**: `/verify` 전체 실행

---

## 조정 규칙

### 인터페이스 계약 (진실의 원천)
| 계약 | 문서 | 관련 역할 |
|------|------|----------|
| SSE 이벤트 프로토콜 | `docs/02-agent-workflow.md` | sse-specialist, agent-architect, frontend-dev |
| API 요청/응답 | `docs/05-api-spec.md` | api-dev, frontend-dev, sse-specialist |
| DB 스키마 | `docs/03-data-model.md` | db-engineer, tool-dev, sync-engineer |
| 출력 스키마 | `backend/app/agent/schemas.py` | prompt-engineer, frontend-dev, sse-specialist |
| UI 스펙 | `docs/design/` | ui-ux-designer, frontend-dev |

### 통신 규칙
- **스키마 변경**: 변경자 → 영향받는 역할에 SendMessage (변경 커밋 전에)
- **태스크 관리**: lead가 TaskCreate, 각 멤버가 TaskUpdate로 완료 표시
- **디자인 핸드오프**: ui-ux-designer → frontend-dev에 스펙 문서 SendMessage
- **도구↔DB 조정**: tool-dev가 queries.py 사용 시 db-engineer에 확인

### 참조 문서 매핑
| 역할 | 반드시 읽을 문서 |
|------|----------------|
| ui-ux-designer | `docs/04-feature-spec.md` (UI 동작), `docs/02-agent-workflow.md` (출력 스키마) |
| frontend-dev | `docs/04-feature-spec.md`, `docs/05-api-spec.md`, `docs/design/` |
| sse-specialist | `docs/02-agent-workflow.md` (SSE 프로토콜), `docs/05-api-spec.md` |
| api-dev | `docs/05-api-spec.md`, `docs/01-architecture.md` |
| agent-architect | `docs/02-agent-workflow.md` (에이전트 설계 전체) |
| tool-dev | `docs/02-agent-workflow.md` (도구 스펙), `docs/03-data-model.md` |
| prompt-engineer | `docs/02-agent-workflow.md` (프롬프트, 출력 스키마), `docs/00-overview.md` |
| db-engineer | `docs/03-data-model.md`, `docs/01-architecture.md` |
| sync-engineer | `docs/03-data-model.md` (동기화 전략, 필드 매핑) |
| backend-qa | `docs/06-dev-plan.md` (검증 계획), `docs/02-agent-workflow.md` |
| frontend-qa | `docs/06-dev-plan.md`, `docs/04-feature-spec.md` |
