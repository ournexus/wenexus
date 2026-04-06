"""
Threads Router

Provides endpoints for managing threads compatible with LangGraph SDK.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from wenexus.model.run import RunStreamRequest
from wenexus.model.thread import (
    Thread,
    ThreadHistoryRequest,
    ThreadSearchRequest,
    ThreadState,
    ThreadStateUpdateRequest,
)
from wenexus.repository.checkpointer import checkpointer
from wenexus.service.langgraph_api.run_service import execute_stream_run

logger = structlog.get_logger()
router = APIRouter(prefix="/threads", tags=["threads"])

# In-memory thread registry
_threads: dict[str, Thread] = {}


def _serialize_message(msg: Any) -> dict:
    """Serialize a LangChain message to dict."""
    if hasattr(msg, "model_dump"):
        return msg.model_dump()
    if hasattr(msg, "dict"):
        return msg.dict()
    if isinstance(msg, dict):
        return msg
    return {
        "type": getattr(msg, "type", "unknown"),
        "content": getattr(msg, "content", str(msg)),
        "id": getattr(msg, "id", str(uuid4())),
        "additional_kwargs": getattr(msg, "additional_kwargs", {}),
        "response_metadata": getattr(msg, "response_metadata", {}),
    }


def _is_message(obj: Any) -> bool:
    """Check if an object is a LangChain message."""
    return hasattr(obj, "content") or (isinstance(obj, dict) and "content" in obj)


def _json_safe(value: Any) -> Any:
    """Best-effort conversion of arbitrary objects to JSON-serializable values.

    - Pydantic / dataclass-like objects: use model_dump()/dict()
    - dict / list / tuple / set: recurse
    - primitives: return as-is
    - others: fallback to str()
    """
    # Primitive types
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # Pydantic / dataclass-like
    if hasattr(value, "model_dump"):
        try:
            return _json_safe(value.model_dump())
        except Exception:
            return str(value)
    if hasattr(value, "dict") and not isinstance(value, dict):
        try:
            return _json_safe(value.dict())
        except Exception:
            return str(value)

    # Mapping types
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    # Sequence types
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]

    # Fallback
    return str(value)


def _extract_values_from_checkpoint(checkpoint: dict) -> dict:
    """
    Extract state values (messages, todos, files, etc.) from a checkpoint.

    约定：
    - values.messages: 会话消息列表
    - values.todos: DeepAgentState.todos 列表
    - values.files: DeepAgentState.files 映射 {path: content}

    之前的实现按 value 遍历 channel_values，无法区分 channel 名：
    - todos 被当成 messages 合并进 messages 数组
    - files 的内容按 key 展开成顶层字段，而不是挂在 values.files
    """
    values: dict = {}
    channel_values = checkpoint.get("channel_values", {}) or {}

    for channel_name, node_data in channel_values.items():
        # 1) 显式处理 todos 通道 → values.todos
        if channel_name == "todos":
            if isinstance(node_data, list):
                flat: list[Any] = []
                for item in node_data:
                    if isinstance(item, list):
                        flat.extend(item)
                    else:
                        flat.append(item)
                values["todos"] = _json_safe(flat)
            else:
                values["todos"] = [_json_safe(node_data)]
            continue

        # 2) 显式处理 files 通道 → values.files
        if channel_name == "files":
            # DeepAgentState.files: dict[str, str]
            if isinstance(node_data, dict):
                # 前端期望 Record<string, string>
                values["files"] = {str(k): str(v) for k, v in node_data.items()}
            else:
                # 兜底：非 dict 形式时直接挂到 files，前端会做字符串化处理
                values["files"] = str(node_data)
            continue

        # 3) 处理包含 messages 的通道 → values.messages
        if isinstance(node_data, dict):
            if "messages" in node_data:
                serialized = [
                    _json_safe(_serialize_message(m)) for m in node_data["messages"]
                ]
                values.setdefault("messages", []).extend(serialized)

            # 其他字段（非 messages / todos / files）原样挂载
            for key, val in node_data.items():
                if key not in {"messages", "todos", "files"}:
                    values[key] = _json_safe(val)
            continue

        # 4) list-of-messages 通道（兼容旧形态）
        if isinstance(node_data, list):
            flat = []
            for item in node_data:
                if isinstance(item, list):
                    flat.extend(item)
                else:
                    flat.append(item)
            if flat and _is_message(flat[0]):
                serialized = [_json_safe(_serialize_message(m)) for m in flat]
                values.setdefault("messages", []).extend(serialized)
            else:
                # 非消息列表，挂到对应 channel 名下
                values[channel_name] = _json_safe(node_data)
            continue

        # 5) 其他标量/对象通道，直接挂到 values[channel_name]
        values[channel_name] = _json_safe(node_data)

    return values


@router.post("")
async def create_thread(metadata: dict | None = None):
    """Create a new thread."""
    thread_id = str(uuid4())
    thread = Thread(
        thread_id=thread_id,
        metadata=metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    _threads[thread_id] = thread
    logger.info(f"Created thread: {thread_id}")
    return thread.model_dump()


@router.post("/search")
async def search_threads(request: ThreadSearchRequest = None):
    """
    Search for threads.

    Returns threads from both in-memory registry and checkpointer.
    """
    logger.info("Searching threads")

    # Get threads from checkpointer
    thread_ids_from_checkpointer = set()
    try:
        all_tuples = list(checkpointer.list(None))
        for t in all_tuples:
            config = t.config or {}
            configurable = config.get("configurable", {})
            tid = configurable.get("thread_id")
            if tid:
                thread_ids_from_checkpointer.add(tid)
    except Exception as e:
        logger.warning(f"Failed to list checkpoints: {e}")

    # Merge with in-memory threads
    all_thread_ids = set(_threads.keys()) | thread_ids_from_checkpointer

    threads = []
    for tid in all_thread_ids:
        if tid in _threads:
            threads.append(_threads[tid])
        else:
            thread = Thread(
                thread_id=tid,
                metadata={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            _threads[tid] = thread
            threads.append(thread)

    if request and request.status:
        threads = [t for t in threads if t.status == request.status]

    offset = request.offset if request else 0
    limit = request.limit if request else 10

    return [t.model_dump() for t in threads[offset : offset + limit]]


@router.get("/{thread_id}")
async def get_thread(thread_id: str):
    """Get thread by ID."""
    logger.info(f"Getting thread: {thread_id}")

    if thread_id in _threads:
        return _threads[thread_id].model_dump()

    # Check if thread exists in checkpointer
    try:
        tuples = list(checkpointer.list({"configurable": {"thread_id": thread_id}}))
        if tuples:
            thread = Thread(
                thread_id=thread_id,
                metadata={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            _threads[thread_id] = thread
            return thread.model_dump()
    except Exception as e:
        logger.warning(f"Failed to check checkpointer: {e}")

    raise HTTPException(status_code=404, detail="Thread not found")


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread."""
    if thread_id in _threads:
        del _threads[thread_id]
        logger.info(f"Deleted thread: {thread_id}")
        return {"status": "deleted", "thread_id": thread_id}

    raise HTTPException(status_code=404, detail="Thread not found")


@router.get("/{thread_id}/state")
async def get_thread_state(thread_id: str, checkpoint_id: str | None = None):
    """Get current state for a thread."""
    logger.info(f"Getting state for thread: {thread_id}")

    config = {"configurable": {"thread_id": thread_id}}
    if checkpoint_id:
        config["configurable"]["checkpoint_id"] = checkpoint_id

    try:
        tuples = list(checkpointer.list(config, limit=1))
        if not tuples:
            return ThreadState(
                values={},
                next=[],
                checkpoint_id=None,
                metadata={"thread_id": thread_id},
            ).model_dump()

        latest = tuples[0]
        values = _extract_values_from_checkpoint(latest.checkpoint)

        return ThreadState(
            values=values,
            next=[],
            checkpoint_id=latest.checkpoint.get("id"),
            created_at=latest.checkpoint.get("ts"),
            metadata={"thread_id": thread_id},
        ).model_dump()
    except Exception as e:
        logger.error(f"Failed to get thread state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{thread_id}/state")
async def update_thread_state(thread_id: str, request: ThreadStateUpdateRequest):
    """Update thread state."""
    logger.info(f"Updating state for thread: {thread_id}")

    # For now, just return success - actual state update would require
    # more complex checkpoint manipulation
    return {
        "checkpoint_id": str(uuid4()),
        "thread_id": thread_id,
        "status": "updated",
    }


@router.api_route("/{thread_id}/history", methods=["GET", "POST"])
async def get_thread_history(
    thread_id: str,
    request: ThreadHistoryRequest | None = None,
):
    """
    Get thread history.

    Returns list of checkpoints for the thread, grouped by step.
    For each step, only the checkpoint with the most messages is returned.
    """
    logger.info(f"Getting history for thread: {thread_id}")

    limit = request.limit if request else 10

    try:
        tuples = list(
            checkpointer.list(
                {"configurable": {"thread_id": thread_id}},
                limit=limit * 2,  # Get more to handle grouping
            )
        )

        if not tuples:
            return []

        # Group by step, keep checkpoint with most messages
        grouped: dict[int, list] = {}
        for t in tuples:
            metadata = t.metadata or {}
            step = (
                getattr(metadata, "step", 0)
                if hasattr(metadata, "step")
                else metadata.get("step", 0)
            )
            grouped.setdefault(step, []).append(t)

        history: list[dict[str, Any]] = []
        for step in sorted(grouped.keys()):
            candidates = grouped[step]
            best = max(
                candidates,
                key=lambda t: len(
                    _extract_values_from_checkpoint(t.checkpoint).get("messages", [])
                ),
            )

            # values: messages/todos/files 等，来自 checkpoint.channel_values
            values = _extract_values_from_checkpoint(best.checkpoint)

            # 构造符合 LangGraph ThreadState.checkpoint 结构的 checkpoint 字段
            config = (best.config or {}).get("configurable", {})
            checkpoint = {
                "thread_id": config.get("thread_id", thread_id),
                "checkpoint_ns": config.get("checkpoint_ns", ""),
                "checkpoint_id": config.get("checkpoint_id")
                or best.checkpoint.get("id"),
                "checkpoint_map": None,
            }

            # parent_checkpoint：当前场景可为空，占位即可满足 SDK 类型
            parent_config = getattr(best, "parent_config", None) or {}
            parent_conf_cfg = (
                parent_config.get("configurable")
                if isinstance(parent_config, dict)
                else None
            )
            parent_checkpoint: dict[str, Any] | None
            if parent_conf_cfg:
                parent_checkpoint = {
                    "thread_id": parent_conf_cfg.get("thread_id", thread_id),
                    "checkpoint_ns": parent_conf_cfg.get("checkpoint_ns", ""),
                    "checkpoint_id": parent_conf_cfg.get("checkpoint_id"),
                    "checkpoint_map": None,
                }
            else:
                parent_checkpoint = None

            # 合并 metadata：保留原有信息并补充 thread_id / step
            best_metadata = best.metadata or {}
            metadata: dict[str, Any] = (
                {**best_metadata} if isinstance(best_metadata, dict) else {}
            )
            metadata.setdefault("thread_id", thread_id)
            metadata.setdefault("step", step)

            history.append(
                {
                    "values": values,
                    "next": [],
                    "checkpoint": checkpoint,
                    "metadata": metadata,
                    "created_at": best.checkpoint.get("ts"),
                    "parent_checkpoint": parent_checkpoint,
                    "tasks": [],
                }
            )

        return history[:limit]
    except Exception as e:
        logger.error(f"Failed to get thread history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{thread_id}/runs/stream")
async def stream_run(thread_id: str, request: RunStreamRequest):
    """
    Execute a streaming run for a thread.

    This is the core endpoint for agent execution with SSE streaming.
    """
    logger.info(f"Starting stream run for thread: {thread_id}")

    # Ensure thread exists
    if thread_id not in _threads:
        _threads[thread_id] = Thread(
            thread_id=thread_id,
            metadata={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def event_generator():
        async for event in execute_stream_run(
            thread_id=thread_id,
            assistant_id=request.assistant_id,
            input_data=request.input,
            stream_mode=request.stream_mode,
            stream_subgraphs=request.stream_subgraphs,
            config=request.config,
        ):
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
