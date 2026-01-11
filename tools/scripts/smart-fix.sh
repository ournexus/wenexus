#!/bin/bash

# WeNexus Smart Fix Script
# Simple pre-commit auto-fix for common issues

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log() { echo -e "$1"; }

# Apply safe fixes to staged files only
apply_fixes() {
    log "${GREEN}🔧 WeNexus Smart Fix${NC}"

    # Get staged files
    local staged_files=$(git diff --cached --name-only --diff-filter=ACM)

    if [[ -z "$staged_files" ]]; then
        log "${YELLOW}No staged files to fix${NC}"
        exit 0
    fi

    # Frontend fixes (if in frontend directory or has frontend files)
    local frontend_files=$(echo "$staged_files" | grep -E '^frontend/.*\.(js|jsx|ts|tsx)$' || true)
    if [[ -n "$frontend_files" ]]; then
        log "  📝 Formatting frontend files..."
        cd "$PROJECT_ROOT/frontend"
        echo "$frontend_files" | sed 's|^frontend/||' | xargs -I {} npx prettier --write "{}" 2>/dev/null || true
        echo "$frontend_files" | sed 's|^frontend/||' | xargs -I {} npx eslint --fix "{}" 2>/dev/null || true
        cd "$PROJECT_ROOT"
    fi

    # Python fixes
    local python_files=$(echo "$staged_files" | grep -E '^backend/python/.*\.py$' || true)
    if [[ -n "$python_files" ]]; then
        log "  🐍 Formatting Python files..."
        cd "$PROJECT_ROOT/backend/python"
        echo "$python_files" | sed 's|^backend/python/||' | xargs -I {} black "{}" 2>/dev/null || true
        echo "$python_files" | sed 's|^backend/python/||' | xargs -I {} isort "{}" 2>/dev/null || true
        cd "$PROJECT_ROOT"
    fi

    # Re-stage fixed files
    echo "$staged_files" | xargs git add 2>/dev/null || true

    log "${GREEN}✅ Smart fix complete${NC}"
}

apply_fixes
