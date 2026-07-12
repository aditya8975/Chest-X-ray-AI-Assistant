@echo off
setlocal
cd /d "%~dp0"

echo == Chest X-ray AI Assistant ==
echo This is a research/educational demo — not a medical device. See README.md.
echo.

cd backend
if not exist ".venv" (
  echo [backend] creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [backend] installing dependencies (first run downloads PyTorch + model weights, a few GB)...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo [backend] starting API on http://localhost:8000 ...
start "backend" cmd /k uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd ..

cd frontend
if not exist "node_modules" (
  echo [frontend] installing dependencies...
  call npm install
)
echo [frontend] starting Next.js dev server on http://localhost:3000 ...
start "frontend" cmd /k npm run dev
cd ..

echo.
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo Two new windows were opened for backend and frontend. Close them to stop.
