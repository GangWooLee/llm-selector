# SSE/Agent Debugging Team — 복합 버그 전문 디버깅 팀

## 사용 시점
- SSE + 에이전트 경계 복합 버그
- 3회 이상 solo 디버깅 실패
- 간헐적/타이밍 의존 버그

## 구성 (3명 + lead)

| 역할 | 모델 | 모드 | 추적 경로 |
|------|------|------|----------|
| lead | opus | default | 가설 수립, 수정 적용, 회귀 테스트 |
| **tracer-backend** | opus | default | FastAPI Route → Service → Agent → Tool → DB |
| **tracer-sse** | opus | default | SSE format_sse → StreamingResponse → HTTP → ReadableStream → Parser |
| **tracer-frontend** | opus | default | SSE Client → React State → Component Render → UI |

**기존 2명에서 3명으로 확장**: SSE 경로를 프론트엔드에서 분리하여 독립 tracer 배정

## 실행 흐름

### Step 1: 버그 정의 + 가설 수립 (lead)
```
증상: [사용자가 보는 것]
경로: User → SSE Client → FastAPI /advise → Agent → Tool → DB
기대: [예상 동작]
실제: [실제 동작]
```
3개 경쟁 가설 → 각 tracer에 1개씩 할당

### Step 2: 병렬 조사 (3 tracers 동시)

| tracer | 조사 범위 |
|--------|----------|
| tracer-backend | agent/advisor.py, agent/tools/, db/queries.py, services/ |
| tracer-sse | api/routes/advise.py, utils/sse.py, lib/sse-client.ts 파서 부분 |
| tracer-frontend | components/advisor/, React state, AbortController 생명주기 |

### Step 3: 평가 (lead)
가설 비교 → 확인되면 수정, 모두 기각되면 새 가설 → Step 2 반복

### Step 4: 수정 (lead 또는 해당 tracer)
실패 재현 테스트 → 최소 수정 → 전체 테스트

## 3-Strike 규칙
3회 연속 실패 → 즉시 중단 → 아키텍처 전제 재검토 → 대안 2-3개 제시
