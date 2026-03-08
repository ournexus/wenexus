"""
backend/python/tests — WeNexus Python Backend 测试

测试结构：
    tests/
    ├── conftest.py           # 共享 fixture（DB session, test client）
    ├── unit/                  # 单元测试（不依赖外部服务）
    │   ├── test_config.py     # 配置加载测试
    │   └── test_health.py     # 健康检查端点测试
    └── integration/           # 集成测试
        └── cases.yaml         # 语义化用例（API 实现后编写 pytest）

运行方式：
    cd backend/python
    python3 -m pytest tests/unit/        # 运行单元测试
    python3 -m pytest --cov=wenexus      # 带覆盖率
"""
