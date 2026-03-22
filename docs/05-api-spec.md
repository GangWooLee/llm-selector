# API 엔드포인트 설계

## 개요

프론트엔드(Next.js, Vercel)와 백엔드(FastAPI, Render) 간 API 통신 규격.

---

## Next.js (Vercel) — 프론트엔드 프록시

### POST /api/validate-key
OpenRouter API 키 유효성 검증을 프론트엔드에서 프록시.

**Request**:
```json
{
  "api_key": "sk-or-..."
}
```

**Response (200)**:
```json
{
  "valid": true,
  "credits_remaining": 12.50,
  "usage": {
    "daily": 0.45,
    "weekly": 3.20,
    "monthly": 15.00
  }
}
```

**Response (401)**:
```json
{
  "valid": false,
  "error": "Invalid API key"
}
```

---

## FastAPI (Render) — 에이전트 백엔드

Base URL: `https://<render-app>.onrender.com`

### POST /api/v1/advise
에이전트 실행. SSE(Server-Sent Events)로 추론 과정 스트리밍.

**Request**:
```json
{
  "user_input": "한국어 고객 상담 챗봇을 만들고 싶어. 월 100만 건 정도 처리해야 해.",
  "api_key": "sk-or-...",
  "analysis_model": "anthropic/claude-3.5-sonnet"
}
```

**Response**: SSE Stream
```
event: thinking
data: {"message": "사용자 요구를 분석합니다..."}

event: tool_call
data: {"tool": "search_models", "reasoning": "다국어 지원 + 저가 모델 검색", "params": {"task_type": "chatbot", "budget_range": "low"}}

event: tool_result
data: {"tool": "search_models", "summary": "12개 후보 모델 발견", "count": 12}

event: tool_call
data: {"tool": "compare_pricing", "reasoning": "월 100만 건 기준 비용 비교"}

event: tool_result
data: {"tool": "compare_pricing", "summary": "가격 비교 완료"}

event: report
data: {"top_recommendation": {...}, "recommendations": [...], "summary": "...", "data_sources": [...], "agent_reasoning": [...]}

event: done
data: {}
```

**Error (400)**:
```json
{"detail": "user_input is required"}
```

**Error (401)**:
```json
{"detail": "Invalid OpenRouter API key"}
```

**Error (504)**:
```json
{"detail": "Agent execution timed out"}
```

---

### GET /api/v1/models
모델 목록 조회 (페이지네이션, 필터).

**Query Parameters**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| page | int | N | 페이지 번호 (기본: 1) |
| per_page | int | N | 페이지당 항목 수 (기본: 20, 최대: 100) |
| provider | str | N | 제공사 필터 (e.g., "openai") |
| min_context | int | N | 최소 컨텍스트 길이 |
| max_price_input | float | N | 최대 입력 토큰 가격 |
| has_tools | bool | N | Function Calling 지원 여부 |
| has_vision | bool | N | Vision 지원 여부 |
| is_free | bool | N | 무료 모델만 |
| search | str | N | 이름/설명 텍스트 검색 |
| sort_by | str | N | 정렬 기준 (price_asc, price_desc, context_length, name) |

**Response (200)**:
```json
{
  "data": [
    {
      "id": "uuid",
      "openrouter_id": "openai/gpt-4o-mini",
      "name": "GPT-4o Mini",
      "provider": "openai",
      "context_length": 128000,
      "pricing_input": 0.00000015,
      "pricing_output": 0.0000006,
      "is_free": false,
      "modalities": ["text", "image"],
      "supported_parameters": ["tools", "structured_outputs"]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 412,
    "total_pages": 21
  }
}
```

---

### GET /api/v1/models/{model_id}
모델 상세 조회 (벤치마크, 태그 포함).

**Response (200)**:
```json
{
  "id": "uuid",
  "openrouter_id": "openai/gpt-4o-mini",
  "name": "GPT-4o Mini",
  "provider": "openai",
  "description": "...",
  "context_length": 128000,
  "pricing_input": 0.00000015,
  "pricing_output": 0.0000006,
  "modalities": ["text", "image"],
  "supported_parameters": ["tools", "structured_outputs"],
  "max_completion_tokens": 16384,
  "architecture": {"tokenizer": "o200k_base", "instruction_type": "chat"},
  "benchmarks": [
    {"benchmark_name": "MMLU", "score": 82.0, "max_score": 100, "source_url": "..."},
    {"benchmark_name": "HumanEval", "score": 87.2, "max_score": 100}
  ],
  "tags": [
    {"category": "coding", "strength_level": 4},
    {"category": "multilingual", "strength_level": 3}
  ],
  "updated_at": "2026-03-22T00:00:00Z"
}
```

**Response (404)**:
```json
{"detail": "Model not found"}
```

---

### POST /api/v1/sync
모델 DB 동기화 트리거 (관리자용).

**Response (200)**:
```json
{
  "status": "completed",
  "models_added": 5,
  "models_updated": 23,
  "models_deactivated": 1,
  "total_active": 412,
  "synced_at": "2026-03-22T12:00:00Z"
}
```

---

## CORS 설정

백엔드(Render)에서 프론트엔드(Vercel) 도메인만 허용:

```python
ALLOWED_ORIGINS = [
    "https://llm-selector.vercel.app",
    "http://localhost:3000",  # 개발용
]
```

---

## 인증

- 별도 로그인/회원가입 없음 (MVP)
- OpenRouter API 키는 사용자가 매 요청 시 헤더 또는 바디로 전달
- 백엔드는 키를 저장하지 않음 (stateless)
