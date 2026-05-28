from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ..core.quantum_engine import QuantumEngine

router = APIRouter()

class GateModel(BaseModel):
    gate: str
    target: int
    control: Optional[int] = None
    angle: Optional[float] = None

class SimulateRequest(BaseModel):
    gates: List[GateModel]
    num_qubits: int
    noisy: bool = False

def fig_to_base64(fig):
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str
    except Exception:
        return ""

@router.post("/simulate")
async def simulate(req: SimulateRequest):
    try:
        engine = QuantumEngine(num_qubits=req.num_qubits)
        for g in req.gates:
            gate_dict = {
                'gate': g.gate,
                'target': g.target,
                'control': g.control
            }
            if g.angle is not None:
                gate_dict['angle'] = g.angle
            engine.gates.append(gate_dict)
        
        sv = engine.get_statevector()
        bloch_angles = engine.run_simulation()
        probabilities = engine.get_probabilities(noisy=req.noisy)
        
        # Capture circuit figure
        fig = engine.get_circuit_figure()
        fig_b64 = fig_to_base64(fig)
            
        sv_list = [str(c) for c in sv.data]
        
        return {
            "statevector": sv_list,
            "bloch_angles": bloch_angles,
            "probabilities": probabilities,
            "circuit_figure": fig_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_circuit(req: SimulateRequest):
    try:
        engine = QuantumEngine(num_qubits=req.num_qubits)
        for g in req.gates:
            gate_dict = {
                'gate': g.gate,
                'target': g.target,
                'control': g.control
            }
            if g.angle is not None:
                gate_dict['angle'] = g.angle
            engine.gates.append(gate_dict)
        return {
            "code": engine.get_qiskit_code()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
