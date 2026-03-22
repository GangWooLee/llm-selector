import httpx

from app.config import settings

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def web_search(search_query: str) -> list[dict]:
    """DB에 없는 최신 모델 정보를 웹에서 검색.

    Args:
        search_query: 검색 쿼리 문자열.

    Returns:
        관련 검색 결과 목록 (URL + 핵심 내용).
    """
    if not settings.TAVILY_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": search_query,
                "max_results": 5,
            },
        )
        response.raise_for_status()
        data = response.json()

    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        }
        for r in data.get("results", [])
    ]
