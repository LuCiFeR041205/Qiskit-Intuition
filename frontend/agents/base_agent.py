import os
import requests
import streamlit as st
from agents.base_agent import generate_stream as local_generate_stream

BACKEND_URL = "http://localhost:8000"

def is_backend_online():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False

def stream_from_backend(endpoint: str, payload: dict, local_generator):
    if is_backend_online():
        try:
            headers = {}
            if "user_gemini_api_key" in st.session_state and st.session_state["user_gemini_api_key"]:
                headers["X-Gemini-API-Key"] = st.session_state["user_gemini_api_key"]
            response = requests.post(f"{BACKEND_URL}/agent/{endpoint}", json=payload, stream=True, headers=headers)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith("data:"):
                            yield decoded[5:].strip()
                return
        except Exception:
            pass
    # Fallback to local
    yield from local_generator

def generate_stream(system_prompt: str, user_prompt: str):
    return stream_from_backend(
        "stream",
        {"system_prompt": system_prompt, "user_prompt": user_prompt},
        local_generate_stream(system_prompt, user_prompt)
    )
