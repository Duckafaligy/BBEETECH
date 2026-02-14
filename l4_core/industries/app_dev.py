# l4_core/industries/app_dev.py

"""
App Development Industry Preset (L4+)
-------------------------------------
Defines the default engines, flows, and pages for App Dev workspaces.

This preset is:
  - Stateless
  - Pure data
  - Safe to import anywhere
  - Fully compatible with WorkspaceFactory (L4+)
  - Future-proof for IR-level flows, multimodal UX, and codegen pipelines
"""

from __future__ import annotations
from typing import List, Dict, Any


# ============================================================
# ENGINE PRESETS
# ============================================================

def get_app_dev_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for app dev workspaces.
    Tuned for:
      - product flows
      - mobile/desktop app generation
      - UX-heavy reasoning
      - IR → UI mapping
    """
    return [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "label": "OpenAI GPT-4o (App Logic & UX)",
            "enabled": True,
            "priority": 1,
            "allow_fallback": True,
        },
        {
            "provider": "deepseek",
            "model": "deepseek-coder",
            "label": "DeepSeek Coder (App Code & APIs)",
            "enabled": True,
            "priority": 2,
            "allow_fallback": True,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "label": "Claude 3 Opus (Flows & Product Reasoning)",
            "enabled": True,
            "priority": 3,
            "allow_fallback": True,
        },
        {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "label": "Gemini 1.5 Pro (Multimodal UX & Assets IR)",
            "enabled": False,
            "priority": 4,
            "allow_fallback": True,
        },
        {
            "provider": "internal",
            "model": "app-ir-teacher",
            "label": "Internal App IR Teacher (Patterns & Reuse)",
            "enabled": False,
            "priority": 5,
            "allow_fallback": False,
        },
    ]


# ============================================================
# FLOW PRESETS
# ============================================================

def get_app_dev_default_flows() -> List[Dict[str, Any]]:
    """
    High-level IR-driven flow templates for app dev workspaces.
    These are interpreted by the FlowEngine (L4+).
    """
    return [
        {
            "key": "design_app_flow",
            "label": "Design App Flow",
            "description": "From IR, design screens, navigation, and user journeys.",
            "definition": {
                "steps": [
                    "collect_app_ir",
                    "define_user_personas",
                    "define_screens_and_states",
                    "define_navigation_and_edges",
                    "generate_flow_diagram_ir",
                ]
            },
        },
        {
            "key": "generate_mobile_app",
            "label": "Generate Mobile App",
            "description": "Generate React Native/Flutter/Swift/Kotlin code from IR.",
            "definition": {
                "steps": [
                    "collect_platform_preferences",
                    "generate_data_model",
                    "generate_app_screens",
                    "generate_navigation_code",
                    "generate_api_integration",
                    "generate_readme_and_setup",
                ]
            },
        },
        {
            "key": "generate_desktop_app",
            "label": "Generate Desktop App",
            "description": "Generate Electron/Tauri/native desktop app from IR.",
            "definition": {
                "steps": [
                    "collect_app_ir",
                    "generate_window_and_menu_structure",
                    "generate_core_logic",
                    "generate_persistence_layer",
                    "generate_build_and_packaging_files",
                ]
            },
        },
        {
            "key": "optimize_app_experience",
            "label": "Optimize App Experience",
            "description": "Analyze flows and suggest UX, performance, and accessibility improvements.",
            "definition": {
                "steps": [
                    "collect_existing_flows",
                    "analyze_pain_points",
                    "propose_improvements",
                    "generate_diff_and_explanations",
                ]
            },
        },
        {
            "key": "generate_app_docs",
            "label": "Generate App Docs",
            "description": "Produce user guides, onboarding flows, and release notes.",
            "definition": {
                "steps": [
                    "collect_app_ir",
                    "summarize_features",
                    "generate_user_guide",
                    "generate_onboarding_copy",
                    "generate_release_notes_template",
                ]
            },
        },
    ]


# ============================================================
# PAGE PRESETS
# ============================================================

def get_app_dev_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for an app dev workspace.
    These are IR-level page definitions consumed by the PageEngine (L4+).
    """
    return [
        {
            "key": "dashboard",
            "label": "App Dev Dashboard",
            "widgets": [
                {"type": "stat", "key": "total_apps"},
                {"type": "stat", "key": "recent_runs"},
                {"type": "list", "key": "recent_flows"},
                {"type": "list", "key": "active_app_projects"},
            ],
        },
        {
            "key": "flow_lab",
            "label": "Flow Lab",
            "widgets": [
                {"type": "editor", "key": "app_ir_input"},
                {"type": "output_panel", "key": "flow_design_output"},
                {"type": "output_panel", "key": "screen_map_output"},
            ],
        },
        {
            "key": "app_codegen",
            "label": "App Code Generation",
            "widgets": [
                {"type": "editor", "key": "app_codegen_spec"},
                {"type": "output_panel", "key": "generated_app_code"},
                {"type": "explanation_panel", "key": "architecture_explanation"},
            ],
        },
        {
            "key": "experience_optimization",
            "label": "Experience Optimization",
            "widgets": [
                {"type": "editor", "key": "existing_flow_ir"},
                {"type": "output_panel", "key": "optimization_suggestions"},
                {"type": "output_panel", "key": "copy_variants"},
            ],
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "widgets": [
                {"type": "chart", "key": "engine_usage"},
                {"type": "chart", "key": "flow_success_rate"},
                {"type": "chart", "key": "app_iterations"},
            ],
        },
    ]


# ============================================================
# FULL PRESET
# ============================================================

def get_app_dev_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize an app dev workspace.
    Fully compatible with WorkspaceFactory (L4+).
    """
    return {
        "type": "app_dev",
        "label": "App Development",
        "engines": get_app_dev_default_engines(),
        "flows": get_app_dev_default_flows(),
        "pages": get_app_dev_default_pages(),
        "version": 1,
    }


APP_DEV_PRESET = get_app_dev_workspace_preset()
