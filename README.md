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

Qiskit Intuition is a focused quantum-computing course built around one continuous learning loop:

1. Learn a precise concept.
2. Predict what a circuit will do.
3. Run and modify the worked circuit in the lesson.
4. Explain the result using the state or probabilities as evidence.
5. Continue to the next lesson, with targeted code help available in context.

The project includes a Streamlit app for Hugging Face Spaces and a separate Next.js client. Both work without a hosted model or external simulator.

## Public learning experience

- **Learning path:** each lesson keeps the concept, prediction, experiment, explanation, and completion step in one guided sequence.
- **In-lesson experiment:** a focused circuit builder, probability view, exact state, and matching Qiskit code appear only after the learner makes a prediction.
- **Playground:** an optional open workspace switches between the visual circuit builder and restricted Qiskit code runner without affecting course progress.
- **Code coach:** context-aware help receives the current lesson, circuit, code, and latest traceback. It detects common Qiskit 1.x migration issues and explains real code line by line.
- **Transfer challenges:** optional circuit targets move into the playground when a learner wants more practice.
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
pytest tests -q
node web/tests/simulator.test.mjs
cd web && npm run build
```

The suite covers quantum probabilities and statevectors, quest fidelity, sandbox safety, code-review diagnostics, tutor context, and the browser-side simulator.

## Project structure

```text
app.py                              Streamlit / Hugging Face entry point
frontend/streamlit_app.py           Public learning interface
frontend/learning_content.py        Default curriculum and practice data
frontend/site_content.json          Editable published content configuration
backend/core/quantum_engine.py      Qiskit simulation and export
backend/core/notebook_engine.py     Restricted teaching sandbox
backend/core/teaching_assistant.py  Code review, tutoring, and optional model path
backend/routers/agents.py           Tutor and compatibility endpoints
web/                                Standalone Next.js learning client
tests/                              Python integration and unit tests
```
