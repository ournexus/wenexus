# Python Backend 测试

## 目录结构

```
tests/
├── conftest.py           # 共享 fixture
├── unit/                  # 单元测试（无外部依赖，直接跑）
│   ├── test_config.py
│   └── test_health.py
└── integration/           # 集成测试
    └── cases.yaml         # 语义化用例（API 实现后编写对应 pytest）
```

## 运行方式

```bash
# 运行单元测试
python3 -m pytest tests/unit/

# 带覆盖率
python3 -m pytest tests/unit/ --cov=wenexus
```

## 集成测试用例

`tests/integration/cases.yaml` 定义了 API 级别的语义测试用例。
待 API 路由实现后，根据用例编写对应的 pytest 测试文件。
