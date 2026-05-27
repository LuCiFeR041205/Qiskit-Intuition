from .base_agent import stream_from_backend, load_root_agent

_root = load_root_agent("socratic_tutor")

def generate_problem(concept: str):
    return stream_from_backend(
        "challenge",
        {"concept": concept},
        _root.generate_problem(concept)
    )
