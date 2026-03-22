"""Advisor (run_advisor) unit tests — LLM calls are mocked."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent.advisor import run_advisor


pytestmark = pytest.mark.asyncio


@asynccontextmanager
async def _mock_agent_iter(events, result_output=None):
    """Simulate advisor_agent.iter() async context manager."""
    class MockRun:
        def __init__(self):
            if result_output is not None:
                self.result = MagicMock()
                self.result.output.model_dump.return_value = result_output
            else:
                self.result = None

        async def __aiter__(self):
            for ev in events:
                yield ev

    yield MockRun()


async def test_run_advisor_yields_done_event():
    with patch("app.agent.advisor.advisor_agent") as mock_agent, \
         patch("app.agent.advisor._build_model"):
        mock_agent.iter = lambda *a, **kw: _mock_agent_iter(events=[])
        mock_agent.is_call_tools_node.return_value = False
        mock_agent.is_model_request_node.return_value = False

        events = []
        async for event in run_advisor(
            user_input="test",
            api_key="test-key",
            analysis_model="test/model",
            db=AsyncMock(),
        ):
            events.append(event)

    assert events[-1]["event"] == "done"
    assert events[-1]["data"] == {}


async def test_run_advisor_yields_report_when_result_exists():
    report_data = {
        "top_recommendation": {"model_id": "1", "model_name": "GPT-4o", "reason": "Best"},
        "recommendations": [],
        "summary": "Test summary",
        "data_sources": ["db"],
        "agent_reasoning": [],
    }

    with patch("app.agent.advisor.advisor_agent") as mock_agent, \
         patch("app.agent.advisor._build_model"):
        mock_agent.iter = lambda *a, **kw: _mock_agent_iter(
            events=[], result_output=report_data
        )
        mock_agent.is_call_tools_node.return_value = False
        mock_agent.is_model_request_node.return_value = False

        events = []
        async for event in run_advisor(
            user_input="recommend a model",
            api_key="test-key",
            analysis_model="test/model",
            db=AsyncMock(),
        ):
            events.append(event)

    report_events = [e for e in events if e["event"] == "report"]
    assert len(report_events) == 1
    assert report_events[0]["data"]["summary"] == "Test summary"


async def test_run_advisor_yields_error_on_exception():
    with patch("app.agent.advisor.advisor_agent") as mock_agent, \
         patch("app.agent.advisor._build_model"):
        mock_agent.iter.side_effect = RuntimeError("LLM connection failed")

        events = []
        async for event in run_advisor(
            user_input="test",
            api_key="bad-key",
            analysis_model="test/model",
            db=AsyncMock(),
        ):
            events.append(event)

    assert len(events) == 1
    assert events[0]["event"] == "error"
    assert "오류" in events[0]["data"]["message"]
