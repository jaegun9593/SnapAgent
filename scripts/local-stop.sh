#!/bin/bash
# SnapAgent Local Development Stop Script

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping SnapAgent local services...${NC}"

# Stop backend (uvicorn)
pkill -f "uvicorn app.main:app.*--port 8001" 2>/dev/null && \
  echo -e "${GREEN}  Backend stopped${NC}" || \
  echo "  Backend not running"

# Stop frontend (vite)
pkill -f "vite.*--port 5174" 2>/dev/null && \
  echo -e "${GREEN}  Frontend stopped${NC}" || \
  echo "  Frontend not running"

# Stop DB Docker
docker-compose -f "$PROJECT_ROOT/docker-compose.local.yml" down 2>/dev/null && \
  echo -e "${GREEN}  DB stopped${NC}" || \
  echo "  DB not running"

echo -e "${GREEN}All services stopped.${NC}"
