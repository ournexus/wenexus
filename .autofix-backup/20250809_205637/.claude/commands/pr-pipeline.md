---
allowed-tools: [Bash(git:*), Bash(gh:*), Read(*), Write(*), Edit(*), LS(*), Glob(*), Grep(*)]
description: 完整的PR流程管理：检查变更合理性、合并主分支、创建有意义的提交、发起PR
version: '1.0.0'
created: '2025-08-09'
updated: '2025-08-09'
changelog:
  - version: '1.0.0'
    date: '2025-08-09'
    changes: ['初始版本：完整的PR流程管理命令']
---

# PR Pipeline Command

这个命令提供了一个完整的Pull Request流程管理，包括：

1. 检查当前变更的合理性
2. 智能合并主分支变更
3. 创建有意义的提交信息
4. 发起结构化的Pull Request

## 使用方法

/pr-pipeline [feature-description] [options]

### 参数说明

- `feature-description`: 功能描述（可选，用于自动生成提交信息）
- 选项：
  - `--draft`: 创建草稿PR
  - `--reviewer <username>`: 指定审查者
  - `--label <label>`: 添加标签
  - `--skip-tests`: 跳过测试运行
  - `--force`: 强制推送（谨慎使用）

## 工作流程

### 1. 变更检查阶段

- 检查当前分支状态
- 分析变更文件的合理性
- 验证代码质量（通过预提交钩子）
- 评估测试覆盖率

### 2. 主分支同步阶段

- 获取最新的主分支变更
- 智能合并策略（rebase优先）
- 处理合并冲突
- 保持提交历史的整洁

### 3. 提交创建阶段

- 基于变更内容生成有意义的提交信息
- 遵循Conventional Commits规范
- 自动分类变更类型（feat/fix/docs等）
- 智能识别变更范围

### 4. PR发起阶段

- 创建结构化的PR描述
- 自动关联相关Issue
- 设置合适的标签和审查者
- 提供测试说明和检查清单

## 实际使用示例

### 基本使用

```
/pr-pipeline "添加用户认证功能"
```

### 高级使用

```
/pr-pipeline "重构数据验证逻辑" --draft --reviewer @tech-lead --label enhancement
```

### 紧急修复

```
/pr-pipeline "修复生产环境安全漏洞" --label security --reviewer @security-team
```

## 智能特性

### 自动变更分析

- 检测变更类型（功能/修复/重构）
- 识别影响的模块范围
- 评估潜在风险等级
- 建议最佳实践

### 提交信息生成

基于变更内容自动生成符合规范的提交信息：

- 分析文件变更模式
- 提取关键功能描述
- 智能分类变更类型
- 生成清晰的提交说明

### 冲突解决助手

- 提供合并冲突的详细分析
- 建议解决策略
- 保留重要变更
- 维护代码完整性

### PR模板定制

根据变更类型自动生成合适的PR模板：

- 功能开发模板
- Bug修复模板
- 重构模板
- 文档更新模板

## 错误处理

### 常见问题及解决方案

1. **测试失败**
   - 自动运行修复脚本
   - 提供详细的错误报告
   - 建议修复方案

2. **合并冲突**
   - 识别冲突文件
   - 提供三方合并工具
   - 逐步解决指导

3. **权限问题**
   - 检查GitHub Token配置
   - 验证仓库权限
   - 提供权限申请指导

4. **网络问题**
   - 重试机制
   - 离线模式支持
   - 进度保存

## 配置选项

### 个性化设置

可以在项目根目录创建 `.pr-pipeline.yaml` 文件进行个性化配置：

```yaml
# 默认审查者
default_reviewers:
  - @tech-lead
  - @senior-dev

# 自动标签
auto_labels:
  feature: enhancement
  fix: bug
  docs: documentation

# 提交模板
commit_templates:
  feature: "feat({scope}): {description}"
  fix: "fix({scope}): {description}"
  docs: "docs({scope}): {description}"

# 测试配置
run_tests: true
fail_on_low_coverage: false
min_coverage: 80
```

## 集成支持

### CI/CD集成

- 自动触发GitHub Actions
- 与现有测试流程集成
- 支持多种CI平台

### 通知系统

- Slack集成
- 邮件通知
- GitHub通知

### 报告生成

- 变更影响报告
- 代码质量报告
- 测试覆盖率报告

## 安全考虑

### 敏感信息检测

- 自动扫描密钥和token
- 防止意外提交敏感文件
- 提供清理建议

### 权限验证

- 验证用户权限
- 检查分支保护规则
- 确保符合安全策略

## 故障排除

### 调试模式

```
/pr-pipeline --debug
```

### 手动回滚

```
# 回滚到上一个稳定状态
git reset --hard HEAD~1
git push --force-with-lease
```

### 日志查看

```
cat .pr-pipeline.log
```

## 扩展性

### 插件系统

支持自定义插件扩展：

- 自定义检查规则
- 特殊项目需求
- 团队特定流程

### 钩子机制

- 预提交钩子
- 后提交钩子
- PR创建钩子

这个命令将大大简化您的PR流程，确保高质量的代码提交和有效的团队协作。
