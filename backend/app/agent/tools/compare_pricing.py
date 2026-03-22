"""compare_pricing — 모델 가격 비교 + 월 비용 시뮬레이션."""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries

SCENARIO_MULTIPLIERS: dict[str, Decimal] = {
    "low": Decimal("0.5"),
    "medium": Decimal("1.0"),
    "high": Decimal("2.0"),
}


async def compare_pricing(
    db: AsyncSession,
    model_ids: list[str],
    estimated_monthly_input_tokens: int,
    estimated_monthly_output_tokens: int,
) -> list[dict]:
    """후보 모델들의 가격 비교 + 월 비용 시뮬레이션.

    Args:
        db: 데이터베이스 세션.
        model_ids: 모델 UUID 또는 openrouter_id 목록 (둘 다 지원).
        estimated_monthly_input_tokens: 월 예상 입력 토큰 수.
        estimated_monthly_output_tokens: 월 예상 출력 토큰 수.

    Returns:
        모델별 월 비용 시뮬레이션 (저/중/고 3단계).
    """
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

    input_tokens = Decimal(str(estimated_monthly_input_tokens))
    output_tokens = Decimal(str(estimated_monthly_output_tokens))

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
