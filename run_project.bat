@echo off
title FoodFresh AI - Launcher
echo ============================================================
echo           🌱 FoodFresh AI - Launching Project...
echo ============================================================
echo.
echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FoodFresh AI - FastAPI Backend (:8000)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Vite Frontend on http://localhost:3000 ...
start "FoodFresh AI - React Frontend (:3000)" cmd /k "npm --prefix frontend run dev"

echo.
echo ============================================================
echo  FoodFresh AI is now running!
echo  Backend Docs: http://127.0.0.1:8000/docs
echo  Frontend App: http://localhost:3000
echo ============================================================
timeout /t 3 >nul
start http://localhost:3000
