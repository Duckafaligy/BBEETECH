# l4_core/industries/graphics_3d.py

from typing import List, Dict, Any


def get_graphics_3d_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for graphics / 3D workspaces.
    Tuned for code, IR, and asset descriptions (not public content creation).
    """
    return [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "label": "OpenAI GPT-4o (Graphics & 3D Code/IR)",
            "enabled": True,
            "priority": 1,
            "allow_fallback": True,
        },
        {
            "provider": "deepseek",
            "model": "deepseek-coder",
            "label": "DeepSeek Coder (Shaders, Pipelines, Tools)",
            "enabled": True,
            "priority": 2,
            "allow_fallback": True,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "label": "Claude 3 Opus (Visual Systems & Docs)",
            "enabled": True,
            "priority": 3,
            "allow_fallback": True,
        },
        {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "label": "Gemini 1.5 Pro (Multimodal Asset IR)",
            "enabled": False,
            "priority": 4,
            "allow_fallback": True,
        },
        {
            "provider": "internal",
            "model": "graphics-ir-teacher",
            "label": "Internal Graphics IR Teacher (Patterns & Reuse)",
            "enabled": False,
            "priority": 5,
            "allow_fallback": False,
        },
    ]


def get_graphics_3d_default_flows() -> List[Dict[str, Any]]:
    """
    High-level flow templates for graphics / 3D workspaces.
    IR-level definitions; the flow engine will interpret them.
    """
    return [
        {
            "key": "design_visual_style",
            "label": "Design Visual Style",
            "description": "From IR, define visual language, palettes, materials, and lighting style.",
            "steps": [
                "collect_style_ir",
                "define_color_palette",
                "define_material_families",
                "define_lighting_and_postfx",
                "generate_style_guide_doc",
            ],
        },
        {
            "key": "generate_shader_pipeline",
            "label": "Generate Shader Pipeline",
            "description": "Generate shader code (GLSL/HLSL/Unreal/Unity) and integration notes.",
            "steps": [
                "collect_shader_ir",
                "choose_target_engine",
                "generate_shader_code",
                "generate_material_setup_instructions",
                "generate_debug_and_profiling_tips",
            ],
        },
        {
            "key": "generate_3d_asset_ir",
            "label": "Generate 3D Asset IR",
            "description": "Define 3D assets in IR: topology, scale, materials, LODs, usage.",
            "steps": [
                "collect_asset_ir",
                "define_geometry_and_scale",
                "define_material_slots",
                "define_lods_and_variants",
                "define_usage_contexts",
                "generate_asset_spec",
            ],
        },
        {
            "key": "generate_blender_script",
            "label": "Generate Blender Script",
            "description": "Generate Blender Python scripts to create or modify assets/scenes.",
            "steps": [
                "collect_asset_or_scene_ir",
                "generate_blender_python_script",
                "generate_import_export_instructions",
                "generate_readme_for_artists",
            ],
        },
        {
            "key": "integrate_assets_unreal",
            "label": "Integrate Assets (Unreal)",
            "description": "Generate Unreal asset setup: materials, blueprints, folders, metadata.",
            "steps": [
                "collect_asset_ir",
                "generate_unreal_import_settings",
                "generate_material_and_instance_setup",
                "generate_blueprint_or_actor_setup",
                "generate_folder_structure_and_naming",
                "generate_integration_readme",
            ],
        },
        {
            "key": "integrate_assets_unity",
            "label": "Integrate Assets (Unity)",
            "description": "Generate Unity import settings, prefabs, and scene integration.",
            "steps": [
                "collect_asset_ir",
                "generate_unity_import_settings",
                "generate_prefab_setup",
                "generate_scene_integration_instructions",
                "generate_folder_structure_and_naming",
            ],
        },
        {
            "key": "generate_animation_graph_ir",
            "label": "Generate Animation Graph IR",
            "description": "Define animation states, transitions, and parameters in IR.",
            "steps": [
                "collect_character_or_object_ir",
                "define_animation_states",
                "define_transitions_and_conditions",
                "define_parameters_and_curves",
                "generate_animation_graph_spec",
            ],
        },
        {
            "key": "generate_cursor_reactive_3d_element",
            "label": "Generate Cursor-Reactive 3D Element",
            "description": "Generate 3D element (e.g., Three.js/R3F) that reacts to cursor movement.",
            "steps": [
                "collect_interaction_ir",
                "generate_3d_component_code",
                "generate_input_mapping_logic",
                "generate_styling_and_theming",
                "generate_integration_instructions_for_web_or_app",
            ],
        },
    ]


def get_graphics_3d_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for a graphics / 3D workspace.
    Page IRs; the page engine will render them.
    """
    return [
        {
            "key": "dashboard",
            "label": "Graphics & 3D Dashboard",
            "widgets": [
                {"type": "stat", "key": "total_assets"},
                {"type": "stat", "key": "total_shaders"},
                {"type": "stat", "key": "recent_runs"},
                {"type": "list", "key": "recent_flows"},
            ],
        },
        {
            "key": "style_lab",
            "label": "Style Lab",
            "widgets": [
                {"type": "editor", "key": "style_ir_input"},
                {"type": "output_panel", "key": "style_guide_output"},
                {"type": "output_panel", "key": "material_families_output"},
            ],
        },
        {
            "key": "shader_lab",
            "label": "Shader Lab",
            "widgets": [
                {"type": "editor", "key": "shader_ir_input"},
                {"type": "output_panel", "key": "shader_code_output"},
                {"type": "output_panel", "key": "engine_integration_notes"},
            ],
        },
        {
            "key": "asset_lab",
            "label": "Asset Lab",
            "widgets": [
                {"type": "editor", "key": "asset_ir_input"},
                {"type": "output_panel", "key": "asset_spec_output"},
                {"type": "output_panel", "key": "engine_integration_scripts"},
            ],
        },
        {
            "key": "animation_lab",
            "label": "Animation Lab",
            "widgets": [
                {"type": "editor", "key": "animation_ir_input"},
                {"type": "output_panel", "key": "animation_graph_spec"},
                {"type": "output_panel", "key": "engine_graph_setup_instructions"},
            ],
        },
        {
            "key": "interactive_elements",
            "label": "Interactive Elements",
            "widgets": [
                {"type": "editor", "key": "interaction_ir_input"},
                {"type": "output_panel", "key": "interactive_3d_component_code"},
                {"type": "output_panel", "key": "integration_readme"},
            ],
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "widgets": [
                {"type": "chart", "key": "engine_usage"},
                {"type": "chart", "key": "flow_success_rate"},
                {"type": "chart", "key": "asset_iterations"},
            ],
        },
    ]


def get_graphics_3d_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize a graphics / 3D workspace.
    Stateless, pure, safe to call from workspace creation logic.
    """
    return {
        "type": "graphics_3d",
        "label": "Graphics & 3D",
        "default_engines": get_graphics_3d_default_engines(),
        "default_flows": get_graphics_3d_default_flows(),
        "default_pages": get_graphics_3d_default_pages(),
    }
