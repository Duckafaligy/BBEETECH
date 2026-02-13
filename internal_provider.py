# l4_core/ai/providers/internal_provider.py

from typing import Tuple, Dict, Any
from ..router import AIRequest


async def call_internal_model(request: AIRequest, model: str) -> Tuple[str, Dict[str, Any]]:
    """
    Your own future models live here.
    Could be:
    - fine-tuned LLMs
    - local models
    - custom inference servers
    """
    content = f"[internal:{model}] {request.prompt}"
    raw = {"provider": "internal", "model": model, "placeholder": True}
    return content, raw
