"""
app - 应用编排层，组合多个 service 完成业务用例。

职责: 编排领域服务、事务管理、权限检查。
依赖方向: app → service
禁止: 直接访问 repository 层或处理 HTTP 细节。
"""
