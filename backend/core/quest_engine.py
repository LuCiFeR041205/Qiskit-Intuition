import numpy as np
import streamlit as st

QUESTS = [
    {
        "id": "q1",
        "qubits": 2,
        "title": "Quest 1: The Quantum Flip",
        "category": "Basics",
        "description": "Your first mission: flip Qubit 0 from |0> to |1>. This is the quantum NOT, the simplest gate in the lab.",
        "hints": ["Use the Pauli-X gate on Qubit 0.", "X rotates the state vector from the north pole to the south pole of the Bloch sphere."],
        "target_state": [0, 1, 0, 0],
    },
    {
        "id": "q2",
        "qubits": 2,
        "title": "Quest 2: Into the Superposition",
        "category": "Basics",
        "description": "Move Qubit 0 onto the equator so it is half |0> and half |1>. Measurement becomes a coin flip.",
        "hints": ["The Hadamard (H) gate is your friend here.", "H sends |0> to |+> = (|0> + |1>)/sqrt(2)."],
        "target_state": [0.70710678, 0.70710678, 0, 0],
    },
    {
        "id": "q3",
        "qubits": 2,
        "title": "Quest 3: Spooky Action at a Distance",
        "category": "Entanglement",
        "description": "Entanglement time. Build a Bell state so Qubit 0 and Qubit 1 are perfectly correlated. Use 2 qubits.",
        "hints": ["Put Qubit 0 into superposition with H.", "Then add a CNOT with Qubit 0 as control and Qubit 1 as target."],
        "target_state": [0.70710678, 0, 0, 0.70710678],
    },
    {
        "id": "q4",
        "qubits": 2,
        "title": "Quest 4: The Phase Kick",
        "category": "Phase",
        "description": "Some gates change phase without touching measurement odds. Start from |+> and arrive at |->, the other equator pole. Use 2 qubits (the target sits on Qubit 0).",
        "hints": ["Build |+> first with H on Qubit 0.", "Then apply Z. The probabilities stay 50/50, but the phase flips to make |->."],
        "target_state": [0.70710678, -0.70710678, 0, 0],
    },
    {
        "id": "q5",
        "qubits": 2,
        "title": "Quest 5: Anti-Correlation",
        "category": "Entanglement",
        "description": "Build the second Bell state, where the qubits are entangled but always disagree. Use 2 qubits.",
        "hints": ["Start from the |00> + |11> Bell state (H then CNOT).", "Flip both qubits with X, or flip the target only, to land on |01> + |10>."],
        "target_state": [0, 0.70710678, 0.70710678, 0],
    },
    {
        "id": "q6",
        "qubits": 1,
        "title": "Quest 6: The Precise Tilt",
        "category": "Rotation",
        "description": "Use a continuous rotation to land partway between the poles. Set Qubit 0 to a state that is 75% |0> and 25% |1>. Use 1 qubit.",
        "hints": ["An Ry rotation changes the |0>/|1> balance.", "Solve cos(theta/2)^2 = 0.75. That angle is about 1.318 rad, or roughly 0.42 pi."],
        "target_state": [0.8660254, 0.5],
    },
    {
        "id": "q7",
        "qubits": 3,
        "title": "Quest 7: The Three-Way Bell (GHZ)",
        "category": "Entanglement",
        "description": "Scale entanglement up. Build a GHZ state across three qubits: |000> + |111> (all three agree). Use 3 qubits.",
        "hints": ["Hadamard on Qubit 0, then CNOT 0->1, then CNOT 1->2.", "The result is a fully entangled cat state spread over all three qubits."],
        "target_state": [0.70710678, 0, 0, 0, 0, 0, 0, 0.70710678],
    },
    {
        "id": "q8",
        "qubits": 1,
        "title": "Quest 8: The Identity Trick",
        "category": "Basics",
        "description": "Prove to yourself that gates compose. Build a circuit that returns Qubit 0 exactly to |0> after starting there. Use 1 qubit.",
        "hints": ["Any gate followed by its inverse works: H then H, or X then X.", "The final statevector should match the starting |0>."],
        "target_state": [1, 0],
    },
]

def _as_statevector_array(state):
    if state is None:
        return None
    if isinstance(state, dict):
        state = state.get("statevector")
    if hasattr(state, "data"):
        state = state.data

    try:
        # Pre-process inputs to parse complex strings or API dictionaries safely
        if isinstance(state, (list, tuple)):
            processed = []
            for val in state:
                if isinstance(val, dict):
                    processed.append(complex(val.get('real', 0.0), val.get('imag', 0.0)))
                elif isinstance(val, str):
                    processed.append(complex(val.replace('i', 'j').strip('()')))
                else:
                    processed.append(complex(val))
            vector = np.asarray(processed, dtype=complex)
        else:
            vector = np.asarray(state, dtype=complex)
    except (TypeError, ValueError):
        return None

    if vector.ndim != 1 or vector.size == 0:
        return None

    norm = np.linalg.norm(vector)
    if norm == 0:
        return None
    return vector / norm


def calculate_fidelity(state1, state2):
    """
    Calculate the quantum fidelity between two state vectors.
    F = |<psi|phi>|^2
    """
    s1 = _as_statevector_array(state1)
    s2 = _as_statevector_array(state2)
    if s1 is None or s2 is None:
        return 0.0

    # If the circuit and the target use different qubit counts, embed the
    # smaller state into the larger one by assuming the extra qubits sit in
    # |0>. That is exactly zero-extension on the higher indices.
    if len(s1) != len(s2):
        size = max(len(s1), len(s2))
        s1 = np.pad(s1, (0, size - len(s1)))
        s2 = np.pad(s2, (0, size - len(s2)))

    overlap = np.vdot(s1, s2)
    fidelity = np.abs(overlap) ** 2
    return float(fidelity)

def get_quests():
    # Keep the public progression deliberately short and testable.  The first
    # three challenges cover bit flips, superposition, and entanglement; later
    # draft challenges remain above for future curriculum work but are not
    # published until they have complete solution and progression coverage.
    return QUESTS[:3]

def render_quest_tab(engine):
    st.markdown("## Quantum Quests")
    st.caption("Complete these challenges by building the correct circuit in the Builder below.")

    if "current_quest_index" not in st.session_state:
        st.session_state.current_quest_index = 0

    quests = get_quests()

    # Quest tracker in the sidebar so learners can jump between missions.
    with st.sidebar:
        st.divider()
        st.markdown("### Quest Tracker")
        for idx, quest in enumerate(quests):
            label = f"✅ {quest['title']}" if idx < st.session_state.current_quest_index else quest["title"]
            if st.button(label, key=f"quest_jump_{idx}", use_container_width=True,
                         disabled=idx == st.session_state.current_quest_index,
                         type="primary" if idx == st.session_state.current_quest_index else "secondary"):
                st.session_state.current_quest_index = idx
                st.session_state.composer_gates = []
                st.rerun()

    if st.session_state.current_quest_index >= len(quests):
        st.success("You have completed every quest. You are a Quantum Master.")
        st.balloons()
        return

    current_quest = quests[st.session_state.current_quest_index]
    progress_pct = int(100 * st.session_state.current_quest_index / len(quests))

    st.markdown(
        f"""
        <div class="physics-card" role="region" aria-label="Active quest" tabindex="0">
            <strong>{current_quest['title']}</strong><br>
            <span>{current_quest['description']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(progress_pct)
    st.caption(f"Quest {st.session_state.current_quest_index + 1} of {len(quests)} · {current_quest.get('category', '')}")

    with st.expander("Need a hint?"):
        for hint in current_quest["hints"]:
            st.markdown(f"- {hint}")

    # Match the circuit's qubit count to the quest so exploration is honest.
    required_qubits = current_quest.get("qubits", 2)
    if st.session_state.num_qubits != required_qubits:
        st.session_state.num_qubits = required_qubits
        st.session_state.composer_gates = []
        st.session_state.composer_step = 0
        st.rerun()

    st.markdown("### Fidelity Scanner")

    # Current state vector comes from the engine passed in.
    current_simulation = engine._last_simulation
    target_state = current_quest["target_state"]

    if current_simulation is not None:
        current_state = current_simulation.get("statevector")
        fidelity = calculate_fidelity(current_state, target_state)

        st.progress(min(fidelity, 1.0))
        st.markdown(f"**Current Match:** `{fidelity * 100:.2f}%`")

        if fidelity > 0.99:
            st.success("Target State Reached! Quest Complete!")
            if st.button("Next Quest ➡️"):
                st.session_state.current_quest_index += 1
                st.session_state.composer_gates = []
                st.rerun()
    else:
        st.info("Build a circuit in the Builder to see your state match.")
