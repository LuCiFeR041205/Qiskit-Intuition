from .base_agent import stream_from_backend, is_backend_online

def explain_composer_action_local_fallback(latest_gate: str, qubit: int, full_circuit_desc: str):
    # Rule-based physical explanation of adding a gate in British AI persona
    gate_upper = latest_gate.upper()
    
    physical_explanations = {
        "H": f"Boss, adding a **Hadamard (H) gate** to Qubit {qubit} rotates its state vector onto the equator of the Bloch sphere. This places it in a delicate superposition, representing a 50/50 balance between |0⟩ and |1⟩. Think of it as a spinning coin before it lands!",
        "X": f"Boss, applying a **Pauli-X gate** to Qubit {qubit} rotates the state vector by π (180 degrees) around the X-axis. This acts as a quantum bit-flip, cleanly swapping |0⟩ to |1⟩ and vice versa.",
        "Y": f"Boss, applying a **Pauli-Y gate** to Qubit {qubit} rotates the state vector by π around the Y-axis. This induces both a bit-flip and a complex phase shift, introducing a relative imaginary twist to the quantum state.",
        "Z": f"Boss, applying a **Pauli-Z gate** to Qubit {qubit} rotates the state vector by π around the Z-axis. This reflects its phase relative to the other basis states without changing its measurement probabilities. It is a pure phase-flip!",
        "S": f"Boss, adding a **Phase (S) gate** to Qubit {qubit} performs a quarter-turn (90 degrees or π/2) rotation around the Z-axis of the Bloch sphere. This changes the relative phase of equator states, useful for building phase interference.",
        "T": f"Boss, adding a **Phase (T) gate** to Qubit {qubit} performs a fine-grained eighth-turn (45 degrees or π/4) rotation around the Z-axis. This is a critical building block for universal fault-tolerant quantum computation.",
        "RX": f"Boss, applying a **Parameterized RX rotation** to Qubit {qubit} rotates the state vector continuously around the X-axis. This continuously adjusts the phase and state amplitudes.",
        "RY": f"Boss, applying a **Parameterized RY rotation** to Qubit {qubit} rotates the state vector continuously around the Y-axis. This continuously shifts the measurement probability ratio between 0 and 1.",
        "RZ": f"Boss, applying a **Parameterized RZ rotation** to Qubit {qubit} rotates the state vector continuously around the Z-axis, updating its relative phase angle while keeping the measurement odds fixed.",
        "CNOT": f"Boss, applying a **Controlled-X (CNOT) gate** targets Qubit {qubit} with a bit-flip conditionally depending on the control qubit. This gate is the primary vehicle for entangling your qubits, linking their physical realities together!"
    }
    
    # Try to find explanation or default
    explanation = physical_explanations.get(gate_upper, f"Boss, you added a '{latest_gate}' gate to Qubit {qubit}. This updates the circuit recipe. The full sequence of gates is: {full_circuit_desc}.")
    
    import time
    for word in explanation.split(" "):
        yield word + " "
        time.sleep(0.012)

def explain_composer_action(latest_gate: str, qubit: int, full_circuit_desc: str):
    if is_backend_online():
        try:
            # Try to fetch from backend
            generator = stream_from_backend(
                "coach",
                {
                    "latest_gate": latest_gate,
                    "qubit": qubit,
                    "full_circuit_desc": full_circuit_desc
                },
                None
            )
            # If generator is valid and yields data, return it
            # To be safe, we check online and fallback to offline rules if API returns system error
            # Or we can simply use the offline rules directly when API key is missing.
            # Here we wrap it in a try-except streaming loop
            def safe_stream():
                has_yielded = False
                for chunk in generator:
                    if chunk:
                        if "J.A.R.V.I.S. System Error" in chunk or "RESOURCE_EXHAUSTED" in chunk:
                            # If Gemini limit reached, yield the beautiful offline explanation instead of the raw error!
                            yield from explain_composer_action_local_fallback(latest_gate, qubit, full_circuit_desc)
                            return
                        yield chunk
                        has_yielded = True
                if not has_yielded:
                    yield from explain_composer_action_local_fallback(latest_gate, qubit, full_circuit_desc)
            return safe_stream()
        except Exception:
            pass
    # Fallback directly to local rules
    return explain_composer_action_local_fallback(latest_gate, qubit, full_circuit_desc)
