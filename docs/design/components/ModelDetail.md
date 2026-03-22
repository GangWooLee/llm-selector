# ModelDetail Page Spec

> 모델 상세 페이지 (`/models/[id]`) — 모델의 전체 프로필, 가격, 벤치마크, 태그 표시

---

## 1. 페이지 구조 개요

```
+------------------------------------------------------------------+
| Header (공유)                              [API Key Input]        |
+------------------------------------------------------------------+
|                                                                    |
| [← 모델 목록] (뒤로가기 링크)                                       |
|                                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ [Provider 아이콘]                                [FREE Badge]  │ |
| │ h2: Claude 3.5 Sonnet                                         │ |
| │ caption: Anthropic                                             │ |
| │ body: 모델 설명 전체 텍스트                                      │ |
| │                                                                │ |
| │ [OpenRouter에서 보기 →] (외부 링크 버튼)                         │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| ┌──────────────────────┐  ┌───────────────────────────────────┐   |
| │ 가격 정보              │  │ 기능 & 스펙                       │   |
| │                        │  │                                   │   |
| │ Input:  $3.00/1M      │  │ 모달리티: [Text] [Image]          │   |
| │ Output: $15.00/1M     │  │ 파라미터: [Tools] [Streaming]     │   |
| │ Image:  -              │  │ 컨텍스트: 200K tokens             │   |
| │ Request: -             │  │ 최대 출력: 8,192 tokens           │   |
| └──────────────────────┘  └───────────────────────────────────┘   |
|                                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ 벤치마크                                                       │ |
| │ ┌──────────────┬────────┬──────────┬──────────────────────┐   │ |
| │ │ 벤치마크      │ 점수    │ 최대 점수 │ 출처                  │   │ |
| │ ├──────────────┼────────┼──────────┼──────────────────────┤   │ |
| │ │ MMLU         │ 88.7   │ 100      │ [링크]               │   │ |
| │ │ HumanEval    │ 92.1   │ 100      │ [링크]               │   │ |
| │ │ MT-Bench     │ 9.2    │ 10       │ [링크]               │   │ |
| │ └──────────────┴────────┴──────────┴──────────────────────┘   │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| ┌────────────────────────────────────────────────────────────────┐ |
| │ 특성 태그                                                       │ |
| │                                                                │ |
| │ coding        ████░  (4/5)                                    │ |
| │ multilingual  ███░░  (3/5)                                    │ |
| │ analysis      █████  (5/5)                                    │ |
| └────────────────────────────────────────────────────────────────┘ |
|                                                                    |
| Footer                                                             |
+------------------------------------------------------------------+
```

라우트: `/models/[id]` (id = `openrouter_id` 인코딩)

---

## 2. 섹션별 상세

### 2.1 헤더 섹션

```
뒤로가기:
  <Link className="flex items-center gap-1.5 text-sm text-muted-foreground
                    hover:text-foreground transition-colors mb-6">
    <ChevronLeft className="size-4" />
    모델 목록
  </Link>

헤더 카드:
  <Card className="p-6">
    상단 행:  flex items-start justify-between gap-4
      좌측:
        모델명:   text-2xl md:text-3xl font-semibold text-card-foreground
        제공사:   text-sm text-muted-foreground mt-1
      우측:
        FREE 뱃지 (조건부):
          <Badge className="bg-emerald-100 text-emerald-700
                            dark:bg-emerald-900 dark:text-emerald-300
                            text-sm font-medium">
            FREE
          </Badge>

    설명:   mt-4 text-base leading-relaxed text-card-foreground

    링크 버튼:
      <Button variant="outline" size="sm" className="mt-4 gap-1.5" asChild>
        <a href="https://openrouter.ai/models/{openrouter_id}"
           target="_blank" rel="noopener noreferrer">
          OpenRouter에서 보기
          <ExternalLink className="size-3.5" />
        </a>
      </Button>
  </Card>
```

| 데이터 | DB 필드 | 표시 |
|--------|---------|------|
| 모델명 | `models.name` | 전체 표시 (truncate 없음) |
| 제공사 | `models.provider` | capitalize |
| 설명 | `models.description` | 전문 표시 |
| FREE | `models.is_free` | true일 때 뱃지 표시 |
| 링크 | `models.openrouter_id` | `https://openrouter.ai/models/{openrouter_id}` |

---

### 2.2 가격 테이블

```
<Card className="p-6">
  <h3 className="text-xl font-medium mb-4">가격 정보</h3>

  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>항목</TableHead>
        <TableHead className="text-right">가격</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell>Input (per 1M tokens)</TableCell>
        <TableCell className="text-right font-mono">$3.00</TableCell>
      </TableRow>
      <TableRow>
        <TableCell>Output (per 1M tokens)</TableCell>
        <TableCell className="text-right font-mono">$15.00</TableCell>
      </TableRow>
      <!-- 조건부: pricing_image가 있을 때 -->
      <TableRow>
        <TableCell>Image (per image)</TableCell>
        <TableCell className="text-right font-mono">$0.01</TableCell>
      </TableRow>
      <!-- 조건부: pricing_request가 있을 때 -->
      <TableRow>
        <TableCell>Request (per request)</TableCell>
        <TableCell className="text-right font-mono">$0.005</TableCell>
      </TableRow>
    </TableBody>
  </Table>
</Card>
```

| 항목 | DB 필드 | 표시 형식 | 조건 |
|------|---------|----------|------|
| Input | `pricing_input` | `$X.XX` (× 1,000,000) | 항상 표시 |
| Output | `pricing_output` | `$X.XX` (× 1,000,000) | 항상 표시 |
| Image | `pricing_image` | `$X.XXXX` | `pricing_image > 0`일 때만 |
| Request | `pricing_request` | `$X.XXXX` | `pricing_request > 0`일 때만 |

무료 모델 (`is_free = true`): 모든 가격을 `FREE`로 표시하되, 행은 동일하게 유지.

**shadcn/ui 컴포넌트**: `Card`, `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, `TableCell`

---

### 2.3 기능 & 스펙 카드

```
<Card className="p-6">
  <h3 className="text-xl font-medium mb-4">기능 & 스펙</h3>

  <div className="space-y-4">
    <!-- 모달리티 -->
    <div>
      <p className="text-sm text-muted-foreground mb-2">모달리티</p>
      <div className="flex flex-wrap gap-1.5">
        <Badge variant="secondary">Text</Badge>
        <Badge variant="secondary">Image</Badge>
      </div>
    </div>

    <!-- 지원 파라미터 -->
    <div>
      <p className="text-sm text-muted-foreground mb-2">지원 파라미터</p>
      <div className="flex flex-wrap gap-1.5">
        <Badge variant="outline">Tools</Badge>
        <Badge variant="outline">Streaming</Badge>
        <Badge variant="outline">JSON Mode</Badge>
      </div>
    </div>

    <!-- 컨텍스트 길이 -->
    <div className="flex items-center justify-between">
      <p className="text-sm text-muted-foreground">컨텍스트 길이</p>
      <p className="text-sm font-mono">{context_length} tokens</p>
    </div>

    <!-- 최대 출력 -->
    <div className="flex items-center justify-between">
      <p className="text-sm text-muted-foreground">최대 출력 토큰</p>
      <p className="text-sm font-mono">{max_completion_tokens} tokens</p>
    </div>
  </div>
</Card>
```

| 항목 | DB 필드 | 표시 형식 |
|------|---------|----------|
| 모달리티 | `models.modalities` (JSONB) | 각 항목을 `Badge variant="secondary"`로 표시 |
| 지원 파라미터 | `models.supported_parameters` (JSONB) | 각 항목을 `Badge variant="outline"`로 표시 |
| 컨텍스트 길이 | `models.context_length` | `200K tokens` 형식 (1000 단위 K 변환) |
| 최대 출력 | `models.max_completion_tokens` | `8,192 tokens` (천 단위 콤마) |

값이 없는 필드(`null`)는 "정보 없음"으로 표시하지 않고 해당 행 자체를 숨긴다.

---

### 2.4 벤치마크 테이블

```
<Card className="p-6">
  <h3 className="text-xl font-medium mb-4">벤치마크</h3>

  <!-- 데이터 있을 때 -->
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>벤치마크</TableHead>
        <TableHead className="text-right">점수</TableHead>
        <TableHead className="text-right">최대 점수</TableHead>
        <TableHead className="text-right">출처</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-medium">MMLU</TableCell>
        <TableCell className="text-right font-mono text-emerald-600 dark:text-emerald-400">
          88.7
        </TableCell>
        <TableCell className="text-right font-mono text-muted-foreground">
          100
        </TableCell>
        <TableCell className="text-right">
          <a href="{source_url}" target="_blank" rel="noopener noreferrer"
             className="text-primary hover:underline text-sm">
            출처 ↗
          </a>
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>

  <!-- 데이터 없을 때 (빈 상태) -->
  <div className="flex flex-col items-center justify-center py-8 text-center">
    <BarChart3 className="size-8 text-muted-foreground/50 mb-3" />
    <p className="text-sm text-muted-foreground">
      이 모델의 벤치마크는 아직 등록되지 않았습니다
    </p>
  </div>
</Card>
```

#### 점수 색상 규칙

벤치마크 점수는 `max_score` 대비 비율로 색상 적용 (디자인 토큰의 Score 색상):

| 비율 (score/max_score × 100) | Tailwind 클래스 |
|------------------------------|----------------|
| 80-100% | `text-emerald-600 dark:text-emerald-400` |
| 60-79% | `text-blue-600 dark:text-blue-400` |
| 40-59% | `text-amber-600 dark:text-amber-400` |
| 0-39% | `text-red-600 dark:text-red-400` |

`max_score`가 없을 때는 색상 없이 기본 텍스트 색상 사용.

| 데이터 | DB 필드 | 표시 |
|--------|---------|------|
| 벤치마크명 | `model_benchmarks.benchmark_name` | 그대로 |
| 점수 | `model_benchmarks.score` | 소수점 1자리 |
| 최대 점수 | `model_benchmarks.max_score` | 소수점 1자리 (없으면 "-") |
| 출처 | `model_benchmarks.source_url` | 외부 링크 (`target="_blank"`) |

**shadcn/ui 컴포넌트**: `Card`, `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, `TableCell`

---

### 2.5 특성 태그 (Strength Bars)

```
<Card className="p-6">
  <h3 className="text-xl font-medium mb-4">특성 태그</h3>

  <!-- 데이터 있을 때 -->
  <div className="space-y-3">
    <!-- 각 태그 행 -->
    <div className="flex items-center gap-4">
      <span className="text-sm w-32 shrink-0 capitalize">coding</span>

      <!-- Strength bar: 5칸 중 채워진 칸 -->
      <div className="flex gap-1 flex-1 max-w-40">
        <div className="h-2 flex-1 rounded-sm bg-primary" />      <!-- 1 -->
        <div className="h-2 flex-1 rounded-sm bg-primary" />      <!-- 2 -->
        <div className="h-2 flex-1 rounded-sm bg-primary" />      <!-- 3 -->
        <div className="h-2 flex-1 rounded-sm bg-primary" />      <!-- 4 -->
        <div className="h-2 flex-1 rounded-sm bg-muted" />        <!-- 5 (비활성) -->
      </div>

      <span className="text-xs text-muted-foreground w-8 text-right">4/5</span>
    </div>
  </div>

  <!-- 데이터 없을 때 (빈 상태) -->
  <div className="flex flex-col items-center justify-center py-8 text-center">
    <Tags className="size-8 text-muted-foreground/50 mb-3" />
    <p className="text-sm text-muted-foreground">
      이 모델의 특성 태그는 아직 등록되지 않았습니다
    </p>
  </div>
</Card>
```

| 데이터 | DB 필드 | 표시 |
|--------|---------|------|
| 카테고리 | `model_tags.category` | capitalize (e.g., "coding" → "Coding") |
| 강도 | `model_tags.strength_level` | 5칸 바 (1-5), 채워진 칸 = `bg-primary`, 빈 칸 = `bg-muted` |

태그는 `strength_level` 내림차순으로 정렬하여 강한 특성이 먼저 보이도록 한다.

---

## 3. 반응형 레이아웃

### 모바일 (< 768px): 단일 컬럼

```
[← 모델 목록]
[헤더 카드 (전체 너비)]
[가격 테이블 (전체 너비)]
[기능 & 스펙 (전체 너비)]
[벤치마크 (전체 너비)]
[특성 태그 (전체 너비)]
```

```
래퍼: max-w-7xl mx-auto px-4 py-6 space-y-6
```

### 데스크톱 (md+): 2-Column Grid

```
[← 모델 목록]
[헤더 카드 (전체 너비, col-span-2)]
┌──────────────────────┐  ┌──────────────────────┐
│ 가격 테이블            │  │ 기능 & 스펙           │
└──────────────────────┘  └──────────────────────┘
[벤치마크 (전체 너비, col-span-2)]
[특성 태그 (전체 너비, col-span-2)]
```

```
그리드:  grid grid-cols-1 md:grid-cols-2 gap-6
헤더:    md:col-span-2
벤치마크: md:col-span-2
태그:    md:col-span-2
```

가격 테이블과 기능 카드만 나란히 배치되고, 나머지는 전체 너비를 사용한다.

---

## 4. 다크 모드

shadcn/ui CSS 변수 시스템 사용으로 대부분 자동 대응.

| 요소 | Light | Dark |
|------|-------|------|
| 페이지 배경 | `bg-background` | 자동 |
| 카드 배경 | `bg-card` (Card 기본) | 자동 |
| 텍스트 | `text-card-foreground` | 자동 |
| 보조 텍스트 | `text-muted-foreground` | 자동 |
| 테두리 | `border-border` | 자동 |
| Strength bar 활성 | `bg-primary` | 자동 |
| Strength bar 비활성 | `bg-muted` | 자동 |
| FREE 뱃지 | `bg-emerald-100 text-emerald-700` | `dark:bg-emerald-900 dark:text-emerald-300` |
| 점수 색상 | `text-emerald-600` 등 | `dark:text-emerald-400` 등 |

---

## 5. 접근성

| 항목 | 구현 |
|------|------|
| 뒤로가기 | `<Link>` with visible text, 키보드 접근 가능 |
| 외부 링크 | `target="_blank" rel="noopener noreferrer"`, `aria-label="OpenRouter에서 {모델명} 보기 (새 탭)"` |
| 테이블 | 시맨틱 `<table>` 요소 사용 (shadcn Table) |
| Strength bar | `aria-label="{category} 강도 {level}/5"`, `role="meter"`, `aria-valuemin="1"`, `aria-valuemax="5"`, `aria-valuenow="{level}"` |
| 빈 상태 | 아이콘에 `aria-hidden="true"`, 메시지 텍스트로 의미 전달 |
| 색상 대비 | Score 색상은 보조 수단 — 숫자로도 동일 정보 제공 |
| 포커스 | 모든 인터랙티브 요소에 `focus-visible:ring-2` |

---

## 6. 로딩 상태

페이지 전체 스켈레톤:

```
[← 모델 목록]

<Card className="p-6 space-y-4">
  <Skeleton className="h-8 w-[50%]" />
  <Skeleton className="h-4 w-[30%]" />
  <Skeleton className="h-4 w-full" />
  <Skeleton className="h-4 w-[90%]" />
  <Skeleton className="h-10 w-36" />
</Card>

<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <Card className="p-6 space-y-3">
    <Skeleton className="h-6 w-[40%]" />
    <Skeleton className="h-4 w-full" />
    <Skeleton className="h-4 w-full" />
    <Skeleton className="h-4 w-[60%]" />
  </Card>
  <Card className="p-6 space-y-3">
    <Skeleton className="h-6 w-[40%]" />
    <Skeleton className="h-5 w-20 rounded-sm" />
    <Skeleton className="h-5 w-20 rounded-sm" />
    <Skeleton className="h-4 w-full" />
  </Card>
</div>

<Card className="p-6 space-y-3">
  <Skeleton className="h-6 w-[30%]" />
  <Skeleton className="h-4 w-full" />
  <Skeleton className="h-4 w-full" />
  <Skeleton className="h-4 w-[80%]" />
</Card>
```

`animate-pulse` 적용. 뒤로가기 링크는 스켈레톤 동안에도 활성.

---

## 7. 에러 상태

모델이 존재하지 않을 때 (`404`):

```
<div className="flex flex-col items-center justify-center py-16 text-center">
  <AlertCircle className="size-12 text-muted-foreground/50 mb-4" />
  <h3 className="text-lg font-medium">모델을 찾을 수 없습니다</h3>
  <p className="text-sm text-muted-foreground mt-1">
    요청하신 모델이 삭제되었거나 존재하지 않습니다
  </p>
  <Button variant="outline" className="mt-4" asChild>
    <Link href="/models">모델 목록으로 돌아가기</Link>
  </Button>
</div>
```
