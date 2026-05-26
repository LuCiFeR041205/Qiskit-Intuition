from .base_agent import generate_stream

TUTOR_PROMPT = """
You are the Diagnostic Protocol running a check on the user's understanding.
Pose a highly conceptual 'What if?' scenario to test their quantum intuition.
Keep it under 100 words. Be encouraging but analytical, addressing the user as Boss or Creator (avoid gendered terms like Sir).
"""

def generate_problem(concept: str, api_key: str = None):
    user_prompt = f"Run a diagnostic scenario for the concept of '{concept}'."
    return generate_stream(TUTOR_PROMPT, user_prompt, api_key=api_key)
