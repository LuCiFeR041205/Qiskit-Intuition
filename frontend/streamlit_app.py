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

    def _fetch_simulation(self):
        if self._last_simulation is not None:
            return self._last_simulation
        if is_backend_online():
            try:
                r = requests.post(f"{BACKEND_URL}/simulate", json={
                    "gates": self.gates,
                    "num_qubits": self.num_qubits
                }, timeout=5.0)
                if r.status_code == 200:
                    self._last_simulation = r.json()
                    return self._last_simulation
            except Exception:
                pass
        # Fallback to local simulation
        from backend.core.quantum_engine import QuantumEngine as LocalEngine
        local = LocalEngine(self.num_qubits)
        local.gates = self.gates
        sv = local.get_statevector()
        bloch_angles = local.run_simulation()
        probabilities = local.get_probabilities()
        self._last_simulation = {
            "statevector": [str(c) for c in sv.data],
            "bloch_angles": bloch_angles,
            "probabilities": probabilities,
            "circuit_figure": None
        }
        return self._last_simulation

    def run_simulation(self):
        sim = self._fetch_simulation()
        angles = {}
        for k, v in sim["bloch_angles"].items():
            angles[int(k)] = v
        return angles

    def get_probabilities(self):
        sim = self._fetch_simulation()
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

    def get_circuit_figure(self):
        sim = self._fetch_simulation()
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


GATE_LIBRARY = {
    "H": {
        "label": "Hadamard",
        "family": "Superposition",
        "description": "Splits a basis state onto the equator so measurement can return 0 or 1.",
    },
    "X": {
        "label": "Pauli-X",
        "family": "Bit flip",
        "description": "Rotates the qubit through π around the X axis, swapping |0⟩ and |1⟩.",
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
        "description": "Flips the target only when the control is |1⟩, creating conditional motion.",
    },
}


CURRICULUM = {
    "Level 0: Python + Qiskit Setup": {
        "Python for Circuits": {
            "big_idea": "Qiskit circuits are Python objects, so learners need functions, lists, loops, and clean notebook habits.",
            "composer": "Read the exported code after each composer action and connect every line to a visual gate.",
            "checkpoint": "What does `qc.h(0)` mean as Python code and as a physical operation?",
            "practice": "Create a QuantumCircuit, add one gate, print it, and draw it.",
            "lesson_text": "Before we manipulate quantum mechanics, we must understand the language of our control system: Python.<br><br>A quantum circuit is essentially a **digital recipe**. Each line of code adds a new instruction (like a physical gate) to our qubits, from left to right. We use Qiskit's `QuantumCircuit` class to initialize our qubits (which default to the standard state |0⟩).<br><br>To write a circuit, we initialize the object, apply operations, and print it:<br><code>from qiskit import QuantumCircuit<br>qc = QuantumCircuit(1) # Create 1 qubit circuit<br>qc.h(0)                # Apply a Hadamard gate to qubit 0<br>print(qc)              # Print a text-based circuit diagram</code><br><br>Just like a baking recipe, the circuit doesn't do anything until we put it in the oven (simulator or hardware) to run it! This tab helps you see exactly how composer actions translate to real Python lines.",
            "tutorial_code": "from qiskit import QuantumCircuit\n\n# Initialize a circuit with 1 qubit and 1 classical bit\nqc = QuantumCircuit(1, 1)\n\n# Apply a Hadamard gate to qubit 0\nqc.h(0)\n\n# Print a text representation of the circuit\nprint('--- Quantum Circuit recipe ---')\nprint(qc)\n",
            "tutor_challenge": "Boss, what happens if you run `qc.h(0)` twice in a row? Try pasting it in the Sandbox, click Run, and observe the state vector. Does it return back to |0⟩? Why?"
        },
        "Qiskit Objects": {
            "big_idea": "QuantumCircuit, Statevector, AerSimulator, transpiler passes, and backends are the core objects learners reuse everywhere.",
            "composer": "Export a circuit, then paste it into the sandbox and add Statevector inspection.",
            "checkpoint": "Why is a circuit a recipe while a statevector is a simulated physical state?",
            "practice": "Use `QuantumCircuit(2)`, `Statevector.from_instruction(qc)`, and `qc.draw(output='mpl')`.",
            "lesson_text": "Now that we can construct a circuit recipe, let's look at the actual ingredients and baking sheets in Qiskit:<br><br><ul><li><strong>QuantumCircuit</strong>: This is the abstract recipe (the list of gates to be executed).</li><li><strong>Statevector</strong>: This is the exact mathematical description of the qubit's state at any point. Think of it as the perfect, infinite-precision snapshot of a spinning coin before it lands.</li><li><strong>Sampler</strong>: This is the simulator or device execution tool that shoots actual samples (like flipping a coin 1024 times and counting heads vs tails).</li></ul><br>Understanding the difference between the abstract recipe (circuit) and the simulated physical state (statevector) is the first major step to quantum mastery! Try pasting a circuit in the Sandbox and viewing its output.",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\n# Create a 2-qubit circuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n\n# Get the exact simulated statevector representing the circuit state\nsv = Statevector.from_instruction(qc)\nprint('Perfect Statevector Amplitudes:')\nprint(sv.data)\n",
            "tutor_challenge": "If a Statevector is an exact mathematical snapshot of a quantum state, what happens to the Statevector when a measurement gate is added to the circuit? Test it in the Sandbox!"
        },
    },
    "Level 1: Quantum Foundations": {
        "The Qubit": {
            "big_idea": "A qubit is a physical two-level system whose state points somewhere on the Bloch sphere.",
            "composer": "Move theta and phi, then use H, X, and Z to connect symbols to motion.",
            "checkpoint": "If the vector sits at the north pole, what outcome is guaranteed?",
            "practice": "Prepare |0⟩, |1⟩, |+⟩, and |−⟩ in Qiskit and compare their Bloch vectors.",
            "lesson_text": "A classical bit is simple: it is either a <code>0</code> or a <code>1</code>. Think of it as a standard light switch that can only be fully UP or fully DOWN.<br><br>A <strong>quantum bit (qubit)</strong> is represented visually as a three-dimensional sphere (the Bloch Sphere):<br><ul><li>The <strong>North Pole</strong> represents the state |0⟩ (100% chance of measuring 0).</li><li>The <strong>South Pole</strong> represents the state |1⟩ (100% chance of measuring 1).</li><li>The <strong>Equator</strong> and everything in between represent combinations (superpositions) of both!</li></ul><br>By applying rotation gates, we can point our qubit's state vector <em>anywhere</em> on the surface of this sphere. It is a continuous, physical two-level state! Try dragging the sliders below to see the state vector move across the sphere.",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(1)\n# Flip the qubit to the state |1⟩ using a Pauli-X gate\nqc.x(0)\n\nsv = Statevector.from_instruction(qc)\nprint('Statevector at South Pole (|1⟩):')\nprint(sv.data)\n",
            "tutor_challenge": "Boss, if you start at the North Pole (|0⟩) and apply a Pauli-Y gate instead of a Pauli-X, where does the state vector land on the Bloch sphere? How does its phase angle change?"
        },
        "Superposition": {
            "big_idea": "Superposition means the vector is not at a pole; measurement probabilities come from its projection.",
            "composer": "Apply H to |0⟩ and watch the vector land on the equator.",
            "checkpoint": "Why does a balanced superposition not mean the qubit is secretly both classical values?",
            "practice": "Run a Hadamard circuit with 1024 shots and explain why counts fluctuate.",
            "lesson_text": "Imagine a coin lying flat on a table: it is either heads (|0⟩) or tails (|1⟩). This is classical.<br><br>Now, flick the coin so it spins rapidly on the table. Is it heads? Is it tails? While it is spinning, it is in a <strong>superposition</strong> of both states! Only when you slap your hand down on the coin to stop it (performing a <strong>measurement</strong>) does it force itself to collapse into a classical heads or tails.<br><br>In quantum circuits, the <strong>Hadamard (H) gate</strong> is the 'flick' that starts the qubit spinning, placing it perfectly on the equator of the Bloch sphere, giving it an equal 50/50 chance of collapsing to |0⟩ or |1⟩ upon measurement!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(1)\n# Apply Hadamard to create a balanced superposition state |+⟩\nqc.h(0)\n\nsv = Statevector.from_instruction(qc)\nprint('Superposition Statevector |+⟩:')\nprint(sv.data)\n",
            "tutor_challenge": "What is the probability of measuring 0 versus 1 for a state vector sitting exactly on the equator? Test it on the Composer and check the measurement probabilities."
        },
        "Measurement": {
            "big_idea": "Measurement projects the state onto a classical result and destroys most phase information.",
            "composer": "Compare the probability bars before and after gates that only change phase.",
            "checkpoint": "Which gates change probabilities, and which only change phase?",
            "practice": "Measure X|0⟩, H|0⟩, and ZH|0⟩; compare statevector and sampled counts.",
            "lesson_text": "In the quantum realm, **looking at something changes it!**<br><br>A qubit in superposition is represented by a vector pointing somewhere on the Bloch sphere. When we measure the qubit along the Z-axis, we ask it a simple question: <em>'Are you |0⟩ or |1⟩?'</em><br><br>The qubit <em>must</em> collapse to one of the poles. If the vector was on the equator, it has a 50% chance of collapsing to the North pole (|0⟩) and a 50% chance of collapsing to the South pole (|1⟩). Measurement **destroys** the delicate superposition and turns a rich, continuous sphere state into a classical 0 or 1! Observe how the probability bars reflect this projection.",
            "tutorial_code": "from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.h(0)\n# Measure qubit 0 and store in classical bit 0\nqc.measure_all()\nprint('--- Circuit with Measurement ---')\nprint(qc)\n",
            "tutor_challenge": "If you measure a qubit, get a '0', and then measure it a second time immediately afterward, what state will it be in? Can a measured qubit return to a superposition without another gate?"
        },
        "Entanglement": {
            "big_idea": "Entanglement is shared state: individual qubits can lose a pure vector while the pair stays ordered.",
            "composer": "Apply H on q0, then CNOT q0 → q1 to form a Bell state.",
            "checkpoint": "Why can each single Bloch sphere look mixed while the two-qubit circuit is highly structured?",
            "practice": "Build all four Bell states and identify their measurement correlations.",
            "lesson_text": "Albert Einstein famously called quantum entanglement **'spooky action at a distance.'**<br><br>Imagine you have a pair of magical spinning coins. You keep one, and give the other to a friend who travels to the other side of the universe. If the coins are **entangled**, the moment you stop yours and see 'heads,' your friend's coin instantly stops spinning and collapses into 'tails' — every single time, instantly!<br><br>By applying a Hadamard gate on Qubit 0, and then a **CNOT gate** from Qubit 0 to Qubit 1, we physically link their states. Neither qubit has a pure local state anymore; they are part of a unified, shared quantum system. Look at the 3D Bloch spheres of the qubits when you entangle them—they appear to have a reduced radius, indicating a mixed local state!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(2)\nqc.h(0)      # Superposition control\nqc.cx(0, 1)  # Entangle control to target (creates Bell State)\n\nsv = Statevector.from_instruction(qc)\nprint('Bell State |Phi+⟩ Statevector:')\nprint(sv.data)\n",
            "tutor_challenge": "Look at the individual Bloch spheres on the Composer when you entangle two qubits. Why do their purities drop below 1.0? Can you describe the state of a single entangled qubit without referencing the other?"
        },
    },
    "Level 2: Circuit Composer Skills": {
        "Gate Algebra": {
            "big_idea": "Gates are reversible transformations; order matters because rotations around different axes do not generally commute.",
            "composer": "Compare H then Z versus Z then H and inspect the final vector.",
            "checkpoint": "Why can two circuits with the same gates produce different states?",
            "practice": "Use Qiskit to test XZ versus ZX on |0⟩ and |+⟩.",
            "lesson_text": "Unlike classical algebra where <code>a * b</code> is always equal to <code>b * a</code>, in quantum mechanics, **the order of operations matters!** We call this non-commutativity.<br><br>Because gates are physical rotations in three-dimensional space, rotating 90° around the X-axis and then 90° around the Z-axis lands you in a completely different spot than doing the Z-rotation first! <br><br>For instance, applying a Hadamard then a Z gate points the vector in a different direction than applying a Z then a Hadamard. Try composing both sequences on the Visual Composer and compare their final Bloch vectors!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\n# Circuit A: H then Z\nqcA = QuantumCircuit(1)\nqcA.h(0)\nqcA.z(0)\n\n# Circuit B: Z then H\nqcB = QuantumCircuit(1)\nqcB.z(0)\nqcB.h(0)\n\nprint('State A:', Statevector.from_instruction(qcA).data)\nprint('State B:', Statevector.from_instruction(qcB).data)\n",
            "tutor_challenge": "Why can two circuits with the same gates produce different states? Under what conditions do two gates commute (their order does not matter)?"
        },
        "Phase Kickback": {
            "big_idea": "A controlled operation can push phase information backward into the control qubit.",
            "composer": "Use H gates around controlled operations and inspect the phase-sensitive probabilities.",
            "checkpoint": "What changes when phase becomes visible through interference?",
            "practice": "Build a controlled-Z from H and CNOT, then explain the phase path.",
            "lesson_text": "In classical computing, a controlled gate only affects the target bit. But in the quantum world, it is a two-way street!<br><br>When you perform a controlled operation (like CNOT), you expect the control qubit to affect the target. But if the target is in a superposition state, something magical happens: the target's phase information **'kicks back'** up into the control qubit! <br><br>It is like a weight pulling the string in reverse. Phase kickback is the secret engine behind almost every advanced quantum algorithm, including phase estimation and Shor's algorithm. Add Hadamard gates around a CNOT to see phase kickback in action!",
            "tutorial_code": "from qiskit import QuantumCircuit\n\n# Create a circuit utilizing phase kickback\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.h(1)\nqc.z(1)      # Place target in phase sensitive state\nqc.cx(0, 1)  # Controlled gate kicks target phase back to control qubit 0\nqc.h(0)\nprint(qc)\n",
            "tutor_challenge": "What changes when phase becomes visible through interference? Why does applying H gates on the control qubit before and after a CNOT reveal the kicked-back phase?"
        },
        "Parameterized Rotations": {
            "big_idea": "Rx, Ry, and Rz make circuits tunable, which is the basis of variational algorithms.",
            "composer": "Sweep an angle slider and watch the vector move continuously instead of jumping gate to gate.",
            "checkpoint": "Which rotation changes measurement odds from |0⟩, and which initially hides as phase?",
            "practice": "Create a circuit with a Parameter theta and bind three values.",
            "lesson_text": "Fixed gates like H or X rotate the qubit by exact intervals (like flipping 180°). But what if we want to rotate by just 12° or 45.7°?<br><br>**Parameterized Rotations (Rx, Ry, Rz)** let us rotate the qubit vector continuously by any fraction of a degree. This makes circuits tunable, serving as the foundation of modern machine learning and molecular chemistry simulations on quantum computers.<br><br>Try selecting the Ry gate and sweeping the rotation slider. You will see the vector glide smoothly along the sphere surface rather than jumping!",
            "tutorial_code": "from qiskit import QuantumCircuit\nimport numpy as np\n\nqc = QuantumCircuit(1)\n# Rotate by exactly 45 degrees (pi/4 radians) around Y-axis\nqc.ry(np.pi / 4, 0)\nprint(qc)\n",
            "tutor_challenge": "Which rotation changes measurement odds from |0⟩, and which initially hides as phase? Verify this by comparing Ry and Rz gates on the Composer."
        },
    },
    "Level 3: Simulation + Noise": {
        "Statevector vs Shots": {
            "big_idea": "Statevectors show exact amplitudes, while shot-based simulation imitates repeated experimental sampling.",
            "composer": "Compare probability bars with noisy-looking sampled counts in the sandbox.",
            "checkpoint": "Why can a perfect 50/50 state return 512/512 only rarely?",
            "practice": "Run the same Bell circuit with 128, 1024, and 8192 shots.",
            "lesson_text": "A classical simulator has a massive superpower: it can look 'under the hood' and calculate the exact mathematical **Statevector** of the qubit—representing absolute theoretical perfection.<br><br>But a real quantum computer can only give us a 0 or a 1 when measured. To find the probabilities, we must run the circuit multiple times (called **'shots'**) and count the frequency of outcomes. This introduction of statistical sampling means that even a perfect 50/50 superposition will rarely return exactly 512/512 counts due to standard statistical fluctuations. Try running varying shot counts in the Sandbox!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\n\nprint('This circuit can be simulated in Aer simulator using run() for custom shots.')\nprint(qc)\n",
            "tutor_challenge": "Why can a perfect 50/50 superposition state return 512/512 counts only rarely? How does the statistical deviation change when the number of shots is increased from 100 to 10,000?"
        },
        "Noise Models": {
            "big_idea": "Real devices introduce decoherence, gate error, and readout error, which turn ideal circuits into distributions.",
            "composer": "Use the Bell circuit as a reference, then add noise in the sandbox.",
            "checkpoint": "What kind of error would reduce Bell-state correlation?",
            "practice": "Use Aer noise tools to add depolarizing or thermal-relaxation noise.",
            "lesson_text": "In theory, quantum circuits are pristine and perfect. In reality, physical quantum computers are highly delicate and prone to errors.<br><br>Thermal fluctuations, magnetic fields, and wire resistance cause **decoherence** (where qubits lose their quantum properties and decay into thermal noise) and **gate errors**. This turns a pure, ideal state vector into a fuzzy, mixed state.<br><br>We use classical simulators equipped with **Noise Models** to anticipate these hardware errors and find ways to write more error-tolerant code. Select a preset in the Sandbox and check how adding noise modifications alters the output distribution.",
            "tutorial_code": "from qiskit_aer.noise import NoiseModel, depolarizing_error\n# We define a simple depolarizing noise model in Python\nnoise_model = NoiseModel()\nerror = depolarizing_error(0.05, 1) # 5% gate error\nnoise_model.add_all_qubit_quantum_error(error, ['h', 'x'])\nprint('Noise model defined successfully with a 5% single-qubit gate error.')\n",
            "tutor_challenge": "What kind of error would reduce Bell-state correlation? Why does thermal relaxation (T1) always drag qubits toward the |0⟩ state?"
        },
        "Transpilation": {
            "big_idea": "Transpilation rewrites an abstract circuit into the basis gates and connectivity of a target backend.",
            "composer": "Export the circuit, transpile it, and compare the before/after depth.",
            "checkpoint": "Why might a simple circuit grow when mapped to real hardware?",
            "practice": "Transpile a 3-qubit circuit for a fake backend or coupling map.",
            "lesson_text": "When you design a circuit, you can use any gate on any qubit. But real physical chips have strict constraints:<br><br><ul><li><strong>Basis Gates</strong>: Physical hardware can only execute a small, native set of gates (often only Rx, Rz, and CNOT). Any other gate (like H or T) must be compiled out of these.</li><li><strong>Connectivity</strong>: You can only run a CNOT between qubits that are physically connected by superconducting wires on the chip.</li></ul><br>**Transpilation** is the compilation process that rewrites your idealized circuit to fit a specific chip's geometry and gate set. Try exporting your composer circuit and transpiling it in the Sandbox!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager\nfrom qiskit_aer import AerSimulator\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n\nsim = AerSimulator()\npm = generate_preset_pass_manager(optimization_level=1, backend=sim)\ntranspiled_qc = pm.run(qc)\nprint('Transpiled circuit basis gates:', transpiled_qc.basis_gates if hasattr(transpiled_qc, 'basis_gates') else 'Compiled successfully')\n",
            "tutor_challenge": "Why might a simple circuit grow in depth when mapped to real hardware? How does swap gate insertion allow controlled operations between unconnected qubits?"
        },
    },
    "Level 4: Quantum Algorithms": {
        "Grover Intuition": {
            "big_idea": "Grover search alternates marking a target and amplifying its probability through interference.",
            "composer": "Use the sandbox to build small oracle and diffuser circuits.",
            "checkpoint": "Why is the diffuser often described as inversion about the mean?",
            "practice": "Build a two-qubit Grover search and inspect the amplified target probability.",
            "lesson_text": "Grover's Search is one of the crown jewels of quantum computing. It allows searching an unsorted database of size N in just √N steps (a quadratic speedup).<br><br>Rather than checking entries one-by-one, Grover's algorithm puts all database indexes into a uniform superposition and alternates two steps:<br><ol><li><strong>The Oracle</strong>: Negates the phase of the correct answer (marking it without looking).</li><li><strong>The Diffuser</strong>: Performs an 'inversion about the mean' which amplifies the marked item's probability while suppressing all others.</li></ol><br>Repeat this choreography, and the correct answer will rise to a near 100% chance of measurement! Try running the Grover preset in the Sandbox.",
            "tutorial_code": "from qiskit import QuantumCircuit\n# Small 2-qubit Grover circuit finding state |11>\nqc = QuantumCircuit(2)\nqc.h([0, 1])\n# Oracle for |11>\nqc.cz(0, 1)\n# Diffuser\nqc.h([0, 1])\nqc.x([0, 1])\nqc.cz(0, 1)\nqc.x([0, 1])\nqc.h([0, 1])\nprint(qc)\n",
            "tutor_challenge": "Why is the diffuser often described as 'inversion about the mean'? How does the geometry of Grover rotations map onto a two-dimensional subspace?"
        },
        "QFT Intuition": {
            "big_idea": "The quantum Fourier transform converts periodic structure into phase patterns.",
            "composer": "Explore phase gates first; QFT is phase choreography at scale.",
            "checkpoint": "What information is stored in relative phase instead of direct probability?",
            "practice": "Implement a 3-qubit QFT and then reverse the qubit order.",
            "lesson_text": "Just like the classical Fast Fourier Transform (FFT) breaks a complex sound wave down into its individual frequencies, the **Quantum Fourier Transform (QFT)** translates periodic amplitudes into phase frequencies.<br><br>The QFT maps a qubit state from the computational basis (|0⟩, |1⟩) to the phase basis. By encoding periodic patterns across superpositions and executing phase gate rotations, we can extract periodicities with exponential speedup. This forms the mathematical heart of Shor's algorithm for factoring numbers! View the phase rotations on the Bloch spheres when you apply phase-shifting gates.",
            "tutorial_code": "from qiskit import QuantumCircuit\nimport numpy as np\n\n# 2-qubit Quantum Fourier Transform\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cp(np.pi / 2, 0, 1) # Controlled-phase gate\nqc.h(1)\nqc.swap(0, 1)\nprint(qc)\n",
            "tutor_challenge": "What information is stored in relative phase instead of direct probability? How does the QFT enable quantum systems to solve the hidden subgroup problem?"
        },
        "VQE": {
            "big_idea": "Variational Quantum Eigensolver combines parameterized quantum circuits with a classical optimizer.",
            "composer": "Use Ry/Rz layers as a small ansatz and watch parameters change the state.",
            "checkpoint": "Why does VQE need both a quantum circuit and a classical optimizer?",
            "practice": "Build a tiny ansatz and compute expectation values with Qiskit primitives.",
            "lesson_text": "We are currently in the NISQ (Noisy Intermediate-Scale Quantum) era. Since hardware has noise, we use **Hybrid Algorithms** that split the work between classical CPUs and quantum QPUs.<br><br>The **Variational Quantum Eigensolver (VQE)** is the most famous hybrid algorithm. It is used to find the ground state energy of molecules (incredibly useful for drug discovery and chemistry):<br><ol><li>The quantum chip prepares a state using a parameterized circuit (the <em>Ansatz</em>) and measures its energy.</li><li>A classical computer analyzes the energy and uses an optimizer (like gradient descent) to adjust the circuit's angles.</li><li>The cycle repeats until the lowest possible energy state is found!</li></ol>",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\n\ntheta = Parameter('t')\nqc = QuantumCircuit(1)\n# Setup ansatz with tunable Parameter theta\nqc.ry(theta, 0)\nprint(qc)\n",
            "tutor_challenge": "Why does VQE need both a quantum circuit and a classical optimizer? What is the 'barren plateau' problem, and how does it affect optimizer scaling?"
        },
    },
    "Level 5: Hardware + Advanced Workflows": {
        "Primitives": {
            "big_idea": "Modern Qiskit workflows use primitives such as Sampler and Estimator to run circuit jobs with clear intent.",
            "composer": "Export a circuit, then adapt it to a Sampler or Estimator workflow.",
            "checkpoint": "When do you want counts, and when do you want expectation values?",
            "practice": "Run a Bell circuit through a sampler-style workflow.",
            "lesson_text": "In earlier versions of Qiskit, execution returned raw measurement counts. Modern Qiskit 1.0+ has moved to a more physics-first interface called **Primitives**:<br><br><ul><li><strong>Sampler</strong>: Returns the quasi-probability distribution of the basis states. Use this when you want to get counts or sample outcomes (e.g. key search or cryptography).</li><li><strong>Estimator</strong>: Computes the expectation value of physical operators (observables). Use this when you want to measure physical quantities like energy, magnetization, or expectation values (e.g., in VQE or chemistry).</li></ul><br>Primitives simplify writing hardware-agnostic algorithms by handling error mitigation and hardware layouts behind the scenes!",
            "tutorial_code": "print('Modern Qiskit workflows define: Primitives. Sampler vs Estimator.')\nprint('Example import: from qiskit.primitives import StatevectorSampler, StatevectorEstimator')\n",
            "tutor_challenge": "Boss, when do you want measurement counts (Sampler) and when do you want expectational physical values (Estimator)? Detail a scenario for each!"
        },
        "Error Mitigation": {
            "big_idea": "Error mitigation estimates better answers from noisy data without fully correcting the quantum state.",
            "composer": "Start with shallow circuits and compare ideal versus noisy expectations.",
            "checkpoint": "Why is mitigation not the same as fault-tolerant error correction?",
            "practice": "Compare raw and mitigated expectation values for a small observable.",
            "lesson_text": "True **Quantum Error Correction (QEC)** requires linking thousands of physical qubits together to form a single, perfect 'logical qubit.' Since we don't have enough physical qubits for this yet, we use **Error Mitigation**.<br><br>Error mitigation uses classical mathematical post-processing to 'extrapolate' what the perfect, zero-noise answer would be based on noisy experiments. Techniques like *Zero Noise Extrapolation (ZNE)* run circuits under intentionally increased noise levels, allowing us to map the noise curve and subtract it. This lets us run utility-scale scientific calculations on noisy hardware today!",
            "tutorial_code": "print('Zero Noise Extrapolation (ZNE) runs circuits at multiple noise gains (e.g. 1x, 3x, 5x error),')\nprint('then extrapolates back to the theoretical zero-noise state mathematically.')\n",
            "tutor_challenge": "Why is error mitigation not the same as fault-tolerant error correction? Why is it limited to shallow or intermediate-depth circuits?"
        },
        "Hardware Execution": {
            "big_idea": "Running on IBM Quantum hardware requires backend selection, transpilation, job submission, and result analysis.",
            "composer": "Treat the composer as the circuit design surface, then export and prepare it for a backend.",
            "checkpoint": "What constraints does a real backend impose that the ideal composer hides?",
            "practice": "Prepare a backend-ready notebook using Qiskit Runtime patterns.",
            "lesson_text": "You have reached the final frontier! You are ready to run your circuits on real quantum computers in the cloud.<br><br>Running on real IBM Quantum superconducting hardware requires these exact steps:<br><ol><li><strong>Authenticate</strong>: Initialize your account using your IBM Quantum API token.</li><li><strong>Select Backend</strong>: Query the IBM service to find a device with the shortest queue and lowest error rate.</li><li><strong>Transpile</strong>: Map your custom circuit specifically to that device's physical coupling map and basis gates.</li><li><strong>Runtime Job</strong>: Submit the transpiled circuit to the IBM execution queue using Qiskit Runtime Sampler/Estimator primitives, and await your results!</li></ol><br>Congratulations on completing the pathway, Boss! You have built a solid foundation in quantum computing!",
            "tutorial_code": "print('IBM Quantum hardware authentication:')\nprint('from qiskit_ibm_runtime import QiskitRuntimeService')\nprint('# service = QiskitRuntimeService(channel=\"ibm_quantum\", token=\"YOUR_TOKEN\")')\n",
            "tutor_challenge": "What constraints does a real physical hardware chip impose that the ideal simulation environment completely hides?"
        },
    },
}


# ── Theme ──

def inject_theme():
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    @keyframes pulse-animation {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    .pulse-dot {
        animation: pulse-animation 2s infinite ease-in-out;
    }

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
        font-family: 'Space Grotesk', Inter, ui-sans-serif, system-ui, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }

    [data-testid="stSidebar"] {
        background: rgba(6, 15, 15, 0.96);
        border-right: 1px solid var(--line);
    }

    h1, h2, h3 {
        color: var(--text) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }

    p, li, label, div, span {
        color: var(--text);
    }

    /* ── Physics cards ── */
    .lab-hero {
        border: 1px solid var(--line);
        background:
            linear-gradient(145deg, rgba(10, 27, 25, 0.94), rgba(28, 23, 48, 0.86)),
            repeating-linear-gradient(90deg, rgba(101, 244, 212, 0.08) 0 1px, transparent 1px 48px);
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
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
        transition: border-color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
    }

    .physics-card:hover, .gate-card:hover {
        border-color: var(--line-strong);
        transform: translateY(-2px);
        box-shadow:
            0 22px 44px rgba(0, 0, 0, 0.31),
            0 0 20px rgba(101, 244, 212, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    .physics-card strong, .gate-card strong { color: var(--cyan); }
    .physics-card span, .gate-card span { color: var(--muted); font-size: 0.9rem; }
    .gate-card { min-height: 120px; }

    /* ── Metric strip ── */
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 14px 0 20px 0;
    }

    /* ── Timeline rows ── */
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
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Roadmap ── */
    .roadmap {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0 24px 0;
    }

    .roadmap-step {
        position: relative;
        min-height: 120px;
        border: 1px solid rgba(111, 225, 205, 0.25);
        border-radius: 8px;
        padding: 14px;
        background: linear-gradient(145deg, rgba(14, 33, 31, 0.9), rgba(23, 20, 39, 0.82));
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.25);
        transition: border-color 200ms ease, transform 200ms ease;
    }

    .roadmap-step:hover {
        border-color: var(--line-strong);
        transform: translateY(-2px);
    }

    .roadmap-step strong { color: var(--gold); display: block; font-size: 0.92rem; margin-bottom: 8px; }
    .roadmap-step span { color: var(--muted); font-size: 0.86rem; line-height: 1.45; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid var(--line-strong);
        background: rgba(101, 244, 212, 0.08);
        color: var(--text);
        min-height: 2.55rem;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        transition: all 200ms ease;
    }

    .stButton > button:hover {
        border-color: var(--cyan);
        background: rgba(101, 244, 212, 0.18);
        color: var(--text);
        box-shadow: 0 0 16px rgba(101, 244, 212, 0.15);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        color: var(--muted);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        letter-spacing: 0.02em;
        transition: color 200ms ease;
    }

    .stTabs [aria-selected="true"] {
        color: var(--cyan) !important;
        border-bottom: 2px solid var(--cyan);
    }

    /* ── Code blocks ── */
    .stCodeBlock, .stTextArea textarea {
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextArea textarea {
        background: #080e14 !important;
        color: #e9fff9 !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(145deg, rgba(12, 28, 26, 0.9), rgba(17, 18, 30, 0.85)) !important;
        margin-bottom: 8px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    /* ── Custom progress bars ── */
    .neon-bar-wrap {
        background: rgba(10, 20, 18, 0.8);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 3px;
        margin: 4px 0;
    }

    .neon-bar {
        height: 22px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        padding: 0 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        color: #0a1a19;
        transition: width 400ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    .neon-bar-cyan {
        background: linear-gradient(90deg, #65f4d4, #4db8a0);
        box-shadow: 0 0 12px rgba(101, 244, 212, 0.4);
    }

    /* ── Preset chips ── */
    .preset-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0 16px 0;
    }

    .preset-chip {
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 6px 16px;
        background: rgba(101, 244, 212, 0.06);
        color: var(--cyan);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 200ms ease;
    }

    .preset-chip:hover {
        border-color: var(--cyan);
        background: rgba(101, 244, 212, 0.14);
        box-shadow: 0 0 14px rgba(101, 244, 212, 0.15);
    }

    /* ── Lab shell ── */
    .lab-shell {
        border: 1px solid rgba(111, 225, 205, 0.24);
        border-radius: 8px;
        padding: 16px;
        background:
            linear-gradient(160deg, rgba(9, 24, 23, 0.86), rgba(19, 18, 33, 0.72)),
            repeating-linear-gradient(90deg, rgba(111, 225, 205, 0.035) 0 1px, transparent 1px 36px);
        box-shadow: 0 28px 80px rgba(0, 0, 0, 0.34);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(7, 17, 15, 0.5); }
    ::-webkit-scrollbar-thumb {
        background: rgba(101, 244, 212, 0.25);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(101, 244, 212, 0.4); }

    /* ── Responsive ── */
    @media (max-width: 900px) {
        .metric-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .roadmap { grid-template-columns: 1fr; }
    }
</style>
        """,
        unsafe_allow_html=True,
    )


# ── Session State ──

def init_session_state():
    defaults = {
        "composer_gates": [],
        "composer_last_gate": None,
        "composer_ai_feedback": "",
        "num_qubits": 2,
        "chat_history": [],
        "sandbox_code": PRESET_EXPERIMENTS["Bell State"]["code"],
        "user_gemini_api_key": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Metric Strip ──

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
                explain_composer_action(gate_name, q_idx, " → ".join(sequence))
            )
        else:
            st.markdown(st.session_state.composer_ai_feedback)


# ── Probability Bars ──

def render_probabilities(engine):
    st.markdown("#### Measurement Probabilities")
    probabilities = engine.get_probabilities()
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
<div class="physics-card">
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
<div class="roadmap-step">
    <strong>{level_name}</strong>
    <span>{module_list}</span>
</div>
            """
        )

    st.markdown(f"<div class='roadmap'>{''.join(steps)}</div>", unsafe_allow_html=True)


# ── Learn Tab ──

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

    if "lesson_text" in lesson:
        st.markdown(
            f"""
<div class="lab-hero" style="margin-top: 15px; margin-bottom: 20px;">
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
    if f"feynman_{module}" not in st.session_state:
        st.session_state[f"feynman_{module}"] = ""
        st.session_state[f"code_{module}"] = ""
        st.session_state[f"tutor_{module}"] = ""

    with st.chat_message("assistant", avatar="⚛️"):
        st.markdown("**A.C.E. Tutor**")
        st.markdown(
            f"Welcome to the **{module}** module. "
            f"{lesson['big_idea']} "
            f"Use the button below to activate the AI teaching agents, "
            f"or explore the Bloch sphere and composer on your own first."
        )

    if st.button("🚀 Generate Explanation, Code, and Checkpoint", use_container_width=True):
        import time
        
        def offline_stream(text: str):
            words = text.split(" ")
            for w in words:
                yield w + " "
                time.sleep(0.012) # Satisfying typewriter rate

        def clean_html_to_markdown(html: str) -> str:
            clean = html.replace("<br>", "\n").replace("<strong>", "**").replace("</strong>", "**")
            clean = clean.replace("<ul>", "").replace("</ul>", "").replace("<li>", "- ").replace("</li>", "\n")
            clean = clean.replace("<code>", "`").replace("</code>", "`")
            return clean

        raw_lesson = lesson.get("lesson_text", "Lesson content active.")
        lesson_md = clean_html_to_markdown(raw_lesson)
        code_md = f"Here is the physical code template for **{module}**:\n\n```python\n{lesson.get('tutorial_code', '# Code template')}\n```"
        challenge_md = f"**Diagnostic protocol online:**\n\n{lesson.get('tutor_challenge', 'Ready to test understanding.')}"

        with st.chat_message("assistant", avatar="🧠"):
            st.markdown("**Physical intuition**")
            st.session_state[f"feynman_{module}"] = st.write_stream(offline_stream(lesson_md))
        with st.chat_message("assistant", avatar="⌨️"):
            st.markdown("**Qiskit code**")
            st.session_state[f"code_{module}"] = st.write_stream(offline_stream(code_md))
        with st.chat_message("assistant", avatar="🎯"):
            st.markdown("**Socratic checkpoint**")
            st.session_state[f"tutor_{module}"] = st.write_stream(offline_stream(challenge_md))

    if st.session_state[f"feynman_{module}"]:
        with st.expander("Saved teaching output", expanded=True):
            st.markdown(st.session_state[f"feynman_{module}"])
            st.markdown(st.session_state[f"code_{module}"])
            st.markdown(st.session_state[f"tutor_{module}"])


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
    angles = engine.run_simulation()
    render_metric_strip(engine)

    # Visual circuit composer
    st.markdown("#### Visual Circuit")
    render_circuit_composer(st.session_state.composer_gates, st.session_state.num_qubits)

    controls, visual = st.columns([4, 8])
    with controls:
        render_gate_palette()
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
        if isinstance(fig, plt.Figure):
            st.pyplot(fig, clear_figure=True)
        else:
            st.image(fig)

        st.markdown("#### Qiskit Export")
        st.code(engine.get_qiskit_code(), language="python")


# ── Chat Tab ──

def render_chat():
    st.markdown("## A.C.E. Chat Console")
    st.caption("Ask anything about quantum computing. Your message is automatically routed to the right specialist agent.")

    # Check if API key is provided
    api_key_configured = st.session_state.get("user_gemini_api_key", "").strip()
    
    # Check if backend has a fallback key
    is_online = is_backend_online()
    backend_has_key = False
    if is_online:
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=0.5)
            if r.status_code == 200:
                backend_has_key = r.json().get("api_key_configured", False)
        except Exception:
            pass

    has_active_key = bool(api_key_configured or backend_has_key)

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", None)):
            if msg.get("agent_name"):
                st.markdown(f"**{msg['agent_name']}**")
            st.markdown(msg["content"])

    if not has_active_key:
        st.markdown(
            """
<div class="lab-hero" style="border: 1px solid rgba(255, 111, 145, 0.35); background: rgba(10, 26, 25, 0.85); box-shadow: 0 8px 32px rgba(255, 111, 145, 0.05); padding: 30px; text-align: center; border-radius: 12px; margin-top: 20px;">
    <span style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(255, 111, 145, 0.5));">🔒</span>
    <h3 style="color: #ff6f91 !important; margin-top: 15px; font-family: 'Space Grotesk', sans-serif;">A.C.E. Cognitive Mainframe Offline</h3>
    <p style="color: #8db8b0; font-size: 1.05rem; line-height: 1.6; max-width: 500px; margin: 10px auto;">
        Boss, the live cognitive processor is offline. While all curriculum lessons, interactive Bloch spheres, and circuit simulations are fully available <strong>100% offline &amp; API-free</strong>, dynamic doubt-clearing chat requires a Google Gemini API Key.
    </p>
    <div style="margin-top: 20px;">
        <span style="color: var(--cyan); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; border: 1px dashed rgba(101, 244, 212, 0.3); padding: 8px 16px; border-radius: 6px; background: rgba(101, 244, 212, 0.05);">
            ⚡ Configure your Gemini API Key in the sidebar to activate J.A.R.V.I.S. doubt-clearing
        </span>
    </div>
</div>
            """,
            unsafe_allow_html=True
        )
        st.chat_input("Chat locked. Please provide a Gemini API Key in the sidebar...", disabled=True)
        return

    # Chat input
    user_input = st.chat_input("Ask about quantum computing, request code, or say 'test me'...")

    if user_input:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
        })
        with st.chat_message("user"):
            st.markdown(user_input)

        # Classify and route
        intent = classify_intent(user_input)
        meta = AGENT_META.get(intent, AGENT_META["general"])
        _, response_stream = route_and_respond(user_input, intent=intent)

        with st.chat_message("assistant", avatar=meta["avatar"]):
            st.markdown(f"**{meta['name']}** · *{meta['description']}*")
            response_text = st.write_stream(response_stream)

        # Save to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "avatar": meta["avatar"],
            "agent_name": meta["name"],
            "content": response_text,
        })


# ── Sandbox Tab ──

def render_sandbox():
    st.markdown("## Qiskit Sandbox")
    st.caption("Run short Qiskit experiments locally and compare the output with the visual composer.")

    # Check if API key is provided
    api_key_configured = st.session_state.get("user_gemini_api_key", "").strip()
    is_online = is_backend_online()
    backend_has_key = False
    if is_online:
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=0.5)
            if r.status_code == 200:
                backend_has_key = r.json().get("api_key_configured", False)
        except Exception:
            pass
    has_active_key = bool(api_key_configured or backend_has_key)

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
            disabled=not has_active_key,
            help="Provide a Gemini API Key in the sidebar to enable live code explanations."
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
            from frontend.agents.base_agent import generate_stream
            explain_prompt = """
You are A.C.E., a warm and brilliant code tutor. The user has written Qiskit code.
Explain what each significant line does in plain English, referencing the quantum physics involved.
Be encouraging and address the user as 'Boss' or 'Creator'. Use markdown formatting.
Keep the explanation clear, educational, and under 300 words.
"""
            response = st.write_stream(generate_stream(explain_prompt, f"Explain this code:\n\n```python\n{notebook_code}\n```"))


def render_cognitive_core_sidebar():
    # Check if a key is provided in session state
    api_key_configured = st.session_state.get("user_gemini_api_key", "").strip()
    
    # Check if backend has a fallback key
    is_online = is_backend_online()
    backend_has_key = False
    if is_online:
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=0.5)
            if r.status_code == 200:
                backend_has_key = r.json().get("api_key_configured", False)
        except Exception:
            pass

    has_active_key = bool(api_key_configured or backend_has_key)
    
    status_color = "#65f4d4" if has_active_key else "#ff6f91"
    status_text = "ACTIVE LINK" if has_active_key else "KEY REQUIRED"
    pulse_style = f"background-color: {status_color}; box-shadow: 0 0 10px {status_color};"

    st.sidebar.markdown(
        f"""
        <div style="border: 1px solid rgba({ '101, 244, 212' if has_active_key else '255, 111, 145' }, 0.2); background: rgba(10, 26, 25, 0.85); box-shadow: 0 8px 32px rgba({ '101, 244, 212' if has_active_key else '255, 111, 145' }, 0.05); padding: 16px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.05em; color: {status_color};">COGNITIVE INTERFACE</span>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; color: {status_color}; font-weight: 700;">{status_text}</span>
                    <span class="pulse-dot" style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; {pulse_style}"></span>
                </div>
            </div>
            <p style="font-size: 0.8rem; color: #8fa09e; line-height: 1.4; margin: 0 0 12px 0;">
                Offline simulation &amp; curriculum are active. Live Socratic doubt-clearing requires a Google Gemini Key.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    user_key = st.sidebar.text_input(
        "Gemini API Key",
        value=st.session_state.get("user_gemini_api_key", ""),
        type="password",
        placeholder="AIzaSy...",
        help="Paste your Google Gemini API Key here to unlock the live AI chat assistant."
    )
    if user_key != st.session_state.get("user_gemini_api_key", ""):
        st.session_state["user_gemini_api_key"] = user_key
        st.rerun()


# ── Main ──

inject_theme()
init_session_state()

# Global cognitive core console in the sidebar
render_cognitive_core_sidebar()

render_quantum_field()

tab_learn, tab_compose, tab_chat, tab_sandbox = st.tabs(["📚 Learn", "🔬 Compose", "💬 A.C.E. Chat", "🧪 Sandbox"])

with tab_learn:
    render_curriculum()

with tab_compose:
    render_composer()

with tab_chat:
    render_chat()

with tab_sandbox:
    render_sandbox()
