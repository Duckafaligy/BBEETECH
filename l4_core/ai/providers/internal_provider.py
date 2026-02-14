# l4_core/ai/providers/internal_provider.py

from __future__ import annotations
from typing import Dict, Any
from l4_core.utils.logging import log_engine_event, generate_trace_id


async def call_internal_model(
    request: Dict[str, Any],
    model: str,
    trace_id: str | None = None,
) -> Dict[str, Any]:

    trace_id = trace_id or generate_trace_id()

    log_engine_event(
        engine="internal-provider",
        message="Internal provider invoked (stub)",
        trace_id=trace_id,
        extra={
            "model": model,
            "request_keys": list(request.keys()),
        },
    )

    return {
        "provider": "internal",
        "model": model,
        "output_text": "INTERNAL MODEL RESPONSE (stub)",
        "raw": {},
        "trace_id": trace_id,
    }
