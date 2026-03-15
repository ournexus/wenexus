# 前端消息集成和WebSocket实时更新实现文档

**日期**: 2026-03-13
**状态**: ✅ 已完成
**功能**: 消息输入UI + WebSocket实时更新 + 轮询Fallback

## 概述

完成了 Roundtable 消息发送的前端集成和实时更新机制：

- **前端消息UI**：消息输入框、发送功能、实时显示
- **WebSocket实时推送**：实时消息更新、自动重连、Fallback轮询
- **混合通信**：优先使用WebSocket，降级到轮询

## 实现细节

### 1. 前端消息发送UI

#### API代理路由

**文件**: `frontend/apps/web/src/app/api/domains/roundtable/messages/send/route.ts` (新建)

功能：

- 接收客户端消息请求 (sessionId, content, generateAiReply)
- 验证用户认证（使用better-auth）
- 转发到Python后端 `/api/v1/roundtable/sessions/{sessionId}/messages`
- 返回统一格式响应

特点：

- 支持 Server Component 中的认证验证
- 自动传递session token（通过Cookie）
- 错误处理和响应转换

#### 消息输入组件

**文件**: `frontend/apps/web/src/app/[locale]/(roundtable)/roundtable/[topicId]/message-input.tsx` (新建)

功能：

- 文本输入框（支持自动高度调整）
- 发送按钮
- 快捷键支持（Ctrl+Enter / Cmd+Enter）
- 加载状态和错误提示
- 禁用状态管理

特点：

```typescript
interface MessageInputProps {
  sessionId: string;
  onMessageSent?: (message: {
    userMessage: any;
    aiReplies: any[];
    status: string;
  }) => void;
  disabled?: boolean;
}
```

#### 服务函数

**文件**: `frontend/apps/web/src/domains/roundtable/services/chat-service.ts` (修改)

新增函数：

```typescript
export async function sendMessage(
  sessionId: string,
  content: string,
  generateAiReply: boolean = true
): Promise<SendMessageResult>
```

功能：

- 调用前端API代理路由
- 处理响应和错误
- 返回完整的消息结果对象

#### 客户端页面集成

**文件**: `frontend/apps/web/src/app/[locale]/(roundtable)/roundtable/[topicId]/roundtable-client.tsx` (修改)

修改项：

1. 导入 `MessageInput` 组件和 `useWebSocket` hook
2. 添加轮询管理（Fallback当WebSocket不可用时）
3. 实现 `handleMessageSent` 处理消息发送回调
4. 集成WebSocket连接管理
5. 在JSX中添加消息输入框和连接状态指示器

流程：

```
用户输入消息
  ↓
点击发送 → MessageInput组件
  ↓
POST /api/domains/roundtable/messages/send
  ↓
API路由转发 → Python后端
  ↓
返回 {userMessage, aiReplies, status}
  ↓
立即显示userMessage
  ↓
如果status="pending" → 启动轮询获取aiReplies
  ↓
如果WebSocket连接 → 实时接收aiReplies更新
```

### 2. WebSocket实时更新

#### 后端WebSocket端点

**文件**: `backend/python/src/wenexus/facade/roundtable.py` (修改)

新增路由：

```python
@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(session_id, websocket, user, db)
```

功能：

- 验证用户权限和会话存在
- 接受WebSocket连接
- 广播新消息给所有连接的客户端
- 处理连接断开和错误

特点：

- 支持FastAPI依赖注入
- 自动权限检查
- 完整的错误处理

#### 连接管理器

**文件**: `backend/python/src/wenexus/util/websocket.py` (新建)

类：`ConnectionManager`

功能：

```python
class ConnectionManager:
    async def connect(session_id, websocket)     # 接受连接
    def disconnect(session_id, websocket)       # 移除连接
    async def broadcast(session_id, message)    # 广播消息
    get_connection_count(session_id) -> int     # 获取连接数
```

特点：

- 管理会话级别的连接池
- 自动清理断线客户端
- 无需外部依赖（纯FastAPI）

#### 消息广播

在 `send_message_endpoint` 后调用：

```python
await ws_manager.broadcast(session_id, {
    "type": "new_message",
    "message": result["data"]["userMessage"]
})
```

### 3. 前端WebSocket Hook

**文件**: `frontend/apps/web/src/shared/hooks/use-websocket.ts` (新建)

Hook定义：

```typescript
export function useWebSocket(
  sessionId: string,
  onMessage: (msg: WebSocketMessage) => void,
  onError?: (error: string) => void,
  options?: UseWebSocketOptions
)
```

返回值：

```typescript
{
  connected: boolean,           // 连接状态
  error: string | null,        // 错误消息
  send: (message: any) => void, // 发送消息
  disconnect: () => void,       // 断开连接
  connect: () => void          // 重新连接
}
```

功能：

1. **自动连接**：组件挂载时自动连接
2. **自动重连**：连接断开时自动重连（指数退避）
3. **心跳保活**：每30秒发送ping包
4. **错误恢复**：连接失败时调用onError回调
5. **自动清理**：组件卸载时断开连接

WebSocket URL：

```
ws://localhost:3000/api/v1/roundtable/ws/sessions/{sessionId}
```

消息类型：

```typescript
type WebSocketMessage =
  | { type: 'connected'; sessionId: string; message: string }
  | { type: 'new_message'; message: any }
  | { type: 'session_updated'; session: any }
  | { type: 'pong' }
  | { type: 'error'; message: string }
```

### 4. 消息流程整合

#### 同步流程（用户消息）

```
用户输入 → 按发送
  ↓
MessageInput调用 sendMessage()
  ↓
POST /api/domains/roundtable/messages/send
  ↓
返回 { code: 0, data: { userMessage, ... } }
  ↓
立即更新UI显示userMessage
```

#### 异步流程（AI回复）

```
后端 send_message() 保存用户消息
  ↓
返回 { status: "pending", aiReplies: [] }
  ↓
前端启动轮询或等待WebSocket
  ↓
后端异步生成AI回复
  ↓
保存到discussion_message表
  ↓
**通过WebSocket广播 new_message 事件** ✨
  ↓
或通过轮询 GET /messages 获取
  ↓
前端实时更新消息列表
```

## 关键特性

### 1. 混合通信模式

**优先级**：

1. WebSocket实时推送（最优）
2. 轮询Fallback（备用）

**自动降级**：

- WebSocket连接失败 → 自动启动轮询
- 轮询发现新消息 → 继续使用轮询
- 直到WebSocket重连成功

### 2. 连接指示器

页面头部显示连接状态：

- 🟢 绿色点：WebSocket已连接
- 🟡 黄色点：使用轮询模式

### 3. 错误处理

**前端**：

- API调用失败 → 显示错误提示
- WebSocket连接失败 → 自动重连
- 重连失败5次后 → 仍然使用轮询

**后端**：

- 权限验证失败 → 关闭连接
- 会话不存在 → 关闭连接
- 消息广播失败 → 自动清理断线连接

## 测试方案

### 前端集成验证

1. **启动应用**：

   ```bash
   # 终端1
   cd frontend && pnpm dev --filter @wenexus/web

   # 终端2
   cd backend/python && uv run uvicorn wenexus.main:app --reload --port 8000
   ```

2. **测试消息发送**：
   - 导航到 `/roundtable/[topicId]`
   - 输入消息，点击发送
   - 验证消息立即显示
   - 检查API调用（Network面板）

3. **验证WebSocket**：
   - 打开DevTools → Network → WS过滤器
   - 应看到 WebSocket 连接到 `/api/v1/roundtable/ws/sessions/{sessionId}`
   - 连接指示器应为绿色

4. **验证轮询Fallback**：
   - 在DevTools中关闭网络（模拟断线）
   - 发送消息 → 应通过轮询获取回复
   - 恢复网络 → WebSocket重连

5. **验证AI回复异步生成**：
   - 发送消息
   - 用户消息立即显示
   - AI回复在几秒后显示（通过WebSocket或轮询）

## 文件修改清单

### 新建文件

1. `frontend/apps/web/src/app/api/domains/roundtable/messages/send/route.ts`
2. `frontend/apps/web/src/app/[locale]/(roundtable)/roundtable/[topicId]/message-input.tsx`
3. `frontend/apps/web/src/shared/hooks/use-websocket.ts`
4. `backend/python/src/wenexus/util/websocket.py`

### 修改文件

1. `frontend/apps/web/src/domains/roundtable/services/chat-service.ts`
   - 新增 sendMessage() 函数

2. `frontend/apps/web/src/app/[locale]/(roundtable)/roundtable/[topicId]/roundtable-client.tsx`
   - 导入 MessageInput 和 useWebSocket
   - 添加轮询逻辑
   - 添加消息发送处理
   - 集成WebSocket连接
   - 更新JSX布局

3. `backend/python/src/wenexus/facade/roundtable.py`
   - 新增WebSocket路由
   - 修改send_message_endpoint广播消息

## 后续优化

### Phase 2 可选项

1. **Server-Sent Events (SSE)** - 作为WebSocket的另一个备选方案
2. **消息队列** - 使用Redis Pub/Sub支持多实例部署
3. **消息重试** - 处理暂时性网络故障
4. **消息确认** - 确保消息成功传递

### 性能优化

1. **消息分页加载** - 初始加载最后N条消息，向上滚动加载历史
2. **虚拟滚动** - 处理大量消息时的性能优化
3. **消息压缩** - 减少传输大小
4. **连接池** - 复用WebSocket连接

## 参考资源

- WebSocket实现：原生WebSocket API
- FastAPI WebSocket：FastAPI内置支持
- better-auth：用户认证
- Next.js API Routes：前端API代理
- 后端消息系统：`docs/technical/develop/202603/260313-roundtable-messaging.md`
