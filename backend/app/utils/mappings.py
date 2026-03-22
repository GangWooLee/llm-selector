"""에이전트 도구에서 공유하는 매핑 상수."""

from decimal import Decimal

BUDGET_TO_MAX_PRICE: dict[str, Decimal | None] = {
    "free": Decimal("0"),
    "low": Decimal("0.001"),
    "medium": Decimal("0.01"),
    "high": Decimal("0.1"),
    "unlimited": None,
}

CONTEXT_NEED_TO_MIN_LENGTH: dict[str, int] = {
    "short": 4096,
    "medium": 32000,
    "long": 128000,
    "very_long": 200000,
}
