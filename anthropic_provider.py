# l4_core/ai/providers/anthropic_provider.py

from typing import Tuple, Dict, Any
from ..router import AIRequest
from ...config import settings


async def call_anthropic(request: AIRequest, model: str) -> Tuple[str, Dict[str, Any]]:
    # TODO: wire real Anthropic client here
    content = f"[anthropic:{model}] {request.prompt}"
    raw = {"provider": "anthropic", "model": model, "placeholder": True}
    return content, raw
