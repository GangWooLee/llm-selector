---
name: sse-streaming
description: "SSE 스트리밍 구현 스킬. FastAPI 백엔드 이벤트 생성 + Next.js 프론트엔드 소비 + 테스트 패턴."
---

# SSE 스트리밍 구현 스킬

> **📚 반드시 참조**: `docs/02-agent-workflow.md` — SSE 이벤트 타입, 에이전트 실행 흐름

## SSE 이벤트 타입 (이 프로젝트 표준)

```
event: thinking     → 에이전트 사고 과정
event: tool_call    → 도구 호출 시작 (이유 + 파라미터)
event: tool_result  → 도구 실행 결과 요약
event: report       → 최종 ComparisonReport JSON
event: done         → 완료
event: error        → 에러 발생
```

## 백엔드 구현 (FastAPI)

### StreamingResponse 패턴
```python
# backend/app/api/routes/advise.py
from fastapi.responses import StreamingResponse
import json

async def event_generator(user_input: str, api_key: str):
    """에이전트 실행 결과를 SSE 이벤트로 변환"""
    try:
        yield format_sse("thinking", {"message": "요구사항을 분석합니다..."})

        async for step in agent.run_stream(user_input, api_key):
            if step.type == "tool_call":
                yield format_sse("tool_call", {
                    "tool": step.tool_name,
                    "reasoning": step.reasoning,
                })
            elif step.type == "tool_result":
                yield format_sse("tool_result", {
                    "tool": step.tool_name,
                    "summary": step.summary,
                })

        yield format_sse("report", report.model_dump())
        yield format_sse("done", {})

    except Exception as e:
        yield format_sse("error", {"message": str(e)})

def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
```

### 라우트 정의
```python
@router.post("/api/v1/advise")
async def advise(request: AdviseRequest):
    return StreamingResponse(
        event_generator(request.user_input, request.api_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 버퍼링 비활성화
        },
    )
```

## 프론트엔드 구현 (Next.js)

### SSE 클라이언트 상태머신
```
IDLE → CONNECTING → STREAMING → COMPLETE
                  → ERROR
```

### fetch + ReadableStream 패턴 (권장)
```typescript
// frontend/src/lib/sse-client.ts
type SSEEvent = {
  event: "thinking" | "tool_call" | "tool_result" | "report" | "done" | "error";
  data: Record<string, unknown>;
};

async function* streamAdvise(
  userInput: string,
  apiKey: string,
  signal: AbortSignal
): AsyncGenerator<SSEEvent> {
  const response = await fetch(`${API_URL}/api/v1/advise`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: userInput, api_key: apiKey }),
    signal,
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = parseSSEBuffer(buffer);
    buffer = events.remaining;

    for (const event of events.parsed) {
      yield event;
    }
  }
}
```

### 연결 관리
- **타임아웃**: 최대 120초 (에이전트 응답 대기)
- **AbortController**: 사용자가 취소하거나 컴포넌트 언마운트 시 정리
- **재시도 불필요**: 에이전트 실행은 일회성 (재시도 시 새 요청)

## 테스트 패턴

### 백엔드 (pytest)
```python
@pytest.mark.asyncio
async def test_advise_streams_sse_events(client):
    """에이전트 실행 시 SSE 이벤트가 순서대로 스트리밍된다"""
    response = await client.post("/api/v1/advise", json={...})
    events = parse_sse_response(response.text)

    assert events[0].event == "thinking"
    assert events[-1].event == "done"
    assert any(e.event == "report" for e in events)
```

### 프론트엔드 (Vitest)
```typescript
// mock ReadableStream으로 SSE 응답 시뮬레이션
const mockStream = createMockSSEStream([
  { event: "thinking", data: { message: "분석 중..." } },
  { event: "tool_call", data: { tool: "search_models" } },
  { event: "report", data: mockReport },
  { event: "done", data: {} },
]);
```

## 에러 시나리오

| 시나리오 | 백엔드 처리 | 프론트엔드 처리 |
|---------|-----------|--------------|
| API 키 무효 | `error` 이벤트 + 401 | 키 재입력 유도 |
| 에이전트 타임아웃 (120초) | `error` 이벤트 + timeout | "시간 초과" 메시지 |
| 네트워크 끊김 | 스트림 자동 종료 | AbortController 정리 |
| 빈 결과 | `report` + 빈 recommendations | "조건에 맞는 모델 없음" 표시 |

## 체크리스트
```
- [ ] format_sse 헬퍼 함수 구현
- [ ] StreamingResponse 헤더 설정 (no-cache, no-buffering)
- [ ] 프론트엔드 SSE 파서 구현
- [ ] AbortController로 정리 로직
- [ ] 타임아웃 처리 (120초)
- [ ] 에러 이벤트 전파
- [ ] 스트리밍 중 UI 상태 표시 (로딩 → 진행 → 완료)
```
