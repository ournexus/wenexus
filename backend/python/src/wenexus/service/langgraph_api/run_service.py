"""
Run Service

Provides streaming execution service for LangGraph API.

Supports all SDK StreamMode types:
- values: ValuesStreamEvent<StateType> -> { event: "values", data: StateType }
- messages: MessagesTupleStreamEvent -> { event: "messages", data: [Message, MessageTupleMetadata] }
- updates: UpdatesStreamEvent<UpdateType> -> { event: "updates", data: { [node]: UpdateType } }
- tasks: TasksStreamEvent -> { event: "tasks", data: { id, name, interrupts, input/result/error } }
- checkpoints: CheckpointsStreamEvent -> { event: "checkpoints", data: { values, next, config, metadata, tasks } }
- debug: DebugStreamEvent -> { event: "debug", data: unknown }
- custom: CustomStreamEvent<T> -> { event: "custom", data: T }
- events: EventsStreamEvent -> { event: "events", data: { event, name, tags, run_id, metadata, parent_ids, data } }
"""

import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

import structlog

from wenexus.app.agent_initializer import agent_pool
from wenexus.repository.checkpointer import checkpointer

logger = structlog.get_logger()

# SDK StreamMode to LangGraph agent stream_mode mapping
STREAM_MODE_MAPPING = {
    "values": "values",
    "messages": "messages",
    "messages-tuple": "messages",
    "updates": "updates",
    "debug": "debug",
    "events": "events",
    "tasks": "updates",  # tasks 需要从 updates 中构建
    "checkpoints": "values",  # checkpoints 需要从 state 中构建
    "custom": "custom",
}

# For each SDK mode, which agent_mode chunk is required to produce it
SDK_AGENT_MODE_REQUIRED: dict[str, str] = {
    "values": "values",
    "messages": "messages",
    "messages-tuple": "messages",
    "updates": "updates",
    "tasks": "updates",
    "checkpoints": "values",
    "debug": "debug",
    "events": "events",
    "custom": "custom",
}


def format_sse_event(event_type: str, data: Any) -> str:
    """Format data as SSE event."""
    json_data = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {json_data}\n\n"


def _serialize_message(msg: Any) -> dict:
    """
    Serialize a LangChain message to dict matching SDK Message type.

    SDK Message interface requires:
    - id: string
    - type: "human" | "ai" | "tool" | "system"
    - content: string | ContentBlock[]
    - name?: string
    - additional_kwargs?: Record<string, any>
    - response_metadata?: Record<string, any>
    - tool_calls?: ToolCall[]
    """
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
        "name": getattr(msg, "name", None),
        "additional_kwargs": getattr(msg, "additional_kwargs", {}),
        "response_metadata": getattr(msg, "response_metadata", {}),
        "tool_calls": getattr(msg, "tool_calls", []),
    }


def serialize_state(state: dict) -> dict:
    """Serialize agent state to JSON-compatible dict."""
    result = {}
    for key, value in state.items():
        if key == "messages" and isinstance(value, list):
            result[key] = [_serialize_message(m) for m in value]
        elif hasattr(value, "model_dump"):
            result[key] = value.model_dump()
        else:
            result[key] = value
    return result


def _build_checkpoint_event_data(
    thread_id: str,
    state: dict,
    step: int = 0,
) -> dict:
    """
    Build CheckpointsStreamEvent data structure.

    SDK expects:
    {
        values: StateType,
        next: string[],
        config: Config,
        metadata: Metadata,
        tasks: ThreadTask[]
    }
    """
    return {
        "values": serialize_state(state),
        "next": [],
        "config": {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": None,
            }
        },
        "metadata": {
            "source": "loop",
            "step": step,
            "writes": None,
        },
        "tasks": [],
    }


def _build_tasks_event_data(
    task_id: str,
    node_name: str,
    state: dict,
    is_result: bool = False,
    error: str | None = None,
) -> dict:
    """
    Build TasksStreamEvent data structure.

    SDK expects one of:
    - TasksStreamCreateEvent: { id, name, interrupts, input, triggers }
    - TasksStreamResultEvent: { id, name, interrupts, result: [string, UpdateType][] }
    - TasksStreamErrorEvent: { id, name, interrupts, error }
    """
    base = {
        "id": task_id,
        "name": node_name,
        "interrupts": [],
    }

    if error:
        base["error"] = error
    elif is_result:
        base["result"] = [[node_name, serialize_state(state)]]
    else:
        base["input"] = serialize_state(state)
        base["triggers"] = []

    return base


def _build_events_event_data(
    event_name: str,
    node_name: str,
    run_id: str,
    data: Any,
) -> dict:
    """
    Build EventsStreamEvent data structure.

    SDK expects:
    {
        event: "on_chat_model_start" | "on_llm_stream" | etc,
        name: string,
        tags: string[],
        run_id: string,
        metadata: Record<string, unknown>,
        parent_ids: string[],
        data: unknown
    }
    """
    return {
        "event": event_name,
        "name": node_name,
        "tags": [],
        "run_id": run_id,
        "metadata": {},
        "parent_ids": [],
        "data": data,
    }


def _select_primary_agent_mode(requested_modes: list[str]) -> str:
    """
    Select the primary LangGraph agent stream mode based on requested SDK modes.

    Priority order (most detailed first):
    1. messages - for token-level streaming
    2. values - for full state snapshots
    3. updates - for incremental updates (default)

    This ensures we get the most detailed data from the agent,
    which can then be transformed into any requested SDK format.
    """
    for mode in requested_modes:
        if mode in ("messages", "messages-tuple"):
            return "messages"

    for mode in requested_modes:
        if mode == "values":
            return "values"

    for mode in requested_modes:
        if mode == "debug":
            return "debug"

    return "updates"


def _format_subgraph_path(namespace: Any) -> str:
    if isinstance(namespace, (list, tuple)):
        parts = [str(p) for p in namespace if str(p)]
        return "/".join(parts)
    if namespace is None:
        return ""
    return str(namespace)


def _with_subgraph_suffix(event_type: str, subgraph_path: str) -> str:
    if not subgraph_path:
        return event_type
    return f"{event_type}|{subgraph_path}"


async def execute_stream_run(
    thread_id: str,
    assistant_id: str,
    input_data: dict | None = None,
    stream_mode: list[str] | None = None,
    stream_subgraphs: bool = False,
    config: dict | None = None,
) -> AsyncIterator[str]:
    """
    Execute a streaming run and yield SSE events.

    Supports all SDK StreamMode types with proper data structure alignment:
    - values: StateType (full state after each step)
    - messages/messages-tuple: [Message, MessageTupleMetadata]
    - updates: { [node]: UpdateType }
    - tasks: { id, name, interrupts, input/result/error }
    - checkpoints: { values, next, config, metadata, tasks }
    - debug: unknown (raw debug info)
    - custom: T (custom event data)
    - events: { event, name, tags, run_id, metadata, parent_ids, data }

    Args:
        thread_id: Thread ID for the conversation
        assistant_id: Assistant ID to use
        input_data: Input data containing messages
        stream_mode: Stream modes to use
        config: Additional configuration

    Yields:
        SSE formatted events matching SDK type definitions
    """
    run_id = str(uuid4())
    logger.info(f"Executing stream run: {run_id} for thread: {thread_id}")

    # Send metadata event (SDK expects this first)
    yield format_sse_event("metadata", {"run_id": run_id, "thread_id": thread_id})

    try:
        agent = agent_pool.get_agent(assistant_id)

        run_config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        if config:
            run_config.update(config)

        # Normalize requested SDK stream modes
        requested_modes = stream_mode or ["updates"]

        # Map SDK stream modes to LangGraph agent stream modes.
        # 一个 SDK 模式可能复用同一个 agent 模式（如 tasks→updates, checkpoints→values）。
        agent_modes = sorted({STREAM_MODE_MAPPING[m] for m in requested_modes})

        # Track step for tasks/checkpoints events
        step = 0

        # 透传多个 agent stream_mode，按 (agent_mode, chunk) / (namespace, agent_mode, chunk)
        # 逐个映射为 SDK 事件
        async for agent_chunk in agent.astream(
            input_data or {},
            config=run_config,
            stream_mode=agent_modes,
            subgraphs=stream_subgraphs,
        ):
            agent_mode: str
            chunk: Any
            subgraph_path = ""
            if stream_subgraphs and isinstance(agent_chunk, (list, tuple)):
                # 兼容两种形态：
                # 1) ((namespace_tuple), (agent_mode, chunk))
                # 2) (namespace_tuple, agent_mode, chunk)
                if (
                    len(agent_chunk) == 2
                    and isinstance(agent_chunk[0], (list, tuple))
                    and isinstance(agent_chunk[1], (list, tuple))
                ):
                    namespace, payload = agent_chunk
                    subgraph_path = _format_subgraph_path(namespace)
                    agent_mode, chunk = payload
                elif (
                    len(agent_chunk) == 3
                    and isinstance(agent_chunk[0], (list, tuple))
                    and isinstance(agent_chunk[1], str)
                ):
                    namespace, agent_mode, chunk = agent_chunk
                    subgraph_path = _format_subgraph_path(namespace)
                else:
                    # 回退为普通 (agent_mode, chunk) 逻辑
                    agent_mode, chunk = agent_chunk  # type: ignore[misc]
            else:
                # 不开启 subgraphs 时，LangGraph 通常返回 (agent_mode, chunk)
                # 如有结构变化，抛给后续序列化逻辑处理
                agent_mode, chunk = agent_chunk  # type: ignore[misc]

            step += 1
            # Only emit SDK events whose expected agent_mode matches the current chunk's mode.
            for sdk_mode in requested_modes:
                required_agent_mode = SDK_AGENT_MODE_REQUIRED.get(sdk_mode, sdk_mode)
                if agent_mode != required_agent_mode:
                    continue
                serialized = _serialize_chunk_for_mode(
                    chunk=chunk,
                    sdk_mode=sdk_mode,
                    agent_mode=agent_mode,
                    thread_id=thread_id,
                    run_id=run_id,
                    step=step,
                )
                if serialized is not None:
                    # SDK 约定：MessagesTupleStreamEvent 仍然使用 event: "messages"
                    event_type = (
                        "messages"
                        if sdk_mode in ("messages", "messages-tuple")
                        else sdk_mode
                    )
                    yield format_sse_event(
                        _with_subgraph_suffix(event_type, subgraph_path),
                        serialized,
                    )

        # Emit final values snapshot so SDK can build complete stream.messages
        if "values" in requested_modes:
            try:
                final_tuples = list(
                    checkpointer.list(
                        {"configurable": {"thread_id": thread_id}},
                        limit=1,
                    )
                )
                if final_tuples:
                    latest = final_tuples[0]
                    channel_values = latest.checkpoint.get("channel_values", {})
                    # Extract messages from channel_values
                    final_messages: list = []
                    for _ch_name, ch_data in channel_values.items():
                        if (
                            isinstance(ch_data, list)
                            and ch_data
                            and hasattr(ch_data[0], "content")
                        ):
                            final_messages = ch_data
                            break
                        if isinstance(ch_data, dict) and "messages" in ch_data:
                            final_messages = ch_data["messages"]
                            break
                    final_state = {
                        "messages": [_serialize_message(m) for m in final_messages],
                    }
                    yield format_sse_event("values", final_state)
            except Exception as e:
                logger.warning(f"Failed to emit final values snapshot: {e}")

        # Send end event
        yield format_sse_event("end", {})
        logger.info(f"Stream run completed: {run_id}")

    except Exception as e:
        logger.error(f"Stream run failed: {run_id}", exc_info=True)
        # ErrorStreamEvent: { error: string, message: string }
        yield format_sse_event("error", {"error": type(e).__name__, "message": str(e)})


def _serialize_chunk_for_mode(
    chunk: Any,
    sdk_mode: str,
    agent_mode: str,
    thread_id: str,
    run_id: str,
    step: int,
) -> Any | None:
    """
    Serialize a chunk according to the SDK stream mode's expected data structure.

    Each mode has specific data shape requirements defined in types.stream.d.ts.
    Returns None if the chunk cannot be meaningfully converted to the requested mode.

    Args:
        chunk: Raw chunk from agent.astream
        sdk_mode: The SDK stream mode requested by client
        agent_mode: The actual mode used with agent.astream
        thread_id: Thread ID for context
        run_id: Run ID for context
        step: Current step number
    """
    # messages / messages-tuple: [Message, MessageTupleMetadata]
    if sdk_mode in ("messages", "messages-tuple"):
        # Only emit if agent is in messages mode
        if agent_mode != "messages":
            return None
        if isinstance(chunk, (list, tuple)) and len(chunk) == 2:
            message_like, meta = chunk
            return [_serialize_message(message_like), meta]
        return [_serialize_message(chunk), {"tags": []}]

    # values: StateType (full serialized state)
    if sdk_mode == "values":
        # values mode expects full state, works with values/updates agent mode
        if agent_mode == "messages":
            return None  # Can't derive full state from message chunks
        return serialize_state(chunk) if isinstance(chunk, dict) else chunk

    # updates: { [node]: UpdateType }
    if sdk_mode == "updates":
        # updates mode expects { node: update } structure
        if agent_mode == "messages":
            return None  # Can't derive updates from message chunks
        if isinstance(chunk, dict):
            return {
                k: serialize_state(v) if isinstance(v, dict) else v
                for k, v in chunk.items()
            }
        return chunk

    # tasks: TasksStreamEvent data
    if sdk_mode == "tasks":
        # tasks mode derives from updates
        if agent_mode == "messages":
            return None
        if isinstance(chunk, dict):
            node_name = next(iter(chunk.keys()), "unknown")
            node_data = chunk.get(node_name, {})
            task_id = f"{run_id}-{step}"
            return _build_tasks_event_data(
                task_id=task_id,
                node_name=node_name,
                state=node_data if isinstance(node_data, dict) else {},
                is_result=True,
            )
        return {
            "id": f"{run_id}-{step}",
            "name": "unknown",
            "interrupts": [],
            "result": [],
        }

    # checkpoints: CheckpointsStreamEvent data
    if sdk_mode == "checkpoints":
        # checkpoints mode derives from values/updates
        if agent_mode == "messages":
            return None
        state = chunk if isinstance(chunk, dict) else {}
        return _build_checkpoint_event_data(thread_id, state, step)

    # debug: unknown (pass through raw data)
    if sdk_mode == "debug":
        if isinstance(chunk, dict):
            return serialize_state(chunk)
        return chunk

    # events: EventsStreamEvent data
    if sdk_mode == "events":
        if isinstance(chunk, dict) and "event" in chunk:
            return chunk
        return _build_events_event_data(
            event_name="on_chain_stream",
            node_name="agent",
            run_id=run_id,
            data=serialize_state(chunk) if isinstance(chunk, dict) else chunk,
        )

    # custom: T (pass through)
    if sdk_mode == "custom":
        if isinstance(chunk, dict):
            return serialize_state(chunk)
        return chunk

    # Default: serialize as state
    return serialize_state(chunk) if isinstance(chunk, dict) else chunk
