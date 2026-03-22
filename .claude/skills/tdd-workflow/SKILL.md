---
name: tdd-workflow
description: "TDD 워크플로우. pytest + Vitest 기반 RED → GREEN → REFACTOR 사이클."
---

# TDD 워크플로우 스킬

## 7단계 프로세스

### 1. 사용자 시나리오 작성
구현할 기능의 사용자 관점 시나리오를 정의합니다.

### 2. 테스트 케이스 생성

**백엔드 (pytest)**:
```python
# backend/tests/test_agent/test_search_models.py
import pytest

@pytest.mark.asyncio
async def test_search_models_filters_by_use_case():
    """용도별 모델 검색 시 관련 모델만 반환한다"""
    results = await search_models(use_case="코드 생성", max_results=5)
    assert len(results) <= 5
    assert all(m.supports_code_generation for m in results)

@pytest.mark.asyncio
async def test_search_models_empty_query_returns_popular():
    """빈 쿼리 시 인기 모델을 반환한다"""
    results = await search_models(use_case="", max_results=10)
    assert len(results) > 0
```

**프론트엔드 (Vitest)**:
```typescript
// frontend/src/components/__tests__/ModelCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ModelCard } from '../ModelCard';

describe('ModelCard', () => {
  it('모델명과 가격을 표시한다', () => {
    render(<ModelCard model={mockModel} />);
    expect(screen.getByText('GPT-4o')).toBeInTheDocument();
    expect(screen.getByText('$2.50/1M tokens')).toBeInTheDocument();
  });
});
```

### 3. 테스트 실행 — 실패 확인 (RED)
```bash
# Backend
cd backend && pytest tests/test_agent/test_search_models.py -v

# Frontend
cd frontend && npm run test -- ModelCard.test.tsx
```
**🔴 반드시 실패해야 합니다.**
- 통과하면 → 테스트가 잘못된 것. **테스트를 삭제하고 더 구체적인 assertion으로 다시 작성.**
- 구현 코드가 이미 있는 상태에서 테스트를 작성한 경우 → 구현을 임시 주석처리하고 RED 확인 후 주석 해제.

### 4. 최소 구현 (GREEN)
테스트를 통과하는 **최소한의** 코드만 작성합니다.

### 5. 테스트 재실행
```bash
cd backend && pytest tests/test_agent/test_search_models.py -v
cd frontend && npm run test -- ModelCard.test.tsx
```

### 6. 리팩토링 (REFACTOR)
테스트가 통과하는 상태에서 코드 품질을 개선합니다.

### 7. 전체 테스트 확인
```bash
cd backend && pytest
cd frontend && npm run test
```

## 커버리지 기준

| 영역 | 최소 커버리지 |
|------|-------------|
| 에이전트 도구 | 90% |
| API 엔드포인트 | 80% |
| DB 쿼리 | 80% |
| 서비스 | 80% |
| UI 컴포넌트 | 70% |

## 핵심 원칙
> **항상 테스트를 먼저 작성하고, 테스트를 통과하는 코드를 구현합니다.**

### 해야 할 것
- ✅ 테스트 먼저 작성
- ✅ 실패 확인 후 구현
- ✅ 엣지 케이스 테스트 (None, 빈 값, 경계값)
- ✅ 외부 API 모킹 (respx, pytest-httpx)

### 하지 말아야 할 것
- ❌ 구현 후 테스트 작성
- ❌ 테스트 실행 생략
- ❌ 구현 세부사항 테스트 (동작 테스트)
- ❌ 테스트 간 의존성
