"""
service.discovery - Discovery 域服务层。

当前无复杂业务逻辑，数据访问已下沉到 repository.discovery。
编排逻辑由 app.discovery 处理。

Depends: repository.discovery
Consumers: app.discovery
"""
