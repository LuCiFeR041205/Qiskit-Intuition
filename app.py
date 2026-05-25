import math

import streamlit as st

from agents.composer_agent import explain_composer_action
from agents.feynman_agent import explain_concept, generate_intro
from agents.qiskit_engineer import generate_code
from agents.socratic_tutor import generate_problem
from components.bloch_sphere import render_bloch_sphere
from components.quantum_field import render_quantum_field
from utils.notebook_engine import execute_notebook_code
from utils.quantum_engine import QuantumEngine


st.set_page_config(
    page_title="Qiskit Intuition Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


GATE_LIBRARY = {
    "H": {
        "label": "Hadamard",
        "family": "Superposition",
        "description": "Splits a basis state onto the equator so measurement can return 0 or 1.",
    },
    "X": {
        "label": "Pauli-X",
        "family": "Bit flip",
        "description": "Rotates the qubit through pi around the X axis, swapping |0> and |1>.",
    },
    "Y": {
        "label": "Pauli-Y",
        "family": "Bit + phase flip",
        "description": "Flips the basis state and adds a phase twist through the Y axis.",
    },
    "Z": {
        "label": "Pauli-Z",
        "family": "Phase flip",
        "description": "Keeps measurement odds fixed while reflecting phase across the Z axis.",
    },
    "S": {
        "label": "S phase",
        "family": "Phase",
        "description": "Adds a quarter-turn phase, moving equator states around the Bloch sphere.",
    },
    "T": {
        "label": "T phase",
        "family": "Phase",
        "description": "Adds an eighth-turn phase, useful for fine-grained quantum programs.",
    },
    "RX": {
        "label": "Rx rotation",
        "family": "Parameterized",
        "description": "Rotates continuously around the X axis by a chosen angle.",
    },
    "RY": {
        "label": "Ry rotation",
        "family": "Parameterized",
        "description": "Rotates continuously around the Y axis, changing the chance of 0 versus 1.",
    },
    "RZ": {
        "label": "Rz rotation",
        "family": "Parameterized",
        "description": "Rotates continuously around the Z axis, changing phase without changing odds.",
    },
    "CNOT": {
        "label": "Controlled-X",
        "family": "Entangling",
        "description": "Flips the target only when the control is |1>, creating conditional motion.",
    },
}


CURRICULUM = {
    "Level 0: Python + Qiskit Setup": {
        "Python for Circuits": {
            "big_idea": "Qiskit circuits are Python objects, so learners need functions, lists, loops, and clean notebook habits.",
            "composer": "Read the exported code after each composer action and connect every line to a visual gate.",
            "checkpoint": "What does `qc.h(0)` mean as Python code and as a physical operation?",
            "practice": "Create a QuantumCircuit, add one gate, print it, and draw it.",
        },
        "Qiskit Objects": {
            "big_idea": "QuantumCircuit, Statevector, AerSimulator, transpiler passes, and backends are the core objects learners reuse everywhere.",
            "composer": "Export a circuit, then paste it into the sandbox and add Statevector inspection.",
            "checkpoint": "Why is a circuit a recipe while a statevector is a simulated physical state?",
            "practice": "Use `QuantumCircuit(2)`, `Statevector.from_instruction(qc)`, and `qc.draw(output='mpl')`.",
        },
    },
    "Level 1: Quantum Foundations": {
        "The Qubit": {
            "big_idea": "A qubit is a physical two-level system whose state points somewhere on the Bloch sphere.",
            "composer": "Move theta and phi, then use H, X, and Z to connect symbols to motion.",
            "checkpoint": "If the vector sits at the north pole, what outcome is guaranteed?",
            "practice": "Prepare |0>, |1>, |+>, and |-> in Qiskit and compare their Bloch vectors.",
        },
        "Superposition": {
            "big_idea": "Superposition means the vector is not at a pole; measurement probabilities come from its projection.",
            "composer": "Apply H to |0> and watch the vector land on the equator.",
            "checkpoint": "Why does a balanced superposition not mean the qubit is secretly both classical values?",
            "practice": "Run a Hadamard circuit with 1024 shots and explain why counts fluctuate.",
        },
        "Measurement": {
            "big_idea": "Measurement projects the state onto a classical result and destroys most phase information.",
            "composer": "Compare the probability bars before and after gates that only change phase.",
            "checkpoint": "Which gates change probabilities, and which only change phase?",
            "practice": "Measure X|0>, H|0>, and ZH|0>; compare statevector and sampled counts.",
        },
        "Entanglement": {
            "big_idea": "Entanglement is shared state: individual qubits can lose a pure vector while the pair stays ordered.",
            "composer": "Apply H on q0, then CNOT q0 -> q1 to form a Bell state.",
            "checkpoint": "Why can each single Bloch sphere look mixed while the two-qubit circuit is highly structured?",
            "practice": "Build all four Bell states and identify their measurement correlations.",
        },
    },
    "Level 2: Circuit Composer Skills": {
        "Gate Algebra": {
            "big_idea": "Gates are reversible transformations; order matters because rotations around different axes do not generally commute.",
            "composer": "Compare H then Z versus Z then H and inspect the final vector.",
            "checkpoint": "Why can two circuits with the same gates produce different states?",
            "practice": "Use Qiskit to test XZ versus ZX on |0> and |+>.",
        },
        "Phase Kickback": {
            "big_idea": "A controlled operation can push phase information backward into the control qubit.",
            "composer": "Use H gates around controlled operations and inspect the phase-sensitive probabilities.",
            "checkpoint": "What changes when phase becomes visible through interference?",
            "practice": "Build a controlled-Z from H and CNOT, then explain the phase path.",
        },
        "Parameterized Rotations": {
            "big_idea": "Rx, Ry, and Rz make circuits tunable, which is the basis of variational algorithms.",
            "composer": "Sweep an angle slider and watch the vector move continuously instead of jumping gate to gate.",
            "checkpoint": "Which rotation changes measurement odds from |0>, and which initially hides as phase?",
            "practice": "Create a circuit with a Parameter theta and bind three values.",
        },
    },
    "Level 3: Simulation + Noise": {
        "Statevector vs Shots": {
            "big_idea": "Statevectors show exact amplitudes, while shot-based simulation imitates repeated experimental sampling.",
            "composer": "Compare probability bars with noisy-looking sampled counts in the sandbox.",
            "checkpoint": "Why can a perfect 50/50 state return 512/512 only rarely?",
            "practice": "Run the same Bell circuit with 128, 1024, and 8192 shots.",
        },
        "Noise Models": {
            "big_idea": "Real devices introduce decoherence, gate error, and readout error, which turn ideal circuits into distributions.",
            "composer": "Use the Bell circuit as a reference, then add noise in the sandbox.",
            "checkpoint": "What kind of error would reduce Bell-state correlation?",
            "practice": "Use Aer noise tools to add depolarizing or thermal-relaxation noise.",
        },
        "Transpilation": {
            "big_idea": "Transpilation rewrites an abstract circuit into the basis gates and connectivity of a target backend.",
            "composer": "Export the circuit, transpile it, and compare the before/after depth.",
            "checkpoint": "Why might a simple circuit grow when mapped to real hardware?",
            "practice": "Transpile a 3-qubit circuit for a fake backend or coupling map.",
        },
    },
    "Level 4: Quantum Algorithms": {
        "Grover Intuition": {
            "big_idea": "Grover search alternates marking a target and amplifying its probability through interference.",
            "composer": "Use the sandbox to build small oracle and diffuser circuits.",
            "checkpoint": "Why is the diffuser often described as inversion about the mean?",
            "practice": "Build a two-qubit Grover search and inspect the amplified target probability.",
        },
        "QFT Intuition": {
            "big_idea": "The quantum Fourier transform converts periodic structure into phase patterns.",
            "composer": "Explore phase gates first; QFT is phase choreography at scale.",
            "checkpoint": "What information is stored in relative phase instead of direct probability?",
            "practice": "Implement a 3-qubit QFT and then reverse the qubit order.",
        },
        "VQE": {
            "big_idea": "Variational Quantum Eigensolver combines parameterized quantum circuits with a classical optimizer.",
            "composer": "Use Ry/Rz layers as a small ansatz and watch parameters change the state.",
            "checkpoint": "Why does VQE need both a quantum circuit and a classical optimizer?",
            "practice": "Build a tiny ansatz and compute expectation values with Qiskit primitives.",
        },
    },
    "Level 5: Hardware + Advanced Workflows": {
        "Primitives": {
            "big_idea": "Modern Qiskit workflows use primitives such as Sampler and Estimator to run circuit jobs with clear intent.",
            "composer": "Export a circuit, then adapt it to a Sampler or Estimator workflow.",
            "checkpoint": "When do you want counts, and when do you want expectation values?",
            "practice": "Run a Bell circuit through a sampler-style workflow.",
        },
        "Error Mitigation": {
            "big_idea": "Error mitigation estimates better answers from noisy data without fully correcting the quantum state.",
            "composer": "Start with shallow circuits and compare ideal versus noisy expectations.",
            "checkpoint": "Why is mitigation not the same as fault-tolerant error correction?",
            "practice": "Compare raw and mitigated expectation values for a small observable.",
        },
        "Hardware Execution": {
            "big_idea": "Running on IBM Quantum hardware requires backend selection, transpilation, job submission, and result analysis.",
            "composer": "Treat the composer as the circuit design surface, then export and prepare it for a backend.",
            "checkpoint": "What constraints does a real backend impose that the ideal composer hides?",
            "practice": "Prepare a backend-ready notebook using Qiskit Runtime patterns.",
        },
    },
}


def inject_theme():
    st.markdown(
        """
<style>
    :root {
        --lab-bg: #07110f;
        --panel: rgba(12, 30, 28, 0.78);
        --panel-2: rgba(17, 37, 42, 0.72);
        --line: rgba(111, 225, 205, 0.26);
        --line-strong: rgba(111, 225, 205, 0.52);
        --text: #e9fff9;
        --muted: #8db8b0;
        --cyan: #65f4d4;
        --gold: #f6c85f;
        --rose: #ff6f91;
        --violet: #a7a2ff;
    }

    .stApp {
        color: var(--text);
        background:
            repeating-linear-gradient(90deg, rgba(101, 244, 212, 0.035) 0 1px, transparent 1px 86px),
            repeating-linear-gradient(0deg, rgba(246, 200, 95, 0.028) 0 1px, transparent 1px 86px),
            linear-gradient(135deg, #07110f 0%, #0d171d 45%, #161123 100%);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }

    [data-testid="stSidebar"] {
        background: rgba(6, 15, 15, 0.95);
        border-right: 1px solid var(--line);
    }

    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: 0;
    }

    p, li, label, div {
        color: var(--text);
    }

    .lab-hero {
        border: 1px solid var(--line);
        background:
            linear-gradient(145deg, rgba(10, 27, 25, 0.94), rgba(28, 23, 48, 0.86)),
            repeating-linear-gradient(90deg, rgba(101, 244, 212, 0.08) 0 1px, transparent 1px 48px);
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
        transform-style: preserve-3d;
    }

    .lab-eyebrow {
        color: var(--cyan);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08rem;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .lab-hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: clamp(2rem, 4vw, 4.6rem);
        line-height: 1;
    }

    .lab-hero p {
        color: var(--muted);
        max-width: 920px;
        margin: 0;
        font-size: 1.02rem;
    }

    .metric-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0 20px 0;
    }

    .physics-card, .gate-card, .timeline-row {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(145deg, rgba(18, 39, 37, 0.86), rgba(17, 21, 34, 0.78)),
            repeating-linear-gradient(135deg, rgba(255, 255, 255, 0.025) 0 1px, transparent 1px 12px);
        padding: 14px;
        box-shadow:
            0 18px 38px rgba(0, 0, 0, 0.26),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        transform: translateZ(0);
        transition: border-color 160ms ease, transform 160ms ease, box-shadow 160ms ease;
    }

    .physics-card:hover, .gate-card:hover, .timeline-row:hover {
        border-color: var(--line-strong);
        transform: translateY(-2px);
        box-shadow:
            0 22px 44px rgba(0, 0, 0, 0.31),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    .physics-card strong, .gate-card strong {
        color: var(--cyan);
    }

    .physics-card span, .gate-card span {
        color: var(--muted);
        font-size: 0.9rem;
    }

    .gate-card {
        min-height: 126px;
    }

    .timeline-row {
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }

    .timeline-chip {
        border: 1px solid var(--line-strong);
        border-radius: 999px;
        padding: 4px 10px;
        color: var(--gold);
        white-space: nowrap;
        font-size: 0.82rem;
    }

    .lab-shell {
        border: 1px solid rgba(111, 225, 205, 0.24);
        border-radius: 8px;
        padding: 16px;
        background:
            linear-gradient(160deg, rgba(9, 24, 23, 0.86), rgba(19, 18, 33, 0.72)),
            repeating-linear-gradient(90deg, rgba(111, 225, 205, 0.035) 0 1px, transparent 1px 36px);
        box-shadow: 0 28px 80px rgba(0, 0, 0, 0.34);
        perspective: 900px;
    }

    .roadmap {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0 24px 0;
    }

    .roadmap-step {
        position: relative;
        min-height: 134px;
        border: 1px solid rgba(111, 225, 205, 0.25);
        border-radius: 8px;
        padding: 14px;
        background:
            linear-gradient(145deg, rgba(14, 33, 31, 0.9), rgba(23, 20, 39, 0.82));
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.25);
    }

    .roadmap-step strong {
        color: var(--gold);
        display: block;
        font-size: 0.92rem;
        margin-bottom: 8px;
    }

    .roadmap-step span {
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.45;
    }

    .stButton > button {
        border-radius: 6px;
        border: 1px solid var(--line-strong);
        background: rgba(101, 244, 212, 0.08);
        color: var(--text);
        min-height: 2.55rem;
    }

    .stButton > button:hover {
        border-color: var(--cyan);
        background: rgba(101, 244, 212, 0.18);
        color: var(--text);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        color: var(--muted);
    }

    .stTabs [aria-selected="true"] {
        color: var(--cyan);
        border-bottom: 2px solid var(--cyan);
    }

    .stCodeBlock, .stTextArea textarea {
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
    }

    @media (max-width: 900px) {
        .metric-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .roadmap {
            grid-template-columns: 1fr;
        }
    }
</style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state():
    defaults = {
        "composer_gates": [],
        "composer_last_gate": None,
        "composer_ai_feedback": "",
        "num_qubits": 2,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_metric_strip(engine):
    probabilities = engine.get_probabilities()
    entangling_gates = sum(1 for gate in st.session_state.composer_gates if gate["gate"] == "CNOT")
    depth = len(st.session_state.composer_gates)
    nonzero = sum(1 for value in probabilities.values() if value > 1e-9)

    st.markdown(
        f"""
<div class="metric-strip">
    <div class="physics-card"><strong>{st.session_state.num_qubits}</strong><br><span>active qubits</span></div>
    <div class="physics-card"><strong>{depth}</strong><br><span>gate operations</span></div>
    <div class="physics-card"><strong>{entangling_gates}</strong><br><span>entangling links</span></div>
    <div class="physics-card"><strong>{nonzero}</strong><br><span>visible basis outcomes</span></div>
</div>
        """,
        unsafe_allow_html=True,
    )


def format_gate(gate_data, index):
    gate = gate_data["gate"]
    target = gate_data["target"]
    control = gate_data.get("control")
    if gate == "CNOT":
        detail = f"control q{control} -> target q{target}"
    elif gate in {"RX", "RY", "RZ"}:
        detail = f"q{target}, angle {float(gate_data.get('angle', 0.0)):.3f} rad"
    else:
        detail = f"q{target}"
    return f"{index:02d}. {gate}", detail


def add_gate_to_composer(gate, target, control=None, angle=None):
    gate_data = {"gate": gate, "target": target, "control": control}
    if gate in {"RX", "RY", "RZ"}:
        gate_data["angle"] = angle if angle is not None else math.pi / 2
    st.session_state.composer_gates.append(gate_data)
    st.session_state.composer_last_gate = (GATE_LIBRARY[gate]["label"], target)
    st.session_state.composer_ai_feedback = ""
    st.rerun()


def build_engine():
    engine = QuantumEngine(num_qubits=st.session_state.num_qubits)
    engine.gates = st.session_state.composer_gates
    return engine


def render_gate_palette():
    st.markdown("#### Gate Palette")
    selected_gate = st.selectbox(
        "Gate",
        list(GATE_LIBRARY.keys()),
        format_func=lambda gate: f"{gate} · {GATE_LIBRARY[gate]['label']}",
    )

    gate_info = GATE_LIBRARY[selected_gate]
    st.markdown(
        f"""
<div class="gate-card">
    <strong>{gate_info["family"]}</strong><br>
    <span>{gate_info["description"]}</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    qubit_options = list(range(st.session_state.num_qubits))
    target = st.selectbox("Target qubit", qubit_options, format_func=lambda q: f"q{q}")
    control = None
    if selected_gate == "CNOT":
        control_options = [q for q in qubit_options if q != target]
        control = st.selectbox("Control qubit", control_options, format_func=lambda q: f"q{q}")

    angle = None
    if selected_gate in {"RX", "RY", "RZ"}:
        angle_turns = st.slider("Rotation angle", -2.0, 2.0, 0.5, 0.125, help="Measured in multiples of pi.")
        angle = angle_turns * math.pi
        st.caption(f"Angle = {angle_turns:.3f}π = {angle:.3f} radians")

    add_disabled = selected_gate == "CNOT" and st.session_state.num_qubits < 2
    if st.button("Add Gate", type="primary", use_container_width=True, disabled=add_disabled):
        add_gate_to_composer(selected_gate, target, control, angle)

    col_undo, col_reset = st.columns(2)
    with col_undo:
        if st.button("Undo", use_container_width=True, disabled=not st.session_state.composer_gates):
            st.session_state.composer_gates.pop()
            st.session_state.composer_last_gate = None
            st.session_state.composer_ai_feedback = ""
            st.rerun()
    with col_reset:
        if st.button("Reset", use_container_width=True, disabled=not st.session_state.composer_gates):
            st.session_state.composer_gates = []
            st.session_state.composer_last_gate = None
            st.session_state.composer_ai_feedback = ""
            st.rerun()


def render_timeline():
    st.markdown("#### Circuit Timeline")
    if not st.session_state.composer_gates:
        st.info("Start with H on q0, then add CNOT q0 -> q1 to create your first Bell state.")
        return

    for index, gate_data in enumerate(st.session_state.composer_gates, start=1):
        title, detail = format_gate(gate_data, index)
        st.markdown(
            f"""
<div class="timeline-row">
    <div><strong>{title}</strong><br><span>{detail}</span></div>
    <div class="timeline-chip">{GATE_LIBRARY[gate_data["gate"]]["family"]}</div>
</div>
            """,
            unsafe_allow_html=True,
        )


def render_composer_feedback():
    st.markdown("#### Physics Coach")
    if not st.session_state.composer_last_gate:
        st.markdown(
            """
<div class="physics-card">
    <strong>Ready state:</strong><br>
    <span>Add a gate and the coach will explain what physically changed in the circuit.</span>
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    gate_name, q_idx = st.session_state.composer_last_gate
    with st.chat_message("assistant", avatar="⚛️"):
        st.markdown("**A.C.E. Physics Coach**")
        if not st.session_state.composer_ai_feedback:
            sequence = []
            for gate in st.session_state.composer_gates:
                if gate["gate"] == "CNOT":
                    sequence.append(f"CNOT control q{gate['control']} target q{gate['target']}")
                else:
                    sequence.append(f"{gate['gate']} on q{gate['target']}")
            st.session_state.composer_ai_feedback = st.write_stream(
                explain_composer_action(gate_name, q_idx, " -> ".join(sequence))
            )
        else:
            st.markdown(st.session_state.composer_ai_feedback)


def render_probabilities(engine):
    st.markdown("#### Measurement Probabilities")
    probabilities = engine.get_probabilities()
    for basis, value in probabilities.items():
        st.progress(float(value), text=f"|{basis}>  {value * 100:.1f}%")


def render_state_readout(angles):
    st.markdown("#### Bloch Readout")
    for qubit, data in angles.items():
        purity = data.get("purity", 0.0)
        state_label = "pure vector" if purity > 0.98 else "mixed local state"
        st.markdown(
            f"""
<div class="physics-card">
    <strong>q{qubit}: {state_label}</strong><br>
    <span>x={data["x"]:.3f}, y={data["y"]:.3f}, z={data["z"]:.3f}, purity radius={purity:.3f}</span>
</div>
            """,
            unsafe_allow_html=True,
        )


def render_learning_roadmap():
    st.markdown("### Full Qiskit Learning Path")
    steps = []
    for level_name, modules in CURRICULUM.items():
        module_list = ", ".join(modules.keys())
        steps.append(
            f"""
<div class="roadmap-step">
    <strong>{level_name}</strong>
    <span>{module_list}</span>
</div>
            """
        )

    st.markdown(f"<div class='roadmap'>{''.join(steps)}</div>", unsafe_allow_html=True)


def render_curriculum():
    st.sidebar.header("Learning Path")
    level = st.sidebar.selectbox("Level", list(CURRICULUM.keys()))
    module = st.sidebar.radio("Module", list(CURRICULUM[level].keys()))
    lesson = CURRICULUM[level][module]

    render_learning_roadmap()

    st.markdown(f"## {module}")
    st.markdown(
        f"""
<div class="physics-card">
    <strong>Big idea</strong><br>
    <span>{lesson["big_idea"]}</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    col_one, col_two, col_three = st.columns(3)
    with col_one:
        st.markdown(
            f"""
<div class="physics-card">
    <strong>Composer move</strong><br>
    <span>{lesson["composer"]}</span>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col_two:
        st.markdown(
            f"""
<div class="physics-card">
    <strong>Checkpoint</strong><br>
    <span>{lesson["checkpoint"]}</span>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col_three:
        st.markdown(
            f"""
<div class="physics-card">
    <strong>Practice lab</strong><br>
    <span>{lesson["practice"]}</span>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("### Interactive Bloch Sphere")
    ctrl, sphere = st.columns([4, 6])
    with ctrl:
        theta_deg = st.slider("Polar theta", 0.0, 180.0, 90.0, 1.0)
        phi_deg = st.slider("Azimuthal phi", 0.0, 360.0, 0.0, 1.0)
        theta_rad = math.radians(theta_deg)
        phi_rad = math.radians(phi_deg)
        cos_half = math.cos(theta_rad / 2.0)
        sin_half = math.sin(theta_rad / 2.0)
        st.latex(rf"|\psi\rangle = {cos_half:.3f}|0\rangle + e^{{i{phi_deg:.0f}^\circ}}{sin_half:.3f}|1\rangle")
        st.caption("Theta changes the probability split. Phi changes relative phase around the equator.")
    with sphere:
        render_bloch_sphere(theta_rad, phi_rad, qubit_name="lesson qubit")

    st.divider()
    st.markdown("### AI Teaching Lab")
    if f"intro_{module}" not in st.session_state:
        st.session_state[f"intro_{module}"] = ""
        st.session_state[f"feynman_{module}"] = ""
        st.session_state[f"code_{module}"] = ""
        st.session_state[f"tutor_{module}"] = ""

    with st.chat_message("assistant", avatar="⚛️"):
        st.markdown("**A.C.E. Tutor**")
        if not st.session_state[f"intro_{module}"]:
            st.session_state[f"intro_{module}"] = st.write_stream(generate_intro(module))
        else:
            st.markdown(st.session_state[f"intro_{module}"])

    if st.button("Generate Explanation, Code, and Checkpoint", use_container_width=True):
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown("**Physical intuition**")
            st.session_state[f"feynman_{module}"] = st.write_stream(explain_concept(module))
        with st.chat_message("assistant", avatar="⌨️"):
            st.markdown("**Qiskit code**")
            st.session_state[f"code_{module}"] = st.write_stream(
                generate_code(module, st.session_state[f"feynman_{module}"])
            )
        with st.chat_message("assistant", avatar="🎯"):
            st.markdown("**Socratic checkpoint**")
            st.session_state[f"tutor_{module}"] = st.write_stream(generate_problem(module))

    if st.session_state[f"feynman_{module}"]:
        with st.expander("Saved teaching output", expanded=True):
            st.markdown(st.session_state[f"feynman_{module}"])
            st.markdown(st.session_state[f"code_{module}"])
            st.markdown(st.session_state[f"tutor_{module}"])


def render_composer():
    st.sidebar.header("Composer Setup")
    selected_qubits = st.sidebar.slider("Qubits", 1, 4, st.session_state.num_qubits)
    if selected_qubits != st.session_state.num_qubits:
        st.session_state.num_qubits = selected_qubits
        st.session_state.composer_gates = []
        st.session_state.composer_last_gate = None
        st.session_state.composer_ai_feedback = ""
        st.rerun()

    engine = build_engine()
    angles = engine.run_simulation()
    render_metric_strip(engine)

    controls, visual = st.columns([4, 8])
    with controls:
        render_gate_palette()
        render_timeline()
        render_composer_feedback()

    with visual:
        st.markdown("#### 3D State Laboratory")
        bloch_cols = st.columns(min(st.session_state.num_qubits, 4))
        for qubit in range(st.session_state.num_qubits):
            with bloch_cols[qubit % len(bloch_cols)]:
                st.caption(f"q{qubit}")
                render_bloch_sphere(angles[qubit]["theta"], angles[qubit]["phi"], qubit_name=f"q{qubit}")

        prob_col, readout_col = st.columns([5, 4])
        with prob_col:
            render_probabilities(engine)
        with readout_col:
            render_state_readout(angles)

        st.markdown("#### Circuit Diagram")
        fig = engine.get_circuit_figure()
        st.pyplot(fig, clear_figure=True)

        st.markdown("#### Qiskit Export")
        st.code(engine.get_qiskit_code(), language="python")


def render_sandbox():
    st.markdown("## Qiskit Sandbox")
    st.caption("Run short Qiskit experiments locally and compare the output with the visual composer.")

    notebook_code = st.text_area(
        "Python / Qiskit",
        value="""from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

print("Bell circuit:")
print(qc)

fig = qc.draw(output="mpl")
""",
        height=320,
    )

    if st.button("Run Sandbox", type="primary", use_container_width=True):
        with st.spinner("Running local Qiskit code..."):
            result = execute_notebook_code(notebook_code)

        if result["success"]:
            st.success("Execution completed.")
        else:
            st.error("Execution failed.")
            st.code(result["error"], language="python")

        if result["stdout"]:
            st.markdown("#### stdout")
            st.code(result["stdout"])
        if result["stderr"]:
            st.markdown("#### stderr")
            st.code(result["stderr"])
        if result["figures"]:
            st.markdown("#### Figures")
            for fig in result["figures"]:
                st.pyplot(fig)


inject_theme()
init_session_state()

render_quantum_field()

tab_learn, tab_compose, tab_sandbox = st.tabs(["Learn", "Compose", "Sandbox"])

with tab_learn:
    render_curriculum()

with tab_compose:
    render_composer()

with tab_sandbox:
    render_sandbox()
