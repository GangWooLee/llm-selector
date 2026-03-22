from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
REQUEST_TIMEOUT_SECONDS = 30


async def fetch_all_models() -> list[dict[str, Any]]:
    """OpenRouter API에서 전체 모델 목록을 가져와 DB 스키마에 맞게 매핑."""
    raw_models = await _fetch_raw_models()
    return [_map_model(m) for m in raw_models]


async def _fetch_raw_models() -> list[dict[str, Any]]:
    """OpenRouter /api/v1/models 호출."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(OPENROUTER_MODELS_URL)
        response.raise_for_status()
        data = response.json()
    return data.get("data", [])


def _to_decimal(value: str | None) -> Decimal | None:
    """문자열 가격을 Decimal로 변환. 누락/잘못된 값은 None."""
    if value is None:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def _map_model(raw: dict[str, Any]) -> dict[str, Any]:
    """OpenRouter API 응답 1건을 models 테이블 컬럼에 매핑."""
    openrouter_id = raw.get("id", "")
    pricing = raw.get("pricing") or {}
    architecture = raw.get("architecture") or {}
    top_provider = raw.get("top_provider") or {}

    prompt_price = pricing.get("prompt")
    is_free = prompt_price == "0"

    # architecture.modality → modalities (입력+출력 모달리티 목록)
    input_modalities = architecture.get("input_modalities")
    output_modalities = architecture.get("output_modalities")
    modalities = None
    if input_modalities or output_modalities:
        modalities = {
            "input": input_modalities or [],
            "output": output_modalities or [],
        }

    return {
        "openrouter_id": openrouter_id,
        "name": raw.get("name", openrouter_id),
        "provider": openrouter_id.split("/")[0] if "/" in openrouter_id else openrouter_id,
        "description": raw.get("description"),
        "context_length": raw.get("context_length"),
        "pricing_input": _to_decimal(prompt_price),
        "pricing_output": _to_decimal(pricing.get("completion")),
        "pricing_image": _to_decimal(pricing.get("image")),
        "pricing_request": _to_decimal(pricing.get("request")),
        "modalities": modalities,
        "supported_parameters": raw.get("supported_parameters"),
        "max_completion_tokens": top_provider.get("max_completion_tokens"),
        "architecture": architecture or None,
        "is_free": is_free,
    }
