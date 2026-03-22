# ModelCard Component Spec

> 모델 탐색 페이지의 개별 모델 카드 — shadcn/ui `Card` 기반

---

## 1. 구조 (Anatomy)

```
+-----------------------------------------------+
| [Provider 아이콘/로고]  [FREE Badge] (조건부)    |
| h4: GPT-4o                                     |
| caption: OpenAI                                |
|                                                 |
| body-sm: 모델 설명 텍스트 (최대 2줄, truncate)    |
|                                                 |
| ── 구분선 ──                                     |
|                                                 |
| 가격                                             |
|   Input:  $2.50 / 1M tokens                     |
|   Output: $10.00 / 1M tokens                    |
|                                                 |
| 컨텍스트: 128K tokens                             |
|                                                 |
| [coding] [multilingual] [analysis]  ← 주요 태그  |
+-----------------------------------------------+
```

### 데이터 필드

| 영역 | DB 필드 | 표시 형식 |
|------|---------|----------|
| 모델명 | `models.name` | 그대로 표시, 1줄 truncate |
| 제공사 | `models.provider` | capitalize (e.g., "openai" → "OpenAI") |
| 설명 | `models.description` | 최대 2줄, `line-clamp-2` |
| 입력 가격 | `models.pricing_input` | `$X.XX / 1M tokens` (pricing_input × 1,000,000) |
| 출력 가격 | `models.pricing_output` | `$X.XX / 1M tokens` (pricing_output × 1,000,000) |
| 컨텍스트 | `models.context_length` | `128K tokens` (1000 단위 K 변환) |
| FREE 배지 | `models.is_free` | true일 때만 표시 |
| 태그 | `model_tags.category` | 상위 3개까지만 표시, 초과 시 `+N` 뱃지 |

---

## 2. 상태 (States)

### Default

```
래퍼: rounded-lg border border-border bg-card p-5 cursor-pointer
       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
```

### Hover

```
래퍼: hover:shadow-md hover:border-primary/30
애니메이션: transition-shadow duration-200
```

그림자가 `shadow-sm` → `shadow-md`로 증가하고, 테두리에 Primary 색상 틴트 적용.

### Active / Pressed

```
래퍼: active:scale-[0.98]
애니메이션: transition-transform duration-100
```

미세한 축소 효과로 클릭 피드백 제공.

### Loading (Skeleton)

```
+-----------------------------------------------+
| <Skeleton className="size-6 rounded-full" />   |
| <Skeleton className="h-5 w-[60%]" />           |
| <Skeleton className="h-4 w-[40%]" />           |
|                                                 |
| <Skeleton className="h-4 w-full" />             |
| <Skeleton className="h-4 w-[80%]" />            |
|                                                 |
| <Separator />                                   |
|                                                 |
| <Skeleton className="h-4 w-[50%]" />            |
| <Skeleton className="h-4 w-[50%]" />            |
| <Skeleton className="h-4 w-[45%]" />            |
|                                                 |
| <div className="flex gap-1.5">                  |
|   <Skeleton className="h-5 w-16 rounded-sm" /> |
|   <Skeleton className="h-5 w-16 rounded-sm" /> |
|   <Skeleton className="h-5 w-16 rounded-sm" /> |
| </div>                                          |
+-----------------------------------------------+
```

스켈레톤 카드는 실제 카드와 동일한 레이아웃 구조를 유지한다.
`animate-pulse` 적용.

---

## 3. Tailwind 클래스 상세

### 카드 래퍼

```
<Card>
  className="rounded-lg border border-border bg-card p-5
             hover:shadow-md hover:border-primary/30
             active:scale-[0.98]
             transition-all duration-200
             cursor-pointer
             focus-visible:outline-none focus-visible:ring-2
             focus-visible:ring-ring focus-visible:ring-offset-2"
</Card>
```

### 헤더 영역 (모델명 + 제공사)

```
헤더 래퍼:  flex items-start justify-between gap-2
모델명:     text-lg font-semibold truncate text-card-foreground
제공사:     text-sm text-muted-foreground
FREE 뱃지:  (아래 "뱃지" 섹션 참조)
```

### 설명

```
설명:  mt-2 text-sm text-muted-foreground line-clamp-2
```

### 구분선

```
<Separator className="my-3" />
```

### 가격 영역

```
가격 래퍼:   space-y-1
라벨:        text-xs text-muted-foreground
금액:        text-sm font-mono text-card-foreground
  Input 행:  flex items-center justify-between
  Output 행: flex items-center justify-between
```

무료 모델일 때 가격 대신 FREE 뱃지만 표시:

```
<Badge
  variant="secondary"
  className="bg-emerald-100 text-emerald-700
             dark:bg-emerald-900 dark:text-emerald-300
             text-xs font-medium"
>
  FREE
</Badge>
```

### 컨텍스트 길이

```
래퍼:  mt-2 flex items-center gap-1.5 text-sm text-muted-foreground
아이콘: size-3.5 (Layers 또는 AlignLeft 아이콘)
텍스트: font-mono
```

### 태그 영역

```
래퍼:   mt-3 flex flex-wrap gap-1.5
각 태그: <Badge variant="outline" className="text-xs">
           {category}
         </Badge>
초과:   <Badge variant="outline" className="text-xs text-muted-foreground">
           +{count}
         </Badge>
```

---

## 4. 그리드 레이아웃

```
grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4
```

| 브레이크포인트 | 열 수 | 카드 최소 너비 |
|--------------|-------|-------------|
| mobile (< 640px) | 1 | 전체 너비 |
| sm (640px+) | 2 | ~296px |
| xl (1280px+) | 3 | ~384px |

---

## 5. 반응형 동작

### 모바일 (< 640px)
- 1열 풀 너비 카드
- 설명 텍스트: `line-clamp-2` 유지
- 태그: 최대 2개까지만 표시, 초과 시 `+N`

### sm ~ lg (640px ~ 1279px)
- 2열 그리드
- 필터 사이드바와 함께 배치 (lg+에서)

### xl+ (1280px+)
- 3열 그리드
- 카드 내 모든 정보 표시

---

## 6. 접근성

| 항목 | 구현 |
|------|------|
| 클릭 가능 영역 | 카드 전체가 클릭 대상 (최소 44px 높이 보장) |
| 키보드 내비게이션 | `tabIndex={0}`, `role="link"`, `onKeyDown` (Enter/Space → navigate) |
| Focus 링 | `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2` |
| 스크린 리더 | `aria-label="{모델명} by {제공사}"` |
| 터치 타겟 | 카드 전체 영역 (44x44 최소 충족) |

### 키보드 동작

| 키 | 동작 |
|----|------|
| Tab | 다음 카드로 포커스 이동 |
| Shift+Tab | 이전 카드로 포커스 이동 |
| Enter / Space | 모델 상세 페이지로 이동 |

---

## 7. 다크 모드

| 요소 | Light | Dark |
|------|-------|------|
| 카드 배경 | `bg-card` (white) | `bg-card` (hsl 222 47% 11%) |
| 텍스트 | `text-card-foreground` | `text-card-foreground` |
| 보조 텍스트 | `text-muted-foreground` | `text-muted-foreground` |
| 테두리 | `border-border` | `border-border` |
| 호버 테두리 | `hover:border-primary/30` | `hover:border-primary/30` |
| FREE 뱃지 배경 | `bg-emerald-100` | `dark:bg-emerald-900` |
| FREE 뱃지 텍스트 | `text-emerald-700` | `dark:text-emerald-300` |

shadcn/ui의 CSS 변수 시스템을 사용하므로, `bg-card`, `text-card-foreground`, `border-border` 등이 자동으로 다크 모드에 대응한다.

---

## 8. 인터랙션 흐름

```
[Default] --hover--> [Hover: shadow-md + border tint]
    |                          |
    +--click/enter/space-------+---> Navigate to /models/[id]
    |
    +--focus (tab)---> [Focus: ring-2 표시]
```

카드 클릭 시 Next.js `router.push("/models/{openrouter_id}")` 또는 `<Link>` 사용.
