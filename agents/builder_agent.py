import os
import json
import google.generativeai as genai

BUILDER_PROMPT = """
You are A.C.E., an expert Quantum Circuit Architect.
The user wants to build a quantum circuit using natural language.
Translate their request into a JSON list of gate operations.

Allowed gates: H, X, Y, Z, S, SDG, T, TDG, RX, RY, RZ, CNOT
Format for each gate:
{
    "gate": "GATE_NAME",
    "target": target_qubit_index,
    "control": control_qubit_index (only for CNOT, otherwise null),
    "angle": rotation_angle_in_radians (only for RX, RY, RZ, otherwise null)
}

Example Request: "Entangle qubit 0 and 1"
Example Response:
[
    {"gate": "H", "target": 0, "control": null, "angle": null},
    {"gate": "CNOT", "target": 1, "control": 0, "angle": null}
]

ONLY return valid JSON matching this schema. No markdown wrapping.
"""

def build_circuit_from_prompt(user_prompt: str, num_qubits: int, api_key: str = None) -> list:
    """Takes a natural language prompt and returns a list of gate dicts."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return []

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    full_prompt = f"{BUILDER_PROMPT}\n\nThe circuit has {num_qubits} qubits (indices 0 to {num_qubits - 1}).\nUser Request: {user_prompt}"
    
    try:
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error building circuit: {e}")
        return []
