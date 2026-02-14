# l4_core/ai/providers/deepseek_provider.py

from __future__ import annotations
from typing import Dict, Any
from l4_core.config import settings
from l4_core.utils.logging import log_engine_event, generate_trace_id


async def call_deepseek(
    request: Dict[str, Any],
    model: str,
    trace_id: str | None = None,
) -> Dict[str, Any]:

    trace_id = trace_id or generate_trace_id()
    api_key = settings.DEEPSEEK_API_KEY

    log_engine_event(
        engine="deepseek-provider",
        message="DeepSeek provider invoked (stub)",
        trace_id=trace_id,
        extra={
            "model": model,
            "request_keys": list(request.keys()),
            "api_key_present": bool(api_key),
        },
    )

    return {
        "provider": "deepseek",
        "model": model,
        "output_text": "DEEPSEEK RESPONSE (stub)",
        "raw": {},
        "trace_id": trace_id,
    }
