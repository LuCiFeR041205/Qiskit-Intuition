import math

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

import requests
import json
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

# Client-side agent and component imports
from frontend.agents.composer_agent import explain_composer_action
from frontend.agents.feynman_agent import explain_concept
from frontend.agents.qiskit_engineer import generate_code
from frontend.agents.socratic_tutor import generate_problem
from frontend.agents.router_agent import route_and_respond, classify_intent, AGENT_META
from frontend.components.bloch_sphere import render_bloch_sphere
from frontend.components.quantum_field import render_quantum_field
from frontend.components.circuit_composer import render_circuit_composer
from frontend.components.code_editor import render_sandbox_header, PRESET_EXPERIMENTS
from frontend.components.local_copilot import render_local_copilot
from backend.core.quest_engine import get_quests, render_quest_tab
BACKEND_URL = "http://localhost:8000"

def is_backend_online():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False

# Client-side remote execution wrapper
def execute_notebook_code(code_string):
    if is_backend_online():
        try:
            r = requests.post(f"{BACKEND_URL}/execute", json={"code": code_string}, timeout=10.0)
            if r.status_code == 200:
                data = r.json()
                figures = []
                for fig_b64 in data.get("figures", []):
                    img_bytes = base64.b64decode(fig_b64)
                    figures.append(Image.open(BytesIO(img_bytes)))
                return {
                    "success": data.get("success", False),
                    "stdout": data.get("stdout", ""),
                    "stderr": data.get("stderr", ""),
                    "error": data.get("error", None),
                    "figures": figures
                }
        except Exception:
            pass
    # Fallback to local
    from backend.core.notebook_engine import execute_notebook_code as local_execute
    return local_execute(code_string)

# Client-side remote QuantumEngine wrapper
class QuantumEngine:
    def __init__(self, num_qubits=2):
        self.num_qubits = num_qubits
        self.gates = []
        self._last_simulation = None

    def add_gate(self, gate_name, target, control=None):
        self.gates.append({
            'gate': gate_name.upper(),
            'target': target,
            'control': control
        })

    def add_h(self, qubit):
        self.add_gate('H', qubit)

    def add_x(self, qubit):
        self.add_gate('X', qubit)

    def add_y(self, qubit):
        self.add_gate('Y', qubit)

    def add_z(self, qubit):
        self.add_gate('Z', qubit)

    def add_cnot(self, control, target):
        self.add_gate('CNOT', target, control)

    def add_rotation(self, gate_name, qubit, angle):
        self.gates.append({
            'gate': gate_name.upper(),
            'target': qubit,
            'control': None,
            'angle': angle,
        })

    def clear(self):
        self.gates = []
        self._last_simulation = None

    def _fetch_simulation(self, noisy: bool = False):
        if self._last_simulation is not None and self._last_simulation.get("_was_noisy") == noisy:
            return self._last_simulation
        if is_backend_online():
            try:
                r = requests.post(f"{BACKEND_URL}/simulate", json={
                    "gates": self.gates,
                    "num_qubits": self.num_qubits,
                    "noisy": noisy
                }, timeout=5.0)
                if r.status_code == 200:
                    self._last_simulation = r.json()
                    self._last_simulation["_was_noisy"] = noisy
                    return self._last_simulation
            except Exception:
                pass
        # Fallback to local simulation
        from backend.core.quantum_engine import QuantumEngine as LocalEngine
        local = LocalEngine(self.num_qubits)
        local.gates = self.gates
        sv = local.get_statevector()
        bloch_angles = local.run_simulation()
        probabilities = local.get_probabilities(noisy=noisy)
        self._last_simulation = {
            "statevector": [str(c) for c in sv.data],
            "bloch_angles": bloch_angles,
            "probabilities": probabilities,
            "circuit_figure": None,
            "_was_noisy": noisy
        }
        return self._last_simulation

    def run_simulation(self, noisy: bool = False):
        sim = self._fetch_simulation(noisy=noisy)
        angles = {}
        for k, v in sim["bloch_angles"].items():
            angles[int(k)] = v
        return angles

    def get_probabilities(self, noisy: bool = False):
        sim = self._fetch_simulation(noisy=noisy)
        return sim["probabilities"]

    def get_qiskit_code(self):
        if is_backend_online():
            try:
                r = requests.post(f"{BACKEND_URL}/export", json={
                    "gates": self.gates,
                    "num_qubits": self.num_qubits
                }, timeout=3.0)
                if r.status_code == 200:
                    return r.json()["code"]
            except Exception:
                pass
        from backend.core.quantum_engine import QuantumEngine as LocalEngine
        local = LocalEngine(self.num_qubits)
        local.gates = self.gates
        return local.get_qiskit_code()

    def get_circuit_figure(self, noisy: bool = False):
        sim = self._fetch_simulation(noisy=noisy)
        if sim.get("circuit_figure"):
            img_bytes = base64.b64decode(sim["circuit_figure"])
            return Image.open(BytesIO(img_bytes))
        from backend.core.quantum_engine import QuantumEngine as LocalEngine
        local = LocalEngine(self.num_qubits)
        local.gates = self.gates
        return local.get_circuit_figure()



st.set_page_config(
    page_title="Qiskit Intuition Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.components.data_store import GATE_LIBRARY, CURRICULUM
from frontend.components.theme import inject_theme

def init_session_state():
    defaults = {
        "composer_gates": [],
        "composer_last_gate": None,
        "composer_ai_feedback": "",
        "num_qubits": 2,
        "chat_history": [],
        "sandbox_code": PRESET_EXPERIMENTS["Bell State"]["code"],
        "eli5_mode": False,
        "noisy_simulation": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Metric Strip ──

def render_metric_strip(engine):
    probabilities = engine.get_probabilities(noisy=st.session_state.get("noisy_simulation", False))
    entangling_gates = sum(1 for gate in st.session_state.composer_gates if gate["gate"] == "CNOT")
    depth = len(st.session_state.composer_gates)
    nonzero = sum(1 for value in probabilities.values() if value > 1e-9)

    st.markdown(
        f"""
<div class="metric-strip">
    <div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0"><strong>{st.session_state.num_qubits}</strong><br><span>active qubits</span></div>
    <div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0"><strong>{depth}</strong><br><span>gate operations</span></div>
    <div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0"><strong>{entangling_gates}</strong><br><span>entangling links</span></div>
    <div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0"><strong>{nonzero}</strong><br><span>visible basis outcomes</span></div>
</div>
        """,
        unsafe_allow_html=True,
    )


# ── Gate Helpers ──

def format_gate(gate_data, index):
    gate = gate_data["gate"]
    target = gate_data["target"]
    control = gate_data.get("control")
    if gate == "CNOT":
        detail = f"control q{control} → target q{target}"
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


# ── Gate Palette ──

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
        angle_turns = st.slider("Rotation angle", -2.0, 2.0, 0.5, 0.125, help="Measured in multiples of π.")
        angle = angle_turns * math.pi
        st.caption(f"Angle = {angle_turns:.3f}π = {angle:.3f} radians")

    add_disabled = selected_gate == "CNOT" and st.session_state.num_qubits < 2
    if st.button("Add Gate", type="primary", use_container_width=True, disabled=add_disabled):
        add_gate_to_composer(selected_gate, target, control, angle)

    col_undo, col_reset = st.columns(2)
    with col_undo:
        if st.button("⟲ Undo", use_container_width=True, disabled=not st.session_state.composer_gates):
            st.session_state.composer_gates.pop()
            st.session_state.composer_last_gate = None
            st.session_state.composer_ai_feedback = ""
            st.rerun()
    with col_reset:
        if st.button("⟳ Reset", use_container_width=True, disabled=not st.session_state.composer_gates):
            st.session_state.composer_gates = []
            st.session_state.composer_last_gate = None
            st.session_state.composer_ai_feedback = ""
            st.rerun()


# ── Composer Feedback ──

def render_composer_feedback():
    st.markdown("#### Physics Coach")
    if not st.session_state.composer_last_gate:
        st.markdown(
            """
<div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0">
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
                explain_composer_action(gate_name, q_idx, " → ".join(sequence), eli5_mode=st.session_state.get("eli5_mode", False))
            )
        else:
            st.markdown(st.session_state.composer_ai_feedback)


# ── Probability Bars ──

def render_probabilities(engine):
    st.markdown("#### Measurement Probabilities")
    probabilities = engine.get_probabilities(noisy=st.session_state.get("noisy_simulation", False))
    for basis, value in probabilities.items():
        pct = value * 100
        width = max(pct, 0.5)
        st.markdown(
            f"""
<div class="neon-bar-wrap">
    <div class="neon-bar neon-bar-cyan" style="width:{width}%;">|{basis}⟩ {pct:.1f}%</div>
</div>
            """,
            unsafe_allow_html=True,
        )


# ── State Readout ──

def render_state_readout(angles):
    st.markdown("#### Bloch Readout")
    for qubit, data in angles.items():
        purity = data.get("purity", 0.0)
        state_label = "pure vector" if purity > 0.98 else "mixed local state"
        st.markdown(
            f"""
<div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0">
    <strong>q{qubit}: {state_label}</strong><br>
    <span>x={data["x"]:.3f}, y={data["y"]:.3f}, z={data["z"]:.3f}, purity radius={purity:.3f}</span>
</div>
            """,
            unsafe_allow_html=True,
        )


# ── Learning Roadmap ──

def render_learning_roadmap():
    st.markdown("### Full Qiskit Learning Path")
    steps = []
    for level_name, modules in CURRICULUM.items():
        module_list = ", ".join(modules.keys())
        steps.append(
            f"""
<div class="roadmap-step" role="listitem" tabindex="0">
    <strong>{level_name}</strong>
    <span>{module_list}</span>
</div>
            """
        )

    st.markdown(f"<div class='roadmap' role='list' aria-label='Learning Roadmap'>{''.join(steps)}</div>", unsafe_allow_html=True)


def get_selected_lesson():
    levels = list(CURRICULUM.keys())
    selected_level = st.session_state.get("selected_level", levels[0])
    if selected_level not in CURRICULUM:
        selected_level = levels[0]

    modules = list(CURRICULUM[selected_level].keys())
    selected_module = st.session_state.get("selected_module", modules[0])
    if selected_module not in CURRICULUM[selected_level]:
        selected_module = modules[0]

    return selected_level, selected_module, CURRICULUM[selected_level][selected_module]


def render_ai_teaching_lab(module, lesson, surface=st):
    surface.markdown("### AI Teaching Lab")
    if f"feynman_{module}" not in st.session_state:
        st.session_state[f"feynman_{module}"] = ""
        st.session_state[f"code_{module}"] = ""
        st.session_state[f"tutor_{module}"] = ""

    surface.markdown("**A.C.E. Tutor**")
    surface.markdown(
        f"Welcome to the **{module}** module. "
        f"{lesson['big_idea']} "
        f"Use the button below to activate the AI teaching agents, "
        f"or explore the Bloch sphere and composer on your own first."
    )

    if surface.button("🚀 Generate Explanation, Code, and Checkpoint", use_container_width=True, key=f"teaching_lab_{module}"):
        import time

        def offline_stream(text: str):
            words = text.split(" ")
            for w in words:
                yield w + " "
                time.sleep(0.012)

        def clean_html_to_markdown(html: str) -> str:
            clean = html.replace("<br>", "\n").replace("<strong>", "**").replace("</strong>", "**")
            clean = clean.replace("<ul>", "").replace("</ul>", "").replace("<li>", "- ").replace("</li>", "\n")
            clean = clean.replace("<code>", "`").replace("</code>", "`")
            return clean

        raw_lesson = lesson.get("lesson_text", "Lesson content active.")
        lesson_md = clean_html_to_markdown(raw_lesson)
        code_md = f"Here is the physical code template for **{module}**:\n\n```python\n{lesson.get('tutorial_code', '# Code template')}\n```"
        challenge_md = f"**Diagnostic protocol online:**\n\n{lesson.get('tutor_challenge', 'Ready to test understanding.')}"

        surface.markdown("**Physical intuition**")
        st.session_state[f"feynman_{module}"] = surface.write_stream(offline_stream(lesson_md))
        surface.markdown("**Qiskit code**")
        st.session_state[f"code_{module}"] = surface.write_stream(offline_stream(code_md))
        surface.markdown("**Socratic checkpoint**")
        st.session_state[f"tutor_{module}"] = surface.write_stream(offline_stream(challenge_md))

    if st.session_state[f"feynman_{module}"]:
        with surface.expander("Saved teaching output", expanded=False):
            surface.markdown(st.session_state[f"feynman_{module}"])
            surface.markdown(st.session_state[f"code_{module}"])
            surface.markdown(st.session_state[f"tutor_{module}"])


def render_interactive_code_challenge(module, lesson):
    if not st.session_state.get(f"feynman_{module}"):
        return

    st.divider()
    st.markdown("### 💻 Interactive Code Challenge")
    st.caption("Try writing the Qiskit code to solve the challenge above!")

    challenge_code_key = f"challenge_code_{module}"
    if challenge_code_key not in st.session_state:
        st.session_state[challenge_code_key] = lesson.get("tutorial_code", "# Write your Qiskit code here...\n")

    user_code = st.text_area(
        "Challenge Editor",
        value=st.session_state[challenge_code_key],
        height=250,
        label_visibility="collapsed",
    )
    st.session_state[challenge_code_key] = user_code

    if st.button("▶ Run Challenge Code", type="primary"):
        with st.spinner("Running your code..."):
            result = execute_notebook_code(user_code)

            if result["success"]:
                st.success("Execution completed successfully!")
            else:
                st.error("Execution failed.")
                if result["error"]:
                    st.code(result["error"], language="python")
                elif result["stderr"]:
                    st.code(result["stderr"], language="python")

            if result["stdout"]:
                st.markdown("#### Output")
                st.code(result["stdout"])

            if result["figures"]:
                st.markdown("#### Figures")
                for fig in result["figures"]:
                    if isinstance(fig, plt.Figure):
                        st.pyplot(fig)
                    else:
                        st.image(fig)


# ── Learn Tab ──

def render_curriculum():
    st.sidebar.header("Learning Path")
    levels = list(CURRICULUM.keys())
    level = st.sidebar.selectbox("Level", levels)
    module = st.sidebar.radio("Module", list(CURRICULUM[level].keys()))
    lesson = CURRICULUM[level][module]

    render_learning_roadmap()

    st.markdown(f"## {module}")
    st.markdown(
        f"""
<div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0">
    <strong>Big idea</strong><br>
    <span>{lesson["big_idea"]}</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    if "lesson_text" in lesson:
        st.markdown(
            f"""
<div class="lab-hero" role="region" aria-label="Tutorial Lesson" tabindex="0" style="margin-top: 15px; margin-bottom: 20px;">
    <h3 style="color: var(--cyan) !important; margin-top: 0; font-size: 1.25rem;">📖 Tutorial Lesson</h3>
    <div style="line-height: 1.6; font-size: 1.02rem; color: var(--text);">
        {lesson["lesson_text"]}
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    col_one, col_two, col_three = st.columns(3)
    with col_one:
        st.markdown(
            f"""
<div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0">
    <strong>Composer move</strong><br>
    <span>{lesson["composer"]}</span>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col_two:
        st.markdown(
            f"""
<div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0">
    <strong>Checkpoint</strong><br>
    <span>{lesson["checkpoint"]}</span>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col_three:
        st.markdown(
            f"""
<div class="physics-card" role="region" aria-label="Physics Concept" tabindex="0">
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
    render_ai_teaching_lab(module, lesson)
    render_interactive_code_challenge(module, lesson)


# ── Compose Tab ──

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
    noisy_sim = st.session_state.get("noisy_simulation", False)
    angles = engine.run_simulation(noisy=noisy_sim)
    render_metric_strip(engine)

    tab_build, tab_analyze = st.tabs(["🛠️ Builder", "🔬 Analysis"])
    
    with tab_build:
        st.markdown("#### Visual Circuit")
        render_circuit_composer(st.session_state.composer_gates, st.session_state.num_qubits)
        
        st.markdown("#### 🗣️ Natural Language Circuit Builder")
        st.info("A.C.E. Builder is running locally. Go to the Copilot tab to chat!")
        controls, feedback = st.columns([4, 8])
        with controls:
            render_gate_palette()
        with feedback:
            render_composer_feedback()

    with tab_analyze:
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
        fig = engine.get_circuit_figure(noisy=noisy_sim)
        if isinstance(fig, plt.Figure):
            st.pyplot(fig, clear_figure=True)
        else:
            st.image(fig)

        st.markdown("#### Qiskit Export")
        st.code(engine.get_qiskit_code(), language="python")


# ── Chat Tab ──

def render_chat():
    st.markdown("## A.C.E. Copilot Console")
    st.caption("A.C.E. now lives in the sidebar so it can stay with you across the lab.")
    st.info("Use the sidebar copilot for offline quantum help while you build, learn, and run experiments.")


def render_offline_code_explanation(code: str):
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    observations = []

    if any("QuantumCircuit" in line for line in lines):
        observations.append("You create a `QuantumCircuit`, which is the recipe board where each qubit operation is placed in order.")
    if any(".h(" in line or ".h " in line for line in lines):
        observations.append("A Hadamard gate appears, so at least one qubit is being moved into superposition.")
    if any(".x(" in line or ".x " in line for line in lines):
        observations.append("A Pauli-X gate appears, which acts like a quantum bit flip between |0> and |1>.")
    if any(".cx(" in line or ".cnot(" in line for line in lines):
        observations.append("A controlled-X operation appears, which can entangle qubits by making one qubit depend on another.")
    if any("measure" in line for line in lines):
        observations.append("The circuit includes measurement, so the quantum state is being converted into classical bits.")
    if any("Statevector" in line for line in lines):
        observations.append("Statevector inspection is used, so you are looking at amplitudes before sampling noise or measurement randomness.")
    if any("AerSimulator" in line or "Simulator" in line for line in lines):
        observations.append("A simulator is involved, so the experiment runs locally rather than on quantum hardware.")

    if not observations:
        observations.append("This code is treated as a local Qiskit/Python experiment. Read it top to bottom as setup, circuit construction, execution, then output.")

    text = [
        "**A.C.E. offline readout**",
        "",
        "No API key is used here. I am giving a local structural explanation of the code you wrote.",
        "",
    ]
    text.extend(f"- {item}" for item in observations)
    text.extend([
        "",
        "**Next check:** run the code, then compare the output with the circuit diagram and probability readout.",
    ])
    return "\n".join(text)


# ── Sandbox Tab ──

def render_sandbox():
    st.markdown("## Qiskit Sandbox")
    st.caption("Run short Qiskit experiments locally and compare the output with the visual composer.")

    # Terminal header
    render_sandbox_header()

    # Preset experiments
    st.markdown("**Preset Experiments**")
    preset_cols = st.columns(len(PRESET_EXPERIMENTS))
    for idx, (name, data) in enumerate(PRESET_EXPERIMENTS.items()):
        with preset_cols[idx]:
            if st.button(f"⚡ {name}", use_container_width=True, help=data["description"]):
                st.session_state.sandbox_code = data["code"]
                st.rerun()

    # Code editor
    notebook_code = st.text_area(
        "Python / Qiskit",
        value=st.session_state.sandbox_code,
        height=320,
        label_visibility="collapsed",
    )
    st.session_state.sandbox_code = notebook_code

    col_run, col_explain = st.columns([1, 1])
    with col_run:
        run_clicked = st.button("▶ Run Sandbox", type="primary", use_container_width=True)
    with col_explain:
        explain_clicked = st.button(
            "🧠 Explain This Code",
            use_container_width=True,
            help="Uses a local rule-based explanation. No API key required."
        )

    if run_clicked:
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
                if isinstance(fig, plt.Figure):
                    st.pyplot(fig)
                else:
                    st.image(fig)

    if explain_clicked:
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown("**A.C.E. Code Explainer**")
            st.markdown(render_offline_code_explanation(notebook_code))


def render_cognitive_core_sidebar():
    status_color = "#65f4d4"
    status_text = "OFFLINE COGNITION ACTIVE"
    pulse_style = f"background-color: {status_color}; box-shadow: 0 0 10px {status_color};"

    st.sidebar.markdown(
        f"""
        <div style="border: 1px solid rgba(101, 244, 212, 0.2); background: rgba(10, 26, 25, 0.85); box-shadow: 0 8px 32px rgba(101, 244, 212, 0.05); padding: 16px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.05em; color: {status_color};">COGNITIVE INTERFACE</span>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; color: {status_color}; font-weight: 700;">{status_text}</span>
                    <span class="pulse-dot" style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; {pulse_style}"></span>
                </div>
            </div>
            <p style="font-size: 0.8rem; color: #8fa09e; line-height: 1.4; margin: 0 0 12px 0;">
                A.C.E. uses a browser-local model and local teaching routines. No external account required.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
        
    st.sidebar.divider()
    st.sidebar.markdown("### A.C.E. Offline")
    with st.sidebar:
        render_local_copilot(height=430, compact=True)
    
    #THIS MESSES UP THE SIDEBAR, REMOVED FOR NOW, KEPT THE CODE JUST IN CASE 
    '''st.sidebar.markdown("### 🎛️ Reality Settings")
    
    eli5_col, eli5_info = st.sidebar.columns([3, 1])
    with eli5_col:
        eli5_mode = st.toggle("🧒 ELI5 Mode", value=st.session_state.get("eli5_mode", False))
        if eli5_mode != st.session_state.get("eli5_mode"):
            st.session_state["eli5_mode"] = eli5_mode
            st.rerun()
    with eli5_info:
        st.info("Explain Like I'm 5 (No Math!)", icon="💡")

    noise_col, noise_info = st.sidebar.columns([3, 1])
    with noise_col:
        noisy_simulation = st.toggle("🌩️ Hardware Noise", value=st.session_state.get("noisy_simulation", False))
        if noisy_simulation != st.session_state.get("noisy_simulation"):
            st.session_state["noisy_simulation"] = noisy_simulation
            st.rerun()
    with noise_info:
        st.warning("Simulate real-world quantum decoherence", icon="⚠️")'''


# ── Main ──

inject_theme()
init_session_state()

# Global cognitive core console in the sidebar
render_cognitive_core_sidebar()

render_quantum_field()

tab_learn, tab_compose, tab_quests, tab_chat, tab_sandbox = st.tabs(["📚 Learn", "🔬 Compose", "🎯 Quests", "💬 A.C.E. Chat", "🧪 Sandbox"])

with tab_learn:
    render_curriculum()

with tab_compose:
    render_composer()

with tab_quests:
    q_engine = build_engine()
    render_quest_tab(q_engine)

with tab_chat:
    render_chat()

with tab_sandbox:
    render_sandbox()
