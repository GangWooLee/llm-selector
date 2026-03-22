---
name: planning-with-files
version: "1.0.0"
description: "Manus-style 파일 기반 계획 수립. task_plan.md, findings.md, progress.md 생성. 복잡한 멀티스텝 작업에 사용."
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
---

# Planning with Files

컨텍스트 윈도우 = RAM (휘발성), 파일시스템 = 디스크 (영속성).
중요한 것은 모두 파일에 기록합니다.

## Phase 0: 브레인스토밍 (코드 작성 전 필수)

### 🔴 HARD GATE — 아래 3단계 모두 완료 전까지 코드 작성 절대 금지

### Iteration 1: 범위 확정 (요구사항 명확화)
- 한 번에 하나씩 질문 (AskUserQuestion 사용)
- 파악 대상: 목적, 제약, 성공 기준, 영향 범위
- 관련 기획 문서 확인 (`docs/` 디렉토리)
- **산출물**: 1-2문장 범위 요약

### Iteration 2: 접근법 선택
- 2-3개 방안을 트레이드오프와 함께 제시
- 권장안을 첫 번째에 배치
- 사용자 선택 대기 (선택 전 진행 금지)
- **산출물**: 선택된 접근법 + 이유

### Iteration 3: 설계 합의
- 아키텍처 결정, 데이터 모델, API, 에러 처리, 테스트 전략
- 각 섹션을 200-300자 단위로 발표 → 사용자 승인
- 설계 문서를 `docs/plans/`에 저장
- **산출물**: 승인된 설계 문서

### Phase 0 통과 조건
- [ ] 범위가 1-2문장으로 요약됨
- [ ] 접근법이 사용자에 의해 선택됨
- [ ] 설계가 `docs/plans/`에 저장됨
- [ ] 사용자가 명시적으로 "승인" 또는 "진행" 의사를 표현함

**⛔ Phase 0 스킵 조건 (이것만)**:
- 사용자가 이미 상세 설계를 제공한 경우
- 5줄 이하의 단순 변경

## Quick Start

1. **`task_plan.md` 생성** — Phase별 계획 + 체크박스
2. **`findings.md` 생성** — 탐색/발견 기록
3. **`progress.md` 생성** — 세션 로그 + 테스트 결과
4. **결정 전 계획 재읽기** — 주의 창에 목표 갱신
5. **Phase 완료마다 업데이트** — 상태 체크, 에러 기록

## 파일 역할

| 파일 | 용도 | 업데이트 시점 |
|------|------|-------------|
| `task_plan.md` | Phase, 진행, 결정 | Phase 완료마다 |
| `findings.md` | 탐색, 발견 | 발견 즉시 |
| `progress.md` | 세션 로그, 테스트 결과 | 수시 |

## 핵심 규칙

### 1. 계획 먼저
복잡한 작업은 `task_plan.md` 없이 시작 금지.

### 2. 2-Action Rule
> 2번의 탐색 후 즉시 핵심 발견을 파일에 저장

### 3. 결정 전 읽기
중요 결정 전에 계획 파일 다시 읽기.

### 4. 행동 후 업데이트
Phase 완료마다: 상태 변경, 에러 기록, 변경 파일 목록.

### 5. 3-Strike Error Protocol

```
시도 1: 진단 + 수정
시도 2: 다른 접근법 시도
시도 3: 전제 재검토
3회 실패 후: 사용자에게 에스컬레이션
```

## Phase 분류 가이드

| 규모 | Phase 수 | 소요 시간 |
|------|---------|----------|
| Small | 2-3 | 3-6시간 |
| Medium | 4-5 | 8-15시간 |
| Large | 6-7 | 15-25시간 |

## 검증 명령어 (이 프로젝트)

```bash
# Frontend
cd frontend && npm run build && npm run test

# Backend
cd backend && pytest

# 타입 체크
cd frontend && npx tsc --noEmit

# 린트
cd frontend && npm run lint
cd backend && ruff check .
```
