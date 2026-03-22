# 개발 계획

## 일정: 2주 (14일)

---

## Phase 1 — 프로젝트 셋업 & 인프라 (Day 1-3)

### 프론트엔드
- [ ] Next.js 15 프로젝트 초기화 (App Router, TypeScript, Tailwind 4)
- [ ] shadcn/ui 설치 및 기본 레이아웃 (Header, Footer, 페이지 뼈대)
- [ ] API 키 입력 컴포넌트 (F1)
- [ ] 환경변수 설정 (NEXT_PUBLIC_API_URL)

### 백엔드
- [ ] FastAPI 프로젝트 초기화
- [ ] PostgreSQL 연결 (Render DB)
- [ ] SQLAlchemy + Alembic 셋업
- [ ] DB 스키마 생성 (models, model_benchmarks, model_tags)
- [ ] OpenRouter `/api/v1/models` 동기화 스크립트 구현
- [ ] 초기 데이터 로드 (400+ 모델)
- [ ] Dockerfile + render.yaml 작성
- [ ] Render 초기 배포

### 통합
- [ ] Vercel ↔ Render CORS 설정 확인
- [ ] 프론트엔드에서 백엔드 API 호출 테스트

---

## Phase 2 — 에이전트 워크플로우 핵심 구현 (Day 4-8)

### 에이전트 코어
- [ ] Pydantic AI 에이전트 정의 (ModelAdvisorAgent)
- [ ] 시스템 프롬프트 작성
- [ ] 출력 스키마 (ComparisonReport, ModelRecommendation 등)

### 에이전트 도구 6개
- [ ] `search_models` — DB 필터링 검색
- [ ] `compare_pricing` — 가격 비교 + 월 비용 시뮬레이션
- [ ] `get_benchmarks` — 벤치마크 조회
- [ ] `assess_model_fit` — 적합도 평가 (스코어링 로직)
- [ ] `web_search` — 웹 검색 (Tavily/DuckDuckGo)
- [ ] `get_model_details` — 모델 상세 조회

### API
- [ ] SSE 스트리밍 엔드포인트 (`POST /api/v1/advise`)
- [ ] 모델 목록 엔드포인트 (`GET /api/v1/models`)
- [ ] 모델 상세 엔드포인트 (`GET /api/v1/models/{id}`)

### 프론트엔드 연결
- [ ] SSE 클라이언트 유틸 구현
- [ ] 용도 입력 폼 (UsageForm)
- [ ] 에이전트 추론 과정 스트리밍 표시 (AgentStream)

---

## Phase 3 — 대시보드 UI (Day 9-11)

### 비교 대시보드
- [ ] Top Pick 카드 (TopPickCard)
- [ ] 비교표 (ComparisonTable)
- [ ] 모델 상세 카드 (ModelCard)
- [ ] 리포트 전체 대시보드 (ReportDashboard)
- [ ] "추론 과정 보기" 토글 UI

### 모델 탐색
- [ ] 모델 목록 페이지 (ModelList + ModelFilters)
- [ ] 모델 상세 페이지

### 반응형
- [ ] 모바일 레이아웃 최적화
- [ ] 태블릿 레이아웃

---

## Phase 4 — 마무리 & 배포 (Day 12-14)

### 기능 마무리
- [ ] 랜딩 페이지 (서비스 소개 + CTA)
- [ ] Render Cron Job 설정 (모델 DB 매일 자동 동기화)
- [ ] 에러 핸들링 전체 점검
  - API 키 무효
  - 네트워크 오류
  - 에이전트 타임아웃
  - 빈 결과 처리
- [ ] 로딩/스트리밍 상태 UI 점검

### 배포
- [ ] Vercel 프로덕션 배포 (프론트엔드)
- [ ] Render 프로덕션 배포 (백엔드)
- [ ] 환경변수 프로덕션 설정
- [ ] 통합 테스트 (E2E)

---

## 검증 계획

### 에이전트 검증
1. 다양한 용도 입력 → 에이전트가 적절한 도구를 선택하여 호출하는지 확인
2. 에이전트 추론 과정이 SSE로 실시간 스트리밍되는지 확인
3. 동일 입력에 대해 일관된 품질의 추천이 나오는지 확인
4. 에이전트가 DB 데이터만 활용하고, 자체 지식으로 답하지 않는지 확인

### 데이터 검증
5. OpenRouter 모델 동기화 → DB에 400+ 모델 데이터 적재 확인
6. 가격 데이터 정확성 (OpenRouter 사이트와 대조)

### 통합 검증
7. 프론트엔드 → 백엔드 → 에이전트 → DB 전체 파이프라인 동작 확인
8. API 키 검증 → 에이전트 호출 → 대시보드 표시 E2E 흐름
9. Vercel(프론트) + Render(백엔드) CORS 통신 확인

### UI/UX 검증
10. 모바일/데스크톱 반응형 확인
11. SSE 스트리밍 중 로딩 상태 표시
12. 에러 상태 (키 무효, 네트워크 오류, 에이전트 타임아웃) 처리

---

## 확장 계획 (MVP 이후)

### 4단계 — 실전 비교 테스트
- 동일 프롬프트를 후보 모델 2~3개에 OpenRouter API로 실제 전송
- 응답 품질, 속도, 비용을 직접 비교하는 인터랙티브 UI

### 추가 기능
- 사용자 히스토리 (과거 비교 저장) — 로그인 필요
- 벤치마크 자동 수집 (크롤링/API)
- 모델 변동 알림 (가격 인하, 신규 모델 출시)
- API 통합 가이드 (추천 모델의 빠른 시작 코드 제공)
