# Model List Page Layout

> 모델 탐색 페이지 -- 검색, 필터, 모델 카드 그리드, 페이지네이션

---

## 페이지 구조 개요

```
+------------------------------------------------------------------+
| Header (공유)                              [API Key Input]        |
+------------------------------------------------------------------+
|                                                                    |
| h1: 모델 탐색                                                      |
| caption: N개 모델 | 마지막 동기화: 2026-03-22                        |
|                                                                    |
| [검색바 (full-width)]                                               |
|                                                                    |
+------------------------------------------------------------------+
|          |                                                         |
| 필터     |  모델 카드 그리드                                         |
| 사이드바  |                                                         |
|          |  [카드] [카드] [카드]                                     |
|          |  [카드] [카드] [카드]                                     |
|          |  [카드] [카드] [카드]                                     |
|          |                                                         |
|          |  [페이지네이션]                                           |
+------------------------------------------------------------------+
| Footer                                                             |
+------------------------------------------------------------------+
```

라우트: `/models`

---

## 1. 검색바

```
+------------------------------------------------------------------+
| [Search icon] [     모델명, 제공사, 설명으로 검색...     ]  [정렬 ▾] |
+------------------------------------------------------------------+
```

**shadcn/ui 컴포넌트**: `Input`, `Select`

**Tailwind**
```
래퍼: flex flex-col sm:flex-row gap-3 mb-6
검색 Input 래퍼: relative flex-1
  아이콘: absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground
  Input: pl-10 w-full h-11
정렬 Select: w-full sm:w-48 h-11
```

**정렬 옵션**
- 이름 (가나다순)
- 가격 낮은순
- 가격 높은순
- 컨텍스트 길이 긴순

**인터랙션**
- 디바운스 검색 (300ms)
- 검색어 입력 시 즉시 필터링 (클라이언트) 또는 API 호출 (서버)
- 검색 결과 0건: 빈 상태 일러스트 + "검색 결과가 없습니다" 메시지

---

## 2. 필터 사이드바

### 데스크톱 (lg+): 좌측 고정 사이드바

```
+---------------------------+
| 필터                [초기화]|
+---------------------------+
| 제공사                      |
| [x] OpenAI                 |
| [x] Anthropic              |
| [ ] Google                  |
| [ ] Meta                    |
| ... 더 보기                 |
+---------------------------+
| 가격대                      |
| [x] 무료                    |
| [ ] 저가 (< $1/M tokens)   |
| [ ] 중가 ($1-10/M)         |
| [ ] 고가 (> $10/M)          |
+---------------------------+
| 컨텍스트 길이               |
| [Slider: 4K --- 200K+]     |
+---------------------------+
| 기능                        |
| [x] Vision                 |
| [ ] Function Calling       |
| [ ] JSON Mode              |
| [ ] Streaming              |
+---------------------------+
| 유형                        |
| ( ) 전체                    |
| ( ) 무료만                  |
| ( ) 유료만                  |
+---------------------------+
```

### 모바일 (< lg): 시트/드로워

```
[필터 Button + 활성 필터 수 Badge] -> 하단 Sheet 열림
```

**shadcn/ui 컴포넌트**: `Checkbox`, `RadioGroup`, `Slider`, `Sheet`, `Button`, `Badge`, `Accordion`

**Tailwind**
```
사이드바 (데스크톱):
  위치: sticky top-20 (헤더 높이 + 간격)
  너비: w-64 shrink-0
  내부: space-y-6

섹션:
  제목: text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3
  체크박스 목록: space-y-2
  각 항목: flex items-center gap-2 text-sm

모바일 필터 버튼:
  위치: 검색바 아래
  스타일: <Button variant="outline" className="w-full lg:hidden">
  뱃지: <Badge className="ml-2">{활성 필터 수}</Badge>

Sheet:
  <Sheet>
    <SheetContent side="bottom" className="max-h-[80vh] overflow-y-auto">
```

### 필터 카테고리 상세

| 카테고리 | 타입 | 옵션 |
|---------|------|------|
| 제공사 | Checkbox (다중 선택) | OpenAI, Anthropic, Google, Meta, Mistral, Cohere, 기타 |
| 가격대 | Checkbox (다중 선택) | 무료, 저가(< $1/M), 중가($1-10/M), 고가(> $10/M) |
| 컨텍스트 길이 | Range Slider | 4K ~ 200K+ (단계: 4K) |
| 기능 | Checkbox (다중 선택) | Vision, Function Calling, JSON Mode, Streaming |
| 유형 | RadioGroup (단일) | 전체, 무료만, 유료만 |

**인터랙션**
- 필터 변경 시 즉시 결과 갱신 (디바운스 없음)
- 초기화 버튼: 모든 필터 해제
- 활성 필터 뱃지: 검색바 옆 또는 필터 버튼에 활성 필터 수 표시
- "더 보기": 제공사 5개 초과 시 접기/펼치기

---

## 3. 모델 카드 그리드

### 개별 모델 카드

```
+-------------------------------------------+
| [Provider 로고/아이콘]                       |
| h4: Claude 3.5 Sonnet                      |
| caption: Anthropic                          |
|                                             |
| 가격: $3.00 / $15.00 per 1M tokens          |
|   (입력 / 출력)                              |
|                                             |
| 컨텍스트: 200K tokens                        |
|                                             |
| [Vision] [Function Calling] [Streaming]     |
+-------------------------------------------+
```

**shadcn/ui 컴포넌트**: `Card` (`CardHeader`, `CardContent`), `Badge`

**Tailwind**
```
그리드: grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4

카드:
  래퍼: rounded-lg border border-border p-5 hover:shadow-md hover:border-primary/30 transition-all duration-200 cursor-pointer
  모델명: text-lg font-semibold truncate
  제공사: text-sm text-muted-foreground
  가격 영역: mt-3
    라벨: text-xs text-muted-foreground
    금액: text-sm font-mono
    무료: <Badge variant="secondary" className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">FREE</Badge>
  컨텍스트: mt-2 text-sm text-muted-foreground
  태그 영역: mt-3 flex flex-wrap gap-1.5
    태그: <Badge variant="outline" className="text-xs">Vision</Badge>
```

**카드 인터랙션**
- 호버: 그림자 증가 + 테두리 Primary 틴트
- 클릭: `/models/[id]` 상세 페이지로 이동
- 무료 모델: FREE 뱃지 강조

### 빈 상태

```
+-------------------------------------------+
|                                             |
|  [SearchX icon, size-12, muted]             |
|                                             |
|  h3: 검색 결과가 없습니다                     |
|  p: 검색어나 필터를 조정해 보세요              |
|                                             |
|  [필터 초기화 Button]                        |
+-------------------------------------------+
```

**Tailwind**
```
래퍼: flex flex-col items-center justify-center py-16 text-center
아이콘: size-12 text-muted-foreground/50 mb-4
제목: text-lg font-medium
설명: text-sm text-muted-foreground mt-1
버튼: mt-4
```

### 로딩 상태 (스켈레톤)

```
+-------------------------------------------+
| [Skeleton: 사각형 24x24]                    |
| [Skeleton: 텍스트 60%]                      |
| [Skeleton: 텍스트 40%]                      |
| [Skeleton: 텍스트 50%]                      |
| [Skeleton: 뱃지 x3]                        |
+-------------------------------------------+
```

**shadcn/ui 컴포넌트**: `Skeleton`

**Tailwind**
```
스켈레톤 카드: rounded-lg border border-border p-5 space-y-3
각 Skeleton: <Skeleton className="h-4 w-[60%]" />
뱃지 스켈레톤: flex gap-1.5 -> <Skeleton className="h-5 w-16 rounded-full" /> x 3
```

그리드에 6~9개 스켈레톤 카드 표시.

---

## 4. 페이지네이션

```
+------------------------------------------------------------------+
|                                                                    |
|  N개 모델 중 1-24 표시                                              |
|                                                                    |
|  [< 이전]  [1] [2] [3] ... [12]  [다음 >]                          |
|                                                                    |
+------------------------------------------------------------------+
```

**shadcn/ui 컴포넌트**: `Pagination` (`PaginationContent`, `PaginationItem`, `PaginationLink`, `PaginationNext`, `PaginationPrevious`, `PaginationEllipsis`)

**Tailwind**
```
래퍼: flex flex-col items-center gap-4 py-8
정보 텍스트: text-sm text-muted-foreground
페이지네이션: flex items-center gap-1
```

**동작**
- 페이지당 24개 모델
- 현재 페이지: Primary 배경 강조
- 5페이지 초과 시 Ellipsis(...) 표시
- 첫 페이지: "이전" 비활성
- 마지막 페이지: "다음" 비활성
- 페이지 변경 시 스크롤 최상단으로 이동

---

## 5. 반응형 브레이크포인트별 레이아웃

### 모바일 (< 640px)
```
[Header]
[h1: 모델 탐색]
[검색바 (full-width)]
[정렬 Select (full-width)]
[필터 Button (full-width)] -> Sheet
---
[모델 카드 (1열)]
[모델 카드]
[모델 카드]
---
[페이지네이션]
```

### sm (640px+)
```
[Header]
[h1 + 동기화 정보]
[검색바 + 정렬 수평 배치]
[필터 Button] -> Sheet
---
[모델 카드 (2열 그리드)]
---
[페이지네이션]
```

### lg (1024px+)
```
[Header]
[h1 + 동기화 정보]
[검색바 + 정렬]
+----------+------------------------------------------+
| 필터      | [모델 카드 (2열 그리드)]                    |
| 사이드바   |                                            |
| (w-64)   |                                            |
|          | [페이지네이션]                               |
+----------+------------------------------------------+
```

### xl (1280px+)
```
+----------+------------------------------------------+
| 필터      | [모델 카드 (3열 그리드)]                    |
| 사이드바   |                                            |
+----------+------------------------------------------+
```

**Tailwind 레이아웃**
```
메인 래퍼: max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6
컨텐츠 영역: flex gap-8
  사이드바: hidden lg:block w-64 shrink-0
  메인: flex-1 min-w-0
```

---

## 6. URL 파라미터 (상태 동기화)

| 파라미터 | 예시 | 설명 |
|---------|------|------|
| `q` | `?q=claude` | 검색어 |
| `provider` | `?provider=openai,anthropic` | 제공사 필터 |
| `price` | `?price=free,low` | 가격대 필터 |
| `ctx_min` | `?ctx_min=32000` | 최소 컨텍스트 |
| `cap` | `?cap=vision,tools` | 기능 필터 |
| `type` | `?type=free` | 유형 필터 |
| `sort` | `?sort=price_asc` | 정렬 |
| `page` | `?page=2` | 페이지 번호 |

필터 상태를 URL에 동기화하여 공유/북마크 가능하게 한다.
