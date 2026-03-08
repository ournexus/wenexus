"""
service - 领域服务层，封装核心业务逻辑。

职责: 单一领域的业务规则、数据转换、领域事件。
依赖方向: service → repository
禁止: 依赖 facade/app 层或直接处理 HTTP。
"""
