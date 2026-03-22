# 에이전트 워크플로우 설계

## Agent: ModelAdvisorAgent

Pydantic AI 기반 에이전트. 사용자의 용도를 분석하고, 도구를 **자율적으로** 선택·호출하여 최적 모델을 추천한다.

---

## 시스템 프롬프트

```
당신은 LLM 모델 선택 전문가입니다.

핵심 원칙:
- 당신이 알고 있는 모델 정보로 답하지 마세요.
- 반드시 제공된 도구를 사용하여 최신 데이터를 조회하세요.
- 모든 추천에는 구체적인 데이터 근거를 제시하세요.
- 사용자의 용도에 맞지 않는 모델은 왜 맞지 않는지도 설명하세요.

추론 과정:
1. 사용자의 용도를 분석하여 필요한 역량, 예산, 성능 요구를 파악하세요.
2. search_models로 조건에 맞는 후보 모델을 조회하세요.
3. compare_pricing으로 비용을 비교하고, get_benchmarks로 성능을 비교하세요.
4. 필요하면 web_search로 최신 정보를 보충하세요.
5. assess_model_fit으로 각 후보의 적합도를 평가하세요.
6. 최종적으로 종합 비교 리포트를 생성하세요.
```

---

## 에이전트 도구 (Tools) 정의

### Tool 1: `search_models`
- **목적**: 요구사항 기반 모델 DB 검색
- **입력**:
  - `task_type`: str — chatbot, code_generation, analysis, creative, translation 등
  - `required_capabilities`: dict — {coding: 0-5, multilingual: 0-5, ...}
  - `context_length_need`: str — short/medium/long/very_long
  - `budget_range`: str — free/low/medium/high/unlimited
- **동작**: PostgreSQL 쿼리 — 모달리티, 컨텍스트 길이, 가격대, 지원 기능 필터링
- **출력**: 조건에 맞는 모델 목록 (ID, 이름, 제공사, 가격, 컨텍스트 길이, 지원 기능)

### Tool 2: `compare_pricing`
- **목적**: 후보 모델들의 가격 상세 비교
- **입력**:
  - `model_ids`: list[str] — 비교할 모델 ID 목록
  - `estimated_monthly_input_tokens`: int — 월 예상 입력 토큰
  - `estimated_monthly_output_tokens`: int — 월 예상 출력 토큰
- **동작**: 각 모델의 토큰당 가격 조회 → 월 예상 비용 계산
- **출력**: 모델별 월 비용 시뮬레이션 (저/중/고 사용량 3단계)

### Tool 3: `get_benchmarks`
- **목적**: 특정 모델들의 벤치마크 데이터 조회
- **입력**:
  - `model_ids`: list[str] — 대상 모델 ID 목록
  - `benchmark_categories`: list[str] — coding, reasoning, multilingual, math, creative 등
- **동작**: model_benchmarks 테이블에서 관련 벤치마크 점수 조회
- **출력**: 모델별 벤치마크 점수표

### Tool 4: `assess_model_fit`
- **목적**: 특정 모델이 사용자 용도에 얼마나 적합한지 평가
- **입력**:
  - `model_id`: str — 평가 대상 모델
  - `user_requirements`: dict — 구조화된 요구사항
- **동작**: 모델의 특성(tags, benchmarks, capabilities)과 요구사항 매칭 → 적합도 점수 계산
- **출력**:
  - `fit_score`: int (0-100)
  - `strengths`: list[str] — 이 용도에서의 강점
  - `weaknesses`: list[str] — 이 용도에서의 약점

### Tool 5: `web_search`
- **목적**: DB에 없는 최신 정보 보충
- **입력**:
  - `search_query`: str — 검색 쿼리
- **동작**: Tavily 또는 DuckDuckGo API로 웹 검색
- **출력**: 관련 검색 결과 요약 (URL + 핵심 내용)
- **사용 시점**: 신규 모델 정보, 최근 리뷰, 성능 비교 글 등 보충 필요 시

### Tool 6: `get_model_details`
- **목적**: 특정 모델의 전체 상세 정보 조회
- **입력**:
  - `model_id`: str — 대상 모델 ID
- **동작**: models + benchmarks + tags 조인 쿼리
- **출력**: 모델 전체 프로필 (가격, 성능, 특성, 벤치마크 일체)

---

## 에이전트 실행 흐름 (예시)

```
사용자: "한국어 고객 상담 챗봇을 만들고 싶어. 월 100만 건 정도 처리해야 해."

Agent 추론 시작:
  "한국어 + 챗봇 + 대량 처리 → 다국어 능력, 빠른 응답, 저렴한 가격이 중요"

→ search_models(
    task_type="chatbot",
    required_capabilities={"multilingual": 4, "instruction_following": 4},
    context_length_need="medium",
    budget_range="low"
  )
  결과: [gpt-4o-mini, claude-3.5-haiku, gemini-2.0-flash, ...] 12개 모델

→ compare_pricing(
    model_ids=["gpt-4o-mini", "claude-3.5-haiku", "gemini-2.0-flash", ...],
    estimated_monthly_input_tokens=500_000_000,
    estimated_monthly_output_tokens=200_000_000
  )
  결과: gpt-4o-mini: $225/월, claude-3.5-haiku: $100/월, ...

→ get_benchmarks(
    model_ids=[상위 6개],
    benchmark_categories=["multilingual", "instruction_following"]
  )
  결과: 벤치마크 점수표

→ web_search("best LLM for Korean chatbot 2026 performance comparison")
  결과: 최신 한국어 LLM 성능 비교 리뷰 정보

→ assess_model_fit("claude-3.5-haiku", user_requirements=...)
→ assess_model_fit("gpt-4o-mini", user_requirements=...)
→ assess_model_fit("gemini-2.0-flash", user_requirements=...)
  ...각 후보 모델별 적합도 평가

Agent 최종 리포트 생성:
  ComparisonReport (구조화된 비교 리포트 출력)
```

---

## 에이전트 출력 스키마 (Pydantic 모델)

```python
from pydantic import BaseModel

class MonthlyCost(BaseModel):
    low: float      # 월 예상 비용 (적은 사용)
    medium: float   # 월 예상 비용 (보통 사용)
    high: float     # 월 예상 비용 (많은 사용)

class TopPick(BaseModel):
    model_id: str
    model_name: str
    reason: str     # 왜 이 모델이 최적인지

class ModelRecommendation(BaseModel):
    model_id: str
    model_name: str
    provider: str
    overall_score: int          # 0-100
    price_score: int            # 0-100
    performance_score: int      # 0-100
    fit_score: int              # 0-100 (용도 적합도)
    strengths: list[str]        # 이 상황에서의 강점
    weaknesses: list[str]       # 이 상황에서의 약점
    monthly_cost_estimate: MonthlyCost
    best_for: str               # "이런 경우에 최적"

class AgentStep(BaseModel):
    step_number: int
    action: str                 # "search_models", "compare_pricing" 등
    reasoning: str              # 왜 이 도구를 호출했는지
    result_summary: str         # 도구 실행 결과 요약

class ComparisonReport(BaseModel):
    top_recommendation: TopPick
    recommendations: list[ModelRecommendation]
    summary: str                # 전체 비교 요약
    data_sources: list[str]     # 근거 출처 목록
    agent_reasoning: list[AgentStep]  # 에이전트 추론 과정 (선택적 표시용)
```

---

## SSE 스트리밍 프로토콜

에이전트 추론 과정을 프론트엔드에 실시간으로 전달하기 위한 SSE 이벤트 타입:

```
event: thinking
data: {"message": "한국어 챗봇 용도를 분석합니다..."}

event: tool_call
data: {"tool": "search_models", "reasoning": "다국어 지원 + 저가 모델 검색", "params": {...}}

event: tool_result
data: {"tool": "search_models", "summary": "12개 후보 모델 발견", "count": 12}

event: tool_call
data: {"tool": "compare_pricing", "reasoning": "월 100만 건 기준 비용 비교", "params": {...}}

event: tool_result
data: {"tool": "compare_pricing", "summary": "가격 비교 완료, 최저 $100/월 ~ 최고 $2,400/월"}

event: report
data: {ComparisonReport JSON}

event: done
data: {}
```

---

## 투명성 UI

- **기본**: 결과(ComparisonReport)만 표시
- **"추론 과정 보기" 토글**: AgentStep 목록을 펼쳐서 에이전트가 어떤 도구를 왜 호출했고, 어떤 결과를 받았는지 확인 가능
- 각 스텝에 아이콘 표시: 🔍 검색, 💰 가격 비교, 📊 벤치마크, 🌐 웹 검색, ✅ 적합도 평가
