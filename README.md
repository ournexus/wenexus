<div align="center">
  <img src="docs/design/logos/wenexus-logo-complete.svg" alt="WeNexus Logo" width="120" height="120">

# WeNexus: The Consensus Amplifier

_Connecting minds, building consensus, amplifying understanding_

</div>

WeNexus is a platform designed to bridge information gaps and create meaningful connections in an
age of information overload and polarizing echo chambers. We don't just need another network; we
need a Nexus - a central point where We, as a society, can finally connect, understand, and agree.

## Project Structure

This is a monorepo containing all WeNexus applications and services:

```
wenexus/
├── frontend/               # Frontend monorepo (npm workspaces + Turborepo)
│   ├── apps/
│   │   ├── web/           # Main web application (Next.js)
│   │   ├── admin/         # Admin dashboard (Next.js)
│   │   └── mobile/        # Mobile application (React Native)
│   ├── packages/
│   │   ├── ui/            # Shared UI components
│   │   ├── shared/        # Common utilities and hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── .pre-commit-config.yaml  # Frontend-specific hooks
│
├── backend/                # Backend services
│   ├── java/              # Java microservices (Spring Boot + Maven)
│   │   ├── core-service/
│   │   ├── user-service/
│   │   ├── content-service/
│   │   ├── consensus-service/
│   │   └── .pre-commit-config.yaml  # Java-specific hooks
│   └── python/            # Python services (FastAPI + AI/ML)
│       ├── src/
│       ├── tests/
│       └── .pre-commit-config.yaml  # Python-specific hooks
│
├── docs/                   # Documentation
│   ├── design/            # Design specifications and assets
│   ├── prd/               # Product requirements documents
│   ├── technical/         # Technical specifications
│   └── changelog/         # Release notes and change logs
├── tools/                  # Development tools and scripts
└── .github/                # GitHub workflows and templates
```

## Getting Started

### Prerequisites

- Node.js 20+
- pnpm 9+ (`npm install -g pnpm`)
- Docker & Docker Compose（本地数据库）
- Java 17+（仅 Java 后端开发需要）
- Python 3.11+ & uv（仅 Python 后端开发需要）

### 一键本地启动

```bash
# 启动全部（数据库 + 前端 + Python 后端）
./scripts/dev.sh

# 仅启动数据库 + 前端
./scripts/dev.sh frontend

# 停止所有服务
./scripts/dev.sh stop
```

脚本会自动完成：数据库就绪检测、依赖安装、已有进程的优雅关闭与重启。
日志输出到 `scripts/logs/`。

> **首次运行**：若 `frontend/apps/web/.env.development` 不存在，脚本会自动从
> `.env.example` 创建，但需要手动填写 `AUTH_SECRET`：
>
> ```bash
> openssl rand -base64 32
> ```

启动成功后访问：

| 服务 | 地址 |
|------|------|
| 前端 | <http://localhost:3000> |
| Python API | <http://localhost:8000/docs> |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

### Available Scripts（根目录）

| 命令 | 说明 |
|------|------|
| `pnpm frontend:dev` | 启动前端开发服务器 |
| `pnpm frontend:build` | 构建所有前端应用 |
| `pnpm backend:java:build` | 构建 Java 服务 |
| `pnpm backend:python:dev` | 启动 Python 开发服务器 |
| `pnpm precommit` | 手动运行所有 pre-commit hooks |

## Deployment

部署文档见 [`docs/technical/deployment/`](docs/technical/deployment/)：

- [Cloudflare Workers 部署](docs/technical/deployment/cloudflare-workers.md)

## Architecture Overview

WeNexus follows a microservices architecture with:

- **Frontend**: Next.js applications with TypeScript, managed by Turborepo
- **Backend**: Java services (Spring Boot) for core business logic, Python services (FastAPI) for AI/ML
- **Shared Packages**: Common UI components and utilities across frontend apps

## Pre-commit Hooks

Each technology stack has its own pre-commit configuration:

| Stack | Config Location | Hooks |
|-------|-----------------|-------|
| **Global** | `.pre-commit-config.yaml` | YAML/JSON validation, secrets detection, conventional commits |
| **Frontend** | `frontend/.pre-commit-config.yaml` | ESLint, Prettier, TypeScript |
| **Java** | `backend/java/.pre-commit-config.yaml` | Google Java Format, Checkstyle, SpotBugs |
| **Python** | `backend/python/.pre-commit-config.yaml` | Ruff, mypy |

## Contributing

[Contributing guidelines will be added]

## License

[License information will be added based on project requirements]
