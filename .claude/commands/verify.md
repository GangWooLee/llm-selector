# /verify — 구현 검증

작업 완료 시 전체 검증을 실행합니다.

## 검증 단계

### 1. 빌드 확인
```bash
# Frontend
cd frontend && npm run build

# Backend
cd backend && python -c "from app.main import app; print('OK')"
```

### 2. 린트 확인
```bash
# Frontend
cd frontend && npm run lint

# Backend
cd backend && ruff check .
```

### 3. 테스트 실행
```bash
# Frontend
cd frontend && npm run test

# Backend
cd backend && pytest
```

### 4. 타입 체크
```bash
# Frontend
cd frontend && npx tsc --noEmit
```

### 5. 보안 점검
- `.env` 파일 커밋 여부 확인
- 하드코딩된 시크릿 검색
- CORS 설정 확인

### 6. 변경 사항 리뷰
```bash
git diff --stat
git diff
```

## 모든 단계 통과 시에만 완료 선언
