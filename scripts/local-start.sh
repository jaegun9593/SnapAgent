#!/bin/bash
# SnapAgent Local Development Startup Script
# DB → Docker, Backend → uvicorn, Frontend → vite dev server

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== SnapAgent Local Development ===${NC}"

# 1. Start DB (Docker)
echo -e "${YELLOW}[1/3] Starting PostgreSQL (pgvector)...${NC}"
docker-compose -f "$PROJECT_ROOT/docker-compose.local.yml" up -d

# Wait for DB to be healthy
echo -e "${YELLOW}      Waiting for DB to be ready...${NC}"
until docker exec snapagent-db-local pg_isready -U snapuser > /dev/null 2>&1; do
  sleep 1
done
echo -e "${GREEN}      DB is ready (localhost:5433)${NC}"

# 2. Start Backend
echo -e "${YELLOW}[2/3] Starting Backend...${NC}"
cd "$PROJECT_ROOT/backend"

# Create virtual env if not exists
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}      Creating virtual environment...${NC}"
  python3 -m venv venv
fi

# Activate and install deps
source venv/bin/activate
pip install -q -r requirements.txt

# Create uploads directory
mkdir -p "$PROJECT_ROOT/backend/uploads"

# Start backend in background
UPLOAD_DIR="$PROJECT_ROOT/backend/uploads" \
DATABASE_URL="postgresql+asyncpg://snapuser:snappassword@localhost:5433/snapagentdb" \
ENVIRONMENT=local \
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
echo -e "${GREEN}      Backend started (localhost:8001) [PID: $BACKEND_PID]${NC}"

# 3. Start Frontend
echo -e "${YELLOW}[3/3] Starting Frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# Install deps if needed
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}      Installing npm dependencies...${NC}"
  npm install
fi

# Start frontend in background
VITE_API_BASE_URL=http://localhost:8001/api/v1 \
VITE_ENVIRONMENT=local \
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}      Frontend started (localhost:5174) [PID: $FRONTEND_PID]${NC}"

echo ""
echo -e "${BLUE}=== All services running ===${NC}"
echo -e "  DB:       localhost:5433"
echo -e "  Backend:  http://localhost:8001 (docs: http://localhost:8001/docs)"
echo -e "  Frontend: http://localhost:5174"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Trap Ctrl+C to stop everything
cleanup() {
  echo ""
  echo -e "${YELLOW}Stopping services...${NC}"
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  docker-compose -f "$PROJECT_ROOT/docker-compose.local.yml" down
  echo -e "${GREEN}All services stopped.${NC}"
  exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
