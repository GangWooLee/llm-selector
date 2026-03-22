"""ModelAdvisorAgent — Pydantic AI 기반 모델 선택 에이전트."""

import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.schemas import ComparisonReport

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AGENT_TIMEOUT_SECONDS = 120


@dataclass
class AdvisorDeps:
    """에이전트 실행 시 RunContext에 전달되는 의존성."""

    db: AsyncSession
    api_key: str
    analysis_model: str


def _build_model(api_key: str, model_name: str) -> OpenAIModel:
    """OpenRouter 백엔드로 OpenAIModel 생성."""
    provider = OpenAIProvider(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )
    return OpenAIModel(model_name, provider=provider)


advisor_agent = Agent(
    # model은 run 시점에 동적으로 설정
    model=None,
    instructions=SYSTEM_PROMPT,
    output_type=ComparisonReport,
    deps_type=AdvisorDeps,
    name="model_advisor",
    model_settings=ModelSettings(timeout=AGENT_TIMEOUT_SECONDS),
    defer_model_check=True,
)


async def run_advisor(
    user_input: str,
    api_key: str,
    analysis_model: str,
    db: AsyncSession,
) -> AsyncGenerator[dict[str, Any], None]:
    """에이전트를 실행하고 SSE 이벤트를 yield하는 async generator.

    이벤트 타입: thinking, tool_call, tool_result, report, done, error
    """
    deps = AdvisorDeps(db=db, api_key=api_key, analysis_model=analysis_model)
    model = _build_model(api_key, analysis_model)

    try:
        async with advisor_agent.iter(
            user_input,
            deps=deps,
            model=model,
        ) as agent_run:
            async for node in agent_run:
                if advisor_agent.is_call_tools_node(node):
                    # 도구 호출 이벤트 추출
                    for part in node.model_response.parts:
                        if isinstance(part, ToolCallPart):
                            yield {
                                "event": "tool_call",
                                "data": {
                                    "tool": part.tool_name,
                                    "params": part.args
                                    if isinstance(part.args, dict)
                                    else {},
                                },
                            }

                elif advisor_agent.is_model_request_node(node):
                    # 이전 도구 실행 결과 이벤트 추출
                    for part in node.request.parts:
                        if isinstance(part, ToolReturnPart):
                            content = part.content
                            summary = (
                                str(content)[:200]
                                if not isinstance(content, str)
                                else content[:200]
                            )
                            yield {
                                "event": "tool_result",
                                "data": {
                                    "tool": part.tool_name,
                                    "summary": summary,
                                },
                            }

                    yield {
                        "event": "thinking",
                        "data": {"message": "분석 중..."},
                    }

            # 최종 결과
            result = agent_run.result
            if result is not None:
                yield {
                    "event": "report",
                    "data": result.output.model_dump(),
                }

        yield {"event": "done", "data": {}}

    except Exception:
        logger.exception("Agent execution failed")
        yield {
            "event": "error",
            "data": {"message": "에이전트 실행 중 오류가 발생했습니다."},
        }
