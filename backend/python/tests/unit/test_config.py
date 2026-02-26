"""
单元测试 — 配置加载。

验证环境变量和配置项正确加载。
"""
import pytest


def test_config_loads_without_error() -> None:
    """配置类应能成功实例化。"""
    from wenexus.config import Settings

    settings = Settings()
    assert settings is not None


def test_config_has_required_fields() -> None:
    """配置应包含必要字段。"""
    from wenexus.config import Settings

    settings = Settings()
    # 数据库 URL 必须存在
    assert hasattr(settings, "database_url") or hasattr(settings, "DATABASE_URL")
