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

**Learn quantum computing and Qiskit from zero, intuition first, in a paper lab notebook.**

**▶ Try it:** [huggingface.co/spaces/j76dvyt4q5-cyber/Qiskit-Intuition](https://huggingface.co/spaces/j76dvyt4q5-cyber/Qiskit-Intuition). It works on laptops, tablets and phones, with no sign-up or API key.

Most quantum courses open with linear algebra. This one opens with a picture you can grab and turn. Each idea becomes a prediction you test, then an experiment, and only then the math and the Qiskit code.

## How every lesson works

| Step | What you do |
| --- | --- |
| 1. **Intuition** | Play with an interactive picture: a 3D Bloch sphere you can drag, a shot sampler, interference phasors, an entanglement sampler, a Grover amplifier, live transpiler routing and more. |
| 2. **Predict** | Commit to an answer. Every option, right or wrong, explains why it is tempting. |
| 3. **Experiment** | Build the circuit in a guided builder and watch each qubit's Bloch sphere. |
| 4. **Formalize** | Learn the math, now that the picture exists. |
| 5. **Code it** | Read the Qiskit API line by line, then solve an exercise that is checked automatically. |
| 6. **Reflect** | Explain the result in your own words and get instant feedback on what you covered and what you missed. |

## Curriculum

| Unit | Lessons |
| --- | --- |
| One qubit | What is a qubit? · Flipping with X · Measurement and shots · Superposition with H · Rotations · Phase · Interference · Measuring in other directions |
| Many qubits | Many qubits and bit order · Entanglement · Teleportation |
| Algorithms | Phase kickback: Deutsch's algorithm · Grover search |
| Real hardware & beyond | Noise and transpilation · Running on a real chip · Trainable circuits and quantum ML |

## Features

- **A notebook that remembers.** Progress, predictions, margin notes, explanations and exercise code save automatically in your browser and come back on your next visit. Nothing is sent to a server. **My notebook** collects everything you wrote; download it as JSON to restore later, or as a Markdown write-up.
- **Auto-checked Qiskit exercises.** Your code runs in a sandbox: an import allowlist plus an isolated process with time and memory limits. Its circuit is compared with a reference solution by state fidelity or by measurement distribution.
- **Instant feedback on explanations.** "Check my reasoning" compares what you wrote with each lesson's key ideas and common misconceptions. It works offline. With `GEMINI_API_KEY` set, an AI model adds notes.
- **Playground.** A free circuit builder and Qiskit code runner with a code coach, plus practice challenges. Nothing there affects course progress.
- **Glossary.** Every term with its picture and its precise definition.
- **Built for every screen.** On phones the sidebar tucks away and page tabs take its place, and the 3D sphere works with touch.
- **Easy to read.** A sidebar switch swaps the handwriting for Atkinson Hyperlegible, a font designed for low-vision readers, and straightens tilted notes. Colours meet WCAG AA contrast.
- **Feedback button on every page.** Testers can report what confused them, what broke or what they liked. Each report becomes a GitHub issue tagged with the page, lesson and step.
- **Content Studio.** Course authors can edit every part of a lesson in plain text: intuition, widget, quiz, worked circuit, math, Qiskit example, exercise and reflection rubric. To open it, go to the sidebar → **Course author**. Saving checks the lesson, runs the example and confirms the exercise's solution passes.

## Run locally

Python 3.10 or newer:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501.

## Configuration

Everything is optional. On Hugging Face, add these as **Space secrets**. Locally, put them in a `.env` file.

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Adds AI notes to the Reflect feedback and the code coach. Without it, the built-in feedback and coach still work. |
| `GEMINI_MODEL` | Overrides the default Gemini model name. |
| `FEEDBACK_GITHUB_TOKEN` | A fine-grained GitHub token with **Issues: write** on this repository. It lets the feedback button file issues directly. Without it, testers get a pre-filled issue link to submit themselves. |
| `FEEDBACK_GITHUB_REPO` | Where feedback goes (`owner/name`). Defaults to this repository. |
| `ALLOWED_ORIGINS` | Extra CORS origins for the optional FastAPI service, comma-separated. |

## Deployment

Every push to `main` runs CI. It also uploads the app to the Hugging Face Space through `.github/workflows/sync-to-huggingface.yml`, which needs an `HF_TOKEN` repository secret with write access to the Space. The Space reads the YAML header at the top of this file and starts `app.py`.

## Editing course content

Changes made in the Content Studio apply to your session straight away. To publish them for everyone:

1. Download `site_content.json` from the Content Studio.
2. Replace `frontend/site_content.json` with it.
3. Commit and push. The Space redeploys automatically.

Visitors can't change the live course. See [CONTRIBUTING.md](CONTRIBUTING.md) for the lesson format and how to write lessons directly in Python.

## Tests

```bash
ruff check .
pytest tests -q
```

The tests check the quantum engine, the sandbox (including escape attempts), the exercise checker, the explanation reviewer, Content Studio parsing, notebook save and restore, and feedback filing. They also cover the curriculum: every worked example must run, and every exercise's reference solution must pass while its starter code fails. A smoke test clicks through every stage of every lesson. CI runs everything on each push and pull request.

## Known limits

- Progress is stored per browser. Clearing site data or switching devices starts a fresh notebook, unless you download your notebook first and restore it.
- On the free Hugging Face tier, the Space sleeps when idle, so the first visit afterwards can take about 30 seconds.
- Circuits run on a simulator. The hardware lessons simulate a real chip's layout and noise instead of sending jobs to IBM Quantum.

## Project structure

```text
app.py                               Streamlit / Hugging Face entry point
frontend/streamlit_app.py            The learning app: pages, lesson steps, Content Studio
frontend/learning_content.py         Curriculum, rubrics, presets, practice, glossary
frontend/intuition.py                Interactive intuition widgets and SVG visuals
frontend/bloch3d.py                  Draggable 3D Bloch sphere (runs in the browser)
frontend/lesson_editing.py           Plain-text lesson formats for the Content Studio
frontend/notebook_store.py           Save/restore the learner's notebook
frontend/notebook_storage/           Tiny HTML component that talks to localStorage
frontend/education_theme.py          The paper-notebook look
frontend/site_content.json           Published content overrides
static/fonts/                        Self-hosted fonts (SIL Open Font License)
backend/core/quantum_engine.py       Qiskit simulation, noise and export
backend/core/notebook_engine.py      Code sandbox (allowlist + isolated process)
backend/core/exercise_checker.py     Auto-checks learner code against a reference
backend/core/explanation_review.py   Instant feedback on written explanations
backend/core/feedback.py             Files tester feedback as GitHub issues
backend/core/qiskit_thread.py        Runs in-app Qiskit work on one thread
backend/core/teaching_assistant.py   Code review and tutoring
backend/main.py, backend/routers/    Optional FastAPI service (simulation, execution, tutor)
web/                                 Older standalone Next.js client (not deployed)
tests/                               Python tests
```

The optional API runs with `uvicorn backend.main:app --reload --port 8000`. The older Next.js client in `web/` runs with `npm install && npm run dev` from that folder.

## Licence

MIT. See [LICENSE](LICENSE). The fonts in `static/fonts/` are under the SIL Open Font License.
