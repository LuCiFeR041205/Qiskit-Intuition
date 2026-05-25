# Contributing to Stark Quantum Console

Thank you for choosing to contribute to the **Stark Quantum Console**! We are committed to making quantum computing education intuitive, physical, and accessible to everyone. By contributing, you help shape a premium learning framework.

---

## 🚀 How to Contribute

### 1. Adding New Modules to the Curriculum
Our curriculum is segmented into four distinct authorization levels. If you want to add modules:
1. Update the sidebar database selection inside `app.py`.
2. Implement the corresponding curriculum protocols under the selected level.
3. Configure the **A.C.E.** AI system guide prompts inside `agents/feynman_agent.py` to support the new topic.

### 2. Enhancing 3D Projections
The interactive Bloch sphere runs inside `components/bloch_sphere.py` using CDN-loaded **Three.js**. If you want to add visual HUD details (such as vector tracers, phase rotation paths, or dual-entanglement beams):
1. Modify the raw HTML template inside `bloch_sphere.py`.
2. Hook up any new parameters to receive variables dynamically from the backend state simulator.

### 3. Improving the Composer and Sandbox
The gate engines and notebook execution live in `/utils/`.
- Ensure all Qiskit codes compiled by `quantum_engine.py` use the latest stable **Qiskit 1.0+** syntax.
- All code executed inside the Notebook Sandbox (`notebook_engine.py`) must be executed safely, closing all generated matplotlib figures locally to avoid memory leaks.

---

## 🎨 Design Guidelines
Maintain the high-fidelity **Stark HUD** theme in any CSS modifications:
- Backgrounds: Extremely dark blue/black (`#050A15`, `#02060D`).
- Foreground/Accents: Monospace typography, glowing cyan (`#00F0FF`), glowing hot pink (`#ff0055`) for vectors, and deep indigo (`#2D1A3B`) for diagnostics.
- Keep comments inside the Qiskit engine to a minimum. All conceptual explanations must be handled dynamically by the warm AI dialogue terminal.

---

## 🛡️ Code of Conduct
We support a warm, welcoming, and encouraging environment. Treat all collaborators with respect, just as A.C.E. treats Mr. Stark!
