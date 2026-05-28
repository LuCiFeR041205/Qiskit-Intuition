import sys
sys.path.append("/Users/dhruvsachdeva/.gemini/antigravity/scratch/Qiskit-Intuition")
from backend.core.quantum_engine import QuantumEngine

eng = QuantumEngine(num_qubits=2)
eng.add_h(0)
eng.add_cnot(0, 1)

print("Perfect:")
print(eng.get_probabilities(noisy=False))

print("Noisy:")
print(eng.get_probabilities(noisy=True))
