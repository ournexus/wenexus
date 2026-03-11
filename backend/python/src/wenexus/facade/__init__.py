"""
facade - API 网关层，处理 HTTP 请求路由和响应格式化。

职责: 接收外部请求、参数校验、调用 app 层、返回 HTTP 响应。
依赖方向: facade → app → service → repository
共享依赖: facade.deps 提供认证相关的 FastAPI Depends。
"""
