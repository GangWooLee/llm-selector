# Design System Tokens

> LLM Selector -- shadcn/ui + Tailwind CSS 4 기반

---

## 1. Color Palette

shadcn/ui의 CSS 변수 체계를 따르며, Tailwind 4의 `@theme` 으로 바인딩한다.

### Primary (브랜드 -- 파란 계열)

| 토큰 | Light | Dark | 용도 |
|------|-------|------|------|
| `--primary` | `hsl(221 83% 53%)` | `hsl(217 91% 60%)` | CTA 버튼, 링크, 강조 |
| `--primary-foreground` | `hsl(210 40% 98%)` | `hsl(222 47% 11%)` | Primary 위 텍스트 |

Tailwind: `bg-primary`, `text-primary`, `text-primary-foreground`

### Secondary (보조 -- 회색 계열)

| 토큰 | Light | Dark | 용도 |
|------|-------|------|------|
| `--secondary` | `hsl(210 40% 96%)` | `hsl(217 33% 17%)` | 보조 버튼, 배경 |
| `--secondary-foreground` | `hsl(222 47% 11%)` | `hsl(210 40% 98%)` | Secondary 위 텍스트 |

Tailwind: `bg-secondary`, `text-secondary-foreground`

### Semantic Colors

| 토큰 | Light | Dark | 용도 |
|------|-------|------|------|
| `--success` | `hsl(142 71% 45%)` | `hsl(142 71% 45%)` | 유효한 키, 성공 상태 |
| `--success-foreground` | `hsl(0 0% 100%)` | `hsl(0 0% 100%)` | Success 위 텍스트 |
| `--warning` | `hsl(38 92% 50%)` | `hsl(38 92% 50%)` | 경고, 중간 점수 |
| `--warning-foreground` | `hsl(0 0% 0%)` | `hsl(0 0% 0%)` | Warning 위 텍스트 |
| `--destructive` | `hsl(0 84% 60%)` | `hsl(0 63% 31%)` | 에러, 무효 키 |
| `--destructive-foreground` | `hsl(0 0% 98%)` | `hsl(0 0% 98%)` | Destructive 위 텍스트 |

### Neutral / Background

| 토큰 | Light | Dark | 용도 |
|------|-------|------|------|
| `--background` | `hsl(0 0% 100%)` | `hsl(222 47% 11%)` | 페이지 배경 |
| `--foreground` | `hsl(222 47% 11%)` | `hsl(210 40% 98%)` | 기본 텍스트 |
| `--card` | `hsl(0 0% 100%)` | `hsl(222 47% 11%)` | 카드 배경 |
| `--card-foreground` | `hsl(222 47% 11%)` | `hsl(210 40% 98%)` | 카드 텍스트 |
| `--muted` | `hsl(210 40% 96%)` | `hsl(217 33% 17%)` | 비활성, 보조 텍스트 배경 |
| `--muted-foreground` | `hsl(215 16% 47%)` | `hsl(215 20% 65%)` | 보조 텍스트 |
| `--border` | `hsl(214 32% 91%)` | `hsl(217 33% 17%)` | 테두리 |
| `--input` | `hsl(214 32% 91%)` | `hsl(217 33% 17%)` | 입력 필드 테두리 |
| `--ring` | `hsl(221 83% 53%)` | `hsl(224 64% 33%)` | 포커스 링 |

### Score 색상 (점수 시각화 전용)

| 범위 | 색상 | Tailwind 클래스 |
|------|------|----------------|
| 80-100 | Green | `text-emerald-600 dark:text-emerald-400` |
| 60-79 | Blue | `text-blue-600 dark:text-blue-400` |
| 40-59 | Amber | `text-amber-600 dark:text-amber-400` |
| 0-39 | Red | `text-red-600 dark:text-red-400` |

---

## 2. Typography

Font stack: `Inter, system-ui, sans-serif` (shadcn/ui 기본)
Code font: `"JetBrains Mono", ui-monospace, monospace`

| 레벨 | 크기 | Weight | Line Height | Tailwind 클래스 |
|------|------|--------|-------------|----------------|
| h1 | 36px / 2.25rem | 700 (bold) | 1.2 | `text-4xl font-bold leading-tight` |
| h2 | 30px / 1.875rem | 600 (semibold) | 1.25 | `text-3xl font-semibold leading-snug` |
| h3 | 24px / 1.5rem | 600 (semibold) | 1.3 | `text-2xl font-semibold` |
| h4 | 20px / 1.25rem | 500 (medium) | 1.4 | `text-xl font-medium` |
| body | 16px / 1rem | 400 (regular) | 1.6 | `text-base leading-relaxed` |
| body-sm | 14px / 0.875rem | 400 (regular) | 1.5 | `text-sm` |
| caption | 12px / 0.75rem | 400 (regular) | 1.4 | `text-xs text-muted-foreground` |
| code | 14px / 0.875rem | 400 (regular) | 1.5 | `font-mono text-sm` |

### 모바일 조정
- h1: `text-2xl` (모바일) -> `text-4xl` (md+)
- h2: `text-xl` (모바일) -> `text-3xl` (md+)
- body: 최소 16px 유지 (모바일 줌 방지)

---

## 3. Spacing Scale

4px 기반 스케일. Tailwind의 기본 spacing과 동일.

| 토큰 | 값 | Tailwind | 용도 |
|------|-----|---------|------|
| space-1 | 4px | `p-1`, `gap-1` | 아이콘-텍스트 간격 |
| space-2 | 8px | `p-2`, `gap-2` | 인라인 요소 간격 |
| space-3 | 12px | `p-3`, `gap-3` | 컴팩트 패딩 |
| space-4 | 16px | `p-4`, `gap-4` | 기본 패딩 |
| space-5 | 20px | `p-5`, `gap-5` | 카드 내부 패딩 |
| space-6 | 24px | `p-6`, `gap-6` | 섹션 내부 패딩 |
| space-8 | 32px | `p-8`, `gap-8` | 섹션 간 간격 |
| space-10 | 40px | `p-10`, `gap-10` | 페이지 패딩 (데스크톱) |
| space-12 | 48px | `p-12`, `gap-12` | 대형 섹션 간격 |
| space-16 | 64px | `p-16`, `gap-16` | 페이지 최상위 간격 |

### 컨테이너
- 최대 너비: `max-w-7xl` (1280px)
- 페이지 패딩: `px-4 md:px-6 lg:px-8`
- 섹션 간격: `space-y-8 md:space-y-12`

---

## 4. Shadows

| 토큰 | Tailwind | 용도 |
|------|---------|------|
| shadow-sm | `shadow-sm` | 입력 필드, 작은 카드 |
| shadow-md | `shadow-md` | 일반 카드, 드롭다운 |
| shadow-lg | `shadow-lg` | Top Pick 카드, 모달 |
| shadow-xl | `shadow-xl` | 플로팅 요소 |

---

## 5. Border Radius

| 토큰 | 값 | Tailwind | 용도 |
|------|-----|---------|------|
| radius-sm | 6px | `rounded-sm` | 뱃지, 태그 |
| radius-md | 8px | `rounded-md` | 버튼, 입력 필드 |
| radius-lg | 12px | `rounded-lg` | 카드 |
| radius-xl | 16px | `rounded-xl` | 대형 카드, Top Pick |
| radius-full | 9999px | `rounded-full` | 아바타, 원형 버튼 |

---

## 6. Breakpoints (Mobile-First)

| 이름 | 최소 너비 | Tailwind prefix | 주 용도 |
|------|----------|----------------|---------|
| mobile | 0px | (기본) | 단일 컬럼 |
| sm | 640px | `sm:` | 작은 태블릿 |
| md | 768px | `md:` | 태블릿, 2컬럼 전환 |
| lg | 1024px | `lg:` | 데스크톱, 사이드바 표시 |
| xl | 1280px | `xl:` | 대형 데스크톱, 3컬럼 그리드 |

---

## 7. Animation / Transition

| 용도 | Tailwind 클래스 |
|------|----------------|
| 버튼 호버 | `transition-colors duration-150` |
| 카드 호버 | `transition-shadow duration-200` |
| 모달/드롭다운 진입 | `transition-all duration-200 ease-out` |
| 스켈레톤 로딩 | `animate-pulse` |
| 스트리밍 텍스트 커서 | `animate-pulse` (커스텀) |
| 점수 프로그레스 바 | `transition-all duration-500 ease-out` |

---

## 8. Z-Index Scale

| 레이어 | 값 | Tailwind | 용도 |
|--------|-----|---------|------|
| base | 0 | `z-0` | 기본 콘텐츠 |
| dropdown | 10 | `z-10` | 드롭다운, 필터 패널 |
| sticky | 20 | `z-20` | 고정 헤더 |
| modal-backdrop | 40 | `z-40` | 모달 배경 |
| modal | 50 | `z-50` | 모달 콘텐츠 |
| toast | 60 | -- | 토스트 알림 |
