"""벤치마크 데이터 동기화 — HuggingFace OpenEvals 리더보드에서 수집."""

import logging
import uuid
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Model, ModelBenchmark

logger = logging.getLogger(__name__)

OPENEVAL_API = "https://datasets-server.huggingface.co/rows"
DATASET = "OpenEvals/leaderboard-data"
PAGE_SIZE = 100

BENCHMARK_COLUMNS = {
    "mmluPro_score": ("MMLU_Pro", 100.0),
    "gpqa_score": ("GPQA", 100.0),
    "gsm8k_score": ("GSM8K", 100.0),
    "sweVerified_score": ("SWE_Verified", 100.0),
    "swePro_score": ("SWE_Pro", 100.0),
    "aime2026_score": ("AIME_2026", 100.0),
    "hle_score": ("HLE", 100.0),
    "terminalBench_score": ("TerminalBench", 100.0),
}

SOURCE_URL = "https://huggingface.co/datasets/OpenEvals/leaderboard-data"


async def sync_benchmarks(db: AsyncSession) -> dict[str, Any]:
    """HuggingFace OpenEvals에서 벤치마크 데이터를 가져와 DB에 적재."""
    leaderboard_rows = await _fetch_leaderboard()
    db_models = await _get_all_active_models(db)

    model_map = _build_model_map(db_models)
    added, updated, skipped = 0, 0, 0

    for row in leaderboard_rows:
        hf_name = row.get("model_name", "")
        matched_model = _match_model(hf_name, model_map)
        if not matched_model:
            skipped += 1
            continue

        for col, (bench_name, max_score) in BENCHMARK_COLUMNS.items():
            score = row.get(col)
            if score is None:
                continue

            a, u = await _upsert_benchmark(
                db, matched_model.id, bench_name, float(score), max_score
            )
            added += a
            updated += u

    await db.commit()

    return {
        "status": "success",
        "benchmarks_added": added,
        "benchmarks_updated": updated,
        "models_skipped": skipped,
        "models_matched": len(leaderboard_rows) - skipped,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }


async def _fetch_leaderboard() -> list[dict]:
    """OpenEvals 리더보드 데이터 전체 fetch (페이지네이션)."""
    all_rows: list[dict] = []
    offset = 0

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            resp = await client.get(
                OPENEVAL_API,
                params={
                    "dataset": DATASET,
                    "config": "default",
                    "split": "train",
                    "offset": offset,
                    "length": PAGE_SIZE,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            rows = [r["row"] for r in data.get("rows", [])]
            if not rows:
                break
            all_rows.extend(rows)
            offset += PAGE_SIZE

    logger.info("Fetched %d leaderboard entries", len(all_rows))
    return all_rows


async def _get_all_active_models(db: AsyncSession) -> list[Model]:
    """DB에서 활성 모델 전체 조회."""
    result = await db.execute(
        select(Model).where(Model.is_active.is_(True))
    )
    return list(result.scalars().all())


def _build_model_map(models: list[Model]) -> dict[str, Model]:
    """다양한 키로 모델을 검색할 수 있는 맵 구축."""
    model_map: dict[str, Model] = {}
    for m in models:
        model_map[m.openrouter_id.lower()] = m
        model_map[m.name.lower()] = m
        # provider/model-name 패턴
        parts = m.openrouter_id.split("/")
        if len(parts) == 2:
            model_map[parts[1].lower()] = m
    return model_map


def _match_model(hf_name: str, model_map: dict[str, Model]) -> Model | None:
    """HuggingFace 모델명을 DB 모델과 매칭."""
    key = hf_name.lower().strip()

    # 정확 매칭
    if key in model_map:
        return model_map[key]

    # provider/name 형식 분해 매칭
    if "/" in key:
        _, name_part = key.rsplit("/", 1)
        if name_part in model_map:
            return model_map[name_part]

    # 유사도 매칭 (0.7 이상)
    best_match = None
    best_ratio = 0.0
    for map_key, model in model_map.items():
        ratio = SequenceMatcher(None, key, map_key).ratio()
        if ratio > best_ratio and ratio >= 0.7:
            best_ratio = ratio
            best_match = model

    return best_match


async def _upsert_benchmark(
    db: AsyncSession,
    model_id: uuid.UUID,
    benchmark_name: str,
    score: float,
    max_score: float,
) -> tuple[int, int]:
    """벤치마크 upsert. (added, updated) 반환."""
    query = select(ModelBenchmark).where(
        ModelBenchmark.model_id == model_id,
        ModelBenchmark.benchmark_name == benchmark_name,
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.score = score
        existing.max_score = max_score
        existing.source_url = SOURCE_URL
        existing.measured_at = date.today()
        await db.flush()
        return (0, 1)

    benchmark = ModelBenchmark(
        model_id=model_id,
        benchmark_name=benchmark_name,
        score=score,
        max_score=max_score,
        source_url=SOURCE_URL,
        measured_at=date.today(),
    )
    db.add(benchmark)
    await db.flush()
    return (1, 0)
