from .base_agent import stream_from_backend
from agents.qiskit_engineer import generate_code as local_generate_code

def generate_code(concept: str, analogy: str):
    return stream_from_backend(
        "code",
        {"concept": concept, "analogy": analogy},
        local_generate_code(concept, analogy)
    )
