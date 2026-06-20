import os
import sys
import importlib.util
import requests

# Load the ROOT-level agents/base_agent.py directly by file path
# to avoid the circular import that happens when Python resolves
# `agents.base_agent` to THIS package (frontend/agents/).
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_root_agent(module_name: str):
    """Load a root-level agents/<module_name>.py avoiding circular imports with frontend/agents/."""
    pkg_name = "root_agents"
    # Register the root agents/ directory as a package the first time
    if pkg_name not in sys.modules:
        pkg_path = os.path.join(_root, "agents")
        pkg_init = os.path.join(pkg_path, "__init__.py")
        pkg_spec = importlib.util.spec_from_file_location(
            pkg_name, pkg_init,
            submodule_search_locations=[pkg_path]
        )
        pkg = importlib.util.module_from_spec(pkg_spec)
        pkg.__path__ = [pkg_path]
        pkg.__package__ = pkg_name
        sys.modules[pkg_name] = pkg
        pkg_spec.loader.exec_module(pkg)

    full_name = f"{pkg_name}.{module_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]

    path = os.path.join(_root, "agents", f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(full_name, path,
        submodule_search_locations=[os.path.join(_root, "agents")])
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod

_root_base = load_root_agent("base_agent")
local_generate_stream = _root_base.generate_stream

BACKEND_URL = "http://localhost:8000"

def is_backend_online():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False

def stream_from_backend(endpoint: str, payload: dict, local_generator):
    if is_backend_online():
        try:
            response = requests.post(f"{BACKEND_URL}/agent/{endpoint}", json=payload, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith("data:"):
                            yield decoded[5:].strip()
                return
        except Exception:
            pass
    # Fallback to local
    yield from local_generator

def generate_stream(system_prompt: str, user_prompt: str):
    return stream_from_backend(
        "stream",
        {"system_prompt": system_prompt, "user_prompt": user_prompt},
        local_generate_stream(system_prompt, user_prompt)
    )
