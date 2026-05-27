from .base_agent import stream_from_backend, load_root_agent

_root = load_root_agent("qiskit_engineer")

def generate_code(concept: str, analogy: str):
    return stream_from_backend(
        "code",
        {"concept": concept, "analogy": analogy},
        _root.generate_code(concept, analogy)
    )
