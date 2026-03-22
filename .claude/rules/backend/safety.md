---
description: "백엔드 보안 규칙."
globs: "backend/**"
---

# 백엔드 보안

## API 키 처리
- 사용자의 OpenRouter API 키를 서버에 저장하지 않음
- 요청마다 헤더/바디로 전달받아 사용 후 폐기
- 로그에 API 키 출력 금지

## 입력 검증
- 모든 외부 입력은 Pydantic 모델로 검증
- 길이 제한 필수 (user_input 등 텍스트 필드)
- SQL Injection: ORM 사용, raw SQL 금지

## CORS
- 프로덕션: Vercel 도메인만 허용
- 개발: localhost:3000만 허용
- `allow_credentials=True` 시 `allow_origins=["*"]` 금지

## 의존성 보안
- `requirements.txt`에 버전 고정
- 알려진 취약점이 있는 패키지 사용 금지

## 에러 응답
- 내부 에러 상세를 클라이언트에 노출하지 않음
- 프로덕션: 일반적인 에러 메시지만 반환
- 스택 트레이스는 로그에만 기록
