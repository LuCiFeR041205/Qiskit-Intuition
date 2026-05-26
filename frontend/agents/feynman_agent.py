from .base_agent import stream_from_backend
from agents.feynman_agent import explain_concept as local_explain_concept

def explain_concept(concept: str):
    return stream_from_backend(
        "explain",
        {"concept": concept},
        local_explain_concept(concept)
    )
