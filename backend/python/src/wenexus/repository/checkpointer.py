"""
Shared Checkpointer Module

Provides a singleton MemorySaver instance shared between Agent and API.
This ensures API can read checkpoints written by Agent during execution.
"""

import os
from typing import Literal

import structlog
from langgraph.checkpoint.memory import MemorySaver

logger = structlog.get_logger()

StorageType = Literal["memory", "postgres", "redis"]


class CheckpointerFactory:
    """Factory for creating checkpointer instances."""

    @staticmethod
    def create(storage_type: StorageType = "memory"):
        """
        Create a checkpointer based on storage type.

        Args:
            storage_type: Type of storage backend ("memory", "postgres", "redis")

        Returns:
            Checkpointer instance
        """
        logger.info(f"Creating checkpointer with storage: {storage_type}")

        if storage_type == "memory":
            return MemorySaver()
        elif storage_type == "postgres":
            from langgraph.checkpoint.postgres import PostgresSaver

            return PostgresSaver.from_conn_string(os.getenv("DATABASE_URL"))
        elif storage_type == "redis":
            from langgraph.checkpoint.redis import RedisSaver

            return RedisSaver.from_conn_string(os.getenv("REDIS_URL"))
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")


# Singleton instance shared across Agent and API
checkpointer = CheckpointerFactory.create()
logger.info("Shared checkpointer initialized")
