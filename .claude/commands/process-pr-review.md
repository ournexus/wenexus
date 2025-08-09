---
allowed-tools: [Bash(git:*), Bash(gh:*), Read(*), Write(*), Edit(*), LS(*), Glob(*), Grep(*)]
description: 智能处理PR代码审查意见，支持指定PR编号或自动获取最新PR审查意见
version: '3.0.0'
created: '2024-12-09'
updated: '2024-12-09'
changelog:
  - version: '3.0.0'
    date: '2024-12-09'
    changes:
      [
        '简化为LLM指导文档，移除具体代码实现',
        '专注于操作流程和策略指导',
        '提供清晰的任务分解和检查清单',
      ]
---

# Process PR Review - 智能PR审查处理指南

当需要处理GitHub PR的代码审查意见时，使用此指南来系统性地分析和处理审查建议。

## 🚀 快速操作流程

### 1. 获取PR审查数据

使用GitHub CLI获取审查意见：

```bash
# 获取指定PR的评论
gh api repos/:owner/:repo/pulls/{PR_NUMBER}/comments --jq '.[] | {id: .id, user: .user.login, path: .path, line: .line, body: .body}'

# 获取reviews
gh api repos/:owner/:repo/pulls/{PR_NUMBER}/reviews --jq '.[] | {id: .id, user: .user.login, state: .state, body: .body}'
```

### 2. 智能分类审查意见

#### 📊 评论类型分类

- **代码风格**: format, style, lint, prettier, black, isort
- **Bug修复**: bug, fix, error, exception, fail, crash
- **文档更新**: documentation, doc, readme, comment, explain
- **性能优化**: performance, optimize, slow, fast, efficient
- **安全问题**: security, vulnerability, safe, inject, secret
- **架构改进**: architecture, design, pattern, refactor
- **测试相关**: test, testing, coverage, unit test

#### ⚡ 优先级分级

- **P0 阻塞**: blocking, must fix, critical, security vulnerability
- **P1 高优先级**: high priority, important, should fix
- **P2 中优先级**: medium, consider, suggest, could
- **P3 低优先级**: optional, nice to have, improvement

### 3. 处理策略制定

#### 🔧 自动修复（安全操作）

**可自动修复的问题**:

- 代码格式化（Prettier, Black, Google Java Format）
- 导入排序（isort）
- 简单的lint规则修复
- 尾随空格和换行符问题

**执行步骤**:

1. 检查项目类型（package.json, pyproject.toml, pom.xml）
2. 运行相应的格式化工具
3. 验证修复结果

#### 🤝 交互式处理（人工决策）

**需要人工判断的问题**:

- 逻辑和算法优化
- 架构设计建议
- 性能优化方案
- 安全漏洞修复
- 测试用例补充

**处理流程**:

1. 逐条展示审查意见
2. 显示代码上下文
3. 提供处理选项：
   - ✅ 标记为已处理
   - 📝 添加到待办事项
   - ❓ 需要进一步讨论
   - ⏭️ 跳过本次处理

## 📋 详细操作清单

### 阶段1：数据收集

- [ ] 获取PR编号（指定或最新）
- [ ] 拉取所有审查评论和reviews
- [ ] 解析并分类每条审查意见
- [ ] 评估可自动修复性

### 阶段2：智能分析

- [ ] 按类型统计审查意见
- [ ] 按优先级排序处理
- [ ] 识别可自动修复项
- [ ] 生成分析报告

### 阶段3：处理执行

- [ ] 执行自动修复（格式化、lint等）
- [ ] 交互式处理复杂意见
- [ ] 记录处理结果
- [ ] 生成处理报告

### 阶段4：后续操作

- [ ] 运行测试确保功能正常
- [ ] 提交处理后的修改
- [ ] 推送代码到远程
- [ ] 重新请求代码审查
