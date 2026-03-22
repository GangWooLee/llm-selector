# /wrap-up — 작업 마무리

작업 완료 시 교훈 추출, 문서 업데이트, 커밋을 수행합니다.

## 실행 절차

### 1. 변경 사항 분석
```bash
git diff --stat
git diff --cached
```

### 2. 검증 실행
`/verify` 커맨드 실행으로 전체 검증

### 3. 문서 동기화
- 코드 변경에 따라 `docs/` 문서 업데이트 필요 여부 확인
- `CLAUDE.md`에 주요 변경 사항 반영 필요 여부 확인

### 4. 교훈 추출
이번 작업에서 배운 점을 `CLAUDE.md`의 Project-Specific Notes에 기록:
- 예상치 못한 이슈와 해결 방법
- 다음에 참고할 패턴이나 주의사항
- 프로젝트 특유의 설정이나 규칙

### 5. 커밋
Conventional Commits 형식으로 커밋 메시지 작성.
