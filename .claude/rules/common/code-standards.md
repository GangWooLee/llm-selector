# 코드 품질 표준 (TypeScript + Python)

## 복잡도 제한

| 항목 | 최대값 | 초과 시 조치 |
|------|-------|------------|
| 함수/메서드 길이 | 20줄 | 함수 분리 |
| 파일 길이 | 200줄 | 모듈 분리 |
| 조건문 깊이 | 3단계 | Early return 활용 |
| 파라미터 수 | 4개 | 객체/dict로 묶기 |

## Early Return

```typescript
// ❌ 깊은 중첩
function process(user: User) {
  if (user) {
    if (user.active) {
      if (user.verified) { /* 로직 */ }
    }
  }
}

// ✅ Early Return
function process(user: User) {
  if (!user) return;
  if (!user.active) return;
  if (!user.verified) return;
  // 실제 로직
}
```

```python
# ✅ Python Early Return
def process(user: User) -> None:
    if not user:
        return
    if not user.active:
        return
    # 실제 로직
```

## 상수 사용 (Magic Number 금지)

```typescript
// ❌ const MAX_RESULTS = results.length > 8
// ✅
const MAX_CANDIDATE_MODELS = 8;
if (results.length > MAX_CANDIDATE_MODELS) { ... }
```

## KISS & YAGNI

- 현재 필요한 최소한만 구현 (미래 요구사항 예측 금지)
- 추상화는 3번째 중복부터 (Rule of Three)
- 설정 가능성(configurability) 추가는 실제 요청이 있을 때만

### 자기 점검 (코드 작성 전/후 확인)
- **"시니어 엔지니어가 이 코드를 보면 과도하다고 할까?"** → 그렇다면 단순화
- **"200줄이 50줄로 될 수 있지 않을까?"** → 가능하면 다시 작성
- **"모든 변경 줄이 사용자 요청에 직접 추적 가능한가?"** → 추적 불가능한 변경은 제거

## 수정 범위 규율 (Surgical Changes)

- 요청된 변경에 필요한 것만 수정
- 인접 코드를 "개선"하지 않음
- 기존 스타일을 따름 (본인 선호 스타일 적용 금지)
- 자기 변경이 만든 잔여물만 정리 (기존 미사용 import 등은 건드리지 않음)
- 수정이 3개 파일을 초과하면 → 접근법이 맞는지 재확인

## 네이밍 규칙

### TypeScript (Frontend)
- 변수/함수: `camelCase`
- 컴포넌트/타입/인터페이스: `PascalCase`
- 상수: `SCREAMING_SNAKE_CASE`
- 파일: 컴포넌트는 `PascalCase.tsx`, 유틸은 `camelCase.ts`

### Python (Backend)
- 변수/함수: `snake_case`
- 클래스: `PascalCase`
- 상수: `SCREAMING_SNAKE_CASE`
- 파일: `snake_case.py`

공통: 축약 금지 (`btn` → `button`), 의미 있는 이름, 컬렉션은 복수형

## 에러 처리

```typescript
// ✅ 구체적 에러 처리
try {
  await openRouterClient.chat(params);
} catch (error) {
  if (error instanceof OpenRouterAuthError) {
    throw new ApiKeyInvalidError();
  }
  throw error; // 알 수 없는 에러는 재throw
}
```

```python
# ✅ Python 구체적 에러 처리
try:
    response = await openrouter_client.chat(params)
except httpx.TimeoutException:
    logger.warning("OpenRouter timeout")
    raise AgentTimeoutError()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise InvalidApiKeyError()
    raise
```

## 주석 규칙
- ❌ "무엇"을 설명하는 주석 금지
- ✅ "왜"를 설명하는 주석만 작성
- ✅ TODO에는 기한 포함: `# TODO: 벤치마크 자동 수집 (2026-04-15)`
