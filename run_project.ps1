Write-Host "============================================================" -ForegroundColor Green
Write-Host "          🌱 FoodFresh AI - Launching Project..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
Start-Process -FilePath cmd.exe -ArgumentList "/k `".\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload`"" -WindowStyle Normal

Write-Host "[2/2] Starting Vite Frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process -FilePath cmd.exe -ArgumentList "/k `"npm --prefix frontend run dev`"" -WindowStyle Normal

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
Write-Host "FoodFresh AI launched successfully on http://localhost:3000" -ForegroundColor Green
