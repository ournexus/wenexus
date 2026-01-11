# 知识工程驱动的项目管理

AI 时代的软件工程本质上是**知识工程**。本文档描述 WeNexus 项目如何管理知识的输入、沉淀和传输。

## 核心理念

```
知识输入 → 知识沉淀 → 知识传输
   ↓           ↓           ↓
AI/人理解项目  代码变更时捕获  AI/人高效获取
```

**关键原则**：把知识放在代码变更时必须触碰的地方，而不是独立维护文档。

## 知识输入：AI 如何理解项目

### 入口文件

| 文件 | 用途 | 维护方式 |
|------|------|----------|
| `CLAUDE.md` | AI 开发指南，项目架构和开发原则 | 人工维护（精简） |
| `README.md` | 项目概览，快速启动 | 人工维护 |
| 模块 `index.ts` / `__init__.py` | 模块用途和依赖关系 | 代码变更时强制更新 |

### AI 自助探索

AI 可以通过以下方式自主了解项目：

```bash
# 目录结构
tree -L 3 -I 'node_modules|.git|dist|.next'

# 查找特定文件
find . -name "*.ts" -path "*/src/*" | head -20

# Git 历史
git log --oneline -20
git log --oneline --all --graph

# 搜索代码
grep -r "关键词" --include="*.ts" src/
```

## 知识沉淀：代码变更时自动捕获

### 模块注释规范

每个模块入口文件必须包含标准注释：

**TypeScript (`index.ts`)**：

```typescript
/**
 * @module @wenexus/模块名
 * @description 一句话描述模块用途
 * @depends 依赖的其他模块
 * @consumers 被哪些模块使用
 */
```

**Python (`__init__.py`)**：

```python
"""
模块名 - 一句话描述模块用途

依赖: 列出依赖的其他模块
被依赖: 列出使用此模块的其他模块
"""
```

### Pre-commit 强制检查

`check-module-docs.sh` 脚本在提交时检查：

- `index.ts` 是否有 `@module` / `@description`
- `__init__.py` 是否有 docstring
- `package.json` 是否有 `description`

### Commit Message 规范

使用 Conventional Commits，建议包含 Why/What：

```
feat(auth): add JWT refresh token

Why: 原 token 过期后用户需要重新登录，体验差
What: 添加 refresh token 机制，自动续期
```

## 知识传输：高效获取

### 不需要的东西

| 传统做法 | 为什么不需要 |
|---------|-------------|
| 手动 CHANGELOG | Git 历史本身就是 changelog，AI 可按需生成 |
| 独立 API 文档 | 代码注释 + 类型定义即文档 |
| 架构图文件 | 目录结构 + 模块注释即架构 |
| 知识索引文件 | AI 可用 `tree`/`find`/`grep` 自主探索 |

### 需要的东西

| 做法 | 原因 |
|------|------|
| `CLAUDE.md` | AI 入口，精简的开发指南 |
| 模块注释 | 嵌入代码，变更时必须触碰 |
| ADR（可选） | 重大决策记录，解释"为什么" |

## 架构决策记录（ADR）

对于重大技术决策，可在 `docs/decisions/` 创建 ADR：

```markdown
# ADR-001: 选择 pnpm 作为前端包管理器

## 状态
Accepted

## 背景
需要选择前端包管理器，候选：npm、yarn、pnpm

## 决策
选择 pnpm

## 原因
- 磁盘空间效率高（硬链接）
- 严格的依赖解析（避免幽灵依赖）
- Monorepo 支持好

## 后果
- 团队需要安装 pnpm
- CI/CD 需要配置 pnpm
```

## 实践检查清单

### 创建新模块时

- [ ] 在 `index.ts` / `__init__.py` 添加标准注释
- [ ] 在 `package.json` 添加 `description`
- [ ] 如果是重大架构变更，考虑创建 ADR

### 修改现有模块时

- [ ] 检查模块注释是否仍然准确
- [ ] Commit message 包含变更原因

### 代码审查时

- [ ] 新模块有完整的模块注释
- [ ] 变更的模块注释已更新
- [ ] 重大决策有 ADR 或 commit message 说明原因

## 总结

```
┌─────────────────────────────────────────────────────────┐
│                    知识工程原则                          │
├─────────────────────────────────────────────────────────┤
│ 1. 知识嵌入代码，不独立维护                              │
│ 2. 变更时强制更新，不依赖主动维护                        │
│ 3. AI 可自主探索，不需要索引文件                         │
│ 4. 精简入口文档，不堆砌信息                              │
└─────────────────────────────────────────────────────────┘
```
