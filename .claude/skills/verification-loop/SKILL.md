---
name: verification-loop
description: "Next.js + FastAPI 코드베이스 종합 검증 루프. 빌드, 린트, 테스트, 보안 순차 검증."
disable-model-invocation: true
---

# 검증 루프 스킬

## 6단계 순차 검증

### Phase 1: 빌드 검증
```bash
# Frontend
cd frontend && npm run build

# Backend
cd backend && python -c "from app.main import app; print('Build OK')"
```
**실패 시 즉시 중단** — 빌드가 깨진 상태에서 후속 검증은 무의미.

### Phase 2: 린트 검사
```bash
# Frontend
cd frontend && npm run lint

# Backend (ruff 설치된 경우)
cd backend && ruff check . 2>/dev/null || echo "ruff 미설치"
```

### Phase 3: 타입 체크
```bash
# Frontend TypeScript
cd frontend && npx tsc --noEmit

# Backend (mypy 설치된 경우)
cd backend && mypy app/ 2>/dev/null || echo "mypy 미설치"
```

### Phase 4: 테스트 실행
```bash
# Backend
cd backend && pytest -v

# Frontend
cd frontend && npm run test
```
- 통과/실패 비율 기록
- 실패한 테스트의 파일:라인 번호 수집

### Phase 5: 보안 스캔
```bash
# 하드코딩된 시크릿 검색
grep -rn "api_key\|secret\|password\|token" --include="*.py" --include="*.ts" --include="*.tsx" backend/app/ frontend/src/ | grep -v "test\|\.env\|type\|interface\|mock"

# .env 파일 커밋 여부
git ls-files | grep -E "\.env$|\.env\." | head -5

# 디버그 코드 검색
grep -rn "console\.log\|print(\|breakpoint()\|debugger" --include="*.py" --include="*.ts" --include="*.tsx" backend/app/ frontend/src/
```

### Phase 6: Diff 리뷰
```bash
git diff --stat
git diff --name-only
```
- 의도하지 않은 변경 식별
- 에러 처리 누락 확인

## 검증 보고서

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 검증 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
빌드:       ✅ 통과 / ❌ 실패
린트:       ✅ 0건 / ⚠️ N건 경고 / ❌ N건 오류
타입:       ✅ 통과 / ❌ N건 에러
테스트:     ✅ X개 통과 / ❌ Y개 실패
보안:       ✅ 이상 없음 / ⚠️ N건 경고
Diff:       N개 파일 변경
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PR 준비:    ✅ 가능 / ❌ 수정 필요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
