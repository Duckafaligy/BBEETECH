# l4_core/industries/physics_sim.py

"""
Physics Simulation Industry Preset (L4+)
----------------------------------------
Defines the default engines, flows, and pages for Physics Simulation workspaces.

This preset is:
  - Stateless
  - Pure data
  - Fully compatible with WorkspaceFactory (L4+)
  - Tuned for math, numerical methods, simulation code, and multi-level explanations
"""

from __future__ import annotations
from typing import List, Dict, Any


# ============================================================
# ENGINE PRESETS
# ============================================================

def get_physics_sim_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for physics simulation workspaces.
    Tuned for:
      - mathematical modeling
      - numerical simulation
      - scientific explanation
      - IR → code pipelines
    """
    return [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "label": "OpenAI GPT-4o (Math & Simulation Code)",
            "enabled": True,
            "priority": 1,
            "allow_fallback": True,
        },
        {
            "provider": "deepseek",
            "model": "deepseek-coder",
            "label": "DeepSeek Coder (Numerical Code & Optimization)",
            "enabled": True,
            "priority": 2,
            "allow_fallback": True,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "label": "Claude 3 Opus (Theory & Explanation)",
            "enabled": True,
            "priority": 3,
            "allow_fallback": True,
        },
        {
            "provider": "internal",
            "model": "physics-ir-teacher",
            "label": "Internal Physics IR Teacher (Patterns & Reuse)",
            "enabled": False,
            "priority": 4,
            "allow_fallback": False,
        },
    ]


# ============================================================
# FLOW PRESETS
# ============================================================

def get_physics_sim_default_flows() -> List[Dict[str, Any]]:
    """
    High-level IR-driven flow templates for physics simulation workspaces.
    These are interpreted by the FlowEngine (L4+).
    """
    return [
        {
            "key": "design_simulation",
            "label": "Design Simulation",
            "description": "Define the system, variables, forces, and outputs.",
            "definition": {
                "steps": [
                    "collect_sim_ir",
                    "define_state_variables",
                    "define_forces_and_equations",
                    "define_initial_conditions",
                    "define_observables_and_outputs",
                    "generate_simulation_spec",
                ]
            },
        },
        {
            "key": "generate_python_simulation",
            "label": "Generate Python Simulation",
            "description": "Generate Python code using numpy/scipy or pure math.",
            "definition": {
                "steps": [
                    "analyze_simulation_spec",
                    "choose_numerical_method",
                    "generate_simulation_code",
                    "generate_run_script",
                    "generate_plotting_code",
                    "generate_readme_and_usage",
                ]
            },
        },
        {
            "key": "analyze_results",
            "label": "Analyze Results",
            "description": "Analyze simulation outputs and summarize insights.",
            "definition": {
                "steps": [
                    "collect_simulation_output",
                    "compute_key_metrics",
                    "detect_patterns_or_anomalies",
                    "generate_summary_and_plots_ir",
                ]
            },
        },
        {
            "key": "generate_visualization_ir",
            "label": "Generate Visualization IR",
            "description": "Define how to visualize the simulation in 2D/3D.",
            "definition": {
                "steps": [
                    "collect_simulation_spec",
                    "define_visual_entities",
                    "define_time_mapping",
                    "define_camera_or_view",
                    "generate_visualization_ir",
                ]
            },
        },
        {
            "key": "explain_simulation",
            "label": "Explain Simulation",
            "description": "Explain the math, code, and behavior at multiple levels.",
            "definition": {
                "steps": [
                    "collect_simulation_code",
                    "generate_beginner_explanation",
                    "generate_intermediate_explanation",
                    "generate_expert_explanation",
                ]
            },
        },
    ]


# ============================================================
# PAGE PRESETS
# ============================================================

def get_physics_sim_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for a physics simulation workspace.
    These are IR-level page definitions consumed by the PageEngine (L4+).
    """
    return [
        {
            "key": "dashboard",
            "label": "Physics Sim Dashboard",
            "widgets": [
                {"type": "stat", "key": "total_simulations"},
                {"type": "stat", "key": "recent_runs"},
                {"type": "list", "key": "recent_flows"},
            ],
        },
        {
            "key": "sim_lab",
            "label": "Simulation Lab",
            "widgets": [
                {"type": "editor", "key": "sim_ir_input"},
                {"type": "output_panel", "key": "simulation_spec_output"},
                {"type": "output_panel", "key": "generated_simulation_code"},
                {"type": "output_panel", "key": "plotting_code"},
            ],
        },
        {
            "key": "visualization",
            "label": "Visualization",
            "widgets": [
                {"type": "canvas", "key": "sim_visualization_canvas"},
                {"type": "control_panel", "key": "sim_controls"},
                {"type": "output_panel", "key": "visualization_ir"},
            ],
        },
        {
            "key": "explanations",
            "label": "Explanations",
            "widgets": [
                {"type": "output_panel", "key": "beginner_explanation"},
                {"type": "output_panel", "key": "intermediate_explanation"},
                {"type": "output_panel", "key": "expert_explanation"},
            ],
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "widgets": [
                {"type": "chart", "key": "engine_usage"},
                {"type": "chart", "key": "flow_success_rate"},
                {"type": "chart", "key": "simulation_iterations"},
            ],
        },
    ]


# ============================================================
# FULL PRESET
# ============================================================

def get_physics_sim_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize a physics simulation workspace.
    Fully compatible with WorkspaceFactory (L4+).
    """
    return {
        "type": "physics_sim",
        "label": "Physics Simulation",
        "engines": get_physics_sim_default_engines(),
        "flows": get_physics_sim_default_flows(),
        "pages": get_physics_sim_default_pages(),
        "version": 1,
    }


PHYSICS_SIM_PRESET = get_physics_sim_workspace_preset()
