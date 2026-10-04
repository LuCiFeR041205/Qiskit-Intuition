# Contributing to Qiskit Intuition

Qiskit Intuition teaches quantum computing **intuition first**: every idea starts as a picture the learner can play with, becomes a prediction they test, and only then turns into math and Qiskit code.

## Adding or editing a lesson

Lessons live in `frontend/learning_content.py` as plain dictionaries. Each lesson moves through six stages, and each stage reads specific fields:

| Stage | Fields |
| --- | --- |
| 1. Intuition | `intuition` (plain-language paragraphs, `**bold**` allowed), `widget` (interactive "feel it" widget) |
| 2. Predict | `quiz` — `question`, `options`, `answer` (index), and one `explanations` entry per option |
| 3. Experiment | `preset` (a key of `PRESETS`), `try_this`, optional `noise_toggle` |
| 4. Formalize | `explanation`, `latex`, `misconception` |
| 5. Code it | `qiskit` (`intro`, runnable `code`, line-by-line `notes`) and `code_task` |
| 6. Reflect | `checkpoint`, `practice` (index into `PRACTICE`) |

Guidelines:

- **Picture before formula.** The intuition stage should be understandable without any equations.
- **Wrong answers teach.** Every quiz option needs an explanation of why it is tempting or wrong.
- **One new Qiskit idea per lesson.** The worked example should introduce a single API and run in the sandbox.
- **Auto-checked exercises.** A `code_task` has a `starter`, a reference `solution` that leaves its circuit in `qc`, an optional `match` (`"state"` compares up to global phase, `"probs"` compares the measurement distribution), and optional `required_ops` (e.g. `["h", "cx"]`).

Widgets are implemented in `frontend/intuition.py` (`bloch_dial`, `gate_play`, `shots`, `interference`, `basis_measure`, `bit_order`, `entangle`, `teleport`, `deutsch`, `grover`, `noise`, `routing`, `variational`). They are Python plus inline SVG; the draggable 3D sphere in `frontend/bloch3d.py` is plain HTML/JS. No front-end build step is needed. Lesson numbers come from their position in `LESSONS`, so you can insert a lesson anywhere.

## Running Qiskit inside the app

Streamlit runs each rerun on a fresh thread, and Qiskit's Rust extension can segfault when used that way. Any Qiskit call made in the app process must go through `@on_qiskit_thread` (`backend/core/qiskit_thread.py`), and should return plain Python, NumPy or Matplotlib objects. `tests/test_app_smoke.py` reruns every lesson stage to catch regressions.

## Code sandbox

Learner code runs through `backend/core/notebook_engine.py`: an AST check (import allowlist, no dunder or module-escape attributes, no file writes), then a fresh Python process with a timeout. Keep new lesson code inside the allowlisted modules (Qiskit, Qiskit Aer, NumPy, Matplotlib, and small stdlib helpers).

## Before opening a pull request

```bash
ruff check .
pytest tests -q
node web/tests/simulator.test.mjs
```

`tests/test_curriculum.py` runs every worked example and checks that each exercise's reference solution passes while its starter code does not, so a broken lesson fails the suite.
