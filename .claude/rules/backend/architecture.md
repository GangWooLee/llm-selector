---
description: "FastAPI + Pydantic AI 백엔드 아키텍처 규칙."
globs: "backend/**"
---

# 백엔드 아키텍처 (FastAPI + Pydantic AI)

> **📚 기획 문서 참조** (backend 작업 전 반드시 확인):
> - 아키텍처/배포: `docs/01-architecture.md`
> - 에이전트/도구: `docs/02-agent-workflow.md`
> - DB 스키마: `docs/03-data-model.md`
> - API 스펙: `docs/05-api-spec.md`

## 계층 분리

```
API Routes (app/api/routes/)     ← HTTP 파싱, 응답 형식만
    ↓
Services (app/services/)          ← 비즈니스 로직 조율
    ↓
Agent (app/agent/)               ← Pydantic AI 에이전트 + 도구
    ↓
DB Queries (app/db/queries.py)   ← 데이터 접근만
```

의존성은 항상 아래쪽(DB) 방향. 상위 계층이 하위를 호출.

## API Routes 규칙

- HTTP 파싱, 인증, 응답 형식 처리만
- 비즈니스 로직 금지 — Service/Agent에 위임
- 에러 처리: HTTPException으로 변환

```python
# ✅ 라우트는 얇게
@router.post("/api/v1/advise")
async def advise(request: AdviseRequest, api_key: str = Header(...)):
    try:
        return StreamingResponse(
            advisor_service.run(request.user_input, api_key),
            media_type="text/event-stream"
        )
    except InvalidApiKeyError:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

## Pydantic AI 에이전트 규칙

- 시스템 프롬프트에 "자체 지식으로 답하지 말 것" 명시
- 모든 도구는 타입 힌트 + docstring 필수
- 출력 스키마는 Pydantic BaseModel로 정의
- 에이전트 실행 타임아웃 설정 필수

## SQLAlchemy 규칙

- 모든 쿼리는 `app/db/queries.py`에 집중
- `async` 세션 사용 (FastAPI 비동기 호환)
- N+1 방지: `selectinload`/`joinedload` 사용
- Raw SQL 금지 — ORM 또는 Core Expression 사용

## 에러 처리

```python
# ✅ 구체적 예외만 catch
try:
    result = await openrouter_client.chat(params)
except httpx.TimeoutException:
    raise AgentTimeoutError("LLM 호출 타임아웃")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise InvalidApiKeyError()
    raise

# ❌ bare except 금지
except:
    pass
```

## 보안

- SQL Injection: 항상 ORM 파라미터화 쿼리, raw SQL 금지
- API 키: 서버에 저장하지 않음, 요청마다 전달받아 사용
- CORS: 허용 도메인만 명시적으로 설정
- 환경변수: `.env` 파일, `pydantic-settings`로 관리
