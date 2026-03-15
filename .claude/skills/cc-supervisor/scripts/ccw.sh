#!/usr/bin/env bash
# Claude Code Worker 管理脚本
#
# 用法：
#   ccw start <name> [--dir path] [--prompt "task"]  # 启动 worker
#   ccw stop <name>                                   # 停止 worker
#   ccw stop-all                                      # 停止所有 worker
#   ccw send <name> <message>                         # 发送指令
#   ccw output <name> [--lines N]                     # 读取输出
#   ccw list                                          # 列出所有 worker
#   ccw status <name>                                 # 查看 worker 状态

set -euo pipefail

# ── 常量 ─────────────────────────────────────────────────────────────────────
CCW_BASE="/tmp/cc-workers"
CCW_SOCKETS="$CCW_BASE/sockets"
CCW_STATE="$CCW_BASE/state"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 颜色 ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; DIM='\033[2m'; RESET='\033[0m'

log()  { echo -e "${BLUE}[ccw]${RESET} $*"; }
ok()   { echo -e "${GREEN}[ccw]${RESET} $*"; }
warn() { echo -e "${YELLOW}[ccw]${RESET} $*"; }
err()  { echo -e "${RED}[ccw]${RESET} $*" >&2; }

# ── 工具函数 ──────────────────────────────────────────────────────────────────
ensure_dirs() {
  mkdir -p "$CCW_SOCKETS" "$CCW_STATE"
}

validate_name() {
  local name="$1"
  if [[ -z "$name" ]]; then
    err "Worker name cannot be empty"
    exit 1
  fi
  if [[ ! "$name" =~ ^[a-zA-Z0-9][-a-zA-Z0-9]*$ ]]; then
    err "Invalid name '$name': use alphanumeric and hyphens, start with letter/digit"
    exit 1
  fi
  if (( ${#name} > 30 )); then
    err "Name too long (max 30 chars): '$name'"
    exit 1
  fi
}

socket_path() { echo "$CCW_SOCKETS/$1.sock"; }
state_path()  { echo "$CCW_STATE/$1.json"; }

session_exists() {
  local sock
  sock=$(socket_path "$1")
  tmux -S "$sock" list-sessions 2>/dev/null | grep -q "^$1:" 2>/dev/null
}

write_state() {
  local name="$1" dir="$2" status="$3"
  local sock
  sock=$(socket_path "$name")
  cat > "$(state_path "$name")" <<EOF
{
  "name": "$name",
  "dir": "$dir",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "$status",
  "last_command": null,
  "last_command_at": null,
  "socket": "$sock"
}
EOF
}

update_state_field() {
  local name="$1" field="$2" value="$3"
  local state_file
  state_file=$(state_path "$name")
  [[ -f "$state_file" ]] || return 1
  # macOS sed 用 -i ''，Linux sed 用 -i
  local sed_inplace=(-i '')
  if [[ "$(uname)" != "Darwin" ]]; then sed_inplace=(-i); fi
  if [[ "$value" == "null" ]]; then
    sed "${sed_inplace[@]}" "s|\"$field\": .*|\"$field\": null,|" "$state_file"
  else
    # 转义 sed 分隔符
    local escaped_value="${value//|/\\|}"
    sed "${sed_inplace[@]}" "s|\"$field\": .*|\"$field\": \"$escaped_value\",|" "$state_file"
  fi
}

detect_status() {
  local name="$1"
  local sock
  sock=$(socket_path "$name")
  if ! session_exists "$name"; then
    echo "stopped"
    return
  fi
  local output
  output=$(tmux -S "$sock" capture-pane -p -J -t "$name":0 -S -10 2>/dev/null || echo "")
  # Claude Code 空闲时最后几行会包含提示符或等待输入的标志
  # 常见模式：❯、>、空行后光标、"Claude Code" 标题行
  if echo "$output" | grep -qE '❯|^\$|^>'; then
    echo "idle"
  elif echo "$output" | grep -qi "initializing\|loading\|starting"; then
    echo "starting"
  elif echo "$output" | grep -q "^(base).*%$"; then
    # 回到 shell 提示符 = Claude Code 已退出
    echo "stopped"
  else
    echo "busy"
  fi
}

tmux_send() {
  local sock="$1" session="$2" text="$3"
  tmux -S "$sock" send-keys -t "$session":0 -l -- "$text" && \
    sleep 0.1 && \
    tmux -S "$sock" send-keys -t "$session":0 Enter
}

wait_for_ready() {
  local name="$1" max_wait="${2:-60}"
  local sock
  sock=$(socket_path "$name")
  local elapsed=0
  log "Waiting for $name to initialize..."
  while (( elapsed < max_wait )); do
    local output
    output=$(tmux -S "$sock" capture-pane -p -J -t "$name":0 -S -10 2>/dev/null || echo "")
    if echo "$output" | grep -q "❯"; then
      return 0
    fi
    sleep 2
    (( elapsed += 2 ))
  done
  warn "Timeout waiting for $name (${max_wait}s). May still be starting."
  return 1
}

# ── 子命令：start ─────────────────────────────────────────────────────────────
cmd_start() {
  local name="" dir="" prompt=""

  # 解析参数
  name="${1:-}"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dir)   dir="$2"; shift 2 ;;
      --prompt) prompt="$2"; shift 2 ;;
      *)       err "Unknown option: $1"; exit 1 ;;
    esac
  done

  [[ -z "$name" ]] && { err "Usage: ccw start <name> [--dir path] [--prompt \"task\"]"; exit 1; }
  validate_name "$name"
  dir="${dir:-$(pwd)}"

  if [[ ! -d "$dir" ]]; then
    err "Directory not found: $dir"
    exit 1
  fi

  ensure_dirs
  local sock
  sock=$(socket_path "$name")

  # 清理已有同名 session
  if session_exists "$name"; then
    warn "Worker '$name' already exists, stopping first..."
    tmux -S "$sock" kill-session -t "$name" 2>/dev/null || true
    sleep 0.5
  fi

  # 创建 tmux session
  tmux -S "$sock" new -d -s "$name" -n claude
  write_state "$name" "$dir" "starting"

  # cd 到工作目录
  tmux_send "$sock" "$name" "cd \"$dir\""
  sleep 0.3

  # 清除嵌套检测环境变量，加载 nvm
  tmux_send "$sock" "$name" "unset CLAUDECODE && export NVM_DIR=\"\$HOME/.nvm\" && [ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\" && nvm use 20"
  sleep 1

  # 启动 Claude Code
  local claude_cmd="claude --dangerously-skip-permissions"
  tmux_send "$sock" "$name" "$claude_cmd"

  # 等待 Claude Code 就绪
  if wait_for_ready "$name" 60; then
    update_state_field "$name" "status" "idle"
    ok "Worker '$name' started"
  else
    update_state_field "$name" "status" "starting"
    warn "Worker '$name' launched but not yet ready"
  fi

  # 发送初始任务
  if [[ -n "$prompt" ]]; then
    sleep 1
    tmux_send "$sock" "$name" "$prompt"
    update_state_field "$name" "status" "busy"
    update_state_field "$name" "last_command" "$prompt"
    update_state_field "$name" "last_command_at" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    log "Initial prompt sent to '$name'"
  fi

  echo ""
  echo "  Name:      $name"
  echo "  Directory: $dir"
  echo "  Socket:    $sock"
  echo "  Attach:    tmux -S '$sock' attach -t '$name'"
}

# ── 子命令：stop ──────────────────────────────────────────────────────────────
cmd_stop() {
  local name="${1:-}"
  [[ -z "$name" ]] && { err "Usage: ccw stop <name>"; exit 1; }
  validate_name "$name"

  local sock
  sock=$(socket_path "$name")

  if ! session_exists "$name"; then
    warn "Worker '$name' not found (already stopped?)"
    rm -f "$(state_path "$name")" "$sock"
    return
  fi

  # 优雅退出：先发 /exit
  log "Stopping '$name'..."
  tmux_send "$sock" "$name" "/exit" 2>/dev/null || true
  sleep 3

  # 强制 kill session
  tmux -S "$sock" kill-session -t "$name" 2>/dev/null || true

  # 清理
  rm -f "$(state_path "$name")" "$sock"
  ok "Worker '$name' stopped"
}

# ── 子命令：stop-all ──────────────────────────────────────────────────────────
cmd_stop_all() {
  ensure_dirs
  local count=0
  for state_file in "$CCW_STATE"/*.json; do
    [[ -f "$state_file" ]] || continue
    local name
    name=$(basename "$state_file" .json)
    cmd_stop "$name"
    (( count++ ))
  done
  if (( count == 0 )); then
    log "No workers to stop"
  else
    ok "Stopped $count worker(s)"
  fi
}

# ── 子命令：send ──────────────────────────────────────────────────────────────
cmd_send() {
  local name="${1:-}"
  shift || true
  local message="$*"

  [[ -z "$name" ]] && { err "Usage: ccw send <name> <message>"; exit 1; }
  [[ -z "$message" ]] && { err "Message cannot be empty"; exit 1; }
  validate_name "$name"

  local sock
  sock=$(socket_path "$name")

  if ! session_exists "$name"; then
    err "Worker '$name' not found. Start it first: ccw start $name"
    exit 1
  fi

  tmux_send "$sock" "$name" "$message"
  update_state_field "$name" "status" "busy"
  update_state_field "$name" "last_command" "$message"
  update_state_field "$name" "last_command_at" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  ok "Sent to '$name': $message"
}

# ── 子命令：output ────────────────────────────────────────────────────────────
cmd_output() {
  local name="" lines=200

  name="${1:-}"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lines) lines="$2"; shift 2 ;;
      *)       shift ;;
    esac
  done

  [[ -z "$name" ]] && { err "Usage: ccw output <name> [--lines N]"; exit 1; }
  validate_name "$name"

  local sock
  sock=$(socket_path "$name")

  if ! session_exists "$name"; then
    err "Worker '$name' not found"
    exit 1
  fi

  tmux -S "$sock" capture-pane -p -J -t "$name":0 -S -"$lines"
}

# ── 子命令：list ──────────────────────────────────────────────────────────────
cmd_list() {
  ensure_dirs

  local has_workers=false
  printf "${DIM}%-15s %-10s %-45s %s${RESET}\n" "NAME" "STATUS" "DIRECTORY" "STARTED"
  printf "${DIM}%-15s %-10s %-45s %s${RESET}\n" "───────────────" "──────────" "─────────────────────────────────────────────" "───────────"

  for state_file in "$CCW_STATE"/*.json; do
    [[ -f "$state_file" ]] || continue
    has_workers=true

    local name dir started_at
    name=$(basename "$state_file" .json)
    dir=$(grep '"dir"' "$state_file" | sed 's/.*: *"\(.*\)".*/\1/' || echo "?")
    started_at=$(grep '"started_at"' "$state_file" | sed 's/.*: *"\(.*\)".*/\1/' || echo "?")

    # 实时检测状态
    local status
    status=$(detect_status "$name")

    # 状态着色
    local status_colored
    case "$status" in
      idle)     status_colored="${GREEN}idle${RESET}" ;;
      busy)     status_colored="${YELLOW}busy${RESET}" ;;
      starting) status_colored="${CYAN}starting${RESET}" ;;
      stopped)  status_colored="${RED}stopped${RESET}" ;;
      *)        status_colored="${DIM}unknown${RESET}" ;;
    esac

    # 截断长路径
    local dir_short="$dir"
    if (( ${#dir} > 45 )); then
      dir_short="...${dir: -42}"
    fi

    printf "%-15s %-10b %-45s %s\n" "$name" "$status_colored" "$dir_short" "$started_at"
  done

  if ! $has_workers; then
    log "No active workers"
  fi
}

# ── 子命令：status ────────────────────────────────────────────────────────────
cmd_status() {
  local name="${1:-}"
  [[ -z "$name" ]] && { err "Usage: ccw status <name>"; exit 1; }
  validate_name "$name"

  local state_file
  state_file=$(state_path "$name")
  local status
  status=$(detect_status "$name")

  echo "Worker: $name"
  echo "Status: $status"

  if [[ -f "$state_file" ]]; then
    local dir started_at last_cmd
    dir=$(grep '"dir"' "$state_file" | sed 's/.*: *"\(.*\)".*/\1/' || echo "?")
    started_at=$(grep '"started_at"' "$state_file" | sed 's/.*: *"\(.*\)".*/\1/' || echo "?")
    last_cmd=$(grep '"last_command"' "$state_file" | head -1 | sed 's/.*: *"\(.*\)",*/\1/; s/.*: *null.*/none/' || echo "none")
    echo "Dir:    $dir"
    echo "Since:  $started_at"
    echo "Last:   $last_cmd"
    echo "Socket: $(socket_path "$name")"
    echo "Attach: tmux -S '$(socket_path "$name")' attach -t '$name'"
  else
    echo "No state file found"
  fi

  # 显示最后几行输出
  if session_exists "$name"; then
    local sock
    sock=$(socket_path "$name")
    echo ""
    echo "── Recent output (last 5 lines) ──"
    tmux -S "$sock" capture-pane -p -J -t "$name":0 -S -5 2>/dev/null || echo "(unable to capture)"
  fi
}

# ── 用法提示 ──────────────────────────────────────────────────────────────────
usage() {
  echo "Usage: ccw <command> [args]"
  echo ""
  echo "Commands:"
  echo "  start <name> [--dir path] [--prompt \"task\"]  Start a worker"
  echo "  stop <name>                                   Stop a worker"
  echo "  stop-all                                      Stop all workers"
  echo "  send <name> <message>                         Send prompt to worker"
  echo "  output <name> [--lines N]                     Read worker output"
  echo "  list                                          List all workers"
  echo "  status <name>                                 Worker status details"
}

# ── 主入口 ────────────────────────────────────────────────────────────────────
CMD="${1:-}"
shift || true

case "$CMD" in
  start)    cmd_start "$@" ;;
  stop)     cmd_stop "$@" ;;
  stop-all) cmd_stop_all ;;
  send)     cmd_send "$@" ;;
  output)   cmd_output "$@" ;;
  list)     cmd_list ;;
  status)   cmd_status "$@" ;;
  help|-h|--help) usage ;;
  *)
    [[ -n "$CMD" ]] && err "Unknown command: $CMD"
    usage
    exit 1
    ;;
esac
