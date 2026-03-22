---
name: implement
description: "기능 구현 가이드. 계획 기반으로 Phase별 체계적 구현 수행."
---

# 기능 구현 스킬

## 전제 조건
- `docs/plans/PLAN_<feature>.md` 존재 (사용자 승인 완료)
- 또는 `task_plan.md` 존재

## 구현 순서 (이 프로젝트 표준)

### 1단계: 데이터 레이어 (Backend)
```
backend/app/db/models.py    ← SQLAlchemy 모델 정의
backend/app/db/queries.py   ← 쿼리 함수
backend/alembic/versions/   ← 마이그레이션
```

### 2단계: 에이전트 도구 (Backend)
```
backend/app/agent/tools/    ← 6개 도구 구현
backend/app/agent/advisor.py ← Pydantic AI 에이전트
```

### 3단계: API 엔드포인트 (Backend)
```
backend/app/api/routes/     ← FastAPI 라우트
backend/app/services/       ← 서비스 계층
backend/app/schemas/        ← Pydantic 요청/응답 스키마
```

### 4단계: 프론트엔드 (Frontend)
```
frontend/src/app/           ← Next.js App Router 페이지
frontend/src/components/    ← UI 컴포넌트
frontend/src/lib/           ← API 클라이언트, 유틸
frontend/src/types/         ← TypeScript 타입 정의
```

## Phase 실행 규칙

### 배치 실행
- 3개 태스크 단위로 실행
- 배치 완료 후 중간 보고 (완료 목록, 테스트 결과, 이슈)
- 사용자 피드백 대기

### Quality Gate (Phase 완료마다)
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run build && npm run test && npx tsc --noEmit
```
**모든 검증 통과 전 다음 Phase 진행 금지**

### 파일 수정 후 확인
- 변경한 파일 관련 테스트 즉시 실행
- 3개 이상 파일 수정 시 전체 테스트 실행
- import 변경 시 빌드 확인

## Anti-Patterns

| 하지 마 | 대신 |
|---------|------|
| 계획 없이 시작 | `task_plan.md` 먼저 확인 |
| Phase 건너뛰기 | 순서대로 진행 |
| Quality Gate 생략 | 반드시 검증 후 다음 진행 |
| 한 번에 많은 변경 | 배치 단위로 점진적 구현 |
