# 데이터 모델

## 데이터베이스: PostgreSQL (Render)

ORM: SQLAlchemy + Alembic (마이그레이션)

---

## 테이블 설계

### models
모델의 기본 정보. OpenRouter `/api/v1/models` API에서 자동 동기화.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK, default uuid4 | |
| openrouter_id | VARCHAR(255) | UNIQUE, NOT NULL | OpenRouter 모델 ID (e.g., "openai/gpt-4o") |
| name | VARCHAR(255) | NOT NULL | 표시명 |
| provider | VARCHAR(100) | NOT NULL, INDEX | 제공사 (openai, anthropic, google, meta 등) |
| description | TEXT | | 모델 설명 |
| context_length | INTEGER | | 최대 컨텍스트 길이 (토큰) |
| pricing_input | DECIMAL(20,10) | | 입력 토큰당 가격 (USD) |
| pricing_output | DECIMAL(20,10) | | 출력 토큰당 가격 (USD) |
| pricing_image | DECIMAL(20,10) | | 이미지당 가격 (USD) |
| pricing_request | DECIMAL(20,10) | | 요청당 고정 가격 (USD) |
| modalities | JSONB | | 지원 모달리티 (e.g., ["text", "image"]) |
| supported_parameters | JSONB | | 지원 파라미터 (e.g., ["tools", "structured_outputs"]) |
| max_completion_tokens | INTEGER | | 최대 출력 토큰 |
| architecture | JSONB | | 토크나이저, instruction type 등 |
| is_free | BOOLEAN | DEFAULT false | 무료 모델 여부 |
| is_active | BOOLEAN | DEFAULT true | 현재 활성 여부 |
| created_at | TIMESTAMP | DEFAULT now() | |
| updated_at | TIMESTAMP | DEFAULT now() | |

**인덱스**:
- `idx_models_provider` — provider 필터링
- `idx_models_pricing_input` — 가격 정렬/필터링
- `idx_models_context_length` — 컨텍스트 길이 필터링
- `idx_models_is_active` — 활성 모델 필터링

---

### model_benchmarks
벤치마크 점수. 수동 보강 + 향후 자동화 가능.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | |
| model_id | UUID | FK → models.id, NOT NULL | |
| benchmark_name | VARCHAR(100) | NOT NULL | MMLU, HumanEval, Chatbot Arena, MT-Bench 등 |
| score | DECIMAL(10,4) | NOT NULL | 점수 |
| max_score | DECIMAL(10,4) | | 해당 벤치마크 최대 점수 (정규화용) |
| source_url | VARCHAR(500) | | 출처 URL |
| measured_at | DATE | | 측정일 |
| created_at | TIMESTAMP | DEFAULT now() | |

**인덱스**:
- `idx_benchmarks_model_id` — 모델별 벤치마크 조회
- `idx_benchmarks_name` — 벤치마크명 필터링
- UNIQUE(model_id, benchmark_name) — 모델당 벤치마크 중복 방지

---

### model_tags
모델 특성 태그. 에이전트의 `assess_model_fit` 도구가 사용.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | |
| model_id | UUID | FK → models.id, NOT NULL | |
| category | VARCHAR(50) | NOT NULL | coding, creative, analysis, multilingual, math, instruction_following, speed 등 |
| strength_level | INTEGER | NOT NULL, CHECK 1-5 | 1=약함, 5=최강 |
| created_at | TIMESTAMP | DEFAULT now() | |

**인덱스**:
- `idx_tags_model_id` — 모델별 태그 조회
- `idx_tags_category` — 카테고리별 조회
- UNIQUE(model_id, category) — 모델당 카테고리 중복 방지

---

## 데이터 소스 매핑

### OpenRouter API → models 테이블

| OpenRouter 필드 | models 컬럼 |
|-----------------|------------|
| id | openrouter_id |
| name | name |
| id.split("/")[0] | provider |
| description | description |
| context_length | context_length |
| pricing.prompt | pricing_input |
| pricing.completion | pricing_output |
| pricing.image | pricing_image |
| pricing.request | pricing_request |
| architecture.modality | modalities |
| supported_parameters | supported_parameters |
| top_provider.max_completion_tokens | max_completion_tokens |
| architecture | architecture |
| pricing.prompt == "0" | is_free |

---

## 동기화 전략

### 자동 동기화 (Render Cron Job, 매일 1회)
1. OpenRouter `/api/v1/models` 호출
2. 각 모델에 대해:
   - DB에 없으면: INSERT
   - DB에 있고 가격/정보 변경: UPDATE (updated_at 갱신)
   - DB에 있지만 API에 없으면: is_active = false

### 수동 보강
- model_benchmarks: 관리자가 벤치마크 점수 입력
- model_tags: 관리자가 모델 특성 태그 입력
- 향후: 벤치마크 사이트 크롤링 자동화 검토
