# Task Plan: [기능명]

## 개요
**목표**: [1-2문장]
**시작**: YYYY-MM-DD
**상태**: 🟡 진행 중

## Phase 목록

### Phase 1: [데이터/인프라]
**상태**: ⬜ 대기

#### 마이크로 태스크 (각 2-5분)
```
Task 1.1 (3분): [구체적 작업명]
  파일: backend/app/db/models.py
  내용: [핵심 코드 1-3줄]
  검증: cd backend && python -c "from app.db.models import Model; print('OK')"

Task 1.2 (5분): [구체적 작업명]
  파일: backend/alembic/versions/xxx_create_models.py
  내용: [핵심 코드 1-3줄]
  검증: cd backend && alembic upgrade head
```

**Phase 검증**:
```bash
cd backend && pytest tests/test_db/
```

### Phase 2: [백엔드 로직]
**상태**: ⬜ 대기

#### 마이크로 태스크
```
Task 2.1 (5분): [구체적 작업명]
  파일: [정확한 경로]
  내용: [핵심 코드 1-3줄]
  검증: [검증 명령어]
```

**Phase 검증**:
```bash
cd backend && pytest
```

### Phase 3: [프론트엔드 UI]
**상태**: ⬜ 대기

#### 마이크로 태스크
```
Task 3.1 (5분): [구체적 작업명]
  파일: [정확한 경로]
  내용: [핵심 코드 1-3줄]
  검증: [검증 명령어]
```

**Phase 검증**:
```bash
cd frontend && npm run build && npm run test
```

## 배치 실행 규칙
- 3개 태스크 단위로 실행
- 배치 완료 후 중간 보고 (완료 목록, 테스트 결과, 이슈)
- 10분 이상 걸리는 태스크 → 분할 필요

## 에러 기록

| 에러 | 시도 | 해결 |
|------|------|------|

## 결정 로그

| 결정 | 이유 | 날짜 |
|------|------|------|

## Time Tracking

| Phase | 예상 | 실제 | 차이 |
|-------|------|------|------|
