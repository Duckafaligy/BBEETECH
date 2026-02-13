# l4_core/ai/providers/deepseek_provider.py

from typing import Tuple, Dict, Any
from ..router import AIRequest
from ...config import settings


async def call_deepseek(request: AIRequest, model: str) -> Tuple[str, Dict[str, Any]]:
    # TODO: wire real DeepSeek client here
    content = f"[deepseek:{model}] {request.prompt}"
    raw = {"provider": "deepseek", "model": model, "placeholder": True}
    return content, raw
