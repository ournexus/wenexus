#!/bin/bash

# WeNexus Smart Fix Script
# Intelligent automatic fixing with progressive retry mechanism

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.autofix.yaml"
LOG_FILE="$PROJECT_ROOT/.autofix.log"
BACKUP_DIR="$PROJECT_ROOT/.autofix-backup"

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        # Parse YAML config (simplified)
        AUTOFIX_LEVEL=$(grep "^level:" "$CONFIG_FILE" | cut -d':' -f2 | xargs || echo "safe")
        AUTO_COMMIT=$(grep "^auto-commit:" "$CONFIG_FILE" | cut -d':' -f2 | xargs || echo "false")
        BACKUP_ENABLED=$(grep "^backup:" "$CONFIG_FILE" | cut -d':' -f2 | xargs || echo "true")
    else
        AUTOFIX_LEVEL="safe"
        AUTO_COMMIT="false"
        BACKUP_ENABLED="true"
    fi
}

# Logging function
log() {
    echo -e "${1}" | tee -a "$LOG_FILE"
}

# Create backup
create_backup() {
    if [[ "$BACKUP_ENABLED" == "true" ]]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local backup_path="$BACKUP_DIR/$timestamp"
        mkdir -p "$backup_path"

        # Backup staged files
        git diff --cached --name-only | while read file; do
            if [[ -f "$file" ]]; then
                mkdir -p "$backup_path/$(dirname "$file")"
                cp "$file" "$backup_path/$file"
            fi
        done

        log "${GREEN}📦 Backup created at: $backup_path${NC}"
    fi
}

# Safe fixes - can be applied automatically
apply_safe_fixes() {
    log "${BLUE}🔧 Applying safe fixes...${NC}"

    local fixes_applied=0

    # Prettier formatting
    if command -v npx &> /dev/null; then
        log "  📝 Running Prettier..."
        npx prettier --write . --ignore-path .gitignore 2>/dev/null && fixes_applied=$((fixes_applied + 1))
    fi

    # ESLint auto-fix
    if command -v npx &> /dev/null; then
        log "  🔍 Running ESLint auto-fix..."
        npx eslint . --fix --ext .js,.jsx,.ts,.tsx 2>/dev/null && fixes_applied=$((fixes_applied + 1))
    fi

    # Remove trailing whitespace
    log "  🧹 Removing trailing whitespace..."
    find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" \) \
        -not -path "./node_modules/*" -not -path "./.next/*" -not -path "./dist/*" \
        -exec sed -i '' 's/[[:space:]]*$//' {} \; 2>/dev/null && fixes_applied=$((fixes_applied + 1))

    # Fix end of file newlines
    log "  📄 Fixing end-of-file newlines..."
    find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" \) \
        -not -path "./node_modules/*" -not -path "./.next/*" -not -path "./dist/*" \
        -exec bash -c 'if [[ -n "$(tail -c1 "$1")" ]]; then echo >> "$1"; fi' _ {} \; 2>/dev/null && fixes_applied=$((fixes_applied + 1))

    log "${GREEN}✅ Applied $fixes_applied safe fixes${NC}"
    return $fixes_applied
}

# Interactive fixes - require user confirmation
apply_interactive_fixes() {
    log "${YELLOW}🤔 Interactive fixes required...${NC}"

    local fixes_applied=0

    # Check for TODO/FIXME comments
    local todo_files=$(grep -r "TODO\|FIXME\|XXX" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" --exclude-dir=node_modules . 2>/dev/null | cut -d':' -f1 | sort -u)

    if [[ -n "$todo_files" ]]; then
        log "${YELLOW}  📝 Found TODO/FIXME comments in:${NC}"
        echo "$todo_files" | while read file; do
            log "    - $file"
        done

        if [[ "$AUTOFIX_LEVEL" == "interactive" || "$AUTOFIX_LEVEL" == "aggressive" ]]; then
            read -p "Remove TODO/FIXME comments? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "$todo_files" | while read file; do
                    sed -i '' '/TODO\|FIXME\|XXX/d' "$file"
                done
                fixes_applied=$((fixes_applied + 1))
                log "${GREEN}  ✅ Removed TODO/FIXME comments${NC}"
            fi
        fi
    fi

    # Check for missing exports
    local no_export_files=$(find apps packages -name "*.ts" -not -path "./node_modules/*" -not -path "./.next/*" -exec grep -L "export" {} \; 2>/dev/null | grep -v "\.(d|test|spec)\.ts$" || true)

    if [[ -n "$no_export_files" ]]; then
        log "${YELLOW}  📦 Found TypeScript files without exports:${NC}"
        echo "$no_export_files" | while read file; do
            log "    - $file"
        done

        if [[ "$AUTOFIX_LEVEL" == "interactive" || "$AUTOFIX_LEVEL" == "aggressive" ]]; then
            read -p "Add empty exports to these files? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "$no_export_files" | while read file; do
                    echo "export {};" >> "$file"
                done
                fixes_applied=$((fixes_applied + 1))
                log "${GREEN}  ✅ Added empty exports${NC}"
            fi
        fi
    fi

    return $fixes_applied
}

# Manual fixes - only report issues
report_manual_fixes() {
    log "${RED}🚨 Manual fixes required:${NC}"

    # Run type checking
    if command -v npx &> /dev/null && [[ -f "tsconfig.json" ]]; then
        log "  🔍 Running TypeScript type checking..."
        if ! npx tsc --noEmit 2>/dev/null; then
            log "${RED}    ❌ TypeScript type errors found${NC}"
            log "    💡 Run 'npx tsc --noEmit' to see detailed errors"
        fi
    fi

    # Check for security issues (if detect-secrets is available)
    if command -v detect-secrets &> /dev/null; then
        log "  🔐 Running security scan..."
        if ! detect-secrets scan --baseline .secrets.baseline 2>/dev/null; then
            log "${RED}    ❌ Potential security issues found${NC}"
            log "    💡 Run 'detect-secrets scan' to see detailed report"
        fi
    fi
}

# Progressive retry mechanism
run_progressive_fixes() {
    local attempt=1
    local max_attempts=3

    log "${BLUE}🚀 Starting progressive fix process...${NC}"

    while [[ $attempt -le $max_attempts ]]; do
        log "${BLUE}📍 Attempt $attempt of $max_attempts${NC}"

        # Run pre-commit checks
        if pre-commit run --all-files 2>/dev/null; then
            log "${GREEN}🎉 All checks passed!${NC}"
            return 0
        fi

        case $attempt in
            1)
                log "${YELLOW}🔧 Attempt 1: Applying safe fixes...${NC}"
                apply_safe_fixes
                ;;
            2)
                if [[ "$AUTOFIX_LEVEL" != "safe" ]]; then
                    log "${YELLOW}🤔 Attempt 2: Applying interactive fixes...${NC}"
                    apply_interactive_fixes
                else
                    log "${YELLOW}⚠️  Skipping interactive fixes (safe mode)${NC}"
                fi
                ;;
            3)
                log "${RED}🚨 Attempt 3: Reporting manual fixes needed...${NC}"
                report_manual_fixes
                ;;
        esac

        attempt=$((attempt + 1))
    done

    log "${RED}❌ Some issues still require manual intervention${NC}"
    return 1
}

# Smart commit strategy
smart_commit() {
    if [[ "$AUTO_COMMIT" == "true" ]]; then
        # Check if there are any staged changes
        if git diff --cached --quiet; then
            log "${YELLOW}📝 No changes to commit${NC}"
            return 0
        fi

        # Get the original commit message if available
        local original_message=""
        if [[ -f .git/COMMIT_EDITMSG ]]; then
            original_message=$(cat .git/COMMIT_EDITMSG)
        fi

        # Create commit message
        local commit_message="$original_message"
        if [[ -z "$commit_message" ]]; then
            commit_message="fix: auto-fix code quality issues"
        else
            commit_message="$commit_message

🤖 Auto-fixed by WeNexus Smart Fix"
        fi

        # Commit changes
        git add .
        git commit -m "$commit_message"
        log "${GREEN}✅ Changes committed automatically${NC}"
    else
        log "${YELLOW}📝 Auto-commit disabled. Please review and commit manually.${NC}"
    fi
}

# Main execution
main() {
    log "${GREEN}🌟 WeNexus Smart Fix Started$(date)${NC}"

    # Load configuration
    load_config
    log "${BLUE}📋 Configuration:${NC}"
    log "  - Level: $AUTOFIX_LEVEL"
    log "  - Auto-commit: $AUTO_COMMIT"
    log "  - Backup: $BACKUP_ENABLED"

    # Create backup if enabled
    create_backup

    # Run progressive fixes
    if run_progressive_fixes; then
        log "${GREEN}🎉 All fixes completed successfully!${NC}"
        smart_commit
    else
        log "${RED}⚠️  Some issues require manual attention${NC}"
        log "💡 Check the log file: $LOG_FILE"
    fi

    log "${GREEN}✨ Smart Fix Complete$(date)${NC}"
}

# Run main function
main "$@"
