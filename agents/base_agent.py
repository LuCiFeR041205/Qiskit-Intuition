import time

def generate_stream(system_prompt: str, user_prompt: str):
    """
    Offline fallback stream used by legacy agent wrappers.

    The app's public AI paths should not require external accounts. This
    keeps the older agent interface intact while returning deterministic local
    guidance instead of calling an external model.
    """
    prompt = f"{system_prompt}\n{user_prompt}".lower()

    if "code" in prompt or "qiskit" in prompt:
        response = (
            "Explorer, I am running in offline mode. Read the code as a circuit recipe: "
            "imports prepare the tools, `QuantumCircuit` creates the qubits/classical bits, "
            "gate calls transform the quantum state, and measurement or statevector calls reveal "
            "what the circuit predicts. For exact behavior, run it in the Sandbox and compare the "
            "output with the circuit diagram."
        )
    elif "challenge" in prompt or "problem" in prompt or "checkpoint" in prompt:
        response = (
            "Explorer, try this offline checkpoint: identify which operation changes probability, "
            "which operation changes phase, and which operation links two qubits. Then predict how "
            "the measurement bars should shift before running the circuit."
        )
    else:
        response = (
            "Explorer, I am using a local offline teaching routine. Focus on the physical picture: "
            "qubits begin as |0>, gates rotate or entangle their state, and measurement turns that "
            "state into classical outcomes. Use the Learn, Compose, and Sandbox panels together to "
            "test the idea."
        )

    for word in response.split(" "):
        yield word + " "
        time.sleep(0.01)
