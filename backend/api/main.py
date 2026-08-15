from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import numpy as np

# Adjust path to allow imports from backend.core if run directly
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.core.quantum_engine import QuantumEngine
from backend.core.quest_engine import get_quests, calculate_fidelity

from pydantic import BaseModel, Field

app = FastAPI(title="Qiskit Intuition API", description="Offline Quantum Physics Engine API")

# CORS - Restrict to trusted local origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class GateOperation(BaseModel):
    gate: str
    target: int = Field(ge=0, le=9)
    control: Optional[int] = Field(default=None, ge=0, le=9)
    angle: Optional[float] = None

class SimulationRequest(BaseModel):
    num_qubits: int = Field(default=2, ge=1, le=10)
    gates: List[GateOperation] = Field(..., max_length=100)
    noisy: bool = False

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Quantum Engine is online"}

@app.get("/api/quests")
async def fetch_quests():
    """Returns the list of available quantum quests."""
    return {"quests": get_quests()}

@app.post("/api/simulate")
async def simulate_circuit(request: SimulationRequest):
    """
    Executes a sequence of quantum gates and returns the resulting
    statevector (if not noisy) or probabilities, along with Bloch sphere angles.
    """
    try:
        engine = QuantumEngine(num_qubits=request.num_qubits)
        for g in request.gates:
            if g.gate.upper() == 'CNOT':
                engine.add_cnot(g.control, g.target)
            elif g.gate.upper() in ['RX', 'RY', 'RZ']:
                engine.add_rotation(g.gate, g.target, g.angle if g.angle else np.pi/2)
            else:
                engine.add_gate(g.gate, g.target)
        
        # Run simulation
        angles = engine.run_simulation(noisy=request.noisy)
        probabilities = engine.get_probabilities(noisy=request.noisy)
        
        # Statevector can't be easily JSON serialized if complex, so we convert it
        statevector = None
        if not request.noisy:
            sv = engine._last_simulation
            if sv is not None:
                # Convert complex numbers to strings or dicts
                statevector = [{"real": float(c.real), "imag": float(c.imag)} for c in sv]

        return {
            "success": True,
            "angles": angles,
            "probabilities": probabilities,
            "statevector": statevector
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fidelity")
async def check_fidelity(request: SimulationRequest, target_state: List[float]):
    """
    Run simulation and check fidelity against a target state vector.
    """
    try:
        engine = QuantumEngine(num_qubits=request.num_qubits)
        for g in request.gates:
            if g.gate.upper() == 'CNOT':
                engine.add_cnot(g.control, g.target)
            else:
                engine.add_gate(g.gate, g.target)
        
        engine.run_simulation(noisy=False)
        current_state = engine._last_simulation
        
        if current_state is None:
            return {"fidelity": 0.0}
            
        fidelity = calculate_fidelity(current_state, target_state)
        return {"fidelity": float(fidelity)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
