from .base_agent import generate_stream
from .feynman_agent import explain_concept
from .qiskit_engineer import generate_code
from .socratic_tutor import generate_problem

ROUTER_PROMPT = """
You are a silent routing classifier. Given a user message about quantum computing, 
classify the intent into EXACTLY ONE of these categories. Respond with ONLY the category word:

- explain : The user wants a concept explained, wants an analogy, or asks "what is X?"
- code    : The user wants Qiskit code, a code example, or says "show me how to..."
- test    : The user wants to be quizzed, tested, or challenged on a concept.
- general : Anything else — greetings, meta questions, or unclear intent.

Respond with ONLY the single word: explain, code, test, or general.
"""

GENERAL_PROMPT = """
You are A.C.E. (Advanced Conceptual Explainer), a warm, brilliant AI companion 
for a quantum computing learning lab.
- You address the user as 'Boss' or 'Creator' in a warm, sophisticated British persona.
- You are knowledgeable about quantum computing, Qiskit, and physics.
- You are encouraging, never condescending, and always gender-neutral.
- Keep responses focused, clear, and under 200 words unless a longer explanation is needed.
- If the user greets you, greet them back warmly and suggest what they could explore.
- Reference the tools available: Compose tab for building circuits, Learn tab for curriculum,
  and Sandbox for running code.
"""

AGENT_META = {
    "explain": {
        "name": "Feynman Agent",
        "avatar": "🧠",
        "description": "Physical intuition & analogies",
    },
    "code": {
        "name": "Qiskit Engineer",
        "avatar": "⌨️",
        "description": "Code generation & examples",
    },
    "test": {
        "name": "Socratic Tutor",
        "avatar": "🎯",
        "description": "Conceptual challenges",
    },
    "general": {
        "name": "A.C.E.",
        "avatar": "⚛️",
        "description": "General assistant",
    },
}


import os
import re


def _keyword_classify(msg: str) -> str:
    """Fast, deterministic intent classification using keyword patterns."""
    lower = msg.lower().strip()

    code_patterns = re.compile(
        r"\b(code|show me|write|implement|qiskit|circuit|example|snippet|program|script|build me)\b"
    )
    test_patterns = re.compile(
        r"\b(test me|quiz|challenge|check my|assess|question me|grill)\b"
    )
    explain_patterns = re.compile(
        r"\b(explain|what is|what are|how does|why does|tell me about|describe|intuition|analogy|meaning)\b"
    )

    if test_patterns.search(lower):
        return "test"
    if code_patterns.search(lower):
        return "code"
    if explain_patterns.search(lower):
        return "explain"
    return "general"


def classify_intent(user_message: str, api_key: str = None) -> str:
    """Classify user intent. Uses keywords first; tries Gemini only when the
    API key is set and keywords return 'general' (ambiguous)."""
    keyword_result = _keyword_classify(user_message)

    # If keywords gave a clear specialist match, use it — no API call needed
    if keyword_result != "general":
        return keyword_result

    # For ambiguous messages, try Gemini if available
    if not api_key and not os.environ.get("GEMINI_API_KEY"):
        return keyword_result

    try:
        chunks = []
        for chunk in generate_stream(ROUTER_PROMPT, user_message, api_key=api_key):
            chunks.append(chunk)
        result = "".join(chunks).strip().lower()

        for category in ("explain", "code", "test", "general"):
            if category in result:
                return category
    except Exception:
        pass

    return keyword_result


def route_and_respond(user_message: str, intent: str = None, api_key: str = None):
    """Route a user message to the appropriate agent and return a stream."""
    if intent is None:
        intent = classify_intent(user_message, api_key=api_key)

    if intent == "explain":
        return intent, explain_concept_chat(user_message, api_key=api_key)
    elif intent == "code":
        return intent, generate_code_chat(user_message, api_key=api_key)
    elif intent == "test":
        return intent, generate_problem_chat(user_message, api_key=api_key)
    else:
        return intent, general_chat(user_message, api_key=api_key)


def explain_concept_chat(user_message: str, api_key: str = None):
    prompt = """
You are A.C.E., a highly advanced educational AI. 
Explain the quantum concept the user is asking about using brilliant, real-world 
mechanical or physical analogies. Be warm, address them as 'Boss' or 'Creator'.
Always maintain a polite, sophisticated, and gender-neutral British AI persona.
Use markdown formatting for clarity. Keep it engaging and under 250 words.
"""
    return generate_stream(prompt, user_message, api_key=api_key)


def generate_code_chat(user_message: str, api_key: str = None):
    prompt = """
You are A.C.E., acting as the Qiskit Engineer.
Generate clean, well-commented Qiskit Python code for what the user is asking.
- Use Qiskit 1.0+ syntax.
- Include imports.
- Add clear comments explaining each step.
- If applicable, include a circuit drawing and statevector inspection.
- Address the user warmly as 'Boss' or 'Creator'.
- Wrap code in ```python blocks.
"""
    return generate_stream(prompt, user_message, api_key=api_key)


def generate_problem_chat(user_message: str, api_key: str = None):
    prompt = """
You are A.C.E., acting as the Socratic Tutor.
Create a thought-provoking conceptual challenge related to what the user mentioned.
- Do NOT give the answer directly.
- Present 2-3 "what if" scenarios that test deep understanding.
- Be warm and encouraging, address the user as 'Boss' or 'Creator'.
- Keep it under 150 words.
"""
    return generate_stream(prompt, user_message, api_key=api_key)


def general_chat(user_message: str, api_key: str = None):
    return generate_stream(GENERAL_PROMPT, user_message, api_key=api_key)
