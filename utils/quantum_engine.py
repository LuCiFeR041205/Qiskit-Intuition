import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

class QuantumEngine:
    def __init__(self, num_qubits=2):
        self.num_qubits = num_qubits
        self.gates = []
        
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
        
    def clear(self):
        self.gates = []
        
    def build_circuit(self):
        qc = QuantumCircuit(self.num_qubits)
        for g in self.gates:
            gate = g['gate']
            target = g['target']
            control = g['control']
            
            if gate == 'H':
                qc.h(target)
            elif gate == 'X':
                qc.x(target)
            elif gate == 'Y':
                qc.y(target)
            elif gate == 'Z':
                qc.z(target)
            elif gate == 'CNOT':
                ctrl = control if control is not None else (1 - target)
                qc.cx(ctrl, target)
        return qc
        
    def run_simulation(self):
        qc = self.build_circuit()
        sv = Statevector.from_instruction(qc)
        
        angles = {}
        for q in [0, 1]:
            if q >= self.num_qubits:
                continue
            traced_qubits = [i for i in range(self.num_qubits) if i != q]
            rho = partial_trace(sv, traced_qubits)
            
            data = rho.data
            x = float(2.0 * data[0, 1].real)
            y = float(2.0 * data[1, 0].imag)
            z = float((data[0, 0] - data[1, 1]).real)
            
            r = np.sqrt(x**2 + y**2 + z**2)
            if r < 1e-9:
                theta = 0.0
                phi = 0.0
            else:
                z_norm = np.clip(z / r, -1.0, 1.0)
                theta = np.arccos(z_norm)
                phi = np.arctan2(y, x)
                if phi < 0:
                    phi += 2 * np.pi
                    
            angles[q] = {
                'theta': float(theta),
                'phi': float(phi),
                'x': float(x),
                'y': float(y),
                'z': float(z)
            }
        return angles
        
    def get_circuit_figure(self):
        qc = self.build_circuit()
        dark_style = {
            "backgroundcolor": "#050A15",
            "textcolor": "#00F0FF",
            "linecolor": "#00F0FF",
            "gatetextcolor": "#050A15",
            "gatefacecolor": "#00F0FF",
            "barrierfacecolor": "#1A2536",
            "creglinecolor": "#4DB8FF",
        }
        fig = qc.draw(output='mpl', style=dark_style)
        return fig
