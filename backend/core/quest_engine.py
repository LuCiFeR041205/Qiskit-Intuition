import numpy as np
import streamlit as st

QUESTS = [
    {
        "id": "q1",
        "title": "Quest 1: The Quantum Flip",
        "description": "Welcome, Explorer! Your first quest is to flip Qubit 0 from state |0⟩ to state |1⟩. This represents a classical NOT operation.",
        "hints": ["Try using the Pauli-X gate on Qubit 0."],
        "target_state": [0, 1, 0, 0], # For 2 qubits: |01> where q0 is 1 and q1 is 0. Wait, Qiskit ordering is q1q0. So |01> means q1=0, q0=1. Target state vector is index 1.
    },
    {
        "id": "q2",
        "title": "Quest 2: Into the Superposition",
        "description": "Now, let's venture into the unknown. Put Qubit 0 into an equal superposition of |0⟩ and |1⟩.",
        "hints": ["The Hadamard (H) gate is your friend here."],
        "target_state": [0.70710678, 0.70710678, 0, 0], # |+0>
    },
    {
        "id": "q3",
        "title": "Quest 3: Spooky Action at a Distance",
        "description": "Entanglement time! Create a Bell state where Qubit 0 and Qubit 1 are perfectly entangled.",
        "hints": ["First put Qubit 0 into superposition, then use a CNOT gate with Qubit 0 as control and Qubit 1 as target."],
        "target_state": [0.70710678, 0, 0, 0.70710678], # |00> + |11>
    }
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

    # Pad if necessary (though they should be the same size if num_qubits match)
    if len(s1) != len(s2):
        return 0.0

    overlap = np.vdot(s1, s2)
    fidelity = np.abs(overlap)**2
    return float(fidelity)

def get_quests():
    return QUESTS

def render_quest_tab(engine):
    st.markdown("## 🎯 Quantum Quests")
    st.caption("Complete these challenges by building the correct circuit in the Composer tab!")
    
    if "current_quest_index" not in st.session_state:
        st.session_state.current_quest_index = 0
        
    quests = get_quests()
    
    if st.session_state.current_quest_index >= len(quests):
        st.success("🎉 You have completed all available quests! You are a Quantum Master.")
        st.balloons()
        return
        
    current_quest = quests[st.session_state.current_quest_index]
    
    st.markdown(
        f"""
        <div style="border: 1px solid rgba(101, 244, 212, 0.5); background: rgba(0,0,0,0.4); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <h3 style="color: #00F0FF; margin-top: 0;">{current_quest['title']}</h3>
            <p style="font-size: 1.1rem; line-height: 1.6;">{current_quest['description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("Need a hint?"):
        for hint in current_quest["hints"]:
            st.markdown(f"- {hint}")
            
    st.markdown("### Fidelity Scanner")
    
    # We check the current state vector from the engine passed in
    angles = engine.run_simulation(noisy=False)
    
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
                st.session_state.composer_gates = [] # Reset composer
                st.rerun()
    else:
        st.info("Build a circuit in the Composer to see your state match.")
