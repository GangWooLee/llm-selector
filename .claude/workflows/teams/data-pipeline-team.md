# Data Pipeline Team — 데이터 무결성 전문 검증 팀

## 사용 시점
- OpenRouter 동기화 구현/수정
- 에이전트 도구 쿼리 로직 수정
- DB 스키마 마이그레이션
- 추천 결과 데이터 정확성 의심

## 구성 (3명 + lead)

| 역할 | 모델 | 모드 | 전담 영역 |
|------|------|------|----------|
| lead | opus | default | E2E 데이터 추적, 최종 검증 |
| **sync-validator** | opus | default | OpenRouter API → DB 동기화 정확성 |
| **query-validator** | opus | plan (읽기전용) | queries.py → 도구 함수 → 데이터 정확성 |
| **schema-validator** | opus | plan (읽기전용) | 스키마 정합성, 필드 매핑, 인덱스 |

**기존 2명에서 3명으로 확장**: 스키마 검증 전담 추가

## 검증 항목

### sync-validator
- OpenRouter 필드 매핑 = `docs/03-data-model.md` 매핑 테이블
- upsert 로직: INSERT(신규), UPDATE(가격변동), is_active=false(삭제)
- DECIMAL(20,10) 정밀도 (서브센트 가격)
- JSONB 필드 구조 검증

### query-validator
- 6개 도구 함수 → queries.py → SQL 추적
- `compare_pricing` 월 비용 계산 정확성
- `assess_model_fit` 스코어링 로직 정확성
- N+1 패턴 검출

### schema-validator
- 3개 테이블 스키마가 docs/03-data-model.md와 일치
- 모든 인덱스 존재 확인
- UNIQUE 제약 조건 확인
- FK 관계 정합성

## 참조 문서
> - `docs/03-data-model.md` (스키마, 필드 매핑, 동기화 전략)
> - `docs/02-agent-workflow.md` (도구 입출력 스펙)
