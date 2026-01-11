# 7×24 持续自主开发范式 - Ralph for Claude Code

## 概述

Ralph for Claude Code 是一个自主 AI 开发循环工具，能够让 Claude Code 持续迭代改进项目直到完成，实现 7×24 不间断的智能开发范式。它通过智能退出检测、速率限制和断路器模式等机制，确保开发过程的安全性和效率。

**项目地址**: [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code)

## 核心概念

### 什么是自主开发循环？

Ralph 实现了一个持续的开发循环：

```
读取指令 → 执行 Claude Code → 跟踪进度 → 评估完成度 → 重复
```

这个循环会一直运行，直到：

- 所有任务标记为完成
- 检测到项目完成信号
- 达到 API 限制或触发断路器
- 手动中断

### 为什么需要自主开发？

在传统开发中，人类开发者需要：

- 持续监控任务进度
- 手动迭代优化代码
- 在不同任务间切换上下文
- 等待测试结果再进行下一步

Ralph 通过自动化这些过程，让 AI 能够：

- **夜间工作** - 利用非工作时间持续开发
- **无缝迭代** - 自动进行多轮优化
- **任务串联** - 完成一个任务后自动开始下一个
- **上下文保持** - 跨会话保持开发上下文

## 适用场景

### ✅ 强烈推荐的场景

#### 1. 大型功能开发（预计需要 3+ 小时）

**场景描述**: 实现复杂的新功能，需要多个文件修改、测试编写和文档更新。

**为什么适合 Ralph**:

- 可以持续工作数小时甚至过夜
- 自动处理依赖任务的先后顺序
- 会话连续性确保上下文不丢失

**示例任务**:

```bash
# WeNexus 示例：实现共识算法模块
ralph-import consensus-feature-prd.md consensus-module
cd consensus-module
ralph --monitor --timeout 60
```

#### 2. 代码库重构（影响 10+ 个文件）

**场景描述**: 大规模代码重构，需要修改多个文件、更新测试和保持一致性。

**为什么适合 Ralph**:

- 断路器模式防止破坏性更改
- 自动运行测试验证重构结果
- 循环优化直到所有测试通过

**示例任务**:

```bash
# WeNexus 示例：重构用户服务为微服务架构
# PROMPT.md 内容：
# "Refactor user-service from monolith to microservices:
#  - Extract authentication logic to auth-service
#  - Extract profile management to profile-service
#  - Update all cross-service communication
#  - Ensure all tests pass"

ralph --monitor --calls 150 --timeout 90
```

#### 3. Bug 修复马拉松（多个相关 Bug）

**场景描述**: 修复一批相关的 Bug，每个修复可能影响其他部分。

**为什么适合 Ralph**:

- 自动检测修复是否引入新问题
- 智能退出检测确保所有 Bug 都修复
- 速率限制防止 API 过度使用

**示例任务**:

```markdown
# @fix_plan.md
- [ ] P0: 修复登录页面认证失败问题
- [ ] P0: 修复共识算法计算错误
- [ ] P1: 修复移动端布局错误
- [ ] P1: 修复 API 响应超时
- [ ] P2: 优化数据库查询性能
```

#### 4. 测试覆盖率提升（目标 80%+）

**场景描述**: 为现有代码编写全面的测试用例，提升覆盖率。

**为什么适合 Ralph**:

- 自动识别未覆盖的代码路径
- 持续编写测试直到达到目标覆盖率
- 可以在夜间运行，早上查看结果

**示例任务**:

```bash
# PROMPT.md:
# "Increase test coverage for backend/java/consensus-service to 80%+
#  - Write unit tests for all service classes
#  - Add integration tests for API endpoints
#  - Create edge case tests for consensus algorithms
#  - Ensure all tests pass with mvn test"

ralph --monitor --verbose --timeout 120
```

#### 5. 从 PRD 到原型（快速 MVP 开发）

**场景描述**: 从产品需求文档快速生成可工作的原型。

**为什么适合 Ralph**:

- ralph-import 可以直接转换 PRD 为开发任务
- 自动生成项目结构、代码和文档
- 适合概念验证和演示

**示例任务**:

```bash
# 将 WeNexus 新功能的 PRD 转换为原型
ralph-import docs/prd/social-consensus-feature.md social-consensus-poc
cd social-consensus-poc
ralph --monitor --timeout 180
```

#### 6. 文档生成和维护（API 文档、用户指南）

**场景描述**: 自动生成代码文档、API 文档和用户指南。

**为什么适合 Ralph**:

- 自动扫描代码库生成文档
- 保持文档与代码同步
- 可以定期运行确保文档更新

**示例任务**:

```markdown
# PROMPT.md:
# "Generate comprehensive documentation for WeNexus:
#  - API documentation for all backend services
#  - User guide for web and mobile apps
#  - Developer onboarding guide
#  - Architecture diagrams and explanations"
```

#### 7. 技术债务清理（代码质量改进）

**场景描述**: 清理技术债务，改进代码质量，修复警告。

**为什么适合 Ralph**:

- 自动识别和修复 linting 错误
- 重构重复代码
- 更新过时的依赖

**示例任务**:

```bash
# PROMPT.md:
# "Clean up technical debt in frontend/apps/web:
#  - Fix all ESLint warnings
#  - Remove unused imports and variables
#  - Update deprecated API usage
#  - Refactor components with >300 lines
#  - Ensure all tests pass"

ralph --monitor --calls 100 --timeout 60
```

### ❌ 不推荐的场景

#### 1. 简单的一次性任务（< 30 分钟）

**为什么不适合**:

- Ralph 的启动和配置开销大于任务本身
- 直接使用 Claude Code 更快

**替代方案**: 直接使用 `claude` CLI 工具

#### 2. 需要频繁人工决策的任务

**为什么不适合**:

- Ralph 设计用于自主工作
- 频繁中断会破坏循环效率

**替代方案**: 使用交互式 Claude Code 会话

#### 3. 高度创新性需要人类创意的任务

**为什么不适合**:

- UI/UX 设计需要人类审美判断
- 产品策略需要人类洞察
- 架构决策需要权衡多个因素

**替代方案**: 使用 Ralph 生成初始方案，人类进行创意优化

#### 4. 资源受限环境（严格的 API 配额）

**为什么不适合**:

- Ralph 会持续调用 API 直到完成
- 可能快速消耗 API 配额

**替代方案**: 使用 `--calls` 限制每小时调用次数

## 安装和设置

### 一次性全局安装

```bash
# 克隆 Ralph 仓库
git clone https://github.com/frankbria/ralph-claude-code.git
cd ralph-claude-code

# 全局安装（只需一次）
./install.sh

# 安装完成后可以删除克隆的仓库
cd .. && rm -rf ralph-claude-code
```

这会添加以下全局命令：

- `ralph` - 主循环工具
- `ralph-monitor` - 实时监控面板
- `ralph-setup` - 项目初始化
- `ralph-import` - PRD 导入工具

### 系统依赖

确保已安装：

- Node.js 18+ 和 npm 8.0.0+
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- tmux: `brew install tmux` (macOS) 或 `apt-get install tmux` (Linux)
- jq: `brew install jq` 或 `apt-get install jq`

## 使用方法

### 方式一：从现有 PRD/规范导入（推荐）

```bash
# 将 WeNexus PRD 转换为 Ralph 项目
ralph-import docs/prd/consensus-algorithm.md consensus-feature

cd consensus-feature

# 审查生成的文件：
# - PROMPT.md (Ralph 指令)
# - @fix_plan.md (任务优先级)
# - specs/requirements.md (技术规范)

# 启动自主开发（带监控面板）
ralph --monitor
```

### 方式二：手动创建项目

```bash
# 创建新的 Ralph 项目
ralph-setup wenexus-auth-improvement

cd wenexus-auth-improvement

# 手动配置项目需求
# 1. 编辑 PROMPT.md - 主要开发指令
# 2. 编辑 @fix_plan.md - 任务优先级列表
# 3. 编辑 specs/*.md - 详细技术规范
# 4. 编辑 @AGENT.md - 构建和运行指令

# 启动开发循环
ralph --monitor
```

### 常用命令选项

```bash
# 基础用法（集成监控面板）
ralph --monitor

# 限制 API 调用（50次/小时）
ralph --monitor --calls 50

# 设置执行超时（60分钟）
ralph --monitor --timeout 60

# 详细进度输出
ralph --monitor --verbose

# 查看当前状态
ralph --status

# 重置断路器（从错误恢复）
ralph --reset-circuit

# 重置会话（清除上下文）
ralph --reset-session

# 不使用会话连续性（每次迭代独立）
ralph --no-continue
```

## 最佳实践

### 1. 编写清晰的 PROMPT.md

**好的示例**:

```markdown
# WeNexus Consensus Algorithm Enhancement

## Objective
Improve the consensus building algorithm to handle 10,000+ concurrent opinions
with < 2 second response time.

## Requirements
1. Refactor ConsensusService.java to use parallel processing
2. Add Redis caching for intermediate results
3. Optimize database queries (add indexes, use batch operations)
4. Write comprehensive unit tests (>85% coverage)
5. Update API documentation

## Success Criteria
- All tests pass (mvn test)
- Performance benchmark shows <2s response time
- Code coverage >85%
- No ESLint/Checkstyle warnings

## Constraints
- Maintain backward compatibility with existing API
- Use existing Spring Boot patterns
- Follow WeNexus code quality standards
```

**不好的示例**:

```markdown
# Fix consensus service

Make it faster and add tests.
```

### 2. 使用优先级驱动的 @fix_plan.md

```markdown
# Priority: P0 (Critical - 必须完成)
- [ ] 修复生产环境认证失败 Bug
- [ ] 修复数据丢失问题

# Priority: P1 (High - 应该完成)
- [ ] 实现共识算法优化
- [ ] 添加 Redis 缓存层
- [ ] 编写集成测试

# Priority: P2 (Medium - 可以完成)
- [ ] 重构冗余代码
- [ ] 更新文档
- [ ] 优化数据库查询

# Priority: P3 (Low - 如果有时间)
- [ ] 改进日志格式
- [ ] 添加性能监控
```

Ralph 会自动：

- 优先处理 P0 任务
- 完成一个任务后标记为 `[x]`
- 当所有任务完成时退出

### 3. 利用监控面板

```bash
# 启动带监控的 Ralph（推荐）
ralph --monitor

# 这会创建一个 tmux 会话，分为两个窗格：
# - 左侧：Ralph 执行日志
# - 右侧：实时监控面板
#   - 当前循环次数
#   - API 调用计数
#   - 速率限制倒计时
#   - 最近日志条目
#   - 断路器状态

# tmux 快捷键：
# Ctrl+B 然后 D - 分离会话（Ralph 继续运行）
# Ctrl+B 然后 ←/→ - 切换窗格
# tmux attach - 重新连接会话
```

### 4. 夜间开发工作流

```bash
# 下班前设置长时间任务
cd wenexus-feature-branch

# 配置较高的 API 限制和超时
ralph --monitor --calls 150 --timeout 180 &

# 分离 tmux 会话
# Ctrl+B 然后 D

# 关闭终端，Ralph 继续运行

# 第二天早上重新连接
tmux attach
ralph --status

# 查看完成的任务
cat @fix_plan.md

# 审查更改
git diff
git log
```

### 5. 处理断路器打开

当 Ralph 检测到问题（连续错误、无进展）时会打开断路器：

```bash
# 查看断路器状态
ralph --circuit-status

# 输出示例：
# Circuit Breaker: OPEN
# Reason: No progress detected for 3 consecutive loops
# Failed attempts: 3
# Last error: Tests failing in ConsensusServiceTest.java

# 解决问题后重置
ralph --reset-circuit

# 继续开发
ralph --monitor
```

### 6. 会话管理策略

```bash
# 默认：使用会话连续性（推荐）
ralph --monitor
# → 保持上下文，提高连贯性

# 调试时：禁用会话连续性
ralph --monitor --no-continue
# → 每次迭代独立，便于隔离问题

# 手动重置会话
ralph --reset-session
# → 清除所有上下文，重新开始

# 查看会话历史
cat .ralph_session_history
# → 调试会话转换问题
```

### 7. 与 WeNexus 工作流集成

```bash
# 1. 在功能分支上使用 Ralph
git checkout -b feature/consensus-v2
ralph-import docs/prd/consensus-v2.md consensus-v2-work
cd consensus-v2-work

# 2. 让 Ralph 完成开发
ralph --monitor --timeout 120

# 3. 审查 Ralph 的工作
git diff
npm run frontend:test
npm run backend:java:test

# 4. 将更改合并回 WeNexus 仓库
# 复制必要的文件到 WeNexus 目录
cp -r src/* ../../backend/java/consensus-service/

# 5. 使用 WeNexus 的 pre-commit hooks
cd ../../
git add backend/java/consensus-service/
git commit -m "feat(api): implement consensus algorithm v2"

# 6. 运行 PR 流程
npm run precommit
# 或使用 WeNexus slash command: /commit-push-pr
```

## 监控和调试

### 实时监控

```bash
# 方式一：集成监控（推荐）
ralph --monitor

# 方式二：分离式监控
# 终端 1
ralph --verbose

# 终端 2
ralph-monitor
```

### 日志分析

```bash
# 实时日志
tail -f logs/ralph.log

# 查找错误
grep "ERROR" logs/ralph.log

# 查找断路器事件
grep "Circuit" logs/ralph.log

# 查看完整执行历史
cat logs/ralph.log | less
```

### 状态检查

```bash
# JSON 格式状态
ralph --status

# 输出示例：
# {
#   "loop_count": 12,
#   "api_calls": 47,
#   "api_limit": 100,
#   "circuit_breaker": "CLOSED",
#   "session_active": true,
#   "last_update": "2026-01-11T10:30:45Z"
# }
```

## 性能优化

### API 调用优化

```bash
# 降低调用频率（适合长时间任务）
ralph --calls 50 --timeout 120

# 提高调用频率（适合快速迭代）
ralph --calls 200 --timeout 30
```

### 超时调整

```bash
# 简单任务：短超时
ralph --timeout 10

# 复杂任务：长超时
ralph --timeout 180

# 测试密集型：超长超时
ralph --timeout 240
```

## 常见问题

### 1. Ralph 过早退出

**原因**: 退出阈值设置过低

**解决方案**:

```bash
# 编辑 ~/.ralph/ralph_loop.sh
MAX_CONSECUTIVE_TEST_LOOPS=5  # 增加到 5
MAX_CONSECUTIVE_DONE_SIGNALS=3  # 增加到 3
```

### 2. 断路器频繁打开

**原因**: 任务描述不清晰或存在实际问题

**解决方案**:

1. 检查 PROMPT.md 是否明确
2. 查看 logs/ralph.log 了解具体错误
3. 手动运行一次 Claude Code 验证任务可行性
4. 调整断路器阈值

### 3. API 限制达到

**原因**: 5小时 API 使用限制

**解决方案**:

```bash
# Ralph 会自动提示：
# "Claude API 5-hour limit reached. Options:
#  1. Wait 60 minutes (countdown shown)
#  2. Exit now"

# 选择等待，Ralph 会倒计时后自动继续
```

### 4. 会话上下文丢失

**原因**: 会话过期或手动重置

**解决方案**:

```bash
# 检查会话状态
cat .ralph_session

# 查看会话历史
cat .ralph_session_history

# 如果需要，手动恢复会话上下文
# 编辑 PROMPT.md 添加之前的上下文信息
```

## 与 WeNexus 项目集成

### 在 WeNexus Monorepo 中使用

```bash
# 为 WeNexus 特定服务创建 Ralph 工作空间
cd wenexus/
mkdir .ralph-workspace
cd .ralph-workspace

# 为后端服务创建任务
ralph-setup backend-optimization
cd backend-optimization

# PROMPT.md 示例：
cat > PROMPT.md << 'EOF'
# WeNexus Backend Optimization

## Context
Working on wenexus/backend/java microservices

## Tasks
1. Optimize ConsensusService database queries
2. Add Redis caching to UserService
3. Improve error handling in ContentService
4. Update all service tests to 85%+ coverage

## Build Commands
cd ../../backend/java
mvn clean install
mvn test

## Quality Standards
- Follow WeNexus code quality standards
- Use Google Java Format
- All public methods need Javadoc
- Minimum 85% test coverage
EOF

ralph --monitor --timeout 120
```

### 配置 WeNexus 特定规则

```bash
# .ralph/config (如果支持)
WENEXUS_CODE_STYLE=google-java-format
WENEXUS_TEST_COVERAGE=85
WENEXUS_PRE_COMMIT=enabled
WENEXUS_CONVENTIONAL_COMMITS=enabled
```

## 安全考虑

### 1. 代码审查

**重要**: Ralph 生成的所有代码都应该经过人工审查

```bash
# 审查更改
git diff

# 运行测试
npm run test           # Frontend
mvn test               # Java Backend
uv run pytest          # Python Backend

# 运行 linting
npm run lint
pre-commit run --all-files
```

### 2. 敏感信息保护

```bash
# 确保 .env 文件不被提交
echo ".env" >> .gitignore
echo ".ralph_session" >> .gitignore

# 使用 WeNexus 的 secret 检测
pre-commit run detect-secrets --all-files
```

### 3. API 使用监控

```bash
# 定期检查 API 使用情况
ralph --status

# 设置合理的限制
ralph --calls 100  # 每小时最多 100 次调用
```

## 进阶技巧

### 1. 多项目并行开发

```bash
# 项目 1: 前端优化
cd frontend-work && ralph --monitor --calls 50 &

# 项目 2: 后端重构
cd backend-work && ralph --monitor --calls 50 &

# 监控所有 tmux 会话
tmux list-sessions
```

### 2. 自定义退出条件

编辑 `~/.ralph/ralph_loop.sh`:

```bash
# 添加 WeNexus 特定退出条件
check_wenexus_completion() {
  # 检查所有 WeNexus 测试是否通过
  if npm run test && mvn test; then
    echo "All WeNexus tests passed - marking as complete"
    return 0
  fi
  return 1
}
```

### 3. 集成到 CI/CD

```yaml
# .github/workflows/nightly-improvements.yml
name: Nightly Ralph Improvements

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨 2 点

jobs:
  auto-improve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Ralph
        run: |
          git clone https://github.com/frankbria/ralph-claude-code.git
          cd ralph-claude-code && ./install.sh
      - name: Run Ralph
        run: |
          ralph-setup nightly-improvements
          cd nightly-improvements
          ralph --calls 200 --timeout 180
      - name: Create PR
        run: |
          git checkout -b auto/ralph-improvements-$(date +%Y%m%d)
          git add .
          git commit -m "chore: automated improvements by Ralph"
          gh pr create --title "Automated Improvements" --body "Generated by Ralph"
```

## 总结

### 何时使用 Ralph

| 场景 | 推荐度 | 理由 |
|------|--------|------|
| 大型功能开发 (3+ 小时) | ⭐⭐⭐⭐⭐ | 持续迭代、上下文保持 |
| 代码库重构 (10+ 文件) | ⭐⭐⭐⭐⭐ | 自动化、断路器保护 |
| Bug 修复马拉松 | ⭐⭐⭐⭐⭐ | 批量处理、智能退出 |
| 测试覆盖率提升 | ⭐⭐⭐⭐⭐ | 自动化测试生成 |
| PRD 到原型 | ⭐⭐⭐⭐ | 快速生成、自动导入 |
| 文档生成 | ⭐⭐⭐⭐ | 自动化、保持同步 |
| 技术债务清理 | ⭐⭐⭐⭐ | 持续改进 |
| 简单任务 (< 30 分钟) | ⭐ | 开销大于收益 |
| 需要频繁决策 | ⭐⭐ | 破坏自主性 |
| 高度创新性任务 | ⭐⭐ | 需要人类创意 |

### 核心优势

1. **7×24 持续工作** - 利用非工作时间
2. **上下文保持** - 跨会话的连贯性
3. **智能保护** - 断路器防止破坏
4. **自动化循环** - 无需人工干预
5. **任务驱动** - 优先级清晰

### 快速开始

```bash
# 1. 全局安装（一次性）
git clone https://github.com/frankbria/ralph-claude-code.git
cd ralph-claude-code && ./install.sh

# 2. 创建项目（每个任务）
ralph-import your-prd.md your-project

# 3. 启动开发（带监控）
cd your-project && ralph --monitor

# 4. 分离会话，去做其他事情
# Ctrl+B 然后 D

# 5. 稍后回来查看结果
tmux attach
```

---

**记住**: Ralph 是强大的工具，但不能替代人类判断。始终审查生成的代码，确保符合 WeNexus 的质量标准和项目目标。

**相关资源**:

- [Ralph GitHub 仓库](https://github.com/frankbria/ralph-claude-code)
- [WeNexus 代码质量标准](./code-quality.md)
- [WeNexus 提交规范](../../CLAUDE.md#review--commit-standards)
