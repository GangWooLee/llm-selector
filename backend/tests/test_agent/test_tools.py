"""Agent tools unit tests."""

import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.assess_model_fit import assess_model_fit
from app.agent.tools.compare_pricing import compare_pricing
from app.agent.tools.get_benchmarks import get_benchmarks
from app.agent.tools.get_model_details import get_model_details
from app.agent.tools.search_models import search_models
from app.agent.tools.web_search import web_search
from app.db.models import Model


pytestmark = pytest.mark.asyncio


def _make_model(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "openrouter_id": "openai/gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "description": "Latest GPT-4o",
        "context_length": 128000,
        "max_completion_tokens": 16384,
        "pricing_input": Decimal("0.0025"),
        "pricing_output": Decimal("0.01"),
        "is_free": False,
        "is_active": True,
        "modalities": None,
        "supported_parameters": None,
        "architecture": None,
        "benchmarks": [],
        "tags": [],
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_benchmark(**overrides):
    defaults = {
        "model_id": uuid.uuid4(),
        "benchmark_name": "MMLU",
        "score": Decimal("88.7"),
        "max_score": Decimal("100.0"),
        "source_url": None,
        "measured_at": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ---------- search_models ----------


async def test_search_models_returns_matching_models(
    db_session: AsyncSession, sample_models: list[Model]
):
    results = await search_models(
        db=db_session,
        task_type="coding",
        required_capabilities={"coding": 4},
        context_length_need="medium",
        budget_range="unlimited",
    )

    assert len(results) > 0
    assert all("name" in r for r in results)
    assert all("openrouter_id" in r for r in results)


async def test_search_models_free_budget_returns_only_free(
    db_session: AsyncSession, sample_models: list[Model]
):
    results = await search_models(
        db=db_session,
        task_type="chatbot",
        required_capabilities={},
        context_length_need="short",
        budget_range="free",
    )

    assert len(results) == 1
    assert results[0]["is_free"] is True
    assert results[0]["name"] == "Llama 3.1 8B (Free)"


async def test_search_models_empty_result_for_strict_filters(
    db_session: AsyncSession, sample_models: list[Model]
):
    results = await search_models(
        db=db_session,
        task_type="analysis",
        required_capabilities={},
        context_length_need="very_long",
        budget_range="free",
    )

    assert len(results) == 0


# ---------- compare_pricing ----------


async def test_compare_pricing_calculates_monthly_cost():
    model = _make_model()
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.compare_pricing.queries.get_model_pricing",
        new_callable=AsyncMock,
        return_value=[model],
    ):
        results = await compare_pricing(
            db=mock_db,
            model_ids=[str(model.id)],
            estimated_monthly_input_tokens=1000000,
            estimated_monthly_output_tokens=500000,
        )

    assert len(results) == 1
    result = results[0]
    assert "monthly_cost" in result
    # base = 1M * 0.0025 + 500K * 0.01 = 2500 + 5000 = 7500
    assert result["monthly_cost"]["medium"] == "7500.00"
    assert result["monthly_cost"]["low"] == "3750.00"
    assert result["monthly_cost"]["high"] == "15000.00"


async def test_compare_pricing_empty_for_missing_models():
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.compare_pricing.queries.get_model_pricing",
        new_callable=AsyncMock,
        return_value=[],
    ):
        results = await compare_pricing(
            db=mock_db,
            model_ids=[str(uuid.uuid4())],
            estimated_monthly_input_tokens=100000,
            estimated_monthly_output_tokens=50000,
        )

    assert results == []


# ---------- get_benchmarks ----------


async def test_get_benchmarks_returns_grouped_by_model():
    model_id = uuid.uuid4()
    benchmarks = [
        _make_benchmark(model_id=model_id, benchmark_name="MMLU"),
        _make_benchmark(model_id=model_id, benchmark_name="HumanEval",
                        score=Decimal("90.2")),
    ]
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.get_benchmarks.queries.get_model_benchmarks",
        new_callable=AsyncMock,
        return_value=benchmarks,
    ):
        results = await get_benchmarks(
            db=mock_db,
            model_ids=[str(model_id)],
        )

    model_key = str(model_id)
    assert model_key in results
    assert len(results[model_key]) == 2
    names = {b["benchmark_name"] for b in results[model_key]}
    assert names == {"MMLU", "HumanEval"}


async def test_get_benchmarks_filters_by_category():
    model_id = uuid.uuid4()
    benchmarks = [
        _make_benchmark(model_id=model_id, benchmark_name="MMLU"),
    ]
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.get_benchmarks.queries.get_model_benchmarks",
        new_callable=AsyncMock,
        return_value=benchmarks,
    ):
        results = await get_benchmarks(
            db=mock_db,
            model_ids=[str(model_id)],
            benchmark_categories=["MMLU"],
        )

    model_key = str(model_id)
    assert len(results[model_key]) == 1
    assert results[model_key][0]["benchmark_name"] == "MMLU"


async def test_get_benchmarks_empty_for_no_data():
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.get_benchmarks.queries.get_model_benchmarks",
        new_callable=AsyncMock,
        return_value=[],
    ):
        results = await get_benchmarks(
            db=mock_db,
            model_ids=[str(uuid.uuid4())],
        )

    assert results == {}


# ---------- assess_model_fit ----------


async def test_assess_model_fit_scores_matching_model():
    model = _make_model(
        tags=[
            SimpleNamespace(category="coding", strength_level=4),
            SimpleNamespace(category="reasoning", strength_level=5),
        ],
    )
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.assess_model_fit.queries.get_model_with_details",
        new_callable=AsyncMock,
        return_value=model,
    ):
        result = await assess_model_fit(
            db=mock_db,
            model_id=str(model.id),
            user_requirements={
                "capabilities": {"coding": 4, "reasoning": 3},
                "budget_range": "high",
                "context_length_need": "long",
            },
        )

    assert result["fit_score"] > 0
    assert len(result["strengths"]) > 0
    assert any("coding" in s for s in result["strengths"])
    assert any("reasoning" in s for s in result["strengths"])


async def test_assess_model_fit_returns_zero_for_missing_model():
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.assess_model_fit.queries.get_model_with_details",
        new_callable=AsyncMock,
        return_value=None,
    ):
        result = await assess_model_fit(
            db=mock_db,
            model_id=str(uuid.uuid4()),
            user_requirements={"capabilities": {"coding": 5}},
        )

    assert result["fit_score"] == 0
    assert "모델을 찾을 수 없습니다" in result["weaknesses"]


# ---------- web_search ----------


async def test_web_search_returns_results_on_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"title": "GPT-5 Review", "url": "https://example.com", "content": "Great model"},
        ]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False

    with patch("app.agent.tools.web_search.settings") as mock_settings, \
         patch("app.agent.tools.web_search.httpx.AsyncClient", return_value=mock_client):
        mock_settings.TAVILY_API_KEY = "test-key"
        results = await web_search("latest GPT models")

    assert len(results) == 1
    assert results[0]["title"] == "GPT-5 Review"
    assert results[0]["url"] == "https://example.com"


async def test_web_search_returns_empty_without_api_key():
    with patch("app.agent.tools.web_search.settings") as mock_settings:
        mock_settings.TAVILY_API_KEY = ""
        results = await web_search("test query")

    assert results == []


# ---------- get_model_details ----------


async def test_get_model_details_returns_full_profile():
    model = _make_model(
        benchmarks=[
            SimpleNamespace(benchmark_name="MMLU", score=Decimal("88.7"),
                            max_score=Decimal("100.0")),
            SimpleNamespace(benchmark_name="HumanEval", score=Decimal("90.2"),
                            max_score=Decimal("100.0")),
        ],
        tags=[
            SimpleNamespace(category="coding", strength_level=4),
            SimpleNamespace(category="reasoning", strength_level=5),
        ],
    )
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.get_model_details.queries.get_model_with_details",
        new_callable=AsyncMock,
        return_value=model,
    ):
        result = await get_model_details(
            db=mock_db,
            model_id=str(model.id),
        )

    assert result is not None
    assert result["name"] == "GPT-4o"
    assert result["provider"] == "openai"
    assert len(result["benchmarks"]) == 2
    assert len(result["tags"]) == 2
    assert result["context_length"] == 128000


async def test_get_model_details_returns_none_for_missing():
    mock_db = AsyncMock()

    with patch(
        "app.agent.tools.get_model_details.queries.get_model_with_details",
        new_callable=AsyncMock,
        return_value=None,
    ):
        result = await get_model_details(
            db=mock_db,
            model_id=str(uuid.uuid4()),
        )

    assert result is None
