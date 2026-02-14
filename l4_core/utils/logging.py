# l4_core/utils/logging.py

"""
Logging Utilities (L4+)
-----------------------
Provides structured JSON logging with trace-aware context.

Features:
  - JSON logs for dashboards + analytics
  - Trace ID propagation
  - Engine + flow context fields
  - Safe merging of extra metadata
  - No duplicate handlers
  - Future-proof for distributed tracing
"""

from __future__ import annotations

import logging
import json
import time
import uuid
from typing import Any, Dict, Optional


# ---------------------------------------------------------
# TRACE ID
# ---------------------------------------------------------
def generate_trace_id() -> str:
    """
    Generate a unique ID for tracing a single request or flow.
    """
    return str(uuid.uuid4())


# ---------------------------------------------------------
# JSON FORMATTER
# ---------------------------------------------------------
class JsonFormatter(logging.Formatter):
    """
    Format logs as structured JSON for dashboards + analytics.
    """

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


# ---------------------------------------------------------
# LOGGER FACTORY
# ---------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with JSON formatting.
    Ensures no duplicate handlers are added.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


# ---------------------------------------------------------
# INTERNAL: SAFE EXTRA MERGE
# ---------------------------------------------------------
def _merge_extra(base: Dict[str, Any], extra: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Safely merge extra metadata into the log record.
    """
    if not extra:
        return base
    merged = base.copy()
    merged.update(extra)
    return merged


# ---------------------------------------------------------
# PUBLIC LOGGING HELPERS
# ---------------------------------------------------------
def log_engine_event(
    engine: str,
    message: str,
    trace_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    logger = get_logger("engine")
    logger.info(
        message,
        extra=_merge_extra(
            {"trace_id": trace_id, "engine": engine, "extra": extra},
            {},
        ),
    )


def log_flow_event(
    flow: str,
    message: str,
    trace_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    logger = get_logger("flow")
    logger.info(
        message,
        extra=_merge_extra(
            {"trace_id": trace_id, "flow": flow, "extra": extra},
            {},
        ),
    )


def log_system(
    message: str,
    extra: Optional[Dict[str, Any]] = None,
):
    logger = get_logger("system")
    logger.info(
        message,
        extra=_merge_extra({"extra": extra}, {}),
    )
