#!/usr/bin/env bash
# WeNexus 本地开发环境一键启动脚本
#
# 用法：
#   ./scripts/dev.sh           # 启动全部（数据库 + 前端 + Python 后端）
#   ./scripts/dev.sh frontend  # 仅启动数据库 + 前端
#   ./scripts/dev.sh stop      # 停止所有服务
#
# 数据库支持（自动检测，优先级从高到低）：
#   1. Homebrew PostgreSQL@16 / PostgreSQL + Redis
#   2. Docker / docker-compose
#
# 日志文件输出到 scripts/logs/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_ROOT/scripts/logs"
FRONTEND_DIR="$REPO_ROOT/frontend"
PYTHON_DIR="$REPO_ROOT/backend/python"

PID_FILE_FRONTEND="$LOG_DIR/frontend.pid"
PID_FILE_PYTHON="$LOG_DIR/python.pid"
LOG_FRONTEND="$LOG_DIR/frontend.log"
LOG_PYTHON="$LOG_DIR/python.log"

MODE="${1:-all}"

mkdir -p "$LOG_DIR"

# ── 颜色 ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; RESET='\033[0m'

log()  { echo -e "${BLUE}[dev]${RESET} $*"; }
ok()   { echo -e "${GREEN}[dev]${RESET} $*"; }
warn() { echo -e "${YELLOW}[dev]${RESET} $*"; }
err()  { echo -e "${RED}[dev]${RESET} $*"; }

# ── 工具检测 ──────────────────────────────────────────────────────────────────
need() {
  if ! command -v "$1" &>/dev/null; then
    err "缺少依赖：$1。请先安装后重试。"
    exit 1
  fi
}

# ── 优雅停止已有进程 ──────────────────────────────────────────────────────────
stop_pid_file() {
  local pidfile="$1" name="$2"
  if [[ -f "$pidfile" ]]; then
    local pid
    pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      warn "停止已有 $name 进程 (PID $pid)..."
      kill -TERM "$pid" 2>/dev/null || true
      local i=0
      while kill -0 "$pid" 2>/dev/null && (( i < 10 )); do
        sleep 0.5; (( i++ ))
      done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile"
  fi
}

stop_port() {
  local port="$1"
  local pids
  pids=$(lsof -ti :"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    warn "端口 $port 已被占用，正在释放..."
    echo "$pids" | xargs kill -TERM 2>/dev/null || true
    sleep 1
    echo "$pids" | xargs kill -9 2>/dev/null || true
  fi
}

stop_all() {
  log "停止所有服务..."
  stop_pid_file "$PID_FILE_FRONTEND" "前端"
  stop_pid_file "$PID_FILE_PYTHON"   "Python 后端"
  stop_port 3000
  stop_port 8000
  ok "所有应用进程已停止（数据库服务保持运行）。"
}

# ── stop 子命令 ───────────────────────────────────────────────────────────────
if [[ "$MODE" == "stop" ]]; then
  stop_all
  exit 0
fi

# ── 前置检查 ──────────────────────────────────────────────────────────────────
need pnpm
if [[ "$MODE" == "all" ]]; then
  need uv
fi

# ── 检测并启动数据库 ──────────────────────────────────────────────────────────
# 优先 Homebrew 本地服务，其次 Docker
PSQL=""
for p in psql /usr/local/opt/postgresql@16/bin/psql /opt/homebrew/opt/postgresql@16/bin/psql \
          /usr/local/opt/postgresql@15/bin/psql /opt/homebrew/opt/postgresql@15/bin/psql; do
  if command -v "$p" &>/dev/null || [[ -x "$p" ]]; then
    PSQL="$p"; break
  fi
done

if [[ -n "$PSQL" ]] && command -v brew &>/dev/null; then
  # ── Homebrew PostgreSQL ──────────────────────────────────────────────────
  log "使用 Homebrew PostgreSQL..."

  # 确保 PostgreSQL 服务在运行
  if ! brew services list | grep -E "postgresql" | grep -q "started"; then
    log "启动 PostgreSQL 服务..."
    brew services start postgresql@16 2>/dev/null || brew services start postgresql 2>/dev/null || true
    sleep 2
  else
    ok "PostgreSQL 已在运行"
  fi

  # 确保 Redis 服务在运行
  if command -v redis-cli &>/dev/null; then
    if ! brew services list | grep "redis" | grep -q "started"; then
      log "启动 Redis 服务..."
      brew services start redis 2>/dev/null || true
    else
      ok "Redis 已在运行"
    fi
  fi

  # 等待 PostgreSQL 接受连接
  log "等待 PostgreSQL 就绪..."
  local_i=0
  until "$PSQL" -U "$(whoami)" postgres -c "SELECT 1" &>/dev/null 2>&1; do
    (( local_i++ ))
    if (( local_i > 20 )); then
      err "PostgreSQL 启动超时。"
      exit 1
    fi
    sleep 1
  done
  ok "PostgreSQL 就绪"

  # 确保 wenexus 用户和数据库存在
  "$PSQL" -U "$(whoami)" postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='wenexus'" \
    | grep -q 1 || "$PSQL" -U "$(whoami)" postgres \
      -c "CREATE USER wenexus WITH SUPERUSER PASSWORD 'wenexus_dev_pwd';" 2>/dev/null || true

  "$PSQL" -U "$(whoami)" postgres -tc "SELECT 1 FROM pg_database WHERE datname='wenexus_dev'" \
    | grep -q 1 || "$PSQL" -U "$(whoami)" postgres \
      -c "CREATE DATABASE wenexus_dev OWNER wenexus;" 2>/dev/null || true

else
  # ── Docker fallback ──────────────────────────────────────────────────────
  need docker

  # 检测 compose 命令
  if docker compose version &>/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
  elif command -v docker-compose &>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
  else
    err "找不到 docker compose / docker-compose，且本机没有 Homebrew PostgreSQL。"
    err "请安装其中之一：brew install postgresql@16 redis"
    exit 1
  fi

  log "使用 Docker Compose 启动数据库..."
  $DOCKER_COMPOSE -f "$REPO_ROOT/docker-compose.yml" up -d

  log "等待 PostgreSQL 就绪..."
  local_i=0
  until docker exec wenexus-postgres pg_isready -U wenexus -d wenexus_dev &>/dev/null; do
    (( local_i++ ))
    if (( local_i > 30 )); then
      err "PostgreSQL 启动超时，请检查 Docker 状态。"
      exit 1
    fi
    sleep 1
  done
  ok "PostgreSQL 就绪"
fi

# ── 停止前端/后端已有实例 ─────────────────────────────────────────────────────
log "检查已有进程..."
stop_pid_file "$PID_FILE_FRONTEND" "前端"
stop_pid_file "$PID_FILE_PYTHON"   "Python 后端"
stop_port 3000
[[ "$MODE" == "all" ]] && stop_port 8000

# ── 配置环境变量检查 ──────────────────────────────────────────────────────────
ENV_FILE="$FRONTEND_DIR/apps/web/.env.development"
if [[ ! -f "$ENV_FILE" ]]; then
  warn ".env.development 不存在，从示例文件创建..."
  cp "$FRONTEND_DIR/apps/web/.env.example" "$ENV_FILE"
  warn "请编辑 $ENV_FILE，至少填写 AUTH_SECRET："
  warn "  openssl rand -base64 32"
fi

# ── 安装前端依赖 ──────────────────────────────────────────────────────────────
log "检查前端依赖..."
if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  log "安装前端依赖（首次安装较慢）..."
  pnpm --dir "$FRONTEND_DIR" install
fi

# ── 启动前端 ──────────────────────────────────────────────────────────────────
log "启动前端开发服务器..."
(
  cd "$FRONTEND_DIR"
  pnpm --filter @wenexus/web dev
) > "$LOG_FRONTEND" 2>&1 &
echo $! > "$PID_FILE_FRONTEND"
ok "前端已在后台启动 (PID $(cat "$PID_FILE_FRONTEND"))，日志：$LOG_FRONTEND"

# ── 启动 Python 后端（可选）─────────────────────────────────────────────────
if [[ "$MODE" == "all" ]]; then
  log "安装 Python 依赖..."
  (cd "$PYTHON_DIR" && uv sync --dev) 2>/dev/null || true

  log "启动 Python 后端..."
  (
    cd "$PYTHON_DIR"
    uv run uvicorn src.wenexus.main:app --reload --host 0.0.0.0 --port 8000
  ) > "$LOG_PYTHON" 2>&1 &
  echo $! > "$LOG_DIR/python.pid"
  ok "Python 后端已在后台启动 (PID $(cat "$LOG_DIR/python.pid"))，日志：$LOG_PYTHON"
fi

# ── 等待前端就绪并打印访问地址 ───────────────────────────────────────────────
log "等待前端就绪（首次编译约需 10-30s）..."
local_j=0
until curl -sf http://localhost:3000 &>/dev/null; do
  (( local_j++ ))
  if (( local_j > 90 )); then
    warn "前端尚未就绪，可能还在编译中，请查看日志：$LOG_FRONTEND"
    break
  fi
  sleep 1
done

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}  WeNexus 本地环境已启动${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  前端        →  ${CYAN}http://localhost:3000${RESET}"
[[ "$MODE" == "all" ]] && echo -e "  Python API  →  ${CYAN}http://localhost:8000/docs${RESET}"
echo -e "  PostgreSQL  →  ${CYAN}localhost:5432${RESET}"
echo -e "  Redis       →  ${CYAN}localhost:6379${RESET}"
echo ""
echo -e "  停止所有服务：${YELLOW}./scripts/dev.sh stop${RESET}"
echo -e "  前端日志：    ${YELLOW}tail -f $LOG_FRONTEND${RESET}"
[[ "$MODE" == "all" ]] && echo -e "  后端日志：    ${YELLOW}tail -f $LOG_PYTHON${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
