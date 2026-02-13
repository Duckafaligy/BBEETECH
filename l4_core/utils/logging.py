# l4_core/utils/logging.py

import logging
import json
import time
import uuid
from typing import Any, Dict


def generate_trace_id() -> str:
    """Unique ID for tracing a single request or flow."""
    return str(uuid.uuid4())


class JsonFormatter(logging.Formatter):
    """Format logs as structured JSON for dashboards + analytics."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": time.time(),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "engine": getattr(record, "engine", None),
            "flow": getattr(record, "flow", None),
            "extra": getattr(record, "extra", None),
        }
        return json.dumps(log)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with JSON formatting + colorized console output."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


# Convenience wrappers
def log_engine_event(engine: str, message: str, trace_id: str = None, extra: Dict[str, Any] = None):
    logger = get_logger("engine")
    logger.info(message, extra={"trace_id": trace_id, "engine": engine, "extra": extra})


def log_flow_event(flow: str, message: str, trace_id: str = None, extra: Dict[str, Any] = None):
    logger = get_logger("flow")
    logger.info(message, extra={"trace_id": trace_id, "flow": flow, "extra": extra})


def log_system(message: str, extra: Dict[str, Any] = None):
    logger = get_logger("system")
    logger.info(message, extra={"extra": extra})
