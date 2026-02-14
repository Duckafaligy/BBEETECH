# l4_core/ai/providers/__init__.py

"""
AI Provider Registry (L4+)
-------------------------
This module exposes a unified registry of provider call functions.

Upgrades in L4+ version:
  - Strong typing for provider call signatures
  - Central provider registry for dynamic lookup
  - Audit-ready provider metadata
  - Future-proof for plugin-based provider loading
  - Consistent naming for AIRouter integration
"""

from __future__ import annotations

from typing import Callable, Dict, Any, Awaitable

from .openai_provider import call_openai
from .deepseek_provider import call_deepseek
from .anthropic_provider import call_anthropic
from .gemini_provider import call_gemini
from .internal_provider import call_internal_model


# ---------------------------------------------------------
# TYPE: Provider call signature
# ---------------------------------------------------------
ProviderFn = Callable[..., Awaitable[Dict[str, Any]]]


# ---------------------------------------------------------
# PROVIDER REGISTRY
# ---------------------------------------------------------
# AIRouter will use this registry to dynamically resolve providers.
# The Audit Engine will validate this registry for:
#   - missing providers
#   - mismatched provider names
#   - unsupported models
#   - deprecated providers
#
# This is the central source of truth for all provider integrations.
PROVIDER_REGISTRY: Dict[str, ProviderFn] = {
    "openai": call_openai,
    "deepseek": call_deepseek,
    "anthropic": call_anthropic,
    "gemini": call_gemini,
    "internal": call_internal_model,
}


# ---------------------------------------------------------
# PUBLIC EXPORTS
# ---------------------------------------------------------
__all__ = [
    "ProviderFn",
    "PROVIDER_REGISTRY",
    "call_openai",
    "call_deepseek",
    "call_anthropic",
    "call_gemini",
    "call_internal_model",
]
