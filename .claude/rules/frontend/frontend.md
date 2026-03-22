---
description: "Next.js + Tailwind + shadcn/ui 프론트엔드 규칙."
globs: "frontend/**"
---

# 프론트엔드 (Next.js + Tailwind + shadcn/ui)

> **📚 기획 문서 참조** (frontend 작업 전 반드시 확인):
> - 기능 명세/UI 동작: `docs/04-feature-spec.md`
> - SSE 프로토콜/출력 스키마: `docs/02-agent-workflow.md`
> - API 요청/응답: `docs/05-api-spec.md`

## Next.js App Router

- Server Components 기본, 클라이언트 상태 필요 시에만 `"use client"`
- 데이터 페칭: Server Components에서 직접 또는 Server Actions
- 라우팅: `app/` 디렉토리 파일 기반

## Tailwind CSS

- Mobile-first: `flex flex-col md:flex-row`
- `@apply` 사용 자제 — 인라인 유틸리티 우선
- 간격 일관성: `space-y-N` 사용, 혼합 `mb-2`/`mb-4` 금지
- 다크 모드: `dark:` 프리픽스 활용

## shadcn/ui 컴포넌트

- 기존 shadcn/ui 컴포넌트 우선 활용 (직접 만들기 전에 확인)
- 커스터마이징은 컴포넌트 파일 직접 수정 (소유권 모델)
- 일관된 variant 사용

## 접근성 (CRITICAL)

- 터치 타겟 최소 44x44px
- 모바일 본문 최소 16px
- `aria-label` (아이콘 버튼), `htmlFor` (폼 라벨) 필수
- 색상 대비: 일반 텍스트 4.5:1, 큰 텍스트 3:1
- 포커스 링 제거 금지: `focus-visible:ring-2`

## SSE 클라이언트 규칙

- `EventSource` 또는 `fetch` + ReadableStream 사용
- 연결 실패 시 재시도 로직 포함
- 타임아웃 처리 (에이전트 응답 최대 120초)
- 스트리밍 중 로딩 상태 UI 필수

## 상태 관리

- API 키: `sessionStorage` (보안)
- 서버 상태: React Query 또는 SWR
- 로컬 UI 상태: `useState`/`useReducer`
- 전역 상태 최소화

## TypeScript 규칙

- `any` 타입 금지 — `unknown` 후 타입 가드 사용
- API 응답 타입 정의 필수
- 공통 타입은 `types/` 디렉토리
