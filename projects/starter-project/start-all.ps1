# Starts backend (3003), proxy (3001) and frontend (5173) in separate windows.
# Usage:  ./start-all.ps1
# Requires: Python deps installed in python/, npm deps installed in server/ and web/.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "Starting backend (FastAPI :3003)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$root\python'; uvicorn src.main:app --host 0.0.0.0 --port 3003 --reload"

Write-Host "Starting proxy (Node :3001)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$root\server'; node server.js"

Write-Host "Starting frontend (Vite :5173)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$root\web'; npm run dev"

Write-Host ""
Write-Host "All services launching in separate windows:"
Write-Host "  Backend:  http://localhost:3003  (docs: /docs)"
Write-Host "  Proxy:    http://localhost:3001"
Write-Host "  Frontend: http://localhost:5173"
