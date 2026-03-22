# Phase 2 구현 계획: 에이전트 워크플로우 핵심 구현

## Context

Phase 1에서 구축한 인프라(DB 3테이블 + REST API + Next.js 스켈레톤) 위에,
Pydantic AI 에이전트 + 도구 6개 + SSE 스트리밍을 구현한다.
이것이 LLM Selector의 **핵심 가치** — 사용자 용도 분석 → 모델 매칭 → 근거 기반 비교 리포트.

**참조 문서**: `docs/02-agent-workflow.md` (진실의 원천)

---

## Agent Team 투입 (4명 + Phase 1 에이전트 3명)

| # | 역할 | 태스크 | Wave |
|---|------|--------|------|
| 1 | **prompt-engineer** | 시스템 프롬프트 + ComparisonReport 스키마 | Wave 1 |
| 2 | **agent-architect** | Pydantic AI 에이전트 정의 + 오케스트레이션 | Wave 1 |
| 3 | **tool-dev** | 6개 도구 함수 구현 | Wave 1 |
| 4 | **sse-specialist** | POST /api/v1/advise SSE + 프론트엔드 SSE 클라이언트 | Wave 2 |
| 5 | **frontend-dev** | 어드바이저 UI (입력 폼 + 스트리밍 + 대시보드) | Wave 2 |
| 6 | **backend-qa** | 에이전트 도구 + SSE 테스트 | Wave 3 |
| 7 | **frontend-qa** | SSE 파서 + 대시보드 테스트 | Wave 3 |

---

## Wave 1: 에이전트 코어 (병렬 3트랙)

### Task A: prompt-engineer

| 파일 | 내용 |
|------|------|
| `backend/app/agent/prompts.py` | 시스템 프롬프트 (docs/02 초안 기반) |
| `backend/app/agent/schemas.py` | MonthlyCost, TopPick, ModelRecommendation, AgentStep, ComparisonReport |

**시스템 프롬프트 핵심 4원칙**:
1. 자체 지식으로 답하지 마세요
2. 반드시 도구를 사용하여 최신 데이터 조회
3. 모든 추천에 구체적 데이터 근거 제시
4. 적합하지 않은 이유도 설명

**ComparisonReport Pydantic 모델**:
- TopPick (model_id, model_name, reason)
- ModelRecommendation (8개 필드 + MonthlyCost + strengths/weaknesses)
- AgentStep (step_number, action, reasoning, result_summary)
- ComparisonReport (top_recommendation, recommendations[], summary, data_sources[], agent_reasoning[])

### Task B: agent-architect

| 파일 | 내용 |
|------|------|
| `backend/app/agent/advisor.py` | ModelAdvisorAgent (Pydantic AI Agent 정의 + 실행 함수) |

**구현 내용**:
- `pydantic_ai.Agent` 인스턴스 생성 (시스템 프롬프트, 도구 등록, 출력 스키마)
- `async def run_advisor(user_input, api_key, analysis_model, db)` → SSE 이벤트 생성기
- 에이전트 실행 중 도구 호출을 SSE 이벤트로 변환
- 타임아웃: 전체 120초
- 의존성 주입: db 세션, api_key를 RunContext에 전달

**핵심**: Pydantic AI의 `agent.run_stream()` 사용하여 스트리밍 실행

### Task C: tool-dev

| 파일 | 내용 |
|------|------|
| `backend/app/agent/tools/search_models.py` | task_type, capabilities, context, budget 기반 검색 |
| `backend/app/agent/tools/compare_pricing.py` | 모델 가격 비교 + 월 비용 시뮬레이션 |
| `backend/app/agent/tools/get_benchmarks.py` | 벤치마크 데이터 조회 |
| `backend/app/agent/tools/assess_model_fit.py` | 적합도 평가 (0-100 스코어) |
| `backend/app/agent/tools/web_search.py` | Tavily API 웹 검색 |
| `backend/app/agent/tools/get_model_details.py` | 모델 전체 프로필 (JOIN) |
| `backend/app/agent/tools/__init__.py` | 도구 등록 리스트 export |

**규칙**:
- 모든 도구는 `queries.py` 경유 (직접 DB 금지)
- 타입 힌트 + docstring 필수 (Pydantic AI에 전달)
- 도구 안에서 LLM 호출 금지
- web_search만 외부 API (Tavily) 호출

### Gate 1
```bash
python -c "from app.agent.schemas import ComparisonReport; print('Schema OK')"
python -c "from app.agent.advisor import ModelAdvisorAgent; print('Agent OK')"
python -c "from app.agent.tools import TOOLS; print(f'{len(TOOLS)} tools OK')"
```

---

## Wave 2: SSE + 프론트엔드 (병렬 2트랙)

### Task D: sse-specialist

| 파일 | 내용 |
|------|------|
| `backend/app/utils/sse.py` | format_sse(event, data) 헬퍼 |
| `backend/app/api/routes/advise.py` | POST /api/v1/advise SSE 엔드포인트 |
| `frontend/src/lib/sse-client.ts` | fetch + ReadableStream SSE 클라이언트 |

**백엔드 SSE**:
- FastAPI `StreamingResponse` + async generator
- 에이전트 실행 → 6개 이벤트 타입으로 변환 (thinking, tool_call, tool_result, report, done, error)
- `Cache-Control: no-cache`, `X-Accel-Buffering: no` 헤더
- 120초 타임아웃
- main.py에 advise_router 등록

**프론트엔드 SSE 클라이언트**:
- `fetch` + `ReadableStream` (EventSource 아님)
- 이벤트 파서: `event:` + `data:` 라인 파싱
- 콜백: onThinking, onToolCall, onToolResult, onReport, onDone, onError
- AbortController로 취소/정리

### Task E: frontend-dev

| 파일 | 내용 |
|------|------|
| `frontend/src/app/advisor/page.tsx` | 어드바이저 메인 페이지 |
| `frontend/src/components/advisor/AdvisorForm.tsx` | 용도 입력 폼 + 분석 모델 선택 |
| `frontend/src/components/advisor/StreamingView.tsx` | SSE 스트리밍 진행 표시 |
| `frontend/src/components/advisor/ComparisonDashboard.tsx` | 비교 대시보드 (TopPick + 테이블 + 상세) |
| `frontend/src/components/advisor/TopPickCard.tsx` | 최우선 추천 카드 |
| `frontend/src/components/advisor/ModelComparisonTable.tsx` | 비교표 |
| `frontend/src/components/advisor/ModelDetailCard.tsx` | 모델 상세 카드 (강점/약점/비용) |
| `frontend/src/components/advisor/AgentReasoningPanel.tsx` | 추론 과정 표시 (토글) |

**페이지 상태**:
1. idle — 입력 폼 표시
2. streaming — SSE 진행 표시 (thinking + tool 호출 실시간)
3. complete — ComparisonDashboard 표시
4. error — 에러 메시지 + 재시도

**디자인 참조**: `docs/design/layouts/advisor.md`

### Gate 2
```bash
python -c "from app.api.routes.advise import router; print('Advise route OK')"
cd frontend && npm run build && npx tsc --noEmit
```

---

## Wave 3: 테스트 (병렬 2트랙)

### Task F: backend-qa

| 파일 | 내용 |
|------|------|
| `backend/tests/test_agent/test_tools.py` | 6개 도구 함수 테스트 (DB 사용) |
| `backend/tests/test_agent/test_advisor.py` | 에이전트 통합 테스트 (LLM 모킹) |
| `backend/tests/test_api/test_advise.py` | POST /api/v1/advise SSE 스트리밍 테스트 |

**커버리지 목표**: 에이전트 도구 90%, API 80%

### Task G: frontend-qa

| 파일 | 내용 |
|------|------|
| `frontend/src/lib/__tests__/sse-client.test.ts` | SSE 파서 단위 테스트 |
| `frontend/src/components/advisor/__tests__/AdvisorForm.test.tsx` | 폼 제출 테스트 |
| `frontend/src/components/advisor/__tests__/ComparisonDashboard.test.tsx` | 대시보드 렌더링 테스트 |

**커버리지 목표**: SSE 파서 90%, UI 컴포넌트 70%

### Gate 3 (Phase 2 완료)
```bash
cd backend && pytest -v          # 모든 테스트 통과 (기존 18 + 신규)
cd frontend && npm run build     # 빌드 성공
cd frontend && npm run test      # 모든 테스트 통과 (기존 18 + 신규)
```

---

## 에이전트 간 통신

| 보내는 쪽 | 받는 쪽 | 시점 | 내용 |
|----------|---------|------|------|
| prompt-engineer | agent-architect, sse-specialist | 스키마 완성 | "ComparisonReport 스키마 확정, schemas.py 확인" |
| prompt-engineer | frontend-dev | 스키마 완성 | "출력 스키마 확정, types/ 업데이트 필요" |
| agent-architect | sse-specialist | 에이전트 실행 함수 완성 | "run_advisor 함수 준비, SSE 연동 가능" |
| agent-architect | tool-dev | 도구 등록 인터페이스 | "도구는 TOOLS 리스트로 export" |
| sse-specialist | frontend-dev | SSE 이벤트 형식 확정 | "이벤트 파싱 형식 확인" |

---

## 핵심 파일 (수정 시 가장 주의)

1. `backend/app/agent/advisor.py` — 에이전트 전체 오케스트레이션
2. `backend/app/agent/schemas.py` — ComparisonReport (프론트+백 모두 의존)
3. `backend/app/api/routes/advise.py` — SSE 스트리밍 엔드포인트
4. `frontend/src/lib/sse-client.ts` — SSE 파서 (데이터 수신의 단일 진입점)

---

## 실행 순서

1. Wave 1 (prompt-engineer ∥ agent-architect ∥ tool-dev) → Gate 1
2. Wave 2 (sse-specialist ∥ frontend-dev) → Gate 2
3. Wave 3 (backend-qa ∥ frontend-qa) → Gate 3
4. `/verify` 전체 검증 → `/wrap-up` 커밋
