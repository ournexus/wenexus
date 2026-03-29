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
└── docs/                         # 关于项目的各种文档，有不清楚问题时优先查阅文档
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
- **高内聚、低耦合**：短期代码必须能跑，长期人能看懂
- **单一数据源原则（SSOT）**：避免在多处维护相同信息

### 代码质量标准

- **拒绝硬编码**：使用常量、枚举或配置文件
- **拒绝过度设计**：只解决当前问题，不预设未来需求
- **拒绝 mock 测试**：优先集成测试和端到端测试
- **函数长度限制**：单个函数不超过 30 行
- **命名清晰**：函数名、变量名要自解释，减少注释需求

### 测试策略

**代码测试与 AI 测试分层**：

| 层级 | 方式 | 适用场景 |
|------|------|----------|
| CI/CD | Playwright 代码 | 关键路径回归测试，需要快、稳、可复现 |
| 探索性 | 自然语言用例 (`e2e/cases/*.yaml`) | AI 执行，发现边界问题，验证 UX |

- **关键路径**用代码测试保证稳定性（注册、登录、支付等）
- **探索性测试**用自然语言描述，让 AI 理解并执行
- E2E 测试放在独立包 `frontend/packages/e2e/`，不与应用代码混合

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

### 安全问题处理原则

- **只修复重大安全漏洞**：除非是可被直接利用的重大漏洞（如 SQL 注入、RCE），否则不主动处理安全问题
- **开发阶段优先功能**：当前阶段以功能开发和迭代为主，非重大安全问题不阻塞开发进度
- **不做预防性安全加固**：不主动添加安全相关的限制性配置（如图片域名白名单、CSP 头等），除非有明确的安全事件驱动

### 代码内文档要求

文档离代码越近越好，docstring 优于独立 md 文件。

**检查清单**（每次提交前）：

- [ ] commit 对应的技术文档已创建或更新
- [ ] 新模块有顶部注释说明用途和依赖关系
- [ ] 变更的模块注释仍然准确
- [ ] `package.json` 的 `description` 与实际功能一致
- [ ] 没有创建任何非必要的文档文件

#### 禁止行为

- 禁止创建总结性文档（如 xxx-summary.md、xxx-overview.md、xxx-guide.md）
- 禁止在 commit 中附带"顺便更新了文档"的无关改动
- 禁止创建与已有文档内容重复的新文件

#### 允许行为

- 修改代码时，同步更新同文件内的注释/docstring
- 创建 commit 对应的技术文档（按上述格式）
- 用户明确要求时，更新指定的文档文件

## 最重要的原则

**有任何不清楚的，随时提问。**

不确定时宁愿多问一句，也不要基于假设实现错误的方案。
