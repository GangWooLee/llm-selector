"""ModelAdvisorAgent — Pydantic AI 기반 모델 선택 에이전트."""

import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.settings import ModelSettings
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.schemas import ComparisonReport
from app.agent.tools import search_models as _search_models
from app.agent.tools import compare_pricing as _compare_pricing
from app.agent.tools import get_benchmarks as _get_benchmarks
from app.agent.tools import assess_model_fit as _assess_model_fit
from app.agent.tools import web_search as _web_search
from app.agent.tools import get_model_details as _get_model_details

logger = logging.getLogger(__name__)

AGENT_TIMEOUT_SECONDS = 120


@dataclass
class AdvisorDeps:
    """에이전트 실행 시 RunContext에 전달되는 의존성."""

    db: AsyncSession
    analysis_model: str


def _build_model(api_key: str, model_name: str) -> OpenAIModel:
    """OpenRouter Provider로 모델 생성. model_profile 자동 매핑."""
    provider = OpenRouterProvider(api_key=api_key)
    return OpenAIModel(model_name, provider=provider)


advisor_agent = Agent(
    model=None,
    instructions=SYSTEM_PROMPT,
    output_type=ComparisonReport,
    deps_type=AdvisorDeps,
    name="model_advisor",
    model_settings=ModelSettings(
        timeout=AGENT_TIMEOUT_SECONDS,
        temperature=0.1,
    ),
    defer_model_check=True,
    retries=5,
)


# --- 도구 등록 (RunContext를 통해 db 세션 접근) ---


@advisor_agent.tool
async def search_models(
    ctx: RunContext[AdvisorDeps],
    task_type: str,
    required_capabilities: dict[str, int],
    context_length_need: str,
    budget_range: str,
) -> list[dict]:
    """요구사항 기반 모델 DB 검색. task_type: chatbot/code_generation/analysis/creative/translation. context_length_need: short/medium/long/very_long. budget_range: free/low/medium/high/unlimited."""
    return await _search_models(ctx.deps.db, task_type, required_capabilities, context_length_need, budget_range)


@advisor_agent.tool
async def compare_pricing(
    ctx: RunContext[AdvisorDeps],
    model_ids: list[str],
    estimated_monthly_input_tokens: int,
    estimated_monthly_output_tokens: int,
) -> dict:
    """후보 모델들의 가격 비교 + 월 비용 시뮬레이션. model_ids: 비교할 모델 UUID 문자열 목록."""
    return await _compare_pricing(ctx.deps.db, model_ids, estimated_monthly_input_tokens, estimated_monthly_output_tokens)


@advisor_agent.tool
async def get_benchmarks(
    ctx: RunContext[AdvisorDeps],
    model_ids: list[str],
    benchmark_categories: list[str],
) -> dict:
    """모델별 벤치마크 점수 조회. benchmark_categories: coding/reasoning/multilingual/math/creative."""
    return await _get_benchmarks(ctx.deps.db, model_ids, benchmark_categories)


@advisor_agent.tool
async def assess_model_fit(
    ctx: RunContext[AdvisorDeps],
    model_id: str,
    user_requirements: dict,
) -> dict:
    """특정 모델의 용도 적합도 평가. 0-100 점수 + 강점/약점 반환."""
    return await _assess_model_fit(ctx.deps.db, model_id, user_requirements)


@advisor_agent.tool
async def web_search(
    ctx: RunContext[AdvisorDeps],
    search_query: str,
) -> list[dict]:
    """최신 모델 정보 웹 검색 (Tavily API). DB에 없는 최신 정보 보충용."""
    return await _web_search(search_query)


@advisor_agent.tool
async def get_model_details(
    ctx: RunContext[AdvisorDeps],
    model_id: str,
) -> dict:
    """모델 전체 상세 프로필 조회 (가격, 벤치마크, 태그 포함)."""
    return await _get_model_details(ctx.deps.db, model_id)


# --- 에이전트 실행 ---


async def run_advisor(
    user_input: str,
    api_key: str,
    analysis_model: str,
    db: AsyncSession,
) -> AsyncGenerator[dict[str, Any], None]:
    """에이전트를 실행하고 SSE 이벤트를 yield하는 async generator."""
    deps = AdvisorDeps(db=db, analysis_model=analysis_model)
    model = _build_model(api_key, analysis_model)

    try:
        async with advisor_agent.iter(
            user_input,
            deps=deps,
            model=model,
        ) as agent_run:
            async for node in agent_run:
                if advisor_agent.is_call_tools_node(node):
                    for part in node.model_response.parts:
                        if isinstance(part, ToolCallPart):
                            yield {
                                "event": "tool_call",
                                "data": {
                                    "tool": part.tool_name,
                                    "params": part.args if isinstance(part.args, dict) else {},
                                },
                            }

                elif advisor_agent.is_model_request_node(node):
                    for part in node.request.parts:
                        if isinstance(part, ToolReturnPart):
                            content = part.content
                            summary = str(content)[:200] if not isinstance(content, str) else content[:200]
                            yield {
                                "event": "tool_result",
                                "data": {"tool": part.tool_name, "summary": summary},
                            }

                    yield {"event": "thinking", "data": {"message": "분석 중..."}}

            result = agent_run.result
            if result is not None:
                yield {"event": "report", "data": result.output.model_dump()}

        yield {"event": "done", "data": {}}

    except Exception:
        logger.exception("Agent execution failed")
        yield {
            "event": "error",
            "data": {"message": "에이전트 실행 중 오류가 발생했습니다."},
        }
