---
name: agent-tool
description: "Pydantic AI 에이전트 도구 생성. DB 조회, 벤치마크 비교, 웹 검색 등 에이전트 도구 추가."
---

# Pydantic AI 에이전트 도구 생성 스킬

## 이 프로젝트의 6개 도구

| 도구 | 목적 |
|------|------|
| `search_models` | 요구사항 기반 모델 DB 검색 |
| `compare_pricing` | 후보 모델 가격 비교 + 월 비용 시뮬레이션 |
| `get_benchmarks` | 벤치마크 데이터 조회 |
| `assess_model_fit` | 용도 적합도 평가 (스코어링) |
| `web_search` | 최신 모델 정보 웹 검색 (Tavily) |
| `get_model_details` | 모델 전체 상세 조회 |

## 도구 생성 순서

### 1. 도구 함수 정의
```python
# backend/app/agent/tools/search_models.py
from pydantic_ai import RunContext
from app.db.queries import search_models_by_criteria

async def search_models(
    ctx: RunContext,
    use_case: str,
    max_results: int = 5,
) -> list[dict]:
    """요구사항에 맞는 모델을 DB에서 검색합니다.

    Args:
        use_case: 사용 용도 (예: "코드 생성", "문서 요약")
        max_results: 최대 결과 수

    Returns:
        매칭된 모델 목록 (이름, 가격, 벤치마크 요약)
    """
    return await search_models_by_criteria(
        use_case=use_case,
        limit=max_results,
    )
```

### 2. 에이전트에 도구 등록
```python
# backend/app/agent/advisor.py
from pydantic_ai import Agent

advisor = Agent(
    model=...,
    tools=[search_models, compare_pricing, ...],
    system_prompt="자체 지식으로 답하지 말 것. 반드시 도구를 사용하여 데이터 근거를 제시할 것.",
)
```

### 3. 테스트 작성
```python
# backend/tests/test_agent/test_search_models.py
@pytest.mark.asyncio
async def test_search_models_returns_results():
    """DB에 모델이 있으면 결과를 반환한다"""
    results = await search_models(ctx, use_case="코드 생성")
    assert isinstance(results, list)
    assert len(results) > 0
```

## 도구 작성 규칙

1. **타입 힌트 필수** — 모든 파라미터와 반환값에 타입
2. **docstring 필수** — Pydantic AI가 LLM에게 도구 설명으로 전달
3. **DB 직접 접근 금지** — `app/db/queries.py` 통해서만 접근
4. **에러 핸들링** — 도구 실패 시 명확한 에러 메시지 반환
5. **LLM 호출 금지** — 도구 안에서 다시 LLM을 호출하지 않음

## 체크리스트
```
- [ ] 도구 함수 정의 (타입 힌트 + docstring)
- [ ] DB 쿼리 함수 작성 (queries.py)
- [ ] 에이전트에 등록
- [ ] 단위 테스트 작성 (LLM 모킹)
- [ ] 도구 로직 테스트 (실제 DB)
```
