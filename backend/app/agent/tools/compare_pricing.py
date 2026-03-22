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
    """후보 모델들의 가격 상세 비교 및 월 비용 시뮬레이션.

    Args:
        db: 데이터베이스 세션.
        model_ids: 비교할 모델 UUID 목록.
        estimated_monthly_input_tokens: 월 예상 입력 토큰 수.
        estimated_monthly_output_tokens: 월 예상 출력 토큰 수.

    Returns:
        모델별 월 비용 시뮬레이션 (저/중/고 사용량 3단계).
    """
    uuids = [uuid.UUID(mid) for mid in model_ids]
    models = await queries.get_model_pricing(db, uuids)

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
            "name": m.name,
            "pricing_input": str(price_in),
            "pricing_output": str(price_out),
            "is_free": m.is_free,
            "monthly_cost": monthly,
        })

    return results
