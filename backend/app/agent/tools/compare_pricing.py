"""compare_pricing — 모델 가격 비교 + 월 비용 시뮬레이션."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries

SCENARIO_MULTIPLIERS: dict[str, Decimal] = {
    "low": Decimal("0.5"),
    "medium": Decimal("1.0"),
    "high": Decimal("2.0"),
}


def _compare_from_cache(
    models_cache: list[dict],
    model_ids: list[str],
    input_tokens: Decimal,
    output_tokens: Decimal,
) -> list[dict]:
    """models_cache에서 가격 비교 결과 반환 (No-DB 모드)."""
    lookup = {m["openrouter_id"]: m for m in models_cache}

    results = []
    for mid in model_ids:
        m = lookup.get(mid)
        if not m:
            continue

        price_in = m.get("pricing_input") or Decimal("0")
        price_out = m.get("pricing_output") or Decimal("0")
        # Decimal 변환 보장
        price_in = Decimal(str(price_in))
        price_out = Decimal(str(price_out))
        base_cost = input_tokens * price_in + output_tokens * price_out

        monthly = {
            scenario: str((base_cost * mult).quantize(Decimal("0.01")))
            for scenario, mult in SCENARIO_MULTIPLIERS.items()
        }

        results.append({
            "model_id": m["openrouter_id"],
            "openrouter_id": m["openrouter_id"],
            "name": m.get("name", ""),
            "pricing_input": str(price_in),
            "pricing_output": str(price_out),
            "is_free": m.get("is_free"),
            "monthly_cost": monthly,
        })

    return results


async def compare_pricing(
    db: AsyncSession | None,
    models_cache: list[dict] | None,
    model_ids: list[str],
    estimated_monthly_input_tokens: int,
    estimated_monthly_output_tokens: int,
) -> list[dict]:
    """후보 모델들의 가격 비교 + 월 비용 시뮬레이션.

    Args:
        db: 데이터베이스 세션. None이면 No-DB 모드.
        models_cache: OpenRouter API 캐시 데이터. No-DB 모드에서 사용.
        model_ids: 모델 UUID 또는 openrouter_id 목록 (둘 다 지원).
        estimated_monthly_input_tokens: 월 예상 입력 토큰 수.
        estimated_monthly_output_tokens: 월 예상 출력 토큰 수.

    Returns:
        모델별 월 비용 시뮬레이션 (저/중/고 3단계).
    """
    input_tokens = Decimal(str(estimated_monthly_input_tokens))
    output_tokens = Decimal(str(estimated_monthly_output_tokens))

    if db is None:
        return _compare_from_cache(
            models_cache or [], model_ids, input_tokens, output_tokens,
        )

    # UUID와 openrouter_id를 분리
    uuid_ids = []
    openrouter_ids = []
    for mid in model_ids:
        try:
            uuid_ids.append(uuid.UUID(mid))
        except ValueError:
            openrouter_ids.append(mid)

    models = []
    if uuid_ids:
        models.extend(await queries.get_model_pricing(db, uuid_ids))
    if openrouter_ids:
        models.extend(await queries.get_models_by_openrouter_ids(db, openrouter_ids))

    results = []
    for m in models:
        price_in = m.pricing_input or Decimal("0")
        price_out = m.pricing_output or Decimal("0")
        base_cost = input_tokens * price_in + output_tokens * price_out

        monthly = {
            scenario: str((base_cost * mult).quantize(Decimal("0.01")))
            for scenario, mult in SCENARIO_MULTIPLIERS.items()
        }

        results.append({
            "model_id": str(m.id),
            "openrouter_id": m.openrouter_id,
            "name": m.name,
            "pricing_input": str(price_in),
            "pricing_output": str(price_out),
            "is_free": m.is_free,
            "monthly_cost": monthly,
        })

    return results
