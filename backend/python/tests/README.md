# Python Backend 测试

## 目录结构

测试目录与源码分层一一对应：

```
tests/
├── conftest.py                # 共享 fixture
├── unit/                       # 单元测试（无外部依赖，直接跑）
│   ├── test_main.py           # 健康检查端点
│   ├── config/                # 配置层测试
│   │   └── test_settings.py   # 配置加载
│   ├── facade/                # facade 层测试
│   │   └── test_deps.py       # 认证依赖（cookie 提取）
│   ├── app/                   # app 编排层测试
│   ├── service/               # service 领域服务层测试
│   │   └── test_auth.py       # UserInfo + authenticate
│   ├── repository/            # repository 持久层测试
│   └── util/                  # util 工具层测试
└── integration/                # 集成测试（需要数据库等外部依赖）
    ├── cases.yaml             # 语义化用例
    ├── facade/
    ├── app/
    ├── service/
    ├── repository/
    └── util/
```

## 运行方式

```bash
# 运行全部单元测试
uv run pytest tests/unit/

# 运行指定层的测试
uv run pytest tests/unit/util/
uv run pytest tests/unit/facade/

# 运行集成测试（需先启动 PostgreSQL）
uv run pytest tests/integration/

# 带覆盖率
uv run pytest tests/unit/ --cov=wenexus
```

## 集成测试用例

`tests/integration/cases.yaml` 定义了 API 级别的语义测试用例。
待 API 路由实现后，根据用例编写对应的 pytest 测试文件。
