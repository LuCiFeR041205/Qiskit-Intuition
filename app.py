import streamlit as st
import os
import math
import matplotlib.pyplot as plt

# Import J.A.R.V.I.S.-style agents (A.C.E. brand)
from agents.feynman_agent import explain_concept, generate_intro
from agents.qiskit_engineer import generate_code
from agents.socratic_tutor import generate_problem
from agents.composer_agent import explain_composer_action

# Import Stark Holographic Bloch Sphere component
from components.bloch_sphere import render_bloch_sphere

# Import Feature engines
from utils.quantum_engine import QuantumEngine
from utils.notebook_engine import execute_notebook_code

st.set_page_config(
    page_title="A.C.E. Stark Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stark HUD CSS Theme
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #050A15;
        color: #00F0FF;
        font-family: 'Courier New', Courier, monospace;
    }
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.15) 50%);
        z-index: 99999;
        background-size: 100% 4px;
        pointer-events: none;
        opacity: 0.25;
    }
    
    /* Holographic Titles */
    h1, h2, h3, h4, h5 {
        color: #00F0FF !important;
        text-shadow: 0 0 8px #00F0FF, 0 0 15px rgba(0, 240, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .console-header {
        color: #4DB8FF;
        font-size: 1.1em;
        margin-bottom: 2em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #02060D !important;
        border-right: 1px solid #00F0FF;
        box-shadow: 2px 0 15px rgba(0, 240, 255, 0.2);
    }
    
    /* Interactive Containers */
    .stChatMessage {
        background-color: rgba(0, 240, 255, 0.03) !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: inset 0 0 8px rgba(0, 240, 255, 0.05);
    }
    .console-box {
        background-color: rgba(0, 240, 255, 0.02);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Tabs styling override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #02060D;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid rgba(0, 240, 255, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        color: #4DB8FF !important;
        border: none !important;
        background-color: transparent !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stTabs [aria-selected="true"] {
        color: #00F0FF !important;
        text-shadow: 0 0 5px #00F0FF;
        border-bottom: 2px solid #00F0FF !important;
    }
    
    /* High-Tech buttons */
    .stButton>button {
        background-color: transparent !important;
        color: #00F0FF !important;
        border: 1px solid #00F0FF !important;
        border-radius: 0px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 11px;
        transition: all 0.3s ease;
        box-shadow: 0 0 5px rgba(0, 240, 255, 0.2);
    }
    .stButton>button:hover {
        background-color: #00F0FF !important;
        color: #050A15 !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.6);
    }
    
    /* Text Inputs */
    .stTextArea textarea {
        background-color: rgba(0, 240, 255, 0.03) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        color: #00F0FF !important;
        font-family: 'Courier New', Courier, monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 A.C.E. CONSOLE")
st.markdown('<div class="console-header">Stark Industries: Advanced Quantum Workspace v1.0</div>', unsafe_allow_html=True)

# Main App Tabs
tab_curr, tab_comp, tab_sandbox = st.tabs(["📚 Curriculum Academy", "⚙️ Stark Composer Board", "💻 Diagnostic Sandbox (Notebook)"])

# ==================== TAB 1: CURRICULUM PORTAL ====================
with tab_curr:
    st.sidebar.title("🗄️ Database")
    phase = st.sidebar.selectbox("Protocol Level", ["Level 1: Absolute Basics", "Level 2: Intermediate Circuits", "Level 3: Advanced Algorithms", "Level 4: Real-World Engineering"])

    if phase == "Level 1: Absolute Basics":
        module = st.sidebar.radio(
            "Load Module:",
            ["1. Welcome", "2. The Qubit", "3. Superposition", "4. Measurement", "5. Entanglement"]
        )
        
        if module == "1. Welcome":
            st.markdown("""
            ### INITIALIZING CONSOLE ACADEMY...
            
            Welcome to the Stark Industries Quantum Console, Boss.
            
            I am **A.C.E.** (Advanced Conceptual Explainer), your diagnostic AI. The learning parameters are fully operational, reconfigured to completely bypass traditional linear algebra in favor of visual, physics-first mechanics.
            
            Database sub-protocols online:
            - 🌐 **Intuition Matrix:** Visual analogies explaining physical behaviors.
            - ⚙️ **Code Synthesizer:** Pure Qiskit scripts for immediate execution.
            - 🛡️ **Diagnostic Protocol:** Socratic checkpoints to test your limits.
            
            Please select **2. The Qubit** in the sidebar database to begin loading the core quantum vectors.
            """)
        else:
            concept_name = module.split(". ")[1]
            st.markdown(f"## {module.upper()}")
            
            if f"intro_{module}" not in st.session_state:
                st.session_state[f"intro_{module}"] = ""
                st.session_state[f"feynman_{module}"] = ""
                st.session_state[f"code_{module}"] = ""
                st.session_state[f"tutor_{module}"] = ""

            with st.chat_message("jarvis", avatar="🤖"):
                st.markdown("**A.C.E. System Advisor**")
                if not st.session_state[f"intro_{module}"]:
                    st.session_state[f"intro_{module}"] = st.write_stream(generate_intro(concept_name))
                else:
                    st.markdown(st.session_state[f"intro_{module}"])
                
            # Embed Interactive 3D Bloch sphere for local vector exploration
            if concept_name in ["The Qubit", "Superposition", "Measurement"]:
                st.divider()
                st.markdown("### 🔮 HUD STATE VECTOR PROJECTION")
                
                col_ctrl, col_proj = st.columns([5, 7])
                with col_ctrl:
                    st.markdown("""
                    <div style="border: 1px solid rgba(0, 240, 255, 0.2); padding: 12px; background: rgba(0, 240, 255, 0.02); margin-bottom: 15px;">
                        <div style="color: #00F0FF; font-weight: bold; font-size: 13px; text-transform: uppercase; margin-bottom: 4px;">CONSOLE SLIDER CONTROLS</div>
                        <span style="font-size: 11px; color: #4DB8FF;">Boss, adjust the angles manually to explore the Hilbert space.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    theta_deg = st.slider("Polar θ (0° = |0⟩, 180° = |1⟩)", min_value=0.0, max_value=180.0, value=90.0, step=1.0, key=f"theta_{concept_name}")
                    phi_deg = st.slider("Azimuthal φ (Relative Phase)", min_value=0.0, max_value=360.0, value=0.0, step=1.0, key=f"phi_{concept_name}")
                    
                    theta_rad = math.radians(theta_deg)
                    phi_rad = math.radians(phi_deg)
                    cos_half = math.cos(theta_rad / 2.0)
                    sin_half = math.sin(theta_rad / 2.0)
                    
                    st.markdown(f"""
                    <div style="border-left: 2px solid #ff0055; padding-left: 10px; font-size: 11px; color: #e0e0e0; margin-top: 15px;">
                        <strong style="color: #ff0055;">STATE VECTOR |ψ⟩:</strong><br>
                        |ψ⟩ = {cos_half:.3f}|0⟩ + e^(i·{phi_deg:.0f}°){sin_half:.3f}|1⟩
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_proj:
                    render_bloch_sphere(theta_rad, phi_rad, qubit_name=f"Q0")
                
            st.divider()

            # Execute Swarm button
            if not st.session_state[f"feynman_{module}"]:
                if st.button(f"ENGAGE DEEPER EXPLORATION: {concept_name.upper()}", use_container_width=True):
                    with st.chat_message("intuition", avatar="🌐"):
                        st.markdown("**A.C.E. [Intuition Matrix]**")
                        st.session_state[f"feynman_{module}"] = st.write_stream(explain_concept(concept_name))
                        
                    with st.chat_message("synthesizer", avatar="⚙️"):
                        st.markdown("**A.C.E. [Code Synthesizer]**")
                        st.session_state[f"code_{module}"] = st.write_stream(generate_code(concept_name, st.session_state[f"feynman_{module}"]))
                        
                    with st.chat_message("diagnostic", avatar="🛡️"):
                        st.markdown("**A.C.E. [Diagnostic Protocol]**")
                        st.session_state[f"tutor_{module}"] = st.write_stream(generate_problem(concept_name))
                    st.rerun()

            # Display outputs if generated
            elif st.session_state[f"feynman_{module}"]:
                with st.chat_message("intuition", avatar="🌐"):
                    st.markdown("**A.C.E. [Intuition Matrix]**")
                    st.markdown(st.session_state[f"feynman_{module}"])
                    
                with st.chat_message("synthesizer", avatar="⚙️"):
                    st.markdown("**A.C.E. [Code Synthesizer]**")
                    st.markdown(st.session_state[f"code_{module}"])
                    
                with st.chat_message("diagnostic", avatar="🛡️"):
                    st.markdown("**A.C.E. [Diagnostic Protocol]**")
                    st.markdown(st.session_state[f"tutor_{module}"])
                    
                st.divider()
                st.markdown("### MANUAL OVERRIDE")
                user_answer = st.text_area("Input response to Diagnostic Protocol:", placeholder="Terminal active...")
                if st.button("SUBMIT DIAGNOSTIC", type="primary"):
                    st.success("Diagnostics confirmed, Boss. Outstanding logic.")
    else:
        st.info(f"ACCESS RESTRICTED: {phase} requires higher authorization clearance.")

# ==================== TAB 2: STARK COMPOSER BOARD ====================
with tab_comp:
    st.markdown("### 🎛️ STARK QUANTUM COMPOSER")
    st.markdown("Boss, click buttons below to construct a quantum circuit in real-time. View the dynamic circuit diagram and 3D Bloch sphere projections instantly as you edit.")
    
    # Initialize session state for Composer
    if "composer_gates" not in st.session_state:
        st.session_state.composer_gates = []
    if "composer_last_gate" not in st.session_state:
        st.session_state.composer_last_gate = None
    if "composer_ai_feedback" not in st.session_state:
        st.session_state.composer_ai_feedback = ""
        
    engine = QuantumEngine(num_qubits=2)
    engine.gates = st.session_state.composer_gates
    
    # Layout splits: Controls (Left) vs Visualizations (Right)
    col_comp_ctrl, col_comp_vis = st.columns([5, 7])
    
    with col_comp_ctrl:
        st.markdown("##### 🧱 QUANTUM GATE BOARD")
        
        # Grid of gate buttons
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            if st.button("➕ HADAMARD (H) on Q0"):
                st.session_state.composer_gates.append({'gate': 'H', 'target': 0, 'control': None})
                st.session_state.composer_last_gate = ("Hadamard (H)", 0)
                st.session_state.composer_ai_feedback = ""
                st.rerun()
            if st.button("➕ HADAMARD (H) on Q1"):
                st.session_state.composer_gates.append({'gate': 'H', 'target': 1, 'control': None})
                st.session_state.composer_last_gate = ("Hadamard (H)", 1)
                st.session_state.composer_ai_feedback = ""
                st.rerun()
        with subcol2:
            if st.button("➕ PAULI-X (NOT) on Q0"):
                st.session_state.composer_gates.append({'gate': 'X', 'target': 0, 'control': None})
                st.session_state.composer_last_gate = ("Pauli-X (NOT)", 0)
                st.session_state.composer_ai_feedback = ""
                st.rerun()
            if st.button("➕ PAULI-X (NOT) on Q1"):
                st.session_state.composer_gates.append({'gate': 'X', 'target': 1, 'control': None})
                st.session_state.composer_last_gate = ("Pauli-X (NOT)", 1)
                st.session_state.composer_ai_feedback = ""
                st.rerun()
        with subcol3:
            if st.button("➕ CNOT (Ctrl: Q0, Tgt: Q1)"):
                st.session_state.composer_gates.append({'gate': 'CNOT', 'target': 1, 'control': 0})
                st.session_state.composer_last_gate = ("CNOT", 1)
                st.session_state.composer_ai_feedback = ""
                st.rerun()
            if st.button("➕ CNOT (Ctrl: Q1, Tgt: Q0)"):
                st.session_state.composer_gates.append({'gate': 'CNOT', 'target': 0, 'control': 1})
                st.session_state.composer_last_gate = ("CNOT", 0)
                st.session_state.composer_ai_feedback = ""
                st.rerun()
                
        if st.button("🧹 RESET COMPOSER MAINBOARD", use_container_width=True):
            st.session_state.composer_gates = []
            st.session_state.composer_last_gate = None
            st.session_state.composer_ai_feedback = ""
            st.rerun()
            
        st.divider()
        
        # Real-time J.A.R.V.I.S/A.C.E Interceptor Box
        st.markdown("##### 💬 A.C.E. SYSTEM DIALOGUE")
        if st.session_state.composer_last_gate:
            gate_name, q_idx = st.session_state.composer_last_gate
            gate_desc = f"{gate_name} applied to Qubit {q_idx}"
            
            with st.chat_message("jarvis", avatar="🤖"):
                st.markdown("**A.C.E. Console Companion**")
                if not st.session_state.composer_ai_feedback:
                    # Construct circuit description for AI
                    seq = [f"{g['gate']} on q{g['target']}" for g in st.session_state.composer_gates]
                    full_desc = " -> ".join(seq)
                    st.session_state.composer_ai_feedback = st.write_stream(explain_composer_action(gate_name, q_idx, full_desc))
                else:
                    st.markdown(st.session_state.composer_ai_feedback)
        else:
            st.markdown("""
            <div style="border-left: 2px solid #00F0FF; padding-left: 10px; font-size: 11px; color: #8B949E; font-family: monospace;">
                Boss, the composer circuit is empty. Apply a gate using the mainboard controls above and I will instantly analyze the physical state vector shift.
            </div>
            """, unsafe_allow_html=True)
            
    with col_comp_vis:
        st.markdown("##### 📊 CORE REAL-TIME VISUALIZATIONS")
        
        # Simulate active state vector
        angles = engine.run_simulation()
        
        # Display side by side 3D Bloch Spheres
        q0_col, q1_col = st.columns(2)
        with q0_col:
            st.markdown("<p style='text-align:center; font-size:11px; color:#00F0FF;'>QUBIT 0 (Q0)</p>", unsafe_allow_html=True)
            render_bloch_sphere(angles[0]['theta'], angles[0]['phi'], qubit_name="Q0")
        with q1_col:
            st.markdown("<p style='text-align:center; font-size:11px; color:#00F0FF;'>QUBIT 1 (Q1)</p>", unsafe_allow_html=True)
            render_bloch_sphere(angles[1]['theta'], angles[1]['phi'], qubit_name="Q1")
            
        # Draw Matplotlib Circuit Diagram
        st.markdown("##### 🧬 CIRCUIT BOARD DIAGRAM (MATPLOTLIB PROJECTION)")
        fig = engine.get_circuit_figure()
        st.pyplot(fig, clear_figure=True)

# ==================== TAB 3: DIAGNOSTIC SANDBOX ====================
with tab_sandbox:
    st.markdown("### 💻 STARK DIAGNOSTIC SANDBOX (NOTEBOOK)")
    st.markdown("Boss, this isolated sandbox allows you to compile, write, and execute raw Qiskit and Python code directly inside the terminal. Matplotlib outputs and stdout are grabbed live.")
    
    notebook_code = st.text_area(
        "Sandbox Code Terminal:",
        value="""# Stark Mainframe Sandbox Terminal
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit

# 1. Initialize a 2-qubit circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# 2. Compile and print text description
print("Mainframe: Quantum Circuit compiled successfully.")
print(qc)

# 3. Request high-fidelity circuit projection drawing
# (The console will automatically grab this figure and plot it!)
fig = qc.draw(output='mpl')
""",
        height=300
    )
    
    if st.button("ENGAGE CALCULATION ENGINE", type="primary", use_container_width=True):
        with st.spinner("Compiling Stark protocols..."):
            res = execute_notebook_code(notebook_code)
            
            st.divider()
            
            if res['success']:
                st.success("Execution completed successfully, Boss.")
            else:
                st.error("Execution failed: Traceback compiled below, Boss.")
                st.code(res['error'], language="python")
                
            if res['stdout']:
                st.markdown("##### 📝 CONSOLE STDOUT")
                st.code(res['stdout'])
                
            if res['stderr']:
                st.markdown("##### ⚠️ CONSOLE STDERR")
                st.code(res['stderr'])
                
            if res['figures']:
                st.markdown("##### 🔮 PROJECTIONS")
                for fig in res['figures']:
                    st.pyplot(fig)
