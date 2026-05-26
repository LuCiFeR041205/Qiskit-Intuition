import os
import requests
import json
import streamlit as st
from .base_agent import BACKEND_URL, is_backend_online, generate_stream
from agents.router_agent import (
    _keyword_classify,
    classify_intent as local_classify_intent,
    route_and_respond as local_route_and_respond,
    explain_concept_chat as local_explain_concept_chat,
    generate_code_chat as local_generate_code_chat,
    generate_problem_chat as local_generate_problem_chat,
    general_chat as local_general_chat,
    AGENT_META
)

def classify_intent(user_message: str) -> str:
    if is_backend_online():
        try:
            keyword_res = _keyword_classify(user_message)
            if keyword_res != "general":
                return keyword_res
        except Exception:
            pass
    return local_classify_intent(user_message)

def route_and_respond(user_message: str, intent: str = None):
    if intent is None:
        intent = classify_intent(user_message)
        
    if is_backend_online():
        try:
            headers = {}
            if "user_gemini_api_key" in st.session_state and st.session_state["user_gemini_api_key"]:
                headers["X-Gemini-API-Key"] = st.session_state["user_gemini_api_key"]
            response = requests.post(f"{BACKEND_URL}/agent/route", json={"user_message": user_message}, stream=True, headers=headers)
            if response.status_code == 200:
                def sse_parser():
                    current_event = None
                    for line in response.iter_lines():
                        if line:
                            decoded = line.decode('utf-8').strip()
                            if decoded.startswith("event:"):
                                current_event = decoded[6:].strip()
                            elif decoded.startswith("data:"):
                                data_val = decoded[5:].strip()
                                if current_event == "chunk":
                                    yield data_val
                                elif current_event == "intent":
                                    pass
                                else:
                                    yield data_val
                return intent, sse_parser()
        except Exception:
            pass
            
    return local_route_and_respond(user_message, intent)

def explain_concept_chat(user_message: str):
    if is_backend_online():
        prompt = """
You are A.C.E., a highly advanced educational AI. 
Explain the quantum concept the user is asking about using brilliant, real-world 
mechanical or physical analogies. Be warm, address them as 'Boss' or 'Creator'.
Always maintain a polite, sophisticated, and gender-neutral British AI persona.
Use markdown formatting for clarity. Keep it engaging and under 250 words.
"""
        return generate_stream(prompt, user_message)
    return local_explain_concept_chat(user_message)

def generate_code_chat(user_message: str):
    if is_backend_online():
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
        return generate_stream(prompt, user_message)
    return local_generate_code_chat(user_message)

def generate_problem_chat(user_message: str):
    if is_backend_online():
        prompt = """
You are A.C.E., acting as the Socratic Tutor.
Create a thought-provoking conceptual challenge related to what the user mentioned.
- Do NOT give the answer directly.
- Present 2-3 "what if" scenarios that test deep understanding.
- Be warm and encouraging, address the user as 'Boss' or 'Creator'.
- Keep it under 150 words.
"""
        return generate_stream(prompt, user_message)
    return local_generate_problem_chat(user_message)

def general_chat(user_message: str):
    if is_backend_online():
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
        return generate_stream(GENERAL_PROMPT, user_message)
    return local_general_chat(user_message)
