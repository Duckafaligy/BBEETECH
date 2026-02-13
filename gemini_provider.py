# l4_core/ai/providers/gemini_provider.py

from typing import Tuple, Dict, Any
from ..router import AIRequest
from ...config import settings


async def call_gemini(request: AIRequest, model: str) -> Tuple[str, Dict[str, Any]]:
    # TODO: wire real Gemini client here
    content = f"[gemini:{model}] {request.prompt}"
    raw = {"provider": "gemini", "model": model, "placeholder": True}
    return content, raw
