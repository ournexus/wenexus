"""
统一日志配置工具

提供项目级别的日志配置，支持：
- 控制台和文件双输出
- 按日期和大小自动轮转
- 结构化日志格式
- 不同模块的日志级别控制
"""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path


class LogConfig:
    """日志配置常量"""

    DEFAULT_LOG_DIR = Path("logs")
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5


def setup_logger(
    name: str,
    log_dir: Path | None = None,
    level: int = LogConfig.DEFAULT_LOG_LEVEL,
    console: bool = True,
    file_output: bool = True,
    detailed: bool = False,
) -> logging.Logger:
    """
    设置并返回一个配置好的 logger

    Args:
        name: logger 名称，通常使用 __name__
        log_dir: 日志文件输出目录，默认为项目根目录下的 logs/
        level: 日志级别，默认 INFO
        console: 是否输出到控制台，默认 True
        file_output: 是否输出到文件，默认 True
        detailed: 是否使用详细格式（包含文件名和行号），默认 False

    Returns:
        配置好的 logger 实例

    Example:
        >>> from src.util.logger import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("应用启动")
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    # 选择日志格式
    formatter = logging.Formatter(
        LogConfig.DETAILED_FORMAT if detailed else LogConfig.DEFAULT_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件输出
    if file_output:
        if log_dir is None:
            # 默认使用项目根目录下的 logs/
            project_root = Path(__file__).parent.parent.parent.parent
            log_dir = project_root / "logs"

        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # 按大小轮转的日志文件
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 错误日志单独记录
        error_handler = RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # 按日期轮转的日志文件（保留最近7天）
        daily_handler = TimedRotatingFileHandler(
            log_dir / "daily.log",
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        daily_handler.setLevel(level)
        daily_handler.setFormatter(formatter)
        daily_handler.suffix = "%Y-%m-%d"
        logger.addHandler(daily_handler)

    return logger


def get_logger(name: str, **kwargs) -> logging.Logger:
    """
    获取 logger 的便捷方法

    Args:
        name: logger 名称
        **kwargs: 传递给 setup_logger 的其他参数

    Returns:
        logger 实例
    """
    return setup_logger(name, **kwargs)


def init_logging(
    log_dir: Path | None = None,
    level: int = LogConfig.DEFAULT_LOG_LEVEL,
    detailed: bool = False,
) -> None:
    """
    初始化全局日志配置

    在应用启动时调用一次，配置根 logger

    Args:
        log_dir: 日志文件目录
        level: 全局日志级别
        detailed: 是否使用详细格式

    Example:
        >>> from src.util.logger import init_logging
        >>> init_logging(log_dir=Path("logs"), level=logging.DEBUG)
    """
    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent.parent
        log_dir = project_root / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 配置根 logger
    root_logger = logging.getLogger()

    # 清除现有 handlers
    root_logger.handlers.clear()

    root_logger.setLevel(level)

    formatter = logging.Formatter(
        LogConfig.DETAILED_FORMAT if detailed else LogConfig.DEFAULT_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件输出
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=LogConfig.MAX_BYTES,
        backupCount=LogConfig.BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 错误日志
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=LogConfig.MAX_BYTES,
        backupCount=LogConfig.BACKUP_COUNT,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    logging.info(f"日志系统初始化完成，日志目录: {log_dir.absolute()}")


class StructuredLogger:
    """
    结构化日志记录器，便于 AI 解析

    输出 JSON 格式的日志，包含完整的上下文信息
    """

    def __init__(self, name: str, log_dir: Path | None = None):
        self.logger = logging.getLogger(name)

        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            log_dir = project_root / "logs" / "structured"

        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # JSON 格式日志
        import json

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data, ensure_ascii=False)

        handler = RotatingFileHandler(
            log_dir / "structured.jsonl",
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def log(self, level: str, message: str, **context):
        """
        记录带上下文的日志

        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            message: 日志消息
            **context: 额外的上下文信息
        """
        extra_info = " | ".join(f"{k}={v}" for k, v in context.items())
        full_message = f"{message} | {extra_info}" if context else message

        log_method = getattr(self.logger, level.lower())
        log_method(full_message)
