# l4_core/industries/app_dev.py

from typing import List, Dict, Any


def get_app_dev_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for app dev workspaces.
    Tuned for product flows, mobile/desktop apps, and UX-heavy logic.
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


def get_app_dev_default_flows() -> List[Dict[str, Any]]:
    """
    High-level flow templates for app dev workspaces.
    IR-level definitions; the flow engine will interpret them.
    """
    return [
        {
            "key": "design_app_flow",
            "label": "Design App Flow",
            "description": "From IR, design screens, navigation, and user journeys.",
            "steps": [
                "collect_app_ir",
                "define_user_personas",
                "define_screens_and_states",
                "define_navigation_and_edges",
                "generate_flow_diagram_ir",
            ],
        },
        {
            "key": "generate_mobile_app",
            "label": "Generate Mobile App",
            "description": "Generate React Native/Flutter/Swift/Kotlin code from IR.",
            "steps": [
                "collect_platform_preferences",
                "generate_data_model",
                "generate_app_screens",
                "generate_navigation_code",
                "generate_api_integration",
                "generate_readme_and_setup",
            ],
        },
        {
            "key": "generate_desktop_app",
            "label": "Generate Desktop App",
            "description": "Generate Electron/Tauri/native desktop app from IR.",
            "steps": [
                "collect_app_ir",
                "generate_window_and_menu_structure",
                "generate_core_logic",
                "generate_persistence_layer",
                "generate_build_and_packaging_files",
            ],
        },
        {
            "key": "optimize_app_experience",
            "label": "Optimize App Experience",
            "description": "Analyze flows and suggest UX, performance, and accessibility improvements.",
            "steps": [
                "collect_existing_flows",
                "analyze_pain_points",
                "propose_improvements",
                "generate_diff_and_explanations",
            ],
        },
        {
            "key": "generate_app_docs",
            "label": "Generate App Docs",
            "description": "Produce user guides, onboarding flows, and release notes.",
            "steps": [
                "collect_app_ir",
                "summarize_features",
                "generate_user_guide",
                "generate_onboarding_copy",
                "generate_release_notes_template",
            ],
        },
    ]


def get_app_dev_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for an app dev workspace.
    Page IRs; the page engine will render them.
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


def get_app_dev_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize an app dev workspace.
    Stateless, pure, safe to call from workspace creation logic.
    """
    return {
        "type": "app_dev",
        "label": "App Development",
        "default_engines": get_app_dev_default_engines(),
        "default_flows": get_app_dev_default_flows(),
        "default_pages": get_app_dev_default_pages(),
    }
