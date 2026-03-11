"""
repository - 数据持久层，封装所有数据库访问。

职责: SQL 查询、ORM 操作、数据存取、连接管理 (db.py)。
依赖方向: repository → config (基础设施)
禁止: 包含业务逻辑或依赖上层模块。
"""
