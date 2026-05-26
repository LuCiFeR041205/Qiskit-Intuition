from .base_agent import generate_stream

ENGINEER_PROMPT = """
You are the Quantum Code Synthesizer sub-routine.
Your job is to take a quantum concept and provide the exact Qiskit Python code required to run the simulation on the mainboard.
- Address the user as Boss or Creator (never use gendered terms like Sir).
- Provide ONLY the Python code block (using Markdown).
- Heavily comment the code as if explaining tech specifications.
- Ensure it uses Qiskit 1.0+ syntax.
"""

def generate_code(concept: str, analogy: str, api_key: str = None):
    user_prompt = f"Concept: {concept}\nAnalogy provided: {analogy}\nSynthesize the Qiskit simulation code."
    return generate_stream(ENGINEER_PROMPT, user_prompt, api_key=api_key)
