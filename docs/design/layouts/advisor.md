# Advisor Page Layout

> 메인 어드바이저 페이지 -- 용도 입력, 에이전트 추론 스트리밍, 비교 대시보드

---

## 페이지 구조 개요

```
+------------------------------------------------------------------+
| Header (고정)                              [API Key Input]        |
+------------------------------------------------------------------+
|                                                                    |
|  [용도 입력 폼]                                                     |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  [에이전트 추론 과정] (스트리밍, 토글로 표시/숨김)                      |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  [비교 대시보드]                                                     |
|    - Top Pick 카드                                                  |
|    - 비교표                                                         |
|    - 상세 카드 그리드                                                 |
|    - 요약 + 근거                                                     |
|                                                                    |
+------------------------------------------------------------------+
| Footer                                                             |
+------------------------------------------------------------------+
```

라우트: `/` (메인 페이지)

---

## 1. Header

**구성**: 로고 + 네비게이션 + API Key Input

```
[Logo: LLM Selector]  [어드바이저]  [모델 탐색]       [ApiKeyInput]
```

**Tailwind**
```
header: sticky top-0 z-20 border-b border-border bg-background/95 backdrop-blur
  내부: max-w-7xl mx-auto px-4 md:px-6 lg:px-8 h-14 flex items-center justify-between
  nav: flex items-center gap-6
  ApiKeyInput: ml-auto
```

**반응형**
- 모바일: 로고 + 햄버거 메뉴, API Key는 메뉴 내부 또는 헤더 아래 행
- md+: 전체 수평 레이아웃

---

## 2. 용도 입력 폼

**구성**
- 제목: "어떤 용도로 LLM을 사용하시나요?"
- 텍스트 입력: 멀티라인 textarea
- 분석 모델 선택: 드롭다운 (Select)
- 분석 시작 버튼

**와이어프레임**
```
+------------------------------------------------------------------+
|  h2: 어떤 용도로 LLM을 사용하시나요?                                  |
|  caption: 구체적으로 설명할수록 더 정확한 추천을 받을 수 있습니다          |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  | Textarea                                                      |  |
|  | "예: 한국어 고객 상담 챗봇을 만들고 싶어.                          |  |
|  |  월 100만 건 정도 처리해야 하고, 빠른 응답이 중요해."               |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  [분석 모델: Select ▾ ]              [분석 시작 Button ->]           |
+------------------------------------------------------------------+
```

**shadcn/ui 컴포넌트**: `Textarea`, `Select`, `Button`

**Tailwind**
```
섹션: max-w-3xl mx-auto py-8 md:py-12 px-4
h2: text-2xl md:text-3xl font-semibold text-center
caption: text-sm text-muted-foreground text-center mt-2
Textarea: min-h-32 resize-y mt-6 text-base
하단 행: flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mt-4
Select: w-full sm:w-48
Button: w-full sm:w-auto min-h-11
```

**상태**
- API 키 미입력: 버튼 비활성 + 툴팁 "먼저 API 키를 입력하세요"
- 빈 입력: 버튼 비활성
- 분석 중: 버튼에 스피너 + "분석 중..." 텍스트, textarea 비활성

---

## 3. 에이전트 추론 과정 (스트리밍 영역)

분석 시작 후 SSE로 에이전트 추론 과정을 실시간 표시.

**기본 동작**: 접혀 있음 (결과만 표시). "추론 과정 보기" 토글로 펼침.

### 3a. 스트리밍 진행 중 (로딩)

```
+------------------------------------------------------------------+
|  [Spinner] 에이전트가 분석 중입니다...                                |
|                                                                    |
|  +-  단계 1: 용도 분석 --------------------------------- [완료]  -+  |
|  |   "한국어 챗봇 + 대량 처리 -> 다국어, 속도, 가격 중요"            |  |
|  +---------------------------------------------------------------+  |
|  +-  단계 2: 모델 검색 --------------------------------- [완료]  -+  |
|  |   search_models -> 12개 후보 모델 발견                         |  |
|  +---------------------------------------------------------------+  |
|  +-  단계 3: 가격 비교 -------------------------------- [진행 중] -+  |
|  |   compare_pricing -> [Spinner] 분석 중...                      |  |
|  +---------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

**각 단계 아이콘 매핑** (SSE tool_call event)
- search_models: 검색 아이콘 (`Search`)
- compare_pricing: 달러 아이콘 (`DollarSign`)
- get_benchmarks: 차트 아이콘 (`BarChart3`)
- web_search: 지구 아이콘 (`Globe`)
- assess_model_fit: 체크 아이콘 (`CheckCircle`)
- get_model_details: 정보 아이콘 (`Info`)

**shadcn/ui 컴포넌트**: `Collapsible`, `Card`, `Badge`

**Tailwind**
```
래퍼: max-w-3xl mx-auto px-4 py-6
토글 버튼: flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground
스텝 카드: border border-border rounded-lg p-4 space-y-2
스텝 제목 행: flex items-center justify-between
아이콘: size-4 text-muted-foreground
상태 뱃지 (완료): <Badge variant="outline" className="text-success border-success">완료</Badge>
상태 뱃지 (진행중): <Badge variant="outline">진행 중</Badge> + <Loader2 className="animate-spin size-3" />
단계 목록: space-y-3
```

### 3b. 추론 과정 토글 위치

```
+------------------------------------------------------------------+
|  [비교 대시보드 제목]                                                |
|                               [Switch: 추론 과정 보기]              |
+------------------------------------------------------------------+
```

- shadcn `Switch` 컴포넌트, 대시보드 제목 우측에 배치
- 기본값: OFF (결과만 표시)
- ON 시: 대시보드 위에 추론 과정 섹션 표시

---

## 4. 비교 대시보드

분석 완료 후 ComparisonReport를 시각화.

### 4a. Top Pick 카드

```
+------------------------------------------------------------------+
|  [Crown icon]  TOP PICK                                            |
|                                                                    |
|  h3: Claude 3.5 Haiku                                              |
|  provider: Anthropic                                               |
|                                                                    |
|  종합 점수: [============================] 92/100                   |
|                                                                    |
|  "한국어 처리 능력이 뛰어나고, 토큰당 가격이 가장 저렴하여              |
|   대량 처리 챗봇에 최적입니다."                                       |
|                                                                    |
|  [상세 보기 Button]                                                  |
+------------------------------------------------------------------+
```

**Tailwind**
```
카드: rounded-xl border-2 border-primary bg-primary/5 p-6 shadow-lg
뱃지 행: flex items-center gap-2 text-sm font-medium text-primary uppercase tracking-wide
모델명: text-2xl font-semibold mt-3
provider: text-sm text-muted-foreground
점수 바: mt-4, h-2 rounded-full bg-muted -> 내부 h-2 rounded-full bg-primary transition-all duration-500
이유 텍스트: text-base leading-relaxed mt-4 text-foreground
```

### 4b. 비교표

```
+----------+----------+----------+----------+----------+-----------+----------+
| 모델      | 종합     | 가격     | 성능     | 적합도   | 월 비용    | 최적 용도 |
+----------+----------+----------+----------+----------+-----------+----------+
| Claude   |  92      |  95      |  88      |  93      | $100-400  | 대량 챗봇 |
| 3.5 Haiku| [====]   | [====]   | [===]    | [====]   |           |          |
+----------+----------+----------+----------+----------+-----------+----------+
| GPT-4o   |  85      |  70      |  92      |  88      | $225-900  | 고품질   |
| mini     | [===]    | [==]     | [====]   | [===]    |           | 상담     |
+----------+----------+----------+----------+----------+-----------+----------+
```

**shadcn/ui 컴포넌트**: `Table` (`TableHeader`, `TableBody`, `TableRow`, `TableCell`)

**Tailwind**
```
테이블 래퍼: overflow-x-auto rounded-lg border border-border
Table: w-full
TableHeader: bg-muted/50
TableHead: text-xs font-medium text-muted-foreground uppercase
TableCell: py-3 px-4
점수 셀: flex flex-col gap-1
  숫자: text-sm font-semibold + 점수별 색상 클래스
  바: h-1.5 w-16 rounded-full bg-muted -> 내부 rounded-full + 점수별 색상
비용 셀: text-sm font-mono
```

**반응형**
- 모바일: 수평 스크롤 (`overflow-x-auto`) + 고정 첫 열 (모델명)
- md+: 전체 테이블 표시

### 4c. 상세 카드 그리드

각 추천 모델의 상세 정보를 카드로 표시.

```
+----------------------------+  +----------------------------+
| h4: Claude 3.5 Haiku       |  | h4: GPT-4o mini            |
| Anthropic                   |  | OpenAI                     |
|                             |  |                            |
| 강점                        |  | 강점                       |
| + 뛰어난 한국어 처리         |  | + 높은 추론 능력            |
| + 가장 저렴한 가격           |  | + 풍부한 생태계             |
|                             |  |                            |
| 약점                        |  | 약점                       |
| - 복잡한 추론에서 약세       |  | - 상대적으로 높은 가격       |
|                             |  |                            |
| 월 비용 시뮬레이션           |  | 월 비용 시뮬레이션           |
| 저: $100 | 중: $250 | 고: $400| 저: $225 | 중: $550 | 고: $900|
|                             |  |                            |
| 벤치마크                    |  | 벤치마크                    |
| MMLU: 85 | HumanEval: 78   |  | MMLU: 92 | HumanEval: 85  |
+----------------------------+  +----------------------------+
```

**Tailwind**
```
그리드: grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6
카드: rounded-lg border border-border p-5 space-y-4 hover:shadow-md transition-shadow
모델명: text-lg font-semibold
provider: text-sm text-muted-foreground
섹션 제목: text-sm font-medium text-muted-foreground uppercase tracking-wide
강점 항목: flex items-start gap-2 text-sm
  아이콘: text-success size-4 shrink-0 mt-0.5
  텍스트: text-foreground
약점 항목: flex items-start gap-2 text-sm
  아이콘: text-destructive size-4 shrink-0 mt-0.5
비용 행: grid grid-cols-3 gap-2
  각 셀: text-center p-2 rounded-md bg-muted text-sm
  라벨: text-xs text-muted-foreground
  금액: font-mono font-semibold
```

### 4d. 요약 + 근거

```
+------------------------------------------------------------------+
| h3: 분석 요약                                                      |
|                                                                    |
| "한국어 고객 상담 챗봇에는 Claude 3.5 Haiku를 추천합니다.             |
|  가격 대비 성능이 뛰어나며, 특히 다국어 처리에서 강점을 보입니다..."     |
|                                                                    |
| 데이터 출처                                                        |
| - OpenRouter 모델 DB (2026-03-22 동기화)                            |
| - MMLU 벤치마크                                                    |
| - HumanEval 코딩 벤치마크                                           |
| - Tavily 웹 검색: "Korean LLM chatbot comparison 2026"              |
+------------------------------------------------------------------+
```

**Tailwind**
```
섹션: rounded-lg bg-muted/30 p-6 space-y-4
요약 텍스트: text-base leading-relaxed
출처 제목: text-sm font-medium text-muted-foreground uppercase
출처 리스트: list-disc list-inside text-sm text-muted-foreground space-y-1
```

---

## 5. 페이지 상태 전이

| 상태 | 표시 영역 | 설명 |
|------|----------|------|
| idle | 용도 입력 폼만 | 초기 상태, 대시보드 숨김 |
| streaming | 입력 폼(비활성) + 추론 과정 | SSE 수신 중, 실시간 단계 표시 |
| complete | 입력 폼 + 비교 대시보드 | 분석 완료, 전체 결과 표시 |
| error | 입력 폼 + 에러 메시지 | SSE 에러 발생 |

### idle -> streaming
- 분석 시작 클릭 시 전이
- 입력 폼 비활성화, 스트리밍 영역 진입 애니메이션

### streaming -> complete
- SSE `done` 이벤트 수신 시 전이
- 추론 과정 접힘 (토글 OFF), 대시보드 fade-in

### streaming -> error
- SSE `error` 이벤트 또는 연결 끊김 시 전이
- 에러 카드 표시 + "다시 시도" 버튼

---

## 6. 반응형 브레이크포인트별 레이아웃

### 모바일 (< 768px)
```
[Header: Logo + 햄버거]
[API Key (full-width)]
[용도 입력 (full-width)]
[분석 모델 Select (full-width)]
[분석 시작 (full-width)]
---
[추론 과정 (수직 스택)]
---
[Top Pick 카드 (full-width)]
[비교표 (수평 스크롤)]
[상세 카드 (1열)]
[요약]
```

### 태블릿 md (768px+)
```
[Header: Logo + nav + API Key 인라인]
[용도 입력 (max-w-3xl, 중앙)]
[Select + 버튼 수평 배치]
---
[추론 과정]
---
[Top Pick (max-w-3xl)]
[비교표 (전체 너비)]
[상세 카드 (2열 그리드)]
[요약]
```

### 데스크톱 lg (1024px+)
```
[Header 전체 nav]
[용도 입력 (max-w-3xl)]
---
[Top Pick (max-w-4xl)]
[비교표 (max-w-5xl)]
[상세 카드 (2~3열 그리드)]
[요약 (max-w-4xl)]
```

### 대형 데스크톱 xl (1280px+)
```
[상세 카드: 3열 그리드]
[비교표: 여유 있는 셀 패딩]
```

---

## 7. 컨테이너 너비 정리

| 영역 | 최대 너비 | Tailwind |
|------|----------|---------|
| 전체 페이지 | 1280px | `max-w-7xl mx-auto` |
| 입력 폼 | 768px | `max-w-3xl mx-auto` |
| Top Pick | 896px | `max-w-4xl mx-auto` |
| 비교표 | 1024px | `max-w-5xl mx-auto` |
| 상세 카드 그리드 | 1280px | `max-w-7xl mx-auto` |
| 요약 | 896px | `max-w-4xl mx-auto` |
