import math

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

def _gate(gate: str, target: int, control: int = None, angle: float = None) -> dict:
    return {"gate": gate, "target": target, "control": control, "angle": angle}


def _safe_target(index: int, num_qubits: int) -> int:
    return max(0, min(index, max(num_qubits - 1, 0)))


def build_circuit_from_prompt(user_prompt: str, num_qubits: int) -> list:
    """Takes a natural language prompt and returns simple local gate suggestions."""
    text = user_prompt.lower()
    if num_qubits < 1:
        return []

    target = 0
    control = 0
    paired_target = _safe_target(1, num_qubits)

    if "qubit 1" in text or "q1" in text:
        target = _safe_target(1, num_qubits)
    elif "qubit 2" in text or "q2" in text:
        target = _safe_target(2, num_qubits)
    elif "qubit 3" in text or "q3" in text:
        target = _safe_target(3, num_qubits)

    if "bell" in text or "entangle" in text or "cnot" in text or "cx" in text:
        if num_qubits < 2:
            return [_gate("H", 0)]
        return [_gate("H", control), _gate("CNOT", paired_target, control)]
    if "hadamard" in text or "superposition" in text or " h " in f" {text} ":
        return [_gate("H", target)]
    if "bit flip" in text or "pauli x" in text or " x " in f" {text} ":
        return [_gate("X", target)]
    if "phase" in text or "pauli z" in text or " z " in f" {text} ":
        return [_gate("Z", target)]
    if "rx" in text or "rotate x" in text:
        return [_gate("RX", target, angle=math.pi / 2)]
    if "ry" in text or "rotate y" in text:
        return [_gate("RY", target, angle=math.pi / 2)]
    if "rz" in text or "rotate z" in text:
        return [_gate("RZ", target, angle=math.pi / 2)]

    return []
