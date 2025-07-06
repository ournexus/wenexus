#!/bin/bash

# WeNexus Pre-commit Wrapper with Smart Fix
# This script enhances pre-commit with intelligent auto-fixing

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SMART_FIX_SCRIPT="$SCRIPT_DIR/smart-fix.sh"

log() {
    echo -e "${1}"
}

# Main pre-commit with smart fix
run_precommit_with_smart_fix() {
    local attempt=1
    local max_attempts=3
    
    log "${BLUE}🚀 Running pre-commit with smart fix...${NC}"
    
    while [[ $attempt -le $max_attempts ]]; do
        log "${BLUE}📍 Pre-commit attempt $attempt of $max_attempts${NC}"
        
        # Run pre-commit
        if pre-commit run "$@"; then
            log "${GREEN}🎉 Pre-commit checks passed!${NC}"
            return 0
        fi
        
        # If pre-commit failed and this isn't the last attempt
        if [[ $attempt -lt $max_attempts ]]; then
            log "${YELLOW}⚠️  Pre-commit failed, running smart fix...${NC}"
            
            # Run smart fix
            if [[ -x "$SMART_FIX_SCRIPT" ]]; then
                "$SMART_FIX_SCRIPT"
                log "${GREEN}✅ Smart fix completed, retrying pre-commit...${NC}"
            else
                log "${RED}❌ Smart fix script not found or not executable${NC}"
                break
            fi
        else
            log "${RED}❌ Pre-commit failed after $max_attempts attempts${NC}"
            log "${YELLOW}💡 Try running manually: $SMART_FIX_SCRIPT${NC}"
        fi
        
        attempt=$((attempt + 1))
    done
    
    return 1
}

# Check if this is a git hook call
if [[ "${1:-}" == "--hook" ]]; then
    # Called as a git hook, run with smart fix
    shift
    run_precommit_with_smart_fix "$@"
else
    # Called manually, just run pre-commit
    pre-commit "$@"
fi