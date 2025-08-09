#!/bin/bash

# PR Pipeline Command Implementation
# WeNexus Smart PR Management System

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件
LOG_FILE=".pr-pipeline.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 默认配置
DRAFT=false
REVIEWER=""
LABEL=""
SKIP_TESTS=false
FORCE=false
FEATURE_DESC=""

# 初始化日志
init_log() {
    echo "[$TIMESTAMP] PR Pipeline Started" > "$LOG_FILE"
}

# 日志函数
log() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# 解析参数
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
                error "未知选项: $1"
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

# 检查Git状态
check_git_status() {
    log "检查Git状态..."

    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "当前目录不是Git仓库"
        exit 1
    fi

    local branch=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$branch" == "main" ]] || [[ "$branch" == "master" ]]; then
        error "不能在主分支上直接操作"
        exit 1
    fi

    local changes=$(git status --porcelain | wc -l)
    if [[ $changes -eq 0 ]]; then
        error "没有检测到变更"
        exit 1
    fi

    log "当前分支: $branch"
    log "检测到 $changes 个文件变更"
}

# 分析变更内容
analyze_changes() {
    log "分析变更内容..."

    local modified_files=$(git diff --name-only | head -10)
    local added_files=$(git diff --cached --name-only | head -10)

    log "修改的文件:"
    echo "$modified_files" | while read -r file; do
        [[ -n "$file" ]] && log "  - $file"
    done

    # 检测变更类型
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

    log "检测到的变更类型:"
    $has_js && log "  - JavaScript/TypeScript"
    $has_py && log "  - Python"
    $has_java && log "  - Java"
    $has_docs && log "  - Documentation"
}

# 运行代码质量检查
run_quality_checks() {
    log "运行代码质量检查..."

    if [[ "$SKIP_TESTS" == "true" ]]; then
        warning "跳过测试运行 (--skip-tests)"
        return 0
    fi

    # 运行预提交钩子
    if command -v pre-commit >/dev/null 2>&1; then
        log "运行预提交检查..."
        if ! pre-commit run --all-files; then
            error "预提交检查失败，请修复问题后重试"
            exit 1
        fi
    else
        warning "pre-commit未安装，跳过代码质量检查"
    fi

    # 运行测试
    log "运行测试..."
    if [[ -f "package.json" ]] && npm run test >/dev/null 2>&1; then
        log "前端测试通过"
    elif [[ -f "services/java-backend/pom.xml" ]] && (cd services/java-backend && mvn test >/dev/null 2>&1); then
        log "Java后端测试通过"
    elif [[ -f "services/python-backend/pyproject.toml" ]] && (cd services/python-backend && pytest >/dev/null 2>&1); then
        log "Python后端测试通过"
    else
        warning "无法运行测试，请手动验证"
    fi
}

# 同步主分支
sync_with_main() {
    log "同步主分支..."

    local main_branch="main"
    if ! git show-ref --verify --quiet refs/heads/main; then
        main_branch="master"
    fi

    log "使用主分支: $main_branch"

    # 获取最新变更
    git fetch origin "$main_branch"

    # 检查是否有冲突
    local behind=$(git rev-list --count HEAD..origin/$main_branch)
    if [[ $behind -gt 0 ]]; then
        log "主分支有 $behind 个新提交，开始合并..."

        # 尝试rebase
        if git rebase origin/$main_branch; then
            log "成功rebase到最新主分支"
        else
            warning "rebase失败，尝试merge..."
            git rebase --abort
            if git merge origin/$main_branch; then
                log "成功merge主分支变更"
            else
                error "合并冲突，请手动解决"
                exit 1
            fi
        fi
    else
        log "主分支已是最新"
    fi
}

# 生成提交信息
generate_commit_message() {
    log "生成提交信息..."

    if [[ -n "$FEATURE_DESC" ]]; then
        echo "$FEATURE_DESC"
        return 0
    fi

    # 基于变更生成提交信息
    local type="feat"
    local scope="general"
    local description=""

    # 检测变更类型
    local files_changed=$(git diff --name-only | wc -l)

    # 简单的类型检测
    if git diff --name-only | grep -q "test"; then
        type="test"
    elif git diff --name-only | grep -q "docs/"; then
        type="docs"
    elif git diff --name-only | grep -q "fix\|bug"; then
        type="fix"
    fi

    # 检测范围
    if git diff --name-only | grep -q "^apps/web"; then
        scope="web"
    elif git diff --name-only | grep -q "^apps/mobile"; then
        scope="mobile"
    elif git diff --name-only | grep -q "^services/java-backend"; then
        scope="api"
    elif git diff --name-only | grep -q "^services/python-backend"; then
        scope="ai"
    fi

    # 生成描述
    local first_file=$(git diff --name-only | head -1)
    description="update $(basename "$first_file" .*)"

    echo "$type($scope): $description"
}

# 创建提交
create_commit() {
    log "创建提交..."

    local commit_msg=$(generate_commit_message)

    log "提交信息: $commit_msg"

    # 添加所有变更
    git add .

    # 创建提交
    if git commit -m "$commit_msg"; then
        log "提交创建成功"
    else
        error "提交创建失败"
        exit 1
    fi
}

# 推送到远程
push_to_remote() {
    log "推送到远程仓库..."

    local current_branch=$(git rev-parse --abbrev-ref HEAD)

    if [[ "$FORCE" == "true" ]]; then
        warning "使用强制推送 (--force)"
        git push --force-with-lease origin "$current_branch"
    else
        git push origin "$current_branch"
    fi

    log "推送成功"
}

# 创建PR
create_pr() {
    log "创建Pull Request..."

    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local main_branch="main"

    if ! git show-ref --verify --quiet refs/heads/main; then
        main_branch="master"
    fi

    # 生成PR标题和描述
    local last_commit=$(git log -1 --pretty=%B)
    local title="$last_commit"

    # 生成PR描述
    local description=$(cat <<EOF
## 变更概述
$([ -n "$FEATURE_DESC" ] && echo "$FEATURE_DESC" || echo "请描述本次变更的主要目的")

## 变更详情
$(git log --oneline origin/$main_branch..HEAD --no-merges)

## 测试说明
- [ ] 本地测试已通过
- [ ] 代码质量检查已通过
- [ ] 文档已更新（如需要）

## 检查清单
- [ ] 代码符合项目规范
- [ ] 必要的测试已添加
- [ ] 性能影响已评估
- [ ] 安全考虑已验证

## 相关Issue
<!-- 如有相关Issue，请在此关联 -->

---
*由/pr-pipeline自动创建*
EOF
)

    # 构建gh命令
    local gh_cmd="gh pr create --title \"$title\" --body \"$description\""

    if [[ "$DRAFT" == "true" ]]; then
        gh_cmd="$gh_cmd --draft"
    fi

    if [[ -n "$REVIEWER" ]]; then
        gh_cmd="$gh_cmd --reviewer \"$REVIEWER\""
    fi

    if [[ -n "$LABEL" ]]; then
        gh_cmd="$gh_cmd --label \"$LABEL\""
    fi

    log "执行: $gh_cmd"
    eval "$gh_cmd"

    log "PR创建成功！"
}

# 主函数
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

    log "PR Pipeline 完成！"
    log "请检查GitHub上的PR并添加必要的上下文信息"
}

# 执行主函数
main "$@"
