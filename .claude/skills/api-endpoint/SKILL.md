---
name: api-endpoint
description: "FastAPI 엔드포인트 생성. 스키마 → 라우트 → 서비스 → 테스트 일괄 생성."
---

# FastAPI 엔드포인트 생성 스킬

## 생성 순서

### 1. Pydantic 스키마 정의
```python
# backend/app/schemas/<resource>.py
from pydantic import BaseModel, Field

class AdviseRequest(BaseModel):
    user_input: str = Field(..., max_length=2000)

class AdviseResponse(BaseModel):
    recommendation: str
    models: list[ModelSummary]
    reasoning: str
```

### 2. 서비스 계층
```python
# backend/app/services/<resource>_service.py
class AdvisorService:
    async def run(self, user_input: str, api_key: str):
        # 비즈니스 로직
        pass
```

### 3. 라우트 정의
```python
# backend/app/api/routes/<resource>.py
from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/api/v1")

@router.post("/advise")
async def advise(request: AdviseRequest, x_api_key: str = Header(...)):
    try:
        return StreamingResponse(
            service.run(request.user_input, x_api_key),
            media_type="text/event-stream"
        )
    except InvalidApiKeyError:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

### 4. 라우터 등록
```python
# backend/app/main.py
app.include_router(resource_router)
```

### 5. 테스트 작성
```python
# backend/tests/test_api/test_<resource>.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_advise_returns_200(client: AsyncClient):
    response = await client.post(
        "/api/v1/advise",
        json={"user_input": "코드 생성에 좋은 모델"},
        headers={"X-Api-Key": "test-key"}
    )
    assert response.status_code == 200
```

## 체크리스트
```
- [ ] Pydantic 스키마 정의 (입력 검증 포함)
- [ ] 서비스 계층 구현
- [ ] 라우트 정의 (얇은 라우트 원칙)
- [ ] 라우터 등록
- [ ] 테스트 작성 + 통과 확인
- [ ] 에러 처리 (401, 422, 500)
```
