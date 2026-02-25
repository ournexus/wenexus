# CLAUDE.md

项目开发指南和 AI 辅助编程最佳实践。

## 应用架构

**Monorepo 结构**：全栈应用，包含 Java 后端（Spring Boot 微服务）、Python 后端（FastAPI + AI/ML）和 Next.js/React Native 前端。

### 核心概念

- **技术方案文档**：`docs/technical` - 架构决策和实现方案
- **前端共享包**：`frontend/packages` - UI 组件、类型定义、工具函数
- **后端服务**：`backend/java` + `backend/python` - 微服务架构

### 目录结构

```
wenexus/
├── frontend/                     # 前端 Monorepo (pnpm + Turborepo)
│   ├── apps/
│   │   ├── web/                 # 主 Web 应用 (Next.js)
│   │   ├── admin/               # 管理后台 (Next.js)
│   │   └── mobile/              # 移动端 (React Native)
│   └── packages/
│       ├── ui/                  # 共享 UI 组件
│       ├── types/               # TypeScript 类型定义
│       ├── utils/               # 工具函数
│       └── shared/              # 通用 hooks 和配置
│
├── backend/                      # 后端服务
│   ├── java/                    # Java 微服务 (Spring Boot + Maven)
│   │   ├── core-service/        # 核心业务逻辑
│   │   ├── user-service/        # 用户管理
│   │   ├── content-service/     # 内容管理
│   │   └── consensus-service/   # 共识算法
│   └── python/                  # Python 服务 (FastAPI + AI/ML)
│       └── src/
│           ├── facade/          # API 网关层
│           ├── app/             # 应用层
│           ├── service/         # 领域服务层
│           ├── repository/      # 数据持久层
│           └── model/           # 数据模型
│
└── docs/                         # 文档
    └── technical/               # 技术方案和架构决策
```

### 架构原则

- **分层清晰**：
  - `facade` → `app` → `service` → `repository`
  - 依赖方向单向，不反向依赖
- **配置与实例分离**：配置管理 what to create，实例池管理 when to create
- **契约先行**：API 实现必须严格遵循类型定义

## 常用开发命令

### 前端开发

```bash
cd frontend
pnpm install                     # 安装依赖
pnpm dev                         # 启动开发服务器
pnpm build                       # 构建生产版本
pnpm lint                        # 代码检查
pnpm typecheck                   # 类型检查
```

### Java 后端

```bash
cd backend/java
mvn clean install                # 构建所有服务
mvn spring-boot:run -pl core-service  # 启动指定服务
mvn test                         # 运行测试
```

### Python 后端

```bash
cd backend/python
uv sync --dev                    # 安装依赖
uv run uvicorn src.main:app --reload  # 启动开发服务器
uv run pytest                    # 运行测试
uv run ruff format .             # 格式化代码
uv run ruff check --fix .        # 代码检查
```

### 代码质量

```bash
pre-commit run --all-files       # 运行所有 pre-commit hooks
```

## 开发原则

### 核心理念

- **程序 = 算法 + 数据结构**：编程的核心是控制数据的流动
- **高内聚、低耦合**：短期代码能跑，长期人能看懂
- **单一数据源原则（SSOT）**：避免在多处维护相同信息

### 代码质量标准

- **拒绝硬编码**：使用常量、枚举或配置文件
- **拒绝过度设计**：只解决当前问题，不预设未来需求
- **拒绝 mock 测试**：优先集成测试和端到端测试
- **函数长度限制**：单个函数不超过 30 行
- **命名清晰**：函数名、变量名要自解释，减少注释需求

### 安全问题处理原则

- **只修复重大安全漏洞**：除非是可被直接利用的重大漏洞（如 SQL 注入、RCE），否则不主动处理安全问题
- **开发阶段优先功能**：当前阶段以功能开发和迭代为主，非重大安全问题不阻塞开发进度
- **不做预防性安全加固**：不主动添加安全相关的限制性配置（如图片域名白名单、CSP 头等），除非有明确的安全事件驱动

## AI 工作原则

### 必须完成端到端验证

代码开发后，必须自己完成完整验证，包括：

1. **启动应用**：使用实际启动命令，不能只写代码
2. **检查启动日志**：确保无错误、无警告
3. **验证接口功能**：
   - 使用 curl 或实际前端测试 API
   - 验证返回数据结构符合预期
   - 测试正常流程和异常流程
4. **确认集成正确**：检查日志中的相关信息
5. **只有全部通过后才交给用户最终验证**

**推荐 TDD 方式**：先写测试，再实现功能，确保端到端验证。

**禁止行为**：

- 写完代码就认为任务完成
- 依赖用户进行基本测试
- 假设代码能运行而不实际验证

### 工作流程建议

1. **理解需求**：先提问澄清，避免返工
2. **分解任务**：使用 TodoWrite 跟踪进度
3. **先读后写**：修改代码前必须先读取文件
4. **分步验证**：每完成一个功能点就验证
5. **查阅文档**：遇到不确定的 API 契约，查看 `docs/technical` 下的文档

### 文档规则（强制）

#### 文档权限

| 目录 | 权限 | 说明 |
|------|------|------|
| `docs/theory/` | 只读 | AI 不得创建或修改 |
| `docs/prd/` | 只读 | AI 不得创建或修改 |
| `docs/design/` | 只读 | AI 不得创建或修改 |
| `docs/technical/` | 受控写入 | 仅在对应代码变更时更新，见下方规则 |
| `docs/changelog/` | 受控写入 | 仅在用户明确要求时更新 |

#### 技术文档与 commit 的对应关系

**一次 commit 对应一份技术文档**。每个有意义的代码变更都必须在 `docs/technical/` 下有对应的文档记录，格式：

```
docs/technical/YYMMDD-简短描述.md
```

**注意**：

- 纯格式化、typo 修复等trivial commit 不需要对应文档
- 一个功能如果拆成多个 commit，共用一份文档，在文档中追加更新即可
- 文档在第一个相关 commit 时创建，后续 commit 追加内容而非新建文件

#### 禁止行为

- 禁止在 `docs/` 下新建文件，除非是上述 commit 对应的技术文档或用户明确要求
- 禁止创建总结性文档（如 xxx-summary.md、xxx-overview.md、xxx-guide.md）
- 禁止在 commit 中附带"顺便更新了文档"的无关改动
- 禁止创建与已有文档内容重复的新文件

#### 允许行为

- 修改代码时，同步更新同文件内的注释/docstring
- 创建 commit 对应的技术文档（按上述格式）
- 用户明确要求时，更新指定的文档文件

#### 代码内文档要求

**核心原则**：文档离代码越近越好，docstring 优于独立 md 文件。

修改以下文件时，**必须**同步更新对应注释：

| 文件类型 | 要求 |
|---------|------|
| `package.json` | 更新 `description` 字段 |
| `**/index.ts` | 更新模块顶部 JSDoc 注释 |
| `**/__init__.py` | 更新模块顶部 docstring |
| 新建目录 | 创建 `README.md` 说明用途 |
| 目录内文件变更 | 同步更新该目录的 `README.md` |

**模块注释模板**：

```typescript
// TypeScript 模块 (index.ts)
/**
 * @module 模块名
 * @description 一句话描述模块用途
 * @depends 依赖的其他模块
 * @consumers 被哪些模块使用
 */
```

```python
# Python 模块 (__init__.py)
"""
模块名 - 一句话描述模块用途

依赖: 列出依赖的其他模块
被依赖: 列出使用此模块的其他模块
"""
```

**检查清单**（每次提交前）：

- [ ] commit 对应的技术文档已创建或更新
- [ ] 新模块有顶部注释说明用途和依赖关系
- [ ] 变更的模块注释仍然准确
- [ ] `package.json` 的 `description` 与实际功能一致
- [ ] 没有创建任何非必要的文档文件

## 最重要的原则

**有任何不清楚的，随时提问。**

不确定时宁愿多问一句，也不要基于假设实现错误的方案。
