#!/bin/bash

# WeNexus Module Documentation Checker
# Ensures new/modified modules have proper documentation

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

errors=0

log_error() { echo -e "${RED}❌ $1${NC}"; ((errors++)); }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_ok() { echo -e "${GREEN}✅ $1${NC}"; }

# Check TypeScript index.ts files for JSDoc comments
check_ts_module() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # Check if file has @module or @description in first 10 lines
        if ! head -20 "$file" | grep -qE '(@module|@description|\* .+)'; then
            log_error "Missing module documentation: $file"
            echo "    Add JSDoc comment with @module and @description"
        fi
    fi
}

# Check Python __init__.py files for docstrings
check_py_module() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # Check if file starts with docstring (triple quotes)
        if ! head -5 "$file" | grep -qE '^"""'; then
            # Allow empty __init__.py files
            if [[ -s "$file" ]]; then
                log_error "Missing module docstring: $file"
                echo "    Add docstring at top of file"
            fi
        fi
    fi
}

# Check package.json for description field
check_package_json() {
    local file="$1"
    if [[ -f "$file" ]]; then
        local desc=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$file" | head -1)
        if [[ -z "$desc" ]] || echo "$desc" | grep -qE '"description"[[:space:]]*:[[:space:]]*""'; then
            log_error "Missing or empty description in: $file"
            echo "    Add meaningful description field"
        fi
    fi
}

# Main check function
main() {
    echo -e "${GREEN}🔍 Checking module documentation...${NC}"
    echo ""

    # Get staged files
    local staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

    if [[ -z "$staged_files" ]]; then
        # If no staged files, check all (for manual runs)
        staged_files=$(git diff --name-only HEAD~1 2>/dev/null || find . -type f \( -name "index.ts" -o -name "__init__.py" -o -name "package.json" \) | grep -v node_modules | grep -v .git)
    fi

    # Check TypeScript modules
    local ts_files=$(echo "$staged_files" | grep -E 'index\.ts$' || true)
    for file in $ts_files; do
        [[ -f "$PROJECT_ROOT/$file" ]] && check_ts_module "$PROJECT_ROOT/$file"
    done

    # Check Python modules
    local py_files=$(echo "$staged_files" | grep -E '__init__\.py$' || true)
    for file in $py_files; do
        [[ -f "$PROJECT_ROOT/$file" ]] && check_py_module "$PROJECT_ROOT/$file"
    done

    # Check package.json files
    local pkg_files=$(echo "$staged_files" | grep -E 'package\.json$' || true)
    for file in $pkg_files; do
        [[ -f "$PROJECT_ROOT/$file" ]] && check_package_json "$PROJECT_ROOT/$file"
    done

    echo ""
    if [[ $errors -gt 0 ]]; then
        log_error "Found $errors documentation issue(s)"
        echo ""
        echo "See CLAUDE.md for documentation templates"
        exit 1
    else
        log_ok "All module documentation checks passed"
    fi
}

main "$@"
