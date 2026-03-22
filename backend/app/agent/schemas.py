from pydantic import BaseModel


class MonthlyCost(BaseModel):
    low: float
    medium: float
    high: float


class TopPick(BaseModel):
    model_id: str
    model_name: str
    reason: str


class ModelRecommendation(BaseModel):
    model_id: str
    model_name: str
    provider: str
    overall_score: int
    price_score: int
    performance_score: int
    fit_score: int
    strengths: list[str]
    weaknesses: list[str]
    monthly_cost_estimate: MonthlyCost
    best_for: str


class AgentStep(BaseModel):
    step_number: int
    action: str
    reasoning: str
    result_summary: str


class ComparisonReport(BaseModel):
    top_recommendation: TopPick
    recommendations: list[ModelRecommendation]
    summary: str
    data_sources: list[str]
    agent_reasoning: list[AgentStep]
