---
title: Qiskit Intuition
emoji: ⚛️
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: app.py
pinned: false
---

# Qiskit Intuition

Qiskit Intuition teaches quantum computing and Qiskit from zero, **intuition first**. Every lesson follows the same loop:

1. **Intuition** — a plain-language picture plus an interactive widget: a 3D Bloch sphere you can grab and turn, a shot sampler, interference phasors, measurement bases, an entanglement sampler, a teleportation walkthrough, a phase-kickback black box, a Grover amplifier, live transpiler routing, and noise and training simulators.
2. **Predict** — a multiple-choice prediction with feedback on every option.
3. **Experiment** — the worked circuit in a guided builder with per-qubit Bloch spheres.
4. **Formalize** — the math, once the picture exists.
5. **Code it** — the Qiskit API for the idea, then an auto-checked coding exercise.
6. **Reflect** — explain the result in your own words, with optional coach feedback.

The project includes a Streamlit app for Hugging Face Spaces and a separate Next.js client. Both work without a hosted model or external simulator.

## Curriculum

| Unit | Lessons |
| --- | --- |
| One qubit | What is a qubit? · Flipping with X · Measurement and shots · Superposition with H · Rotations · Phase · Interference · Measuring in other directions |
| Many qubits | Many qubits and bit order · Entanglement · Teleportation |
| Algorithms | Phase kickback: Deutsch's algorithm · Grover search |
| Real hardware & beyond | Noise and transpilation · Running on a real chip · Trainable circuits and quantum ML |

## Public learning experience

- **Course map:** units, progress, a resume button, and a glossary that gives each term's picture and precise definition.
- **Your notebook, kept:** progress, predictions, margin notes, explanations and exercise code save automatically in the browser (localStorage — nothing is sent to a server) and restore on the next visit. The **My notebook** page collects everything you've written and downloads it as JSON (to restore later) or as a Markdown write-up.
- **Playground:** an open workspace that switches between the visual circuit builder and the sandboxed Qiskit code runner without affecting course progress.
- **Code coach:** context-aware help receives the current lesson, circuit, code, and latest traceback.
- **Transfer challenges:** optional circuit targets open in the playground for extra practice.
- **Content Studio:** author controls stay outside the learner navigation and export/import one publishable content file.

## Hugging Face Spaces

The repository root is a ready-to-run Streamlit Space. Simulation, safe code execution, and the built-in teaching engine all run in the same process, so Spaces does not need a second API service.

To deploy:

1. Create a Streamlit Space.
2. Push this repository to the Space.
3. The Space reads the YAML metadata above and starts `app.py`.

For optional model-enhanced tutoring, add `GEMINI_API_KEY` as a private Space secret. Without it, the deterministic code-aware coach remains available. `GEMINI_MODEL` can override the default model name.

## Editing course content

Open **Content studio** in the Streamlit navigation. Changes preview immediately for the current session.

To publish changes permanently:

1. Download `site_content.json` from Content Studio.
2. Replace `frontend/site_content.json` in the repository.
3. Commit and push the file to the Space or main repository.

This design keeps public visitors from modifying deployed course content.

## Run locally

Use Python 3.10 or newer:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The optional FastAPI service exposes simulation, execution, and tutor endpoints:

```bash
uvicorn backend.main:app --reload --port 8000
```

## Standalone web client

The `web` directory contains a lightweight Next.js version of the same course and circuit flow.

```bash
cd web
npm install
npm run dev
```

The web simulator runs entirely in the browser. To connect its Code Coach to the Python tutor API, set:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Hugging Face Space origins are accepted by the API. Additional deployments can be added with the comma-separated `ALLOWED_ORIGINS` environment variable.

## Tests

```bash
ruff check .
pytest tests -q
node web/tests/simulator.test.mjs
cd web && npm run build
```

The suite covers quantum probabilities and statevectors, quest fidelity, sandbox safety and escape attempts, code-review diagnostics, tutor context, the browser-side simulator, and the curriculum itself: every worked example must run and every exercise's reference solution must pass its checker. CI runs all of these on pushes and pull requests.

## Project structure

```text
app.py                              Streamlit / Hugging Face entry point
frontend/streamlit_app.py           Public learning interface
frontend/learning_content.py        Curriculum, presets, practice, glossary
frontend/intuition.py               Interactive intuition widgets and SVG visuals
frontend/bloch3d.py                 Draggable ink-style 3D Bloch sphere (runs in the browser)
frontend/notebook_store.py          Save/restore the learner's notebook (browser storage + file)
frontend/notebook_storage/          Tiny HTML component that talks to localStorage
static/fonts/                       Self-hosted notebook fonts (SIL Open Font License)
frontend/site_content.json          Editable published content configuration
backend/core/quantum_engine.py      Qiskit simulation and export
backend/core/notebook_engine.py     Restricted teaching sandbox (allowlist + isolated process)
backend/core/exercise_checker.py    Auto-checks learner Qiskit code against a reference
backend/core/qiskit_thread.py       Runs in-app Qiskit work on one thread (avoids a Rust-extension crash)
backend/core/teaching_assistant.py  Code review, tutoring, and optional model path
backend/routers/agents.py           Tutor and compatibility endpoints
web/                                Standalone Next.js learning client
tests/                              Python integration and unit tests
```
