---
description: "Git 워크플로우 표준. 커밋 메시지 형식, PR 절차."
globs: "*"
---

# Git 워크플로우

## 커밋 메시지 형식

Conventional Commits:

```
<type>: <description>
```

### 타입
- `feat` — 새 기능
- `fix` — 버그 수정
- `refactor` — 리팩토링
- `docs` — 문서 수정
- `test` — 테스트 추가/수정
- `chore` — 빌드, 설정 등 기타
- `perf` — 성능 개선
- `ci` — CI/CD 설정

### 스코프 (선택)
프론트/백엔드 구분 시 스코프 사용:
```
feat(frontend): 비교 대시보드 컴포넌트 추가
feat(backend): search_models 에이전트 도구 구현
fix(agent): SSE 스트리밍 타임아웃 처리
```

## PR 절차

1. 전체 커밋 히스토리 확인: `git diff main...HEAD`
2. PR 작성 시 변경 요약 + 테스트 계획 포함
3. 새 브랜치 푸시 시 `-u` 플래그: `git push -u origin feature/my-feature`

## 기능 개발 순서

1. 계획 수립 — `/plan`
2. 구현 + 테스트
3. 검증 — `/verify`
4. PR 생성
