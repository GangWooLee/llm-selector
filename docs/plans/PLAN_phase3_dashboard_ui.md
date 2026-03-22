# Phase 3 구현 계획: 대시보드 UI (모델 탐색 + 모델 상세)

## Context

Phase 2에서 어드바이저 UI(F2-F3)는 이미 구현됨. Phase 3의 핵심은:
1. **F4 모델 탐색 페이지** `/models` — 검색, 필터, 정렬, 페이지네이션
2. **모델 상세 페이지** `/models/[id]` — 전체 프로필, 벤치마크, 태그

**참조**: `docs/04-feature-spec.md` F4, `docs/design/layouts/model-list.md`

---

## Agent Team (4명)

| 역할 | 태스크 | Wave |
|------|--------|------|
| ui-ux-designer | 모델 카드/상세 컴포넌트 스펙 보완 | Wave 1 |
| frontend-dev | /models + /models/[id] 페이지 + 컴포넌트 ~16개 | Wave 1 |
| frontend-qa | 모델 탐색/상세 테스트 | Wave 2 |
| backend-qa | 기존 테스트 회귀 확인 | Wave 2 |

---

## Wave 1: 모델 탐색 + 상세 (병렬 2트랙)

### Track A: frontend-dev (핵심)

**모델 탐색 페이지** `/models`:
- `app/models/page.tsx` — 메인 리스트 페이지
- `components/models/ModelSearchBar.tsx` — 검색 + 정렬
- `components/models/ModelFilters.tsx` — 데스크톱 사이드바 필터
- `components/models/ModelFilterSheet.tsx` — 모바일 시트 필터
- `components/models/ModelCard.tsx` — 모델 카드
- `components/models/ModelGrid.tsx` — 반응형 그리드
- `components/models/ModelPagination.tsx` — 페이지네이션
- `components/models/EmptyState.tsx` — 빈 결과
- `components/models/ModelCardSkeleton.tsx` — 스켈레톤

**모델 상세 페이지** `/models/[id]`:
- `app/models/[id]/page.tsx` — 상세 페이지
- `components/models/ModelProfileCard.tsx` — 모델 헤더 + 기본 정보
- `components/models/PricingTable.tsx` — 가격 테이블
- `components/models/BenchmarkTable.tsx` — 벤치마크 점수
- `components/models/CapabilitiesList.tsx` — 기능 목록

**네비게이션**: Header에 /models 링크 추가

### Track B: ui-ux-designer (독립)
- `docs/design/components/ModelCard.md` — 모델 카드 스펙
- `docs/design/components/ModelDetail.md` — 상세 페이지 스펙

### Gate 1
```bash
cd frontend && npm run build && npx tsc --noEmit && npm run lint
```

---

## Wave 2: 테스트 (병렬 2트랙)

### Track C: frontend-qa
- `components/models/__tests__/ModelCard.test.tsx`
- `components/models/__tests__/ModelFilters.test.tsx`
- `components/models/__tests__/ModelSearchBar.test.tsx`

### Track D: backend-qa
- 기존 38개 테스트 회귀 확인

### Gate 2 (Phase 3 완료)
```bash
cd backend && pytest -v
cd frontend && npm run build && npm run test
```
