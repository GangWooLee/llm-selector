"""SSE (Server-Sent Events) 포맷팅 유틸리티."""

import json


def format_sse(event: str, data: dict) -> str:
    """SSE 이벤트를 표준 형식으로 포맷팅."""
    json_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {json_data}\n\n"
