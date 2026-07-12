#!/usr/bin/env bash
# Local dev launcher (no Docker). Uses SQLite so there's zero external setup.
# For the full Postgres + Docker stack, use: docker compose up --build
set -e
cd "$(dirname "$0")"

echo "== Chest X-ray AI Assistant =="
echo "This is a research/educational demo — not a medical device. See README.md."
echo ""

# --- Backend ---
cd backend
if [ ! -d ".venv" ]; then
  echo "[backend] creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "[backend] installing dependencies (first run downloads PyTorch + model weights, a few GB)..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "[backend] starting API on http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# --- Frontend ---
cd frontend
if [ ! -d "node_modules" ]; then
  echo "[frontend] installing dependencies..."
  npm install --silent
fi
echo "[frontend] starting Next.js dev server on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!
cd ..

trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM

echo ""
echo "Backend:  http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both."
wait
