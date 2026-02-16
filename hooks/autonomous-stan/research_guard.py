#!/usr/bin/env python3
"""
Research Guard — Enforces research cascade: Graphiti → Context7 → Web.

PreToolUse Hook for all tools.
Detects when the agent tries to do external research and ensures the
knowledge hierarchy is respected:

1. Graphiti first (own knowledge base)
2. Context7 (live docs for known libraries)
3. Firecrawl / WebSearch / WebFetch (general web)

Tool availability is determined at INIT TIME via `.stan/config.yaml`
(declared by user during /stan init), not at runtime.
If a tool isn't declared as available, that enforcement step is skipped.

Also tracks research activity so other hooks can verify research happened.
"""

import json
import sys
import os
from pathlib import Path

# --- Config Loading ---

def get_project_root():
    """Find project root by looking for .stan/ directory."""
    cwd = Path(os.getcwd())
    # Walk up from cwd looking for .stan/
    for d in [cwd] + list(cwd.parents):
        if (d / ".stan").is_dir():
            return d
    return cwd


def load_tools_config():
    """
    Load tools config from .stan/config.yaml.
    Returns dict with tool availability booleans.
    Falls back to all-False if config doesn't exist.
    """
    root = get_project_root()
    config_file = root / ".stan" / "config.yaml"

    if not config_file.exists():
        return {"graphiti": False, "context7": False, "firecrawl": False}

    try:
        # Try pyyaml first
        import yaml
        with open(config_file) as f:
            data = yaml.safe_load(f)
        tools = data.get("tools", {}) if data else {}
        return {
            "graphiti": bool(tools.get("graphiti", False)),
            "context7": bool(tools.get("context7", False)),
            "firecrawl": bool(tools.get("firecrawl", False)),
        }
    except ImportError:
        pass

    # Fallback: simple line-based parser for tools section
    try:
        in_tools = False
        tools = {"graphiti": False, "context7": False, "firecrawl": False}
        for line in config_file.read_text().splitlines():
            stripped = line.strip()
            # Detect tools: section
            if stripped == "tools:" or stripped.startswith("tools:"):
                in_tools = True
                continue
            # Stop at next top-level section
            if in_tools and not line.startswith(" ") and not line.startswith("\t") and stripped:
                break
            if in_tools:
                for tool in ["graphiti", "context7", "firecrawl"]:
                    if stripped.startswith(f"{tool}:"):
                        val = stripped.split(":", 1)[1].strip().split("#")[0].strip().lower()
                        tools[tool] = val == "true"
        return tools
    except Exception:
        return {"graphiti": False, "context7": False, "firecrawl": False}


# --- Session State (tracks research activity within session) ---

def get_state_path():
    state_dir = Path(os.environ.get('STAN_STATE_DIR', '/tmp'))
    return state_dir / '.stan' / 'research_state.json'


def read_state():
    sp = get_state_path()
    try:
        return json.loads(sp.read_text()) if sp.exists() else {}
    except (json.JSONDecodeError, Exception):
        return {}


def write_state(key, value):
    sp = get_state_path()
    sp.parent.mkdir(parents=True, exist_ok=True)
    try:
        state = read_state()
        state[key] = value
        sp.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def append_to_list(key, value):
    state = read_state()
    lst = state.get(key, [])
    if value not in lst:
        lst.append(value)
    write_state(key, lst)


# --- Tool Detection ---

# Libraries that Context7 likely has docs for
KNOWN_LIBS = [
    "react", "vue", "angular", "svelte", "next", "nuxt", "astro", "solid",
    "express", "fastapi", "django", "flask", "hono", "nestjs",
    "typescript", "node", "deno", "bun", "python",
    "langchain", "llamaindex", "openai", "anthropic",
    "prisma", "drizzle", "supabase", "firebase", "redis",
    "tailwind", "bootstrap", "shadcn", "radix",
    "pytest", "jest", "vitest", "playwright", "cypress",
    "docker", "kubernetes", "terraform",
    "vite", "webpack", "esbuild",
    "zustand", "redux", "pinia",
    "graphql", "trpc",
]

DOC_TERMS = ["docs", "documentation", "api", "guide", "tutorial", "how to",
             "example", "reference", "config", "setup", "install"]


def is_lib_search(query):
    """Check if query is about a known library's docs."""
    ql = query.lower()
    for lib in KNOWN_LIBS:
        if lib in ql and any(t in ql for t in DOC_TERMS):
            return True, lib
    return False, ""


def graphiti_was_searched():
    """Check if Graphiti was already searched this session."""
    return read_state().get("graphiti_searched", False)


# --- Output Helpers ---

def allow(message=None):
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow"
        }
    }
    if message:
        result["hookSpecificOutput"]["message"] = message
    return result


def deny(reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }


# --- Main Hook Logic ---

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        print(json.dumps(allow()))
        return

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Load tool availability from config (declared at /stan init)
    tools = load_tools_config()
    has_graphiti = tools["graphiti"]
    has_context7 = tools["context7"]

    # --- Track Graphiti usage ---

    # Direct MCP calls
    if "graphiti" in tool_name.lower():
        write_state("graphiti_searched", True)
        write_state("research_done", True)
        print(json.dumps(allow()))
        return

    # MCP bridge calls
    if tool_name == "mcp__mcp-funnel__bridge_tool_request":
        bridge_tool = tool_input.get("tool", "").lower()
        args = tool_input.get("arguments", {})

        if "graphiti" in bridge_tool:
            if "search" in bridge_tool:
                write_state("graphiti_searched", True)
                write_state("research_done", True)
            print(json.dumps(allow()))
            return

        if "context7" in bridge_tool:
            # Enforce: Graphiti first (only if declared available)
            if has_graphiti and not graphiti_was_searched():
                query = args.get("query", "") or args.get("topic", "")
                print(json.dumps(deny(
                    "📚 GRAPHITI ZUERST!\n\n"
                    f"Du suchst nach: {query[:60]}\n"
                    "→ Erst eigenes Wissen prüfen: search_nodes(query: \"...\")\n"
                    "→ Dann Context7 für Live-Docs."
                )))
                return

            # Track which libs were looked up
            if "resolve" in bridge_tool or "library" in bridge_tool:
                lib = args.get("libraryName", "")
                if lib:
                    append_to_list("context7_libs_checked", lib.lower())

            write_state("research_done", True)
            print(json.dumps(allow()))
            return

        if "firecrawl" in bridge_tool:
            # Enforce: Graphiti first (only if declared available)
            if has_graphiti and not graphiti_was_searched():
                print(json.dumps(deny(
                    "📚 GRAPHITI ZUERST!\n"
                    "→ search_nodes(query: \"...\") bevor du extern suchst."
                )))
                return

            # Suggest: Context7 for known libs (only if declared available)
            if has_context7:
                query = args.get("query", "") or args.get("url", "")
                is_lib, lib = is_lib_search(query)
                checked = read_state().get("context7_libs_checked", [])
                if is_lib and lib not in checked:
                    print(json.dumps(deny(
                        f"💡 Context7 hat Live-Docs für '{lib}'!\n"
                        f"→ context7.resolve_library_id(libraryName: \"{lib}\")\n"
                        "→ Dann context7.query_docs(...) für aktuelle API-Infos.\n"
                        "Firecrawl nur wenn Context7 nicht reicht."
                    )))
                    return

            write_state("research_done", True)
            print(json.dumps(allow()))
            return

    # --- Direct Context7 MCP calls ---

    if "context7" in tool_name.lower():
        if has_graphiti and not graphiti_was_searched():
            print(json.dumps(deny(
                "📚 GRAPHITI ZUERST!\n"
                "→ search_nodes(query: \"...\") bevor du Context7 nutzt."
            )))
            return
        write_state("research_done", True)
        print(json.dumps(allow()))
        return

    # --- Direct Firecrawl MCP calls ---

    if "firecrawl" in tool_name.lower():
        if has_graphiti and not graphiti_was_searched():
            print(json.dumps(deny(
                "📚 GRAPHITI ZUERST!\n"
                "→ search_nodes(query: \"...\") bevor du extern suchst."
            )))
            return
        write_state("research_done", True)
        print(json.dumps(allow()))
        return

    # --- WebSearch / WebFetch ---

    if tool_name in ("WebSearch", "web_search"):
        # Enforce: Graphiti first (only if declared available)
        if has_graphiti and not graphiti_was_searched():
            query = tool_input.get("query", "")
            print(json.dumps(deny(
                f"📚 GRAPHITI ZUERST!\n\n"
                f"Du suchst: \"{query[:60]}\"\n"
                "→ Erst eigenes Wissen: search_nodes(query: \"...\")\n"
                "→ Dann web_search."
            )))
            return

        # Suggest: Context7 for library docs (only if declared available)
        if has_context7:
            query = tool_input.get("query", "")
            is_lib, lib = is_lib_search(query)
            checked = read_state().get("context7_libs_checked", [])
            if is_lib and lib not in checked:
                print(json.dumps(allow(
                    f"💡 Tipp: Context7 hat Live-Docs für '{lib}'. "
                    "Probier context7.resolve_library_id() für aktuelle API-Infos."
                )))
                write_state("research_done", True)
                return

        write_state("research_done", True)
        print(json.dumps(allow()))
        return

    if tool_name in ("WebFetch", "web_fetch"):
        # Enforce: Graphiti first (only if declared available)
        if has_graphiti and not graphiti_was_searched():
            print(json.dumps(deny(
                "📚 GRAPHITI ZUERST!\n"
                "→ search_nodes(query: \"...\") bevor du extern fetchst."
            )))
            return

        write_state("research_done", True)
        print(json.dumps(allow()))
        return

    # --- All other tools: pass through ---
    print(json.dumps(allow()))


if __name__ == "__main__":
    main()
