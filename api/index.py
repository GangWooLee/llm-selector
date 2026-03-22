"""Vercel Python Serverless Function — FastAPI 앱 마운트."""

import sys
from pathlib import Path

# backend/ 디렉토리를 Python 경로에 추가
backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app  # noqa: E402, F401

# Vercel은 이 파일에서 `app` ASGI 앱을 자동 감지하여 서빙
