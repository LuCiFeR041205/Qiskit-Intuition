from .base_agent import generate_stream

TUTOR_PROMPT = """
You are the Diagnostic Protocol running a check on the user's understanding.
Pose a highly conceptual 'What if?' scenario to test their quantum intuition.
Keep it under 100 words. Be encouraging but analytical, addressing the user as Explorer (avoid gendered terms like Sir).
"""

def generate_problem(concept: str):
    user_prompt = f"Run a diagnostic scenario for the concept of '{concept}'."
    return generate_stream(TUTOR_PROMPT, user_prompt)
