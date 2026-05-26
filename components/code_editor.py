import streamlit as st
import streamlit.components.v1 as components


PRESET_EXPERIMENTS = {
    "Bell State": {
        "description": "Create an entangled pair — the foundation of quantum information.",
        "code": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

sv = Statevector.from_instruction(qc)
print("Bell State |Φ+⟩:")
print(sv)
print()
print(qc)
fig = qc.draw(output='mpl')
""",
    },
    "GHZ State": {
        "description": "Three-qubit entanglement — if one collapses, all three agree.",
        "code": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)

sv = Statevector.from_instruction(qc)
print("GHZ State:")
print(sv)
print()
print(qc)
fig = qc.draw(output='mpl')
""",
    },
    "Teleportation": {
        "description": "Transfer a quantum state using entanglement and classical bits.",
        "code": """from qiskit import QuantumCircuit

qc = QuantumCircuit(3, 2)

# Prepare the state to teleport on q0
qc.rx(1.2, 0)
qc.barrier()

# Create Bell pair between q1 and q2
qc.h(1)
qc.cx(1, 2)
qc.barrier()

# Alice's operations
qc.cx(0, 1)
qc.h(0)
qc.barrier()

# Measure Alice's qubits into classical bits
qc.measure(0, 0)
qc.measure(1, 1)
qc.barrier()

# Bob's classically-conditioned corrections:
# If classical bit 1 (Alice's q1 measurement) is 1 → apply X to q2
# If classical bit 0 (Alice's q0 measurement) is 1 → apply Z to q2
# Note: In Qiskit 1.0+ deferred (dynamic) circuits, use .c_if:
with qc.if_test((1, 1)):
    qc.x(2)
with qc.if_test((0, 1)):
    qc.z(2)

print("Quantum Teleportation Circuit:")
print("Bob's corrections are classically conditioned on Alice's measurements.")
print()
print(qc)
fig = qc.draw(output='mpl')
""",
    },
    "Grover 2-bit": {
        "description": "Search for |11⟩ among 4 possibilities — quantum speedup in action.",
        "code": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(2)

# Uniform superposition
qc.h([0, 1])

# Oracle: mark |11⟩
qc.cz(0, 1)

# Diffuser
qc.h([0, 1])
qc.z([0, 1])
qc.cz(0, 1)
qc.h([0, 1])

sv = Statevector.from_instruction(qc)
print("Grover search — amplified |11⟩:")
print(sv)
probs = sv.probabilities_dict()
for state, prob in sorted(probs.items()):
    print(f"  |{state}⟩  {prob*100:.1f}%")
print()
print(qc)
fig = qc.draw(output='mpl')
""",
    },
    "Random Walk": {
        "description": "Quantum walk on 3 qubits — interference shapes the probability landscape.",
        "code": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(3)

# Three steps of a quantum walk
for step in range(3):
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.barrier()

sv = Statevector.from_instruction(qc)
print("Quantum Random Walk (3 steps):")
probs = sv.probabilities_dict()
for state, prob in sorted(probs.items()):
    if prob > 0.001:
        bar = "█" * int(prob * 40)
        print(f"  |{state}⟩  {prob*100:5.1f}%  {bar}")
print()
print(qc)
fig = qc.draw(output='mpl')
""",
    },
}


def render_sandbox_header():
    """Renders a terminal-style header bar above the code editor."""
    html = """
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
  .term-bar {
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(90deg, #080e14, #0c1520);
    border: 1px solid rgba(101,244,212,0.2);
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 0 14px;
    height: 38px;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
  }
  .dots { display: flex; gap: 7px; align-items: center; }
  .dot { width: 10px; height: 10px; border-radius: 50%; }
  .d-r { background: #ff5f57; }
  .d-y { background: #febc2e; }
  .d-g { background: #28c840; }
  .fname { color: #8db8b0; font-size: 12px; letter-spacing: 0.03em; }
  .badge {
    color: #65f4d4; font-size: 9px; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    border: 1px solid rgba(101,244,212,0.35);
    padding: 2px 10px; border-radius: 3px;
    background: rgba(101,244,212,0.06);
  }
</style>
<div class="term-bar">
  <div class="dots"><div class="dot d-r"></div><div class="dot d-y"></div><div class="dot d-g"></div></div>
  <div class="fname">quantum_experiment.py</div>
  <div class="badge">SANDBOX</div>
</div>
"""
    components.html(html, height=42, scrolling=False)
