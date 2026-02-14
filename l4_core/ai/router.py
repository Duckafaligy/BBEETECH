# l4_core/ai/router.py

"""
AIRouter (L4+)
--------------
Central AI router responsible for:
  - Selecting the best engine (AIEngine)
  - Respecting provider enable/disable switches
  - Dispatching to provider adapters via PROVIDER_REGISTRY
  - Propagating trace IDs
  - Logging structured events
  - Future-proof for:
      • scoring
      • fallback chains
      • multimodal requests
      • cost/performance optimization
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.db.core import get_db
from l4_core.db.models import AIEngine
from l4_core.utils.logging import log_engine_event, generate_trace_id
from l4_core.ai.providers import PROVIDER_REGISTRY


# ---------------------------------------------------------
# FASTAPI ROUTER (required for app startup)
# ---------------------------------------------------------
router = APIRouter()

@router.get("/engines")
async def list_engines(db=Depends(get_db)):
    """
    Temporary placeholder endpoint so the app boots.
    Replace with real AI orchestration endpoints later.
    """
    stmt = select(AIEngine).order_by(AIEngine.priority.asc())
    result = await db.execute(stmt)
    engines = result.scalars().all()

    return {
        "status": "ok",
        "count": len(engines),
        "engines": [
            {
                "id": e.id,
                "provider": e.provider,
                "model": e.model,
                "label": e.label,
                "enabled": e.enabled,
                "priority": e.priority,
            }
            for e in engines
        ],
    }


# ---------------------------------------------------------
# REQUEST / RESPONSE TYPES
# ---------------------------------------------------------
class AIRequest:
    """Normalized AI request object."""

    def __init__(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.metadata = metadata or {}


class AIResponse:
    """Normalized AI response wrapper."""

    def __init__(
        self,
        content: str,
        provider: str,
        model: str,
        trace_id: str,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.trace_id = trace_id
        self.raw = raw or {}


# ---------------------------------------------------------
# AIRouter (L4+)
# ---------------------------------------------------------
class AIRouter:
    """
    Central AI router.
    - Chooses engine based on DB config (AIEngine)
    - Applies provider enable/disable overrides
    - Dispatches to provider adapters via PROVIDER_REGISTRY
    - Emits structured logs
    - Propagates trace IDs
    """

    def __init__(self, db: AsyncSession):
        self.db = db

        # Provider kill-switches
        self.provider_overrides = {
            "openai": True,
            "deepseek": True,
            "anthropic": True,
            "gemini": True,
            "internal": True,
        }

    # ---------------------------------------------------------
    # PUBLIC: ENABLE/DISABLE PROVIDERS
    # ---------------------------------------------------------
    def set_provider_enabled(self, provider: str, enabled: bool):
        if provider in self.provider_overrides:
            self.provider_overrides[provider] = enabled

    # ---------------------------------------------------------
    # INTERNAL: GET AVAILABLE ENGINES
    # ---------------------------------------------------------
    async def _get_available_engines(self) -> List[AIEngine]:
        stmt = (
            select(AIEngine)
            .where(AIEngine.enabled == True)  # noqa: E712
            .order_by(AIEngine.priority.asc())
        )
        result = await self.db.execute(stmt)
        engines = list(result.scalars().all())

        # Apply provider overrides
        engines = [
            e for e in engines
            if self.provider_overrides.get(e.provider, True)
        ]

        # Fallback to internal if everything else is disabled
        if not engines:
            stmt = (
                select(AIEngine)
                .where(
                    AIEngine.enabled == True,  # noqa: E712
                    AIEngine.provider == "internal",
                )
                .order_by(AIEngine.priority.asc())
            )
            result = await self.db.execute(stmt)
            engines = list(result.scalars().all())

        return engines

    # ---------------------------------------------------------
    # INTERNAL: CHOOSE ENGINE
    # ---------------------------------------------------------
    async def _choose_engine(self) -> Optional[AIEngine]:
        engines = await self._get_available_engines()
        return engines[0] if engines else None

    # ---------------------------------------------------------
    # PUBLIC: TEXT GENERATION
    # ---------------------------------------------------------
    async def generate_text(
        self,
        request: AIRequest,
        trace_id: Optional[str] = None,
    ) -> AIResponse:

        trace_id = trace_id or generate_trace_id()
        engine = await self._choose_engine()

        if not engine:
            log_engine_event(
                engine="none",
                message="No AI engines available",
                trace_id=trace_id,
                extra={"request_meta": request.metadata},
            )
            raise RuntimeError("No AI engines are enabled in the system.")

        engine_key = f"{engine.provider}:{engine.model}"

        log_engine_event(
            engine=engine_key,
            message="AI text generation started",
            trace_id=trace_id,
            extra={"request_meta": request.metadata},
        )

        # Provider lookup via registry
        provider_fn = PROVIDER_REGISTRY.get(engine.provider)
        if not provider_fn:
            raise RuntimeError(f"Unknown AI provider: {engine.provider}")

        # Normalize request into provider payload
        provider_payload = {
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "metadata": request.metadata,
        }

        # Call provider adapter
        provider_result = await provider_fn(
            request=provider_payload,
            model=engine.model,
            trace_id=trace_id,
        )

        # Provider result is already structured
        content = provider_result.get("output_text", "")
        raw = provider_result.get("raw", {})

        log_engine_event(
            engine=engine_key,
            message="AI text generation completed",
            trace_id=trace_id,
            extra={"response_preview": content[:120]},
        )

        return AIResponse(
            content=content,
            provider=engine.provider,
            model=engine.model,
            trace_id=trace_id,
            raw=raw,
        )
