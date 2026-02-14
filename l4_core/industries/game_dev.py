# l4_core/industries/game_dev.py

"""
Game Development Industry Preset (L4+)
--------------------------------------
Defines the default engines, flows, and pages for Game Dev workspaces.

This preset is:
  - Stateless
  - Pure data
  - Fully compatible with WorkspaceFactory (L4+)
  - Tuned for systems design, gameplay code, tooling, and level IR
"""

from __future__ import annotations
from typing import List, Dict, Any


# ============================================================
# ENGINE PRESETS
# ============================================================

def get_game_dev_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for game dev workspaces.
    Tuned for:
      - gameplay systems
      - engine/tooling code
      - design reasoning
      - multimodal art/design IR
    """
    return [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "label": "OpenAI GPT-4o (Game Systems & Code)",
            "enabled": True,
            "priority": 1,
            "allow_fallback": True,
        },
        {
            "provider": "deepseek",
            "model": "deepseek-coder",
            "label": "DeepSeek Coder (Engine/Tooling Code)",
            "enabled": True,
            "priority": 2,
            "allow_fallback": True,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "label": "Claude 3 Opus (Design Reasoning & Docs)",
            "enabled": True,
            "priority": 3,
            "allow_fallback": True,
        },
        {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "label": "Gemini 1.5 Pro (Multimodal Design/Art IR)",
            "enabled": False,
            "priority": 4,
            "allow_fallback": True,
        },
        {
            "provider": "internal",
            "model": "game-ir-teacher",
            "label": "Internal Game IR Teacher (Patterns & Reuse)",
            "enabled": False,
            "priority": 5,
            "allow_fallback": False,
        },
    ]


# ============================================================
# FLOW PRESETS
# ============================================================

def get_game_dev_default_flows() -> List[Dict[str, Any]]:
    """
    High-level IR-driven flow templates for game dev workspaces.
    These are interpreted by the FlowEngine (L4+).
    """
    return [
        {
            "key": "design_mechanic",
            "label": "Design Game Mechanic",
            "description": "From IR, design a mechanic with rules, edge cases, and tuning parameters.",
            "definition": {
                "steps": [
                    "collect_mechanic_ir",
                    "define_rules_and_states",
                    "define_failure_and_edge_cases",
                    "define_tuning_parameters",
                    "generate_design_doc",
                ]
            },
        },
        {
            "key": "implement_mechanic_unreal",
            "label": "Implement Mechanic (Unreal)",
            "description": "Generate Unreal C++/Blueprint code and integration notes for a mechanic.",
            "definition": {
                "steps": [
                    "analyze_mechanic_ir",
                    "generate_unreal_cpp_or_blueprint",
                    "generate_editor_setup_instructions",
                    "generate_tests_and_debug_tools",
                    "generate_readme_for_integration",
                ]
            },
        },
        {
            "key": "implement_mechanic_unity",
            "label": "Implement Mechanic (Unity)",
            "description": "Generate Unity C# scripts and scene integration instructions.",
            "definition": {
                "steps": [
                    "analyze_mechanic_ir",
                    "generate_unity_csharp_scripts",
                    "generate_prefab_and_scene_setup",
                    "generate_tests_and_debug_tools",
                    "generate_readme_for_integration",
                ]
            },
        },
        {
            "key": "generate_tooling",
            "label": "Generate Editor Tooling",
            "description": "Create Unreal/Unity editor tools for designers (menus, inspectors, utilities).",
            "definition": {
                "steps": [
                    "collect_tool_ir",
                    "generate_editor_scripts",
                    "generate_ui_elements",
                    "generate_usage_docs",
                ]
            },
        },
        {
            "key": "level_blockout_ir",
            "label": "Level Blockout IR",
            "description": "Define a level in IR: spaces, flows, encounters, pacing.",
            "definition": {
                "steps": [
                    "collect_level_ir",
                    "define_spaces_and_paths",
                    "define_encounters_and_beats",
                    "define_metrics_and_goals",
                    "generate_blockout_spec",
                ]
            },
        },
        {
            "key": "generate_gameplay_docs",
            "label": "Generate Gameplay Docs",
            "description": "Produce GDD-style docs from IR and existing systems.",
            "definition": {
                "steps": [
                    "collect_game_ir",
                    "summarize_existing_systems",
                    "generate_gdd_sections",
                    "generate_open_questions_and_risks",
                ]
            },
        },
    ]


# ============================================================
# PAGE PRESETS
# ============================================================

def get_game_dev_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for a game dev workspace.
    These are IR-level page definitions consumed by the PageEngine (L4+).
    """
    return [
        {
            "key": "dashboard",
            "label": "Game Dev Dashboard",
            "widgets": [
                {"type": "stat", "key": "total_mechanics"},
                {"type": "stat", "key": "total_levels"},
                {"type": "list", "key": "recent_flows"},
                {"type": "list", "key": "open_design_questions"},
            ],
        },
        {
            "key": "mechanic_lab",
            "label": "Mechanic Lab",
            "widgets": [
                {"type": "editor", "key": "mechanic_ir_input"},
                {"type": "output_panel", "key": "mechanic_design_doc"},
                {"type": "output_panel", "key": "engine_code_output"},
                {"type": "explanation_panel", "key": "implementation_explanation"},
            ],
        },
        {
            "key": "level_lab",
            "label": "Level Lab",
            "widgets": [
                {"type": "editor", "key": "level_ir_input"},
                {"type": "output_panel", "key": "blockout_spec"},
                {"type": "output_panel", "key": "encounter_flow"},
            ],
        },
        {
            "key": "tooling",
            "label": "Tooling & Pipelines",
            "widgets": [
                {"type": "editor", "key": "tool_ir_input"},
                {"type": "output_panel", "key": "editor_tool_scripts"},
                {"type": "output_panel", "key": "integration_readme"},
            ],
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "widgets": [
                {"type": "chart", "key": "engine_usage"},
                {"type": "chart", "key": "flow_success_rate"},
                {"type": "chart", "key": "mechanic_iterations"},
            ],
        },
    ]


# ============================================================
# FULL PRESET
# ============================================================

def get_game_dev_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize a game dev workspace.
    Fully compatible with WorkspaceFactory (L4+).
    """
    return {
        "type": "game_dev",
        "label": "Game Development",
        "engines": get_game_dev_default_engines(),
        "flows": get_game_dev_default_flows(),
        "pages": get_game_dev_default_pages(),
        "version": 1,
    }


GAME_DEV_PRESET = get_game_dev_workspace_preset()
