"""
repository.model.base - SQLAlchemy ORM 基类。

Depends: sqlalchemy
Consumers: repository.model.fact_report 及未来所有 ORM 模型
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""

    pass
