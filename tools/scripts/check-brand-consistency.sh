#!/bin/bash

# WeNexus Brand Consistency Checker
# Ensures consistent use of "WeNexus" branding across the codebase

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Search for inconsistent branding
if grep -r -i "we-nexus\|wenexu[^s]" \
    --include="*.md" \
    --include="*.ts" \
    --include="*.tsx" \
    --include="*.java" \
    --include="*.py" \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    .; then
    echo -e "${RED}❌ Inconsistent WeNexus branding found.${NC}"
    echo "Please use \"WeNexus\" (capital W, capital N, no hyphen)"
    exit 1
fi

echo -e "${GREEN}✅ WeNexus branding is consistent${NC}"
exit 0
