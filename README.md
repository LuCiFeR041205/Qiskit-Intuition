---
title: Qiskit Intuition
emoji: ⚛️
colorFrom: blue
colorTo: purple
sdk: streamlit
app_file: app.py
pinned: false
---

# Qiskit Intuition Lab ⚛️

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Qiskit](https://img.shields.io/badge/Qiskit-%E2%89%A51.0-blue)](https://qiskit.org/)

**Note: This is an experimental project in active development.** We encourage anyone interested in quantum computing, frontend development, or AI agents to contribute.

This project makes quantum education **intuitive**. It is an immersive, physics-first quantum learning workspace: a Streamlit frontend for building circuits visually and watching qubits move in 3D, backed by a decoupled FastAPI service for simulation, code execution, and offline teaching helpers.

## Architecture (CPRE)

The app follows a **Composer → Physics → Readout → Explain** flow, decoupled into a frontend and a backend:

- **Frontend (`frontend/streamlit_app.py`)** — Streamlit UI: gate palette, circuit composer, Bloch spheres, probability bars, curriculum roadmap, AI teaching lab, and the Quantum Quests tab.
- **Backend (`backend/`, FastAPI)** — `core/quantum_engine.py` (Qiskit statevector + noise simulation, Bloch angles, Qiskit export), `core/quest_engine.py` (quest targets + fidelity grading), `core/notebook_engine.py` (sandboxed code execution), and routers for `/simulate`, `/execute`, and `/agent/*`.
- **Educational agents (`agents/`, `frontend/agents/`)** — offline tutor, Feynman explainer, code generator, and Socratic checker. No hosted model key required for the public app.

## Features

- **3D quantum field interface:** a physics-inspired Three.js scene frames the app as an interactive quantum lab.
- **Composer-style circuit builder:** add H, X, Y, Z, S, T, CNOT, Rx, Ry, Rz across multiple qubits.
- **Live Bloch sphere visualization:** each qubit gets an interactive 3D Bloch sphere with coordinates, phase angles, and purity readouts.
- **Measurement probabilities:** basis-state probabilities update as the circuit changes (with optional noisy simulation).
- **Qiskit export:** every visual circuit exports as runnable Qiskit code.
- **Quantum Quests:** graded challenges where the learner builds a circuit and the app checks fidelity against a target state.
- **Sandbox notebook:** run short Qiskit/Python experiments and capture stdout plus Matplotlib figures.
- **Offline AI teaching agents:** tutor, code explainer, and Socratic checkpoint helpers.

## Local Setup

Use Python 3.10+.

```bash
git clone https://github.com/LuCiFeR041205/Qiskit-Intuition.git
cd Qiskit-Intuition

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Frontend (Streamlit UI)
streamlit run app.py --server.port 8502

# Backend API (optional, in another terminal)
uvicorn backend.main:app --reload --port 8000
```

Open [http://localhost:8502](http://localhost:8502). The backend serves `/health`, `/simulate`, `/execute`, and `/agent/*` on port 8000.

## Testing

```bash
pytest tests/ -v
```

Tests cover the backend engine (probabilities, Bloch purity, Qiskit export), the sandbox execution core, and the quest grading (every quest target is reachable and unit-norm).

## Project Structure

```text
app.py                              Entry point: launches frontend/streamlit_app.py
backend/
  main.py                           FastAPI app + CORS
  core/
    quantum_engine.py               Qiskit simulation, Bloch angles, export
    quest_engine.py                 Quest targets + fidelity grading
    notebook_engine.py              Sandboxed code execution
  routers/                          simulate, execute, agents
frontend/
  streamlit_app.py                  Streamlit UI (composer, Bloch, quests, teaching lab)
  components/                       bloch_sphere, circuit_composer, quantum_field, ...
agents/  frontend/agents/           Offline teaching helpers
tests/                             Pytest suites for engine, notebook, quests
```

## Notes

The UI prioritizes physical intuition first, then connects every visual action back to runnable Qiskit code.

**The secondary 'Qiskit-Intuition' folder is for Hugging-Faces only, and just meant to keep the site running. Please don't edit it.**
