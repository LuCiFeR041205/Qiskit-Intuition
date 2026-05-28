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

def calculate_fidelity(state1, state2):
    """
    Calculate the quantum fidelity between two state vectors.
    F = |<psi|phi>|^2
    """
    if state1 is None or state2 is None:
        return 0.0
    
    # Ensure they are numpy arrays
    s1 = np.array(state1, dtype=complex)
    s2 = np.array(state2, dtype=complex)
    
    # Pad if necessary (though they should be the same size if num_qubits match)
    if len(s1) != len(s2):
        return 0.0
        
    overlap = np.vdot(s1, s2)
    fidelity = np.abs(overlap)**2
    return fidelity

def get_quests():
    return QUESTS

def render_quest_tab():
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
    
    # We check the current state vector from the engine (assuming it's cached or we can get it from engine run)
    from frontend.streamlit_app import build_engine
    engine = build_engine()
    angles = engine.run_simulation(noisy=False)
    
    current_state = engine._last_simulation
    target_state = current_quest["target_state"]
    
    if current_state is not None:
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
