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

**Note: This is an entirely new, experimental project in its early stages.** 
We know it needs massive improvement, and we highly encourage anyone interested in quantum computing, frontend development, or AI agents to jump in and contribute!

This project is an effort to make quantum education deeply **intuitive**. It is an immersive, physics-first quantum learning workspace built with Streamlit, Qiskit, and a 3D interface.

Our goal is to make Qiskit feel learnable from first principles: learners can build circuits visually, watch qubits move in 3D, inspect measurement probabilities, and progress from basic gates to advanced hardware workflows with the help of sophisticated AI tutors.

## Features

- **3D quantum field interface:** A physics-inspired Three.js scene frames the app as an interactive quantum lab.
- **Composer-style circuit builder:** Add H, X, Y, Z, S, T, CNOT, Rx, Ry, and Rz gates across multiple qubits.
- **Live Bloch sphere visualization:** Each qubit gets an interactive 3D Bloch sphere with coordinates, phase angles, and purity readouts.
- **Measurement probabilities:** See basis-state probabilities update as the circuit changes.
- **Qiskit export:** Every visual circuit can be copied as runnable Qiskit code.
- **Curriculum from basic to advanced:** Lessons now span setup, quantum foundations, circuit skills, simulation, noise, algorithms, primitives, mitigation, and hardware execution.
- **Sandbox notebook:** Run short Qiskit/Python experiments and capture stdout plus Matplotlib figures.
- **AI teaching agents:** Optional Gemini-powered tutor, code generator, and Socratic checkpoint helpers.

## Learning Path

1. **Level 0: Python + Qiskit Setup**
   Python for circuits, Qiskit objects, circuit drawing, and statevector inspection.

2. **Level 1: Quantum Foundations**
   Qubits, superposition, measurement, and entanglement using Bloch-sphere intuition.

3. **Level 2: Circuit Composer Skills**
   Gate algebra, phase kickback, controlled gates, and parameterized rotations.

4. **Level 3: Simulation + Noise**
   Statevectors versus shots, noisy simulation, and transpilation.

5. **Level 4: Quantum Algorithms**
   Grover search, QFT, and VQE.

6. **Level 5: Hardware + Advanced Workflows**
   Qiskit primitives, error mitigation, and IBM Quantum hardware execution patterns.

## Local Setup

Use Python 3.10+.

```bash
git clone https://github.com/LuCiFeR041205/Qiskit-Intuition.git
cd Qiskit-Intuition

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502) or [http://127.0.0.1:8502](http://127.0.0.1:8502).

## Optional AI Tutor Setup

The app runs without an AI key for the visual composer and sandbox. To enable the Gemini-powered teaching agents, add:

```bash
GEMINI_API_KEY=your_actual_api_key
```

to a local `.env` file.

## Project Structure

```text
app.py                         Main Streamlit application
components/bloch_sphere.py     Interactive 3D Bloch sphere
components/quantum_field.py    3D physics-inspired hero scene
utils/quantum_engine.py        Qiskit circuit simulation and export
utils/notebook_engine.py       Local sandbox execution
agents/                        Optional AI teaching agents
```

## Notes

This project is intentionally learner-facing. The UI prioritizes physical intuition first, then connects every visual action back to runnable Qiskit code.

The secondary 'Qiskit-Intuition' folder is for Hugging-Faces only, and just meant to keep the site running. Please don't edit it.
