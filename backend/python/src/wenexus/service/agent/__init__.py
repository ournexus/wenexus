"""
service.agent - Agent 服务层。

Agent 作为 Service 的实现，通过 BaseAgent 统一接口、AgentRegistry 注册/发现/调度。
支持 Functional Agent（各有独立实现）和 Persona Agent（配置驱动）两类。

Depends: model.agent, langgraph, langchain
Consumers: app.agent_registry, facade
"""
