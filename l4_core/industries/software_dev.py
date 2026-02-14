# l4_core/industries/software_dev.py

"""
Software Development Industry Preset (L4+)
------------------------------------------
Defines the default engines, flows, and pages for Software Dev workspaces.

This preset is:
  - Stateless
  - Pure data
  - Fully compatible with WorkspaceFactory (L4+)
  - Tuned for backend, frontend, full‑stack, refactoring, and architecture IR
"""

from __future__ import annotations
from typing import List, Dict, Any


# ============================================================
# ENGINE PRESETS
# ============================================================

def get_software_dev_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for software dev workspaces.
    Tuned for:
      - backend generation
      - frontend generation
      - refactoring
      - architecture reasoning
    """
    return [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "label": "OpenAI GPT-4o (General Coding)",
            "enabled": True,
            "priority": 1,
            "allow_fallback": True,
        },
        {
            "provider": "deepseek",
            "model": "deepseek-coder",
            "label": "DeepSeek Coder (Code-Heavy)",
            "enabled": True,
            "priority": 2,
            "allow_fallback": True,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "label": "Claude 3 Opus (Reasoning)",
            "enabled": True,
            "priority": 3,
            "allow_fallback": True,
        },
        {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "label": "Gemini 1.5 Pro (Multimodal)",
            "enabled": False,
            "priority": 4,
            "allow_fallback": True,
        },
    ]


# ============================================================
# FLOW PRESETS
# ============================================================

def get_software_dev_default_flows() -> List[Dict[str, Any]]:
    """
    High-level IR-driven flow templates for software dev workspaces.
    These are interpreted by the FlowEngine (L4+).
    """
    return [
        {
            "key": "generate_backend_service",
            "label": "Generate Backend Service",
            "description": "Generate FastAPI/Express backend modules, routes, and tests.",
            "definition": {
                "steps": [
                    "collect_requirements",
                    "design_api_schema",
                    "generate_code",
                    "generate_tests",
                    "explain_architecture",
                ]
            },
        },
        {
            "key": "refactor_module",
            "label": "Refactor Module",
            "description": "Refactor an existing module for clarity, performance, and testability.",
            "definition": {
                "steps": [
                    "analyze_existing_code",
                    "propose_refactor_plan",
                    "apply_refactor",
                    "generate_diff_and_explanation",
                ]
            },
        },
        {
            "key": "generate_full_stack_app",
            "label": "Generate Full-Stack App",
            "description": "Generate backend, frontend, and deployment config from IR.",
            "definition": {
                "steps": [
                    "collect_product_ir",
                    "design_data_model",
                    "generate_backend",
                    "generate_frontend",
                    "generate_deployment_files",
                    "generate_readme_and_docs",
                ]
            },
        },
    ]


# ============================================================
# PAGE PRESETS
# ============================================================

def get_software_dev_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for a software dev workspace.
    These are IR-level page definitions consumed by the PageEngine (L4+).
    """
    return [
        {
            "key": "dashboard",
            "label": "Workspace Dashboard",
            "widgets": [
                {"type": "stat", "key": "total_projects"},
                {"type": "stat", "key": "recent_runs"},
                {"type": "list", "key": "recent_flows"},
            ],
        },
        {
            "key": "codegen",
            "label": "Code Generation",
            "widgets": [
                {"type": "editor", "key": "spec_input"},
                {"type": "output_panel", "key": "generated_code"},
                {"type": "explanation_panel", "key": "code_explanation"},
            ],
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "widgets": [
                {"type": "chart", "key": "engine_usage"},
                {"type": "chart", "key": "flow_success_rate"},
            ],
        },
    ]


# ============================================================
# FULL PRESET
# ============================================================

def get_software_dev_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize a software dev workspace.
    Fully compatible with WorkspaceFactory (L4+).
    """
    return {
        "type": "software_dev",
        "label": "Software Development",
        "engines": get_software_dev_default_engines(),
        "flows": get_software_dev_default_flows(),
        "pages": get_software_dev_default_pages(),
        "version": 1,
    }


SOFTWARE_DEV_PRESET = get_software_dev_workspace_preset()
