# l4_core/industries/web_dev.py

"""
Web Development Industry Preset (L4+)
-------------------------------------
Defines the default engines, flows, and pages for Web Dev workspaces.

This preset is:
  - Stateless
  - Pure data
  - Fully compatible with WorkspaceFactory (L4+)
  - Tuned for frontend frameworks, backend APIs, SEO, UX writing, and design systems
"""

from __future__ import annotations
from typing import List, Dict, Any


# ============================================================
# ENGINE PRESETS
# ============================================================

def get_web_dev_default_engines() -> List[Dict[str, Any]]:
    """
    Default engine preferences for web dev workspaces.
    Tuned for:
      - frontend frameworks
      - backend APIs
      - SEO
      - UX writing
      - IR → full-stack pipelines
    """
    return [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "label": "OpenAI GPT-4o (Full-Stack Web)",
            "enabled": True,
            "priority": 1,
            "allow_fallback": True,
        },
        {
            "provider": "deepseek",
            "model": "deepseek-coder",
            "label": "DeepSeek Coder (Frontend/Backend Code)",
            "enabled": True,
            "priority": 2,
            "allow_fallback": True,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "label": "Claude 3 Opus (UX, IA, Reasoning)",
            "enabled": True,
            "priority": 3,
            "allow_fallback": True,
        },
        {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "label": "Gemini 1.5 Pro (Multimodal Web Assets)",
            "enabled": False,
            "priority": 4,
            "allow_fallback": True,
        },
        {
            "provider": "internal",
            "model": "web-ir-teacher",
            "label": "Internal Web IR Teacher (Patterns & Reuse)",
            "enabled": False,
            "priority": 5,
            "allow_fallback": False,
        },
    ]


# ============================================================
# FLOW PRESETS
# ============================================================

def get_web_dev_default_flows() -> List[Dict[str, Any]]:
    """
    High-level IR-driven flow templates for web dev workspaces.
    These are interpreted by the FlowEngine (L4+).
    """
    return [
        {
            "key": "generate_full_stack_website",
            "label": "Generate Full-Stack Website",
            "description": "Generate Next.js/Vite/React frontend + FastAPI/Node backend from IR.",
            "definition": {
                "steps": [
                    "collect_site_ir",
                    "design_information_architecture",
                    "generate_frontend_components",
                    "generate_backend_routes",
                    "generate_api_schemas",
                    "generate_deployment_files",
                    "generate_readme_and_docs",
                ]
            },
        },
        {
            "key": "generate_landing_page",
            "label": "Generate Landing Page",
            "description": "Generate a high-converting landing page with copy, layout, and SEO.",
            "definition": {
                "steps": [
                    "collect_brand_ir",
                    "generate_copywriting",
                    "generate_layout_structure",
                    "generate_react_components",
                    "generate_css_or_tailwind",
                    "generate_seo_metadata",
                ]
            },
        },
        {
            "key": "optimize_website",
            "label": "Optimize Website",
            "description": "Analyze performance, SEO, accessibility, and UX; propose improvements.",
            "definition": {
                "steps": [
                    "collect_existing_site_ir",
                    "analyze_performance",
                    "analyze_accessibility",
                    "analyze_seo",
                    "propose_improvements",
                    "generate_diff_and_explanations",
                ]
            },
        },
        {
            "key": "generate_design_system",
            "label": "Generate Design System",
            "description": "Generate a reusable design system with tokens, components, and docs.",
            "definition": {
                "steps": [
                    "collect_brand_ir",
                    "generate_design_tokens",
                    "generate_component_library",
                    "generate_usage_guidelines",
                    "generate_docs_and_examples",
                ]
            },
        },
        {
            "key": "generate_cms_site",
            "label": "Generate CMS Site",
            "description": "Generate a CMS-backed site (Sanity, Strapi, Contentful) from IR.",
            "definition": {
                "steps": [
                    "collect_cms_ir",
                    "generate_cms_schema",
                    "generate_frontend_pages",
                    "generate_api_integration",
                    "generate_editor_guidelines",
                ]
            },
        },
    ]


# ============================================================
# PAGE PRESETS
# ============================================================

def get_web_dev_default_pages() -> List[Dict[str, Any]]:
    """
    Default UI pages for a web dev workspace.
    These are IR-level page definitions consumed by the PageEngine (L4+).
    """
    return [
        {
            "key": "dashboard",
            "label": "Web Dev Dashboard",
            "widgets": [
                {"type": "stat", "key": "total_sites"},
                {"type": "stat", "key": "recent_runs"},
                {"type": "list", "key": "recent_flows"},
                {"type": "list", "key": "active_projects"},
            ],
        },
        {
            "key": "site_lab",
            "label": "Site Lab",
            "widgets": [
                {"type": "editor", "key": "site_ir_input"},
                {"type": "output_panel", "key": "site_structure_output"},
                {"type": "output_panel", "key": "generated_frontend_code"},
                {"type": "output_panel", "key": "generated_backend_code"},
            ],
        },
        {
            "key": "design_system",
            "label": "Design System",
            "widgets": [
                {"type": "editor", "key": "design_system_ir"},
                {"type": "output_panel", "key": "design_tokens"},
                {"type": "output_panel", "key": "component_library"},
                {"type": "output_panel", "key": "usage_docs"},
            ],
        },
        {
            "key": "seo_lab",
            "label": "SEO Lab",
            "widgets": [
                {"type": "editor", "key": "seo_ir"},
                {"type": "output_panel", "key": "seo_suggestions"},
                {"type": "output_panel", "key": "copy_variants"},
            ],
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "widgets": [
                {"type": "chart", "key": "engine_usage"},
                {"type": "chart", "key": "flow_success_rate"},
                {"type": "chart", "key": "site_iterations"},
            ],
        },
    ]


# ============================================================
# FULL PRESET
# ============================================================

def get_web_dev_workspace_preset() -> Dict[str, Any]:
    """
    Single entrypoint: everything needed to initialize a web dev workspace.
    Fully compatible with WorkspaceFactory (L4+).
    """
    return {
        "type": "web_dev",
        "label": "Web Development",
        "engines": get_web_dev_default_engines(),
        "flows": get_web_dev_default_flows(),
        "pages": get_web_dev_default_pages(),
        "version": 1,
    }


WEB_DEV_PRESET = get_web_dev_workspace_preset()
