from .base_agent import stream_from_backend, load_root_agent

_root = load_root_agent("feynman_agent")

def explain_concept(concept: str):
    return stream_from_backend(
        "explain",
        {"concept": concept},
        _root.explain_concept(concept)
    )
