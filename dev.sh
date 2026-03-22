#!/bin/bash
# 로컬 개발: 백엔드 + 프론트엔드 동시 실행
# 사용법: ./dev.sh

trap 'kill 0' EXIT

echo "🚀 Starting backend (localhost:8000)..."
(cd backend && DATABASE_URL="" .venv/bin/uvicorn app.main:app --reload --port 8000) &

echo "🚀 Starting frontend (localhost:3000)..."
(cd frontend && NEXT_PUBLIC_API_URL="http://localhost:8000" npm run dev) &

wait
