from .base_agent import stream_from_backend
from agents.socratic_tutor import generate_problem as local_generate_problem

def generate_problem(concept: str):
    return stream_from_backend(
        "challenge",
        {"concept": concept},
        local_generate_problem(concept)
    )
