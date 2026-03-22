"""에이전트 출력 스키마 — ComparisonReport 및 관련 모델."""

from pydantic import BaseModel, Field


class MonthlyCost(BaseModel):
    """월간 예상 비용 (저/중/고 사용량 시나리오)."""

    low: float = Field(..., description="월 저사용량 예상 비용 (USD)")
    medium: float = Field(..., description="월 중간사용량 예상 비용 (USD)")
    high: float = Field(..., description="월 고사용량 예상 비용 (USD)")


class TopPick(BaseModel):
    """최우선 추천 모델."""

    model_id: str = Field(..., description="모델의 UUID 문자열 (도구에서 반환된 id)")
    model_name: str = Field(..., description="모델 공식 이름 (예: 'Gemini 3 Flash')")
    reason: str = Field(..., description="이 모델을 최우선 추천하는 이유 (2-3문장)")


class ModelRecommendation(BaseModel):
    """개별 모델 추천 상세."""

    model_id: str = Field(..., description="모델의 UUID 문자열")
    model_name: str = Field(..., description="모델 공식 이름")
    provider: str = Field(..., description="제공사 (google, anthropic, openai 등)")
    overall_score: int = Field(..., ge=0, le=100, description="종합 점수 0-100")
    price_score: int = Field(..., ge=0, le=100, description="가격 점수 0-100 (저렴할수록 높음)")
    performance_score: int = Field(..., ge=0, le=100, description="성능 점수 0-100")
    fit_score: int = Field(..., ge=0, le=100, description="용도 적합도 점수 0-100")
    strengths: list[str] = Field(..., description="이 용도에서의 강점 목록 (3-5개)")
    weaknesses: list[str] = Field(..., description="이 용도에서의 약점 목록 (1-3개)")
    monthly_cost_estimate: MonthlyCost = Field(..., description="월간 예상 비용")
    best_for: str = Field(..., description="이 모델이 최적인 시나리오 (1문장)")


class AgentStep(BaseModel):
    """에이전트 추론 단계."""

    step_number: int = Field(..., description="단계 번호 (1부터)")
    action: str = Field(..., description="수행한 도구명 (search_models, compare_pricing 등)")
    reasoning: str = Field(..., description="이 도구를 호출한 이유 (1-2문장)")
    result_summary: str = Field(..., description="도구 실행 결과 요약 (1-2문장)")


class ComparisonReport(BaseModel):
    """최종 모델 비교 리포트. 반드시 도구로 조회한 데이터만 사용."""

    top_recommendation: TopPick = Field(..., description="최우선 추천 모델 정보")
    recommendations: list[ModelRecommendation] = Field(
        ..., min_length=1, max_length=5, description="추천 모델 목록 (1-5개, 점수 순)"
    )
    summary: str = Field(..., description="전체 비교 요약 (3-5문장)")
    data_sources: list[str] = Field(
        ..., description="데이터 출처 목록 (예: 'DB 검색', '가격 비교', '벤치마크 조회')"
    )
    agent_reasoning: list[AgentStep] = Field(
        ..., description="에이전트 추론 과정 (도구 호출 순서대로)"
    )
