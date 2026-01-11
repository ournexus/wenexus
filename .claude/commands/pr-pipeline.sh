#!/bin/bash

# PR Pipeline Command Implementation
# WeNexus Smart PR Management System

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE=".pr-pipeline.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Default configuration
DRAFT=false
REVIEWER=""
LABEL=""
SKIP_TESTS=false
FORCE=false
FEATURE_DESC=""

# Initialize log
init_log() {
    echo "[$TIMESTAMP] PR Pipeline Started" > "$LOG_FILE"
}

# Logging functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --draft)
                DRAFT=true
                shift
                ;;
            --reviewer)
                REVIEWER="$2"
                shift 2
                ;;
            --label)
                LABEL="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --debug)
                set -x
                shift
                ;;
            -*)
                error "Unknown option: $1"
                exit 1
                ;;
            *)
                if [[ -z "$FEATURE_DESC" ]]; then
                    FEATURE_DESC="$1"
                fi
                shift
                ;;
        esac
    done
}

# Check Git status
check_git_status() {
    log "Checking Git status..."

    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Current directory is not a Git repository"
        exit 1
    fi

    local branch=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$branch" == "main" ]] || [[ "$branch" == "master" ]]; then
        error "Cannot operate directly on main branch"
        exit 1
    fi

    local changes=$(git status --porcelain | wc -l)
    if [[ $changes -eq 0 ]]; then
        error "No changes detected"
        exit 1
    fi

    log "Current branch: $branch"
    log "Detected $changes file changes"
}

# Analyze changes
analyze_changes() {
    log "Analyzing changes..."

    local modified_files=$(git diff --name-only | head -10)
    local added_files=$(git diff --cached --name-only | head -10)

    log "Modified files:"
    echo "$modified_files" | while read -r file; do
        [[ -n "$file" ]] && log "  - $file"
    done

    # Detect change types
    local has_js=false
    local has_py=false
    local has_java=false
    local has_docs=false

    for file in $(git diff --name-only); do
        case "$file" in
            *.js|*.ts|*.jsx|*.tsx) has_js=true ;;
            *.py) has_py=true ;;
            *.java) has_java=true ;;
            *.md|*.txt|*.rst) has_docs=true ;;
        esac
    done

    log "Detected change types:"
    $has_js && log "  - JavaScript/TypeScript"
    $has_py && log "  - Python"
    $has_java && log "  - Java"
    $has_docs && log "  - Documentation"
}

# Run code quality checks
run_quality_checks() {
    log "Running code quality checks..."

    if [[ "$SKIP_TESTS" == "true" ]]; then
        warning "Skipping test execution (--skip-tests)"
        return 0
    fi

    # Run pre-commit hooks
    if command -v pre-commit >/dev/null 2>&1; then
        log "Running pre-commit checks..."
        if ! pre-commit run --all-files; then
            error "Pre-commit checks failed, please fix issues and retry"
            exit 1
        fi
    else
        warning "pre-commit not installed, skipping code quality checks"
    fi

    # Run tests
    log "Running tests..."
    if [[ -f "frontend/package.json" ]] && (cd frontend && pnpm test >/dev/null 2>&1); then
        log "Frontend tests passed"
    elif [[ -f "backend/java/pom.xml" ]] && (cd backend/java && mvn test >/dev/null 2>&1); then
        log "Java backend tests passed"
    elif [[ -f "backend/python/pyproject.toml" ]] && (cd backend/python && uv run pytest >/dev/null 2>&1); then
        log "Python backend tests passed"
    else
        warning "Unable to run tests, please verify manually"
    fi
}

# Sync with main branch
sync_with_main() {
    log "Syncing with main branch..."

    local main_branch="main"
    if ! git show-ref --verify --quiet refs/heads/main; then
        main_branch="master"
    fi

    log "Using main branch: $main_branch"

    # Fetch latest changes
    git fetch origin "$main_branch"

    # Check for conflicts
    local behind=$(git rev-list --count HEAD..origin/$main_branch)
    if [[ $behind -gt 0 ]]; then
        log "Main branch has $behind new commits, starting merge..."

        # Try rebase first
        if git rebase origin/$main_branch; then
            log "Successfully rebased to latest main branch"
        else
            warning "Rebase failed, trying merge..."
            git rebase --abort
            if git merge origin/$main_branch; then
                log "Successfully merged main branch changes"
            else
                error "Merge conflict, please resolve manually"
                exit 1
            fi
        fi
    else
        log "Main branch is up to date"
    fi
}

# Generate commit message
generate_commit_message() {
    log "Generating commit message..."

    if [[ -n "$FEATURE_DESC" ]]; then
        echo "$FEATURE_DESC"
        return 0
    fi

    # Generate commit message based on changes
    local type="feat"
    local scope="general"
    local description=""

    # Detect change type
    local files_changed=$(git diff --name-only | wc -l)

    # Simple type detection
    if git diff --name-only | grep -q "test"; then
        type="test"
    elif git diff --name-only | grep -q "docs/"; then
        type="docs"
    elif git diff --name-only | grep -q "fix\|bug"; then
        type="fix"
    fi

    # Detect scope
    if git diff --name-only | grep -q "^frontend/apps/web"; then
        scope="web"
    elif git diff --name-only | grep -q "^frontend/apps/mobile"; then
        scope="mobile"
    elif git diff --name-only | grep -q "^backend/java"; then
        scope="api"
    elif git diff --name-only | grep -q "^backend/python"; then
        scope="ai"
    fi

    # Generate description
    local first_file=$(git diff --name-only | head -1)
    description="update $(basename "$first_file" .*)"

    echo "$type($scope): $description"
}

# Create commit
create_commit() {
    log "Creating commit..."

    local commit_msg=$(generate_commit_message)

    log "Commit message: $commit_msg"

    # Add all changes
    git add .

    # Create commit
    if git commit -m "$commit_msg"; then
        log "Commit created successfully"
    else
        error "Commit creation failed"
        exit 1
    fi
}

# Push to remote
push_to_remote() {
    log "Pushing to remote repository..."

    local current_branch=$(git rev-parse --abbrev-ref HEAD)

    if [[ "$FORCE" == "true" ]]; then
        warning "Using force push (--force)"
        git push --force-with-lease origin "$current_branch"
    else
        git push origin "$current_branch"
    fi

    log "Push successful"
}

# Create Pull Request
create_pr() {
    log "Creating Pull Request..."

    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local main_branch="main"

    if ! git show-ref --verify --quiet refs/heads/main; then
        main_branch="master"
    fi

    # Generate PR title and description
    local last_commit=$(git log -1 --pretty=%B)
    local title="$last_commit"

    # Generate PR description
    local description=$(cat <<EOF
## Change Summary
$([ -n "$FEATURE_DESC" ] && echo "$FEATURE_DESC" || echo "Please describe the main purpose of this change")

## Change Details
$(git log --oneline origin/$main_branch..HEAD --no-merges)

## Testing Notes
- [ ] Local tests passed
- [ ] Code quality checks passed
- [ ] Documentation updated (if needed)

## Checklist
- [ ] Code follows project conventions
- [ ] Necessary tests added
- [ ] Performance impact assessed
- [ ] Security considerations verified

## Related Issues
<!-- Link related issues here if any -->

---
*Auto-created by /pr-pipeline*
EOF
)

    # Build gh command using array for safety
    local gh_args=("pr" "create" "--title" "$title" "--body" "$description")

    if [[ "$DRAFT" == "true" ]]; then
        gh_args+=("--draft")
    fi

    if [[ -n "$REVIEWER" ]]; then
        gh_args+=("--reviewer" "$REVIEWER")
    fi

    if [[ -n "$LABEL" ]]; then
        gh_args+=("--label" "$LABEL")
    fi

    log "Executing: gh ${gh_args[*]}"
    gh "${gh_args[@]}"

    log "PR created successfully!"
}

# Main function
main() {
    init_log
    parse_args "$@"

    log "Starting PR Pipeline..."

    check_git_status
    analyze_changes
    run_quality_checks
    sync_with_main
    create_commit
    push_to_remote
    create_pr

    log "PR Pipeline completed!"
    log "Please review the PR on GitHub and add necessary context"
}

# Execute main function
main "$@"
