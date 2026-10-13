#!/usr/bin/env bash
# ==============================================================================
#  भू DRISTI — AI Super-Resolution Platform
#  Universal Project Runner (Backend + Frontend)
#  Supports: macOS, Linux, Windows (WSL / Git Bash)
# ==============================================================================

set -e

# --- Color definitions ---
if [ -t 1 ]; then
  BOLD="\033[1m"
  GREEN="\033[0;32m"
  BLUE="\033[0;34m"
  CYAN="\033[0;36m"
  YELLOW="\033[1;33m"
  RED="\033[0;31m"
  RESET="\033[0m"
else
  BOLD=""
  GREEN=""
  BLUE=""
  CYAN=""
  YELLOW=""
  RED=""
  RESET=""
fi

log_info()    { echo -e "${BLUE}[INFO]${RESET} $1"; }
log_success() { echo -e "${GREEN}[OK]${RESET} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET} $1"; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $1" >&2; }

# --- Resolve repository root ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/frontend" ] && [ -d "$SCRIPT_DIR/backend" ]; then
  ROOT_DIR="$SCRIPT_DIR"
elif [ -d "$SCRIPT_DIR/../frontend" ] && [ -d "$SCRIPT_DIR/../backend" ]; then
  ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  log_error "Could not locate project root containing both 'frontend' and 'backend' directories."
  exit 1
fi

BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOGS_DIR="$ROOT_DIR/logs"
mkdir -p "$LOGS_DIR"

BACKEND_PID=""
FRONTEND_PID=""

# --- Cleanup handler ---
cleanup() {
  local exit_code=$?
  echo ""
  log_info "Initiating shutdown sequence for भू DRISTI..."

  if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    log_info "Stopping backend (PID: $BACKEND_PID)..."
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    log_info "Stopping frontend (PID: $FRONTEND_PID)..."
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  # Wait briefly for graceful shutdown
  sleep 1

  # Force kill if still lingering
  if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill -9 "$BACKEND_PID" 2>/dev/null || true
  fi
  if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill -9 "$FRONTEND_PID" 2>/dev/null || true
  fi

  # Extra cleanup for Windows / WSL port listeners if needed
  if command -v taskkill.exe >/dev/null 2>&1; then
    # Kill any dangling node or uvicorn processes on 3000 / 8000
    if command -v netstat.exe >/dev/null 2>&1; then
      for port in 3000 8000; do
        pids=$(netstat.exe -ano 2>/dev/null | grep ":$port " | awk '{print $5}' | tr -d '\r' | sort -u || true)
        for p in $pids; do
          if [ -n "$p" ] && [ "$p" -ne 0 ] 2>/dev/null; then
            taskkill.exe /F /PID "$p" >/dev/null 2>&1 || true
          fi
        done
      done
    fi
  fi

  log_success "All services stopped."
  exit "$exit_code"
}

trap cleanup INT TERM EXIT

echo -e "${BOLD}${CYAN}"
echo "======================================================================"
echo "          भू DRISTI — AI Super-Resolution Platform Runner"
echo "======================================================================"
echo -e "${RESET}"
log_info "Project root: $ROOT_DIR"

# --- 1. Python & Backend Environment Detection ---
log_info "Checking Python backend environment..."
PYTHON_BIN=""

if [ -f "$BACKEND_DIR/.venv/Scripts/python.exe" ]; then
  PYTHON_BIN="$BACKEND_DIR/.venv/Scripts/python.exe"
elif [ -f "$BACKEND_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$BACKEND_DIR/.venv/bin/python"
elif [ -f "$BACKEND_DIR/venv/Scripts/python.exe" ]; then
  PYTHON_BIN="$BACKEND_DIR/venv/Scripts/python.exe"
elif [ -f "$BACKEND_DIR/venv/bin/python" ]; then
  PYTHON_BIN="$BACKEND_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
elif command -v py >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v py)"
else
  log_error "Python was not found. Please install Python 3.10+ (recommended 3.11/3.12)."
  exit 1
fi

log_success "Using Python: $("$PYTHON_BIN" --version 2>&1 | tr -d '\r')"

# Verify / install backend dependencies if needed
if ! "$PYTHON_BIN" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  log_warn "FastAPI / Uvicorn not found in selected Python environment. Installing dependencies..."
  if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    "$PYTHON_BIN" -m pip install -r "$BACKEND_DIR/requirements.txt"
  else
    log_error "backend/requirements.txt missing."
    exit 1
  fi
fi

# --- 2. Node & Frontend Environment Detection ---
log_info "Checking Node.js & Frontend environment..."
NPM_CMD=""

if command -v npm >/dev/null 2>&1; then
  NPM_CMD="npm"
elif command -v npm.cmd >/dev/null 2>&1; then
  NPM_CMD="npm.cmd"
elif command -v cmd.exe >/dev/null 2>&1; then
  NPM_CMD="cmd.exe /c npm"
elif [ -x "/mnt/c/WINDOWS/system32/cmd.exe" ]; then
  NPM_CMD="/mnt/c/WINDOWS/system32/cmd.exe /c npm"
else
  log_error "npm was not found. Please install Node.js 18+ (20 LTS recommended)."
  exit 1
fi

log_success "Using npm: $($NPM_CMD -v 2>&1 | tr -d '\r')"

# Ensure frontend .env.local exists
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
  log_info "Creating frontend/.env.local configured for backend at http://localhost:8000..."
  if [ -f "$FRONTEND_DIR/.env.local.example" ]; then
    cp "$FRONTEND_DIR/.env.local.example" "$FRONTEND_DIR/.env.local"
  else
    echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > "$FRONTEND_DIR/.env.local"
  fi
fi

# Ensure frontend dependencies are installed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  log_warn "frontend/node_modules not found. Running npm install..."
  (cd "$FRONTEND_DIR" && $NPM_CMD install)
fi

# --- 3. Port conflict check ---
is_port_in_use() {
  local port="$1"
  "$PYTHON_BIN" -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', $port)); s.close()" >/dev/null 2>&1
}

if is_port_in_use 8000; then
  log_warn "Port 8000 is already in use. Checking existing service..."
fi

if is_port_in_use 3000; then
  log_warn "Port 3000 is already in use. Checking existing service..."
fi

# --- 4. Launch Backend ---
echo ""
log_info "Starting FastAPI Backend on port 8000..."
(
  cd "$BACKEND_DIR"
  "$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) > "$LOGS_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
log_success "Backend started in background (PID: $BACKEND_PID)"

# --- 5. Launch Frontend ---
log_info "Starting Next.js Frontend on port 3000..."
(
  cd "$FRONTEND_DIR"
  $NPM_CMD run dev
) > "$LOGS_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
log_success "Frontend started in background (PID: $FRONTEND_PID)"

# --- 6. Readiness Verification ---
echo ""
log_info "Waiting for services to become ready..."

wait_for_endpoint() {
  local name="$1"
  local url="$2"
  local max_seconds="$3"
  local pid="$4"
  local count=0

  while [ "$count" -lt "$max_seconds" ]; do
    # Check if process died
    if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
      log_error "$name process exited unexpectedly! Check logs: $LOGS_DIR"
      return 1
    fi

    if "$PYTHON_BIN" -c "import urllib.request; urllib.request.urlopen('$url', timeout=2)" >/dev/null 2>&1; then
      log_success "$name is ready at $url!"
      return 0
    fi

    sleep 1
    count=$((count + 1))
    echo -n "."
  done

  echo ""
  log_error "Timed out waiting for $name after ${max_seconds}s."
  return 1
}

echo -n "Waiting for Backend (http://localhost:8000/docs)"
wait_for_endpoint "Backend API" "http://localhost:8000/docs" 30 "$BACKEND_PID"

echo -n "Waiting for Frontend (http://localhost:3000)"
wait_for_endpoint "Frontend Web App" "http://localhost:3000" 60 "$FRONTEND_PID"

# --- 7. Operational Status Banner ---
echo ""
echo -e "${BOLD}${GREEN}======================================================================"
echo "          भू DRISTI IS UP AND RUNNING SUCCESSFULLY!       "
echo "======================================================================${RESET}"
echo -e "${BOLD}  🌐 Frontend UI      : ${CYAN}http://localhost:3000${RESET}"
echo -e "${BOLD}  🛠️  Backend API Docs : ${CYAN}http://localhost:8000/docs${RESET}"
echo -e "${BOLD}  📡 Backend Base URL : ${CYAN}http://localhost:8000${RESET}"
echo "----------------------------------------------------------------------"
echo -e "  Backend PID  : ${BOLD}$BACKEND_PID${RESET} (Logs: logs/backend.log)"
echo -e "  Frontend PID : ${BOLD}$FRONTEND_PID${RESET} (Logs: logs/frontend.log)"
echo "----------------------------------------------------------------------"
echo -e "${YELLOW}  Press [CTRL+C] at any time to gracefully stop all services.${RESET}"
echo -e "${BOLD}${GREEN}======================================================================${RESET}"
echo ""

# Stream recent logs or wait for termination
wait "$BACKEND_PID" "$FRONTEND_PID"
