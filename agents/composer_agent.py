import re
import time


GATE_NOTES = {
    "H": {
        "name": "Hadamard",
        "plain": "It moves a qubit between a definite pole and the equator of the Bloch sphere, where 0 and 1 outcomes can both appear.",
        "state": "From |0>, H creates an even |0> and |1> superposition. From |1>, it creates the same balance with a flipped phase.",
        "watch": "Measurement odds often move toward 50/50, and later phase gates can now create visible interference.",
        "simple": "It turns the qubit from a settled coin into a balanced spinning coin.",
    },
    "X": {
        "name": "Pauli-X",
        "plain": "It rotates the qubit halfway around the X axis, acting like a quantum bit flip.",
        "state": "It swaps |0> and |1>.",
        "watch": "The most likely measurement usually flips from 0 to 1, or from 1 to 0.",
        "simple": "It flips the qubit from one side to the other.",
    },
    "Y": {
        "name": "Pauli-Y",
        "plain": "It rotates halfway around the Y axis, combining a bit flip with a phase change.",
        "state": "It swaps |0> and |1>, while also adding imaginary phase.",
        "watch": "The measurement flip is visible right away; the phase part matters when more gates interfere later.",
        "simple": "It flips the qubit and gives it a twist at the same time.",
    },
    "Z": {
        "name": "Pauli-Z",
        "plain": "It changes relative phase without moving probability between |0> and |1>.",
        "state": "|0> stays |0>; |1> becomes -|1>.",
        "watch": "Counts may look unchanged until another gate, often H, turns that phase into a probability change.",
        "simple": "It changes the qubit's hidden direction, even if the scoreboard does not move yet.",
    },
    "S": {
        "name": "S phase",
        "plain": "It adds a quarter-turn of phase around the Z axis.",
        "state": "|0> stays |0>; |1> becomes i|1>. It does not flip the qubit.",
        "watch": "By itself it usually keeps 0/1 odds the same, but it changes how the qubit interferes with later gates.",
        "simple": "It does not flip the qubit. It gives the |1> part a quarter-turn twist.",
    },
    "T": {
        "name": "T phase",
        "plain": "It adds a smaller eighth-turn phase around the Z axis.",
        "state": "|0> stays |0>; |1> gains a 45 degree phase.",
        "watch": "It is subtle in raw counts, but powerful when later gates convert phase into interference.",
        "simple": "It gives the qubit a small hidden twist.",
    },
    "RX": {
        "name": "RX rotation",
        "plain": "It rotates the qubit around the X axis by the chosen angle.",
        "state": "Small RX angles nudge the state; larger angles can move population between |0> and |1>.",
        "watch": "Look for both probability and phase to change as you adjust the angle.",
        "simple": "It rolls the qubit around the left-right axis.",
    },
    "RY": {
        "name": "RY rotation",
        "plain": "It rotates the qubit around the Y axis by the chosen angle.",
        "state": "RY is one of the clearest ways to smoothly change the odds of measuring 0 versus 1.",
        "watch": "The probability bars should slide smoothly as the angle changes.",
        "simple": "It tips the qubit up or down, changing what you are likely to measure.",
    },
    "RZ": {
        "name": "RZ rotation",
        "plain": "It rotates phase around the Z axis by the chosen angle.",
        "state": "It changes relative phase while keeping the immediate |0> and |1> probabilities fixed.",
        "watch": "Counts may stay still now, then change after an H or another mixing gate.",
        "simple": "It spins the qubit in place, changing its hidden timing.",
    },
    "CNOT": {
        "name": "Controlled-X",
        "plain": "It flips the target only when the control qubit is in the 1 branch.",
        "state": "After a superposition on the control, CNOT can link two qubits so their results are correlated.",
        "watch": "Look for paired outcomes such as 00 and 11 when the control was prepared with H first.",
        "simple": "One qubit becomes the switch, and the other flips only when that switch says yes.",
    },
}


def _clean_gate_name(gate: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(gate).upper())


def _parse_sequence(full_circuit_desc: str) -> list[str]:
    if not full_circuit_desc:
        return []
    pieces = re.split(r"\s*(?:→|->|,|;)\s*", full_circuit_desc)
    return [piece.strip() for piece in pieces if piece.strip()]


def _has_gate(sequence: list[str], gate_name: str) -> bool:
    gate_name = gate_name.upper()
    return any(_clean_gate_name(item).startswith(gate_name) for item in sequence)


def _build_sequence_note(gate_upper: str, sequence: list[str]) -> str:
    if not sequence:
        return "This is the first move in the circuit, so its effect is easy to isolate."
    if gate_upper in {"S", "T", "Z", "RZ"} and _has_gate(sequence[:-1], "H"):
        return "Because your circuit already includes a mixing gate like H, this phase can become visible as interference later."
    if gate_upper == "CNOT" and _has_gate(sequence[:-1], "H"):
        return "Since H appears earlier, this CNOT has the right setup to create correlated or entangled outcomes."
    if len(sequence) == 1:
        return "Since it is the only gate so far, compare the before and after Bloch vector to see its clean effect."
    return f"This is move {len(sequence)} in the current recipe, so read it as part of the sequence: {' -> '.join(sequence)}."


def _build_explanation(latest_gate: str, qubit: int, full_circuit_desc: str, eli5_mode: bool) -> str:
    gate_upper = _clean_gate_name(latest_gate)
    sequence = _parse_sequence(full_circuit_desc)
    note = GATE_NOTES.get(gate_upper)

    if not note:
        return (
            f"Explorer, you added {latest_gate} on q{qubit}. I do not have a special rule for that gate yet, "
            f"but I can still track the circuit order: {' -> '.join(sequence) or 'no sequence was provided'}."
        )

    if eli5_mode:
        return f"Explorer, {note['simple']} Watch q{qubit}: {note['watch']}"

    sequence_note = _build_sequence_note(gate_upper, sequence)
    return (
        f"Explorer, you added {note['name']} ({gate_upper}) on q{qubit}. "
        f"{note['plain']} {note['state']} {note['watch']} {sequence_note}"
    )


def explain_composer_action(latest_gate: str, qubit: int, full_circuit_desc: str, eli5_mode: bool = False):
    explanation = _build_explanation(latest_gate, qubit, full_circuit_desc, eli5_mode)
    for word in explanation.split(" "):
        yield word + " "
        time.sleep(0.012)
