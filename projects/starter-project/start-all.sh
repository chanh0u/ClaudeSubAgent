#!/usr/bin/env bash
# Starts backend (3003), proxy (3001) and frontend (5173) together.
# Ctrl+C stops all of them. Requires deps installed in python/, server/, web/.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pids=()
cleanup() {
  echo ""
  echo "Stopping services..."
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

echo "Starting backend (FastAPI :3003)..."
( cd "$ROOT/python" && uvicorn src.main:app --host 0.0.0.0 --port 3003 --reload ) &
pids+=($!)

echo "Starting proxy (Node :3001)..."
( cd "$ROOT/server" && node server.js ) &
pids+=($!)

echo "Starting frontend (Vite :5173)..."
( cd "$ROOT/web" && npm run dev ) &
pids+=($!)

echo ""
echo "All services started:"
echo "  Backend:  http://localhost:3003  (docs: /docs)"
echo "  Proxy:    http://localhost:3001"
echo "  Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop."
wait
