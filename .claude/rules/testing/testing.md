---
description: "테스트 규칙 (pytest + Vitest)."
globs: ["backend/tests/**", "frontend/**/*.test.*"]
---

# 테스트 규칙

> **📚 기획 문서 참조** (테스트 작성 전 반드시 확인):
> - 에이전트 도구 스펙: `docs/02-agent-workflow.md` (도구 입출력 기준으로 테스트)
> - API 스펙: `docs/05-api-spec.md` (요청/응답 스키마 기준으로 테스트)
> - 검증 계획: `docs/06-dev-plan.md` (에이전트/데이터/통합/UI 검증 항목)

## 백엔드 (pytest)

### 구조
```
backend/tests/
├── conftest.py          # 공통 fixture
├── test_agent/          # 에이전트 + 도구 테스트
├── test_api/            # API 엔드포인트 테스트
├── test_db/             # DB 쿼리 테스트
└── test_services/       # 서비스 테스트
```

### 규칙
- `async` 테스트: `pytest-asyncio` 사용
- DB 테스트: 테스트용 PostgreSQL 또는 SQLite in-memory
- 외부 API 모킹: `respx` 또는 `pytest-httpx`
- 에이전트 테스트: LLM 호출은 모킹, 도구 로직은 실제 테스트

### 커버리지 목표
| 영역 | 최소 커버리지 |
|------|-------------|
| 에이전트 도구 | 90% |
| API 엔드포인트 | 80% |
| DB 쿼리 | 80% |
| 서비스 | 80% |

## 프론트엔드 (Vitest)

### 규칙
- 컴포넌트 테스트: `@testing-library/react`
- SSE 스트리밍 테스트: mock EventSource
- 스냅샷 테스트: 핵심 UI 컴포넌트만

## 공통 원칙

- 테스트 이름: "~하면 ~한다" 형식
- Arrange → Act → Assert 패턴
- 하나의 테스트에 하나의 검증
- `sleep` 금지 — 비동기 대기 사용
