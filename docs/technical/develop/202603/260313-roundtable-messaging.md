# Roundtable 消息发送功能实现文档

**日期**: 2026-03-13
**状态**: ✅ 已完成
**涉及的层级**: Repository (新) + Service (扩展) + Facade (扩展)

## 概述

实现了 roundtable 会话中用户发送消息的完整功能，采用**混合模式**（hybrid mode）：

- **同步部分**：立即保存用户消息到数据库，返回确认
- **异步部分**：后台并发调用 OpenRouter LLM 生成专家回复

## 实现细节

### 1. Repository 层 (`repository/roundtable.py`) - 新建

四个核心函数：

#### `save_message()`

保存消息到 `discussion_message` 表。

- 支持多种 role 类型：user, participant, expert, system, fact_checker, host
- 自动生成 UUID 和时间戳
- 返回保存的消息对象（包含 ID、时间戳等）

#### `get_session_experts()`

从会话的 `expert_ids` JSON 数组中查询所有专家信息。

- 获取 id, name, role, stance, systemPrompt
- 用于生成专家回复时的上下文

#### `get_session_context()`

获取会话的完整上下文，包括：

- Topic 信息（title, description, type）
- Session 状态和模式
- 最近 10 条消息历史（用于 LLM 上下文）
- 专家 ID 列表

#### `update_session_status()`

更新会话状态（如从 `initializing` → `discussing`）

### 2. Service 层 (`service/roundtable.py`) - 扩展

#### 修复 `get_session_messages()` 函数

原实现查询错误的表（chat_message 而非 discussion_message）。现已修复为查询 `discussion_message` 表。

#### 新增 `send_message()` - 核心函数

混合模式实现：

```python
async def send_message(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    content: str,
    generate_ai_reply: bool = True,
) -> dict
```

**执行流程**：

1. **同步**：调用 `repository.save_message()` 保存用户消息
2. **同步**：更新 session 状态为 `discussing`
3. **异步**（如果 `generate_ai_reply=True`）：
   - 并发调用 `_generate_and_save_expert_response()` 处理所有分配的专家
   - 每个专家独立调用 LLM，生成回复
   - 将 AI 回复保存到数据库

**返回结构**：

```json
{
  "code": 0,
  "data": {
    "userMessage": {...},       // 用户消息对象
    "aiReplies": [...],         // 专家回复列表（可能不完整，如果 AI 仍在生成）
    "status": "success",        // success | pending
    "sessionId": "..."
  }
}
```

#### 新增 `_generate_and_save_expert_response()` - 辅助函数

为单个专家生成回复的帮助函数：

1. 调用 `util.llm.generate_expert_response()` 获取 LLM 生成的内容
2. 如果成功，调用 `save_message()` 保存到 DB
3. 捕获异常并记录日志

### 3. Util 层 (`util/llm.py`) - 新建

#### `generate_expert_response()`

调用 OpenRouter API 生成专家回复。

**参数**：

- 专家信息（name, role, stance, system_prompt）
- 会话上下文（topic, recent messages）
- 用户消息

**提示词构造**：

- System Prompt：基于专家角色和立场动态生成，或使用自定义 prompt
- Messages：最近 5 条消息 + 当前用户消息

**API 调用**：

- 使用 `httpx` 异步调用 OpenRouter v1/chat/completions
- 模型：openrouter/auto（成本优化）
- Temperature: 0.7, Max tokens: 1000

**错误处理**：

- 缺少 API Key：返回 None，记录警告
- HTTP 错误：记录错误，返回 None
- 异常：捕获并记录

### 4. Facade 层 (`facade/roundtable.py`) - 扩展

#### 新增 POST 端点 `/sessions/{session_id}/messages`

**请求体**：

```json
{
  "content": "用户消息内容",
  "generate_ai_reply": true   // 可选，默认 true
}
```

**验证**：

- 检查会话是否存在（404）
- 验证用户权限（403）

**返回**：

- 200: 成功
- 404: 会话不存在
- 403: 用户无权限

## 工作流示例

1. 用户调用 `POST /api/v1/roundtable/sessions/{id}/messages`
2. 后端立即：
   - 保存用户消息到 `discussion_message` 表
   - 更新 session 状态为 `discussing`
   - 返回 200 + 用户消息对象
3. 同时（后台异步）：
   - 获取会话的所有专家
   - 并发调用 OpenRouter LLM（无需等待）
   - 保存每个专家的回复到数据库
4. 前端可以立即显示用户消息，然后轮询 `GET /messages` 获取新增的专家回复

## 混合模式的好处

- ✅ **低延迟**：用户消息立即保存，无需等待 AI 生成
- ✅ **更好的 UX**：立即反馈 + 渐进式显示专家回复
- ✅ **可扩展**：多个专家回复并发生成，互不阻塞
- ✅ **容错性**：单个专家 LLM 失败不影响其他回复

## 数据库架构

### discussion_message 表

```sql
CREATE TABLE discussion_message (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES discussion_session(id),
  expert_id TEXT REFERENCES expert(id),
  user_id TEXT REFERENCES "user"(id),
  role message_role NOT NULL,  -- expert, host, participant, system, fact_checker
  content TEXT NOT NULL,
  thread_ref TEXT,             -- 回复的消息 ID
  citations JSONB,             -- 引用的来源
  status TEXT DEFAULT 'active',
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 测试覆盖

已编写集成测试（`tests/integration/service/test_roundtable_messaging.py`）：

1. **test_send_message_saves_user_message**
   - 验证用户消息被保存到数据库
   - 验证返回的消息对象结构

2. **test_send_message_updates_session_status**
   - 验证会话状态从 `initializing` → `discussing`

**运行测试**：

```bash
cd backend/python && uv run pytest tests/integration/service/test_roundtable_messaging.py -v
```

**结果**：✅ 2 passed

## 后续工作

1. **前端集成**：在 UI 中调用 `/sessions/{id}/messages` 端点
2. **WebSocket 实时更新**：使用 WebSocket 推送新消息，而非轮询
3. **消息流式响应**：支持 Server-Sent Events (SSE) 实时显示 AI 生成过程
4. **错误恢复**：实现重试机制处理暂时性的 LLM API 失败
5. **配置优化**：根据会话模式（autopilot/host/participant）调整 expert 选择逻辑

## 环境配置

确保 `.env.development` 包含：

```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DATABASE_URL=postgresql+asyncpg://wenexus:wenexus_dev_pwd@localhost:5432/wenexus_dev
REDIS_URL=redis://localhost:6379/0
```

## 参考资源

- OpenRouter API 文档：<https://openrouter.ai/docs>
- 数据库 schema：`frontend/apps/web/src/config/db/schema.postgres.ts`
- 本项目六层架构：`docs/technical/develop/202603/260308-auth-system-design.md`
