"""Public learning experience for Qiskit Intuition.

The app runs as a single Streamlit process on Hugging Face Spaces. Simulation,
safe code execution, and tutoring all have in-process paths, so a separate API
server is optional rather than required.

Every lesson follows one loop: Intuition -> Predict -> Experiment ->
Formalize -> Code it -> Reflect. Pictures and interaction come before
equations, and every idea ends as runnable Qiskit code.
"""

from __future__ import annotations

import html
import json
import math
import os
import re
from copy import deepcopy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from backend.core.exercise_checker import check_code_task
from backend.core.notebook_engine import execute_notebook_code
from backend.core.quantum_engine import QuantumEngine
from backend.core.teaching_assistant import (
    TutorContext,
    answer_tutor,
    describe_circuit,
    review_qiskit_code,
)
from frontend.education_theme import inject_education_theme
from frontend.intuition import render_circuit, render_probabilities, render_widget, show_html
from frontend import notebook_store
from frontend.bloch3d import bloch_view_3d
from frontend.learning_content import GLOSSARY, LESSONS, PRACTICE, PRESETS, UNITS

st.set_page_config(
    page_title="Qiskit Intuition — Learn quantum computing",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)


DEFAULT_CODE = """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(1)
qc.h(0)

state = Statevector.from_instruction(qc)
print(qc.draw(output="text"))
print(state.probabilities_dict())
"""

CONTENT_PATH = Path(__file__).with_name("site_content.json")

GATE_OPTIONS = ["H", "X", "Y", "Z", "S", "T", "RX", "RY", "RZ", "CNOT", "CZ", "SWAP"]
TWO_QUBIT_GATES = {"CNOT", "CZ", "SWAP"}
ROTATION_GATES = {"RX", "RY", "RZ"}
PAGES = ["Course map", "Learning path", "My notebook", "Playground"]


def init_state() -> None:
    try:
        saved_content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        saved_content = {}

    default_brand = {
        "name": "Qiskit Intuition",
        "tagline": "Quantum computing, intuition first",
    }
    defaults = {
        "num_qubits": 1,
        "gates": [],
        "noisy": False,
        "workspace_code": DEFAULT_CODE,
        "last_result": None,
        "coach_messages": [],
        "selected_lesson": 0,
        "selected_practice": 0,
        "active_challenge": False,
        "learning_stage": 0,
        "lesson_max_stage": {},
        "completed_lessons": [],
        "quiz_answers": {},
        "tasks_passed": [],
        "notes": {},
        "reflections": {},
        "code_attempts": {},
        "task_feedback": {},
        "code_runs": {},
        "reading_mode": "notebook",
        "explanation_feedback": {},
        "author_mode": False,
        "playground_view": "Circuit builder",
        "site_brand": saved_content.get("brand", default_brand),
        "site_lessons": saved_content.get("lessons", deepcopy(LESSONS)),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def course_lessons() -> list[dict]:
    lessons = st.session_state.get("site_lessons")
    return lessons if isinstance(lessons, list) and lessons else LESSONS


def build_engine() -> QuantumEngine:
    engine = QuantumEngine(st.session_state.num_qubits)
    engine.gates = [dict(gate) for gate in st.session_state.gates]
    return engine


def load_preset(name: str) -> None:
    preset = PRESETS.get(name, PRESETS["Start at |0>"])
    st.session_state.num_qubits = preset["qubits"]
    st.session_state.gates = [dict(gate) for gate in preset["gates"]]
    st.session_state.noisy = False
    sync_workspace_to_circuit()


def sync_workspace_to_circuit() -> None:
    st.session_state.workspace_code = build_engine().get_qiskit_code()
    st.session_state.last_result = None


def navigate(page: str, playground_view: str | None = None) -> None:
    """Switch pages from anywhere. Widget-backed keys can't be set after the
    widget renders, so the change is applied at the start of the next run."""
    st.session_state.pending_nav = page
    if playground_view:
        st.session_state.pending_playground_view = playground_view
    st.rerun()


def set_reading_mode() -> None:
    st.session_state.reading_mode = "plain" if st.session_state.reading_toggle else "notebook"


def remember(store: str, item: str, widget_key: str) -> None:
    """Copy a text widget into a notebook dict. Streamlit forgets widget values
    when you leave the page; the dict keeps them (and gets saved)."""
    text = st.session_state.get(widget_key, "")
    entries = {k: v for k, v in st.session_state[store].items() if k != item}
    if text.strip():
        entries[item] = text
    st.session_state[store] = entries


def open_lesson(index: int, stage: int = 0) -> None:
    st.session_state.selected_lesson = index
    st.session_state.learning_stage = stage
    navigate("Learning path")


def next_lesson_index() -> int:
    lessons = course_lessons()
    done = set(st.session_state.completed_lessons)
    for index, lesson in enumerate(lessons):
        if lesson["id"] not in done:
            return index
    return len(lessons) - 1


def sidebar() -> str:
    brand = st.session_state.site_brand
    brand_name = html.escape(str(brand.get("name", "Qiskit Intuition")))
    brand_tagline = html.escape(str(brand.get("tagline", "Quantum computing, intuition first")))
    st.sidebar.markdown(
        f"""
<div class="brand">
  <div class="brand-mark">Lab notebook · No. 1</div>
  <div class="brand-name">{brand_name}</div>
  <div class="brand-subtitle">{brand_tagline}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.author_mode:
        st.sidebar.markdown("**Course author mode**")
        st.sidebar.caption("Edit lessons and export a publishable content file.")
        if st.sidebar.button("←  Return to learner view", use_container_width=True):
            st.session_state.author_mode = False
            st.rerun()
        return "Content studio"

    pending = st.session_state.pop("pending_nav", None)
    if pending in PAGES:
        st.session_state.main_navigation = pending
    page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed", key="main_navigation")

    lessons = course_lessons()
    done = set(st.session_state.completed_lessons)
    if page == "Learning path":
        st.sidebar.divider()
        st.sidebar.caption("CURRENT LESSON")
        selected = st.sidebar.selectbox(
            "Lesson",
            range(len(lessons)),
            index=min(int(st.session_state.selected_lesson), len(lessons) - 1),
            format_func=lambda index: f"{'✓' if lessons[index]['id'] in done else '○'}  {index + 1}. {lessons[index]['title']}",
            label_visibility="collapsed",
        )
        if selected != st.session_state.selected_lesson:
            st.session_state.selected_lesson = selected
            st.session_state.learning_stage = 0
            st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("COURSE PROGRESS")
    completed = len(done & {lesson["id"] for lesson in lessons})
    st.sidebar.progress(completed / len(lessons))
    st.sidebar.caption(
        f"{completed} of {len(lessons)} lessons · {len(set(st.session_state.tasks_passed))} coding exercises solved"
    )
    if st.session_state.get("nb_storage_ok"):
        st.sidebar.caption("💾 Notebook saved in this browser")
    elif st.session_state.get("nb_hydrated"):
        st.sidebar.caption("⚠ Not saved here — download it from My notebook")

    st.sidebar.divider()
    coach_label = "Model-enhanced coach" if os.getenv("GEMINI_API_KEY") else "Built-in code coach"
    st.sidebar.markdown(
        f"""
<div class="status-note"><span class="status-dot"></span>{coach_label}</div>
<p style="font-size:.74rem;color:#aebdc6;line-height:1.5;margin-top:.5rem;">
Simulation, lessons, and code review work without a separate server or API key.
</p>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.toggle(
        "Easy-read text",
        value=st.session_state.reading_mode == "plain",
        key="reading_toggle",
        on_change=set_reading_mode,
        help="Swap the handwriting for Atkinson Hyperlegible, a font designed for easy reading, and straighten tilted notes.",
    )

    with st.sidebar.expander("Course author"):
        st.caption("Edit the curriculum without exposing author controls in the learner workflow.")
        if st.button("Open content studio", use_container_width=True):
            st.session_state.author_mode = True
            st.rerun()
    return page


def inline_md(text: str) -> str:
    """Escape text for HTML, keeping `code` and **bold** from lesson content."""
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)


def page_header(eyebrow: str, title: str, intro: str) -> None:
    st.markdown(f'<div class="eyebrow">{html.escape(eyebrow)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-intro">{html.escape(intro)}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------- course map

LEARNING_STAGES = [
    ("Intuition", "Picture it first"),
    ("Predict", "Commit to an answer"),
    ("Experiment", "Test it in a circuit"),
    ("Formalize", "Now the math"),
    ("Code it", "Write the Qiskit"),
    ("Reflect", "Explain it back"),
]


def render_course_map() -> None:
    lessons = course_lessons()
    done = set(st.session_state.completed_lessons)
    passed = set(st.session_state.tasks_passed)

    show_html(
        f"""
<div class="cover-label">
  <div class="label-kicker">Laboratory notebook · No. 1</div>
  <div class="label-title">Quantum Computing</div>
  <div class="label-line"><span>Subject</span><b>Qiskit, from the ground up</b></div>
  <div class="label-line"><span>Method</span><b>picture → predict → test → math → code</b></div>
  <div class="label-line"><span>Progress</span><b>{len(done & {lesson["id"] for lesson in lessons})} of {len(lessons)} experiments written up</b></div>
</div>
<p class="intro-note">No physics degree needed. Every idea starts as a <u>picture you can play with</u>, becomes a prediction you
test on a simulator, and only then turns into math and Qiskit code. By the last page you'll have built superposition,
interference, entanglement, Grover search and a trainable circuit yourself.</p>
        """
    )
    loop = '<span class="loop-arrow">→</span>'.join(
        f'<span class="loop-step"><span>{index + 1}</span>{label}<small>{detail}</small></span>'
        for index, (label, detail) in enumerate(LEARNING_STAGES)
    )
    show_html(f'<div class="loop-row">{loop}</div>')

    resume = next_lesson_index()
    all_done = {lesson["id"] for lesson in lessons} <= done
    if all_done:
        resume = 0
    started = bool(done or st.session_state.lesson_max_stage or st.session_state.quiz_answers)
    if all_done:
        label = "Course complete — review from lesson 1"
    elif started:
        label = f"Continue: {resume + 1}. {lessons[resume]['title']}"
    else:
        label = "Start lesson 1"
    if st.button(f"{label}  →", type="primary", key="resume_course"):
        same_lesson = resume == int(st.session_state.selected_lesson)
        open_lesson(resume, int(st.session_state.learning_stage) if same_lesson and not all_done else 0)

    unit_ids = [unit["id"] for unit in UNITS]
    grouped: dict[str, list[tuple[int, dict]]] = {unit_id: [] for unit_id in unit_ids}
    extra: list[tuple[int, dict]] = []
    for index, lesson in enumerate(lessons):
        grouped.get(lesson.get("unit"), extra).append((index, lesson))
    units = [*UNITS, {"id": "more", "title": "More lessons", "blurb": ""}] if extra else UNITS
    grouped["more"] = extra

    columns = st.columns(2, gap="large")
    for unit_index, unit in enumerate(units):
        items = grouped.get(unit["id"], [])
        if not items:
            continue
        unit_done = sum(1 for _, lesson in items if lesson["id"] in done)
        with columns[unit_index % 2]:
            with st.container(key=f"nb-card-unit-{unit['id']}"):
                st.markdown(
                    f'<div class="unit-head"><span>Unit {unit_index + 1}</span><strong>{html.escape(unit["title"])}</strong>'
                    f'<small>{unit_done}/{len(items)} done</small></div><p class="unit-blurb">{html.escape(unit["blurb"])}</p>',
                    unsafe_allow_html=True,
                )
                for index, lesson in items:
                    status = "✓" if lesson["id"] in done else "○"
                    code_badge = " · </> solved" if lesson["id"] in passed else ""
                    left, right = st.columns([4, 1.2])
                    with left:
                        st.markdown(
                            f'<div class="lesson-row {"done" if status == "✓" else ""}"><span>{status}</span>'
                            f'<div><strong>{index + 1}. {html.escape(lesson["title"])}</strong>'
                            f'<small>{html.escape(lesson.get("duration", ""))}{code_badge}</small></div></div>',
                            unsafe_allow_html=True,
                        )
                    with right:
                        if st.button("Open", key=f"map_open_{lesson['id']}", use_container_width=True):
                            open_lesson(index)

    with st.expander("Glossary — every term, intuition first"):
        rows = "".join(
            f"<tr><td><strong>{html.escape(term)}</strong></td><td>{html.escape(picture)}</td><td>{html.escape(formal)}</td></tr>"
            for term, picture, formal in GLOSSARY
        )
        show_html(f'<table class="glossary"><thead><tr><th>Term</th><th>The picture</th><th>The precise version</th></tr></thead><tbody>{rows}</tbody></table>')


# --------------------------------------------------------------------------- learning path


def set_learning_stage(stage: int, lesson_id: str) -> None:
    progress = dict(st.session_state.lesson_max_stage)
    progress[lesson_id] = max(int(progress.get(lesson_id, 0)), stage)
    st.session_state.lesson_max_stage = progress
    st.session_state.learning_stage = stage
    st.rerun()


def render_learning_stepper(stage: int) -> None:
    rendered = []
    for index, (label, detail) in enumerate(LEARNING_STAGES):
        status = "complete" if index < stage else "current" if index == stage else "upcoming"
        marker = "✓" if index < stage else str(index + 1)
        rendered.append(
            f'<div class="journey-step {status}"><span class="journey-marker">{marker}</span>'
            f"<div><strong>{label}</strong><small>{detail}</small></div></div>"
        )
    show_html(f'<div class="journey-stepper">{"".join(rendered)}</div>')


def stage_nav(lesson: dict, stage: int, next_label: str, *, before_next=None, next_disabled: bool = False) -> None:
    back, forward = st.columns([1, 2])
    with back:
        if stage > 0 and st.button(f"←  {LEARNING_STAGES[stage - 1][0]}", use_container_width=True, key=f"back_{stage}"):
            set_learning_stage(stage - 1, lesson["id"])
    with forward:
        if st.button(f"{next_label}  →", type="primary", use_container_width=True, key=f"next_{stage}", disabled=next_disabled):
            if before_next:
                before_next()
            set_learning_stage(stage + 1, lesson["id"])


def render_learning_path() -> None:
    lessons = course_lessons()
    selected = min(int(st.session_state.selected_lesson), len(lessons) - 1)
    lesson = lessons[selected]
    stage = min(max(int(st.session_state.learning_stage), 0), len(LEARNING_STAGES) - 1)
    unit_titles = {unit["id"]: unit["title"] for unit in UNITS}

    show_html(
        f"""
<div class="path-context">
  <span>Lesson {selected + 1} of {len(lessons)}</span>
  <span>{html.escape(unit_titles.get(lesson.get("unit"), lesson.get("eyebrow", "")))}</span>
  <span>{html.escape(lesson.get("duration", ""))}</span>
</div>
        """
    )
    page_header(lesson.get("eyebrow", ""), lesson["title"], lesson.get("summary", ""))
    render_learning_stepper(stage)

    renderers = [
        render_intuition_stage,
        render_predict_stage,
        render_experiment_stage,
        render_formalize_stage,
        render_code_stage,
    ]
    if stage < len(renderers):
        renderers[stage](lesson)
    else:
        render_reflect_stage(lesson, selected, len(lessons))
    render_margin_notes(lesson)


def render_margin_notes(lesson: dict) -> None:
    lesson_id = lesson["id"]
    with st.container(key=f"nb-margin-notes-{lesson_id}"):
        st.markdown('<div class="margin-title">✎ My margin notes</div>', unsafe_allow_html=True)
        st.text_area(
            "Margin notes",
            value=st.session_state.notes.get(lesson_id, ""),
            key=f"margin_{lesson_id}",
            height=120,
            label_visibility="collapsed",
            placeholder="Scribble anything — questions, an 'aha!', a sketch in words. It's kept in your notebook.",
            on_change=remember,
            args=("notes", lesson_id, f"margin_{lesson_id}"),
        )


def render_intuition_stage(lesson: dict) -> None:
    st.markdown('<div class="stage-kicker">Step 1 · Intuition</div>', unsafe_allow_html=True)
    picture, goals = st.columns([1.6, 1], gap="large")
    with picture:
        st.subheader("The picture")
        for paragraph in lesson.get("intuition") or lesson.get("explanation", []):
            st.markdown(paragraph)
    with goals:
        objectives = "".join(f"<li>{inline_md(item)}</li>" for item in lesson.get("objectives", []))
        show_html(
            f"""
<div class="content-card stage-sidecard">
  <strong>By the end of this lesson you can</strong>
  <ul class="objective-list">{objectives}</ul>
</div>
            """
        )

    if lesson.get("widget"):
        st.markdown('<div class="feel-it"><span>Try it!</span><strong>play first — the math comes later</strong></div>', unsafe_allow_html=True)
        with st.container(key=f"nb-card-widget-{lesson['id']}"):
            render_widget(lesson["widget"], key=f"w_{lesson['id']}")

    stage_nav(lesson, 0, "Make a prediction")


def render_predict_stage(lesson: dict) -> None:
    st.markdown('<div class="stage-kicker">Step 2 · Predict</div>', unsafe_allow_html=True)
    st.subheader("Commit to an answer before the simulator shows it")
    quiz = lesson.get("quiz")
    if not quiz:
        render_free_prediction(lesson)
        return

    show_html(
        f"""
<div class="prediction-prompt">
  <span>Prediction</span>
  <strong>{html.escape(quiz["question"])}</strong>
  <p>Being wrong here is useful — the surprise is what makes the idea stick.</p>
</div>
        """
    )
    answers = st.session_state.quiz_answers
    locked = answers.get(lesson["id"])
    choice = st.radio(
        "Your answer",
        range(len(quiz["options"])),
        format_func=lambda index: quiz["options"][index],
        index=locked if locked is not None else None,
        key=f"quiz_{lesson['id']}",
        disabled=locked is not None,
        label_visibility="collapsed",
    )

    if locked is None:
        if st.button("Lock in my answer", type="primary", disabled=choice is None, key=f"lock_{lesson['id']}"):
            st.session_state.quiz_answers = {**answers, lesson["id"]: choice}
            st.rerun()
        if st.button("←  Back to the picture", key=f"predict_back_{lesson['id']}"):
            set_learning_stage(0, lesson["id"])
        return

    correct = quiz["answer"]
    explanations = quiz.get("explanations", [])
    if locked == correct:
        st.success(f"**Correct.** {explanations[locked] if locked < len(explanations) else ''}")
    else:
        st.warning(
            f"**Not quite.** {explanations[locked] if locked < len(explanations) else ''}  \n"
            f"The answer is **{quiz['options'][correct]}**. Run the experiment and see it for yourself."
        )
    with st.expander("Why each option is tempting"):
        for index, option in enumerate(quiz["options"]):
            mark = "✓" if index == correct else "✗"
            reason = explanations[index] if index < len(explanations) else ""
            st.markdown(f"{mark} **{option}** — {reason}")
    if st.button("Change my answer", key=f"unlock_{lesson['id']}"):
        st.session_state.quiz_answers = {k: v for k, v in answers.items() if k != lesson["id"]}
        st.rerun()

    stage_nav(lesson, 1, "Run the experiment", before_next=lambda: load_preset(lesson["preset"]))


def render_free_prediction(lesson: dict) -> None:
    """Fallback for lessons (e.g. imported from older content files) without a quiz."""
    show_html(
        f"""
<div class="prediction-prompt">
  <span>Checkpoint</span>
  <strong>{html.escape(lesson.get("checkpoint", ""))}</strong>
  <p>Describe the final state or measurement pattern and give one reason.</p>
</div>
        """
    )
    prediction = st.text_area("Your prediction", key=f"prediction_{lesson['id']}", placeholder="I expect… because…", height=130)
    stage_nav(lesson, 1, "Run the experiment", before_next=lambda: load_preset(lesson["preset"]), next_disabled=not prediction.strip())


def prediction_summary(lesson: dict) -> str:
    quiz = lesson.get("quiz")
    locked = st.session_state.quiz_answers.get(lesson["id"])
    if quiz and locked is not None:
        verdict = "✓" if locked == quiz["answer"] else "✗"
        return f"{verdict} {quiz['options'][locked]}"
    return st.session_state.get(f"prediction_{lesson['id']}", "")


def gate_controls(prefix: str) -> dict | None:
    """Gate/target/parameter pickers. Returns the operation to add, or None."""
    gate_col, target_col, parameter_col, add_col = st.columns([1.15, 0.9, 1.15, 0.9])
    with gate_col:
        gate_name = st.selectbox("Gate", GATE_OPTIONS, key=f"{prefix}_gate")
    with target_col:
        target = st.selectbox("Target", list(range(st.session_state.num_qubits)), format_func=lambda q: f"q{q}", key=f"{prefix}_target")
    control = None
    angle = None
    with parameter_col:
        if gate_name in TWO_QUBIT_GATES:
            controls = [q for q in range(st.session_state.num_qubits) if q != target]
            label = "Other qubit" if gate_name == "SWAP" else "Control"
            if controls:
                control = st.selectbox(label, controls, format_func=lambda q: f"q{q}", key=f"{prefix}_control")
            else:
                st.selectbox(label, ["Needs 2 qubits"], disabled=True, key=f"{prefix}_control_disabled")
        elif gate_name in ROTATION_GATES:
            angle = st.slider("Angle (× π)", -2.0, 2.0, 0.5, 0.05, key=f"{prefix}_angle") * math.pi
        else:
            st.selectbox("Parameter", ["None"], disabled=True, key=f"{prefix}_parameter")
    with add_col:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        can_add = gate_name not in TWO_QUBIT_GATES or control is not None
        if st.button("＋  Add gate", type="primary", use_container_width=True, disabled=not can_add, key=f"{prefix}_add"):
            operation = {"gate": gate_name, "target": target, "control": control}
            if angle is not None:
                operation["angle"] = angle
            return operation
    return None


def gate_label(gate: dict) -> str:
    name = gate["gate"]
    if name in TWO_QUBIT_GATES and gate.get("control") is not None:
        return f"{name} q{gate['control']}→q{gate['target']}" if name != "SWAP" else f"SWAP q{gate['control']}↔q{gate['target']}"
    if name in ROTATION_GATES and gate.get("angle") is not None:
        return f"{name}({gate['angle'] / math.pi:.2f}π) q{gate['target']}"
    return f"{name} q{gate['target']}"


def render_guided_builder(lesson: dict) -> None:
    operation = gate_controls("guided")
    if operation:
        st.session_state.gates.append(operation)
        sync_workspace_to_circuit()
        st.rerun()

    sequence = st.session_state.gates
    chips = "".join(
        f'<span class="gate-chip"><small>{index + 1}</small><strong>{html.escape(gate_label(gate))}</strong></span>'
        for index, gate in enumerate(sequence)
    ) or '<span class="empty-sequence">No gates yet — the register starts in |0…0⟩.</span>'
    show_html(f'<div class="guided-sequence">{chips}</div>')

    undo, clear, reset, qubits = st.columns([1, 1, 1.4, 1.3])
    with undo:
        if st.button("↶  Undo", use_container_width=True, disabled=not sequence, key="guided_undo"):
            st.session_state.gates = st.session_state.gates[:-1]
            sync_workspace_to_circuit()
            st.rerun()
    with clear:
        if st.button("Clear", use_container_width=True, disabled=not sequence, key="guided_clear"):
            st.session_state.gates = []
            sync_workspace_to_circuit()
            st.rerun()
    with reset:
        if st.button("Reset worked example", use_container_width=True, key="guided_reset"):
            load_preset(lesson["preset"])
            st.rerun()
    with qubits:
        count = st.selectbox(
            "Qubits", [1, 2, 3, 4], index=st.session_state.num_qubits - 1, key="guided_qubits", label_visibility="collapsed",
            format_func=lambda n: f"{n} qubit{'s' if n > 1 else ''}",
        )
        if count != st.session_state.num_qubits:
            set_qubit_count(count)


def set_qubit_count(count: int) -> None:
    st.session_state.num_qubits = count
    st.session_state.gates = [
        gate for gate in st.session_state.gates
        if gate["target"] < count and (gate.get("control") is None or gate["control"] < count)
    ]
    sync_workspace_to_circuit()
    st.rerun()


def render_bloch_row(engine: QuantumEngine) -> None:
    vectors = engine.run_simulation()
    bloch_view_3d([
        {"title": f"q{qubit}", "vector": [data["x"], data["y"], data["z"]]}
        for qubit, data in vectors.items()
    ])


def render_experiment_stage(lesson: dict) -> None:
    st.markdown('<div class="stage-kicker">Step 3 · Experiment</div>', unsafe_allow_html=True)
    st.subheader("Test your prediction on a simulator")

    recap, tries = st.columns([1, 1.5], gap="large")
    with recap:
        show_html(f'<div class="prediction-recap"><span>Your prediction</span><p>{html.escape(prediction_summary(lesson))}</p></div>')
    with tries:
        items = "".join(f"<li>{inline_md(item)}</li>" for item in lesson.get("try_this", []))
        if items:
            show_html(f'<div class="content-card try-card"><strong>Things to try</strong><ol>{items}</ol></div>')

    st.markdown("#### Build — change one operation at a time")
    render_guided_builder(lesson)
    if lesson.get("noise_toggle"):
        st.toggle("Include device noise", key="noisy", help="Adds a simple depolarizing-noise model to sampled probabilities.")

    engine = build_engine()
    noisy = bool(lesson.get("noise_toggle") and st.session_state.noisy)
    probabilities = engine.get_probabilities(noisy=noisy)
    ideal = engine.get_probabilities() if noisy else None

    circuit_col, probability_col = st.columns([1.15, 1], gap="large")
    with circuit_col:
        st.markdown("**Circuit**")
        render_circuit(engine)
    with probability_col:
        st.markdown("**What measurement can return**" + (" (4000 noisy shots)" if noisy else ""))
        render_probabilities(probabilities, compare=ideal, compare_label="ideal simulation" if noisy else "")
        st.caption("Bit strings follow Qiskit's order: q0 is the rightmost bit.")

    st.markdown("**Each qubit's arrow**")
    render_bloch_row(engine)
    show_html(f"<div class='callout'><strong>Read the result</strong><p>{html.escape(describe_circuit(st.session_state.gates, probabilities))}</p></div>")
    with st.expander("See the exact state and the matching Qiskit code"):
        st.latex(statevector_latex(engine.get_statevector().data, st.session_state.num_qubits))
        st.code(engine.get_qiskit_code(), language="python")

    stage_nav(lesson, 2, "Now the math")


def render_formalize_stage(lesson: dict) -> None:
    st.markdown('<div class="stage-kicker">Step 4 · Formalize</div>', unsafe_allow_html=True)
    concept, side = st.columns([1.55, 0.9], gap="large")
    with concept:
        st.subheader("Put numbers on the picture")
        for paragraph in lesson.get("explanation", []):
            st.markdown(paragraph)
        st.latex(lesson.get("latex") or lesson.get("equation", ""))
    with side:
        show_html(
            f"""
<div class="callout warning compact-callout">
  <strong>Common misconception</strong>
  <p>{html.escape(lesson.get("misconception", ""))}</p>
</div>
            """
        )
        if lesson.get("widget"):
            st.caption("Go back to the picture any time — the math describes exactly what the widget showed.")
    stage_nav(lesson, 3, "Write it in Qiskit")


def render_run_output(result: dict) -> None:
    if result["success"]:
        if result.get("stdout"):
            st.code(result["stdout"], language="text")
        else:
            st.caption("The code ran but printed nothing.")
        for figure in result.get("figures", []):
            st.image(figure, use_container_width=True)
    else:
        st.error("The code raised an error:")
        st.code(result.get("error") or result.get("stderr") or "Unknown error", language="text")


def render_code_stage(lesson: dict) -> None:
    st.markdown('<div class="stage-kicker">Step 5 · Code it</div>', unsafe_allow_html=True)
    qiskit = lesson.get("qiskit")
    task = lesson.get("code_task")
    if not qiskit and not task:
        st.info("This lesson has no coding step.")
        stage_nav(lesson, 4, "Reflect")
        return

    lesson_id = lesson["id"]
    if qiskit:
        st.subheader("The Qiskit for this idea")
        st.markdown(qiskit.get("intro", ""))
        editor, notes = st.columns([1.35, 1], gap="large")
        with editor:
            code = st.text_area("Worked example", value=qiskit["code"], height=300, key=f"worked_{lesson_id}")
            run, send = st.columns(2)
            with run:
                if st.button("▶  Run", type="primary", use_container_width=True, key=f"run_worked_{lesson_id}"):
                    with st.spinner("Running in the sandbox…"):
                        st.session_state.code_runs = {**st.session_state.code_runs, lesson_id: execute_notebook_code(code)}
            with send:
                if st.button("Open in the code playground", use_container_width=True, key=f"send_{lesson_id}"):
                    st.session_state.workspace_code = code
                    st.session_state.last_result = None
                    navigate("Playground", "Qiskit code")
        with notes:
            st.markdown("**Line by line**")
            for snippet, meaning in qiskit.get("notes", []):
                st.markdown(f"`{snippet}` — {meaning}")
            run_result = st.session_state.code_runs.get(lesson_id)
            if run_result:
                st.markdown("**Output**")
                render_run_output(run_result)
        if qiskit.get("real_hardware"):
            with st.expander("Run it on real IBM quantum hardware"):
                st.code(qiskit["real_hardware"], language="python")
                st.caption(
                    "Needs `pip install qiskit-ibm-runtime`, a free IBM Quantum account and internet access, "
                    "so it can't run in this sandbox. Put it after the worked example on your own machine."
                )

    if task:
        st.divider()
        st.subheader("Your turn")
        solved = lesson_id in st.session_state.tasks_passed
        show_html(f'<div class="task-card {"solved" if solved else ""}"><span>{"Solved ✓" if solved else "Exercise"}</span><p>{inline_md(task["prompt"])}</p></div>')
        attempt = st.text_area(
            "Your code",
            value=st.session_state.code_attempts.get(lesson_id, task.get("starter", "")),
            height=220,
            key=f"task_{lesson_id}",
            on_change=remember,
            args=("code_attempts", lesson_id, f"task_{lesson_id}"),
        )
        check, hint, solution = st.columns([1.2, 1, 1])
        with check:
            if st.button("✓  Check my code", type="primary", use_container_width=True, key=f"check_{lesson_id}"):
                remember("code_attempts", lesson_id, f"task_{lesson_id}")
                with st.spinner("Running and comparing with the target…"):
                    outcome = check_code_task(attempt, task)
                st.session_state.task_feedback = {**st.session_state.task_feedback, lesson_id: outcome}
                if outcome["passed"]:
                    st.session_state.tasks_passed = list(dict.fromkeys([*st.session_state.tasks_passed, lesson_id]))
        with hint:
            with st.popover("Hint", use_container_width=True):
                st.markdown(task.get("hint", "Re-read the worked example above."))
        with solution:
            with st.popover("Show a solution", use_container_width=True):
                st.code(task["solution"], language="python")
        feedback = st.session_state.task_feedback.get(lesson_id)
        if feedback:
            (st.success if feedback["passed"] else st.warning)(feedback["message"])
            if feedback.get("stdout"):
                st.code(feedback["stdout"], language="text")

    stage_nav(lesson, 4, "Reflect")


def render_reflect_stage(lesson: dict, lesson_index: int, lesson_count: int) -> None:
    st.markdown('<div class="stage-kicker">Step 6 · Reflect</div>', unsafe_allow_html=True)
    st.subheader("Explain it back in your own words")
    show_html(
        f"""
<div class="explanation-brief">
  <strong>Explain the evidence</strong>
  <p>Use what you saw — the arrow, the bars, the amplitudes — not only an analogy. If you can explain it, you own it.</p>
  <blockquote>{html.escape(lesson.get("checkpoint", ""))}</blockquote>
</div>
        """
    )

    reflection_key = f"reflection_{lesson['id']}"
    feedback_key = lesson["id"]
    final_lesson = lesson_index == lesson_count - 1
    completion_label = "Complete the course" if final_lesson else "Complete lesson and continue  →"
    with st.form(f"explanation_form_{lesson['id']}"):
        reflection = st.text_area(
            "Your explanation",
            value=st.session_state.reflections.get(lesson["id"], ""),
            key=reflection_key,
            placeholder="The result shows… This happens because…",
            height=160,
        )
        check_col, complete_col = st.columns([1, 1.4])
        with check_col:
            check_reasoning = st.form_submit_button("Check my reasoning", use_container_width=True)
        with complete_col:
            complete_lesson = st.form_submit_button(completion_label, type="primary", use_container_width=True)

    if check_reasoning or complete_lesson:
        remember("reflections", lesson["id"], reflection_key)

    if check_reasoning:
        if not reflection.strip():
            st.warning("Write a short explanation before asking for feedback.")
        else:
            prompt = (
                f"Evaluate this learner explanation for the lesson '{lesson['title']}': {reflection}. "
                "Identify what is correct, correct one misconception if present, and give one concise verification step."
            )
            with st.spinner("Checking the explanation against the circuit…"):
                answer = answer_tutor(prompt, current_tutor_context(), use_model=True)
            st.session_state.explanation_feedback = {**st.session_state.explanation_feedback, feedback_key: answer["reply"]}

    if complete_lesson:
        if not reflection.strip():
            st.warning("Explain the result in your own words before completing the lesson.")
        else:
            st.session_state.completed_lessons = list(dict.fromkeys([*st.session_state.completed_lessons, lesson["id"]]))
            if not final_lesson:
                st.session_state.selected_lesson = lesson_index + 1
                st.session_state.learning_stage = 0
            else:
                st.balloons()
            st.rerun()

    if st.button("←  Code it", key="reflect_back"):
        set_learning_stage(4, lesson["id"])

    feedback = st.session_state.explanation_feedback.get(feedback_key)
    if feedback:
        st.markdown('<div class="coach-feedback"><span>Coach feedback</span></div>', unsafe_allow_html=True)
        st.markdown(feedback)

    practice_index = min(int(lesson.get("practice", lesson_index // 2)), len(PRACTICE) - 1)
    challenge = PRACTICE[practice_index]
    with st.expander("Optional transfer challenge"):
        st.markdown(f"**{challenge['title']}**")
        st.write(challenge["goal"])
        st.caption("Test the same idea in a new circuit, in the open playground.")
        if st.button("Open challenge in the playground", key=f"challenge_{lesson['id']}"):
            st.session_state.selected_practice = practice_index
            st.session_state.active_challenge = True
            st.session_state.num_qubits = challenge["qubits"]
            st.session_state.gates = []
            sync_workspace_to_circuit()
            navigate("Playground", "Circuit builder")

    if lesson["id"] in st.session_state.completed_lessons:
        if final_lesson:
            st.success("You've completed the whole course. From an arrow on a sphere to a trained circuit — nicely done.")
        else:
            st.success("This lesson is complete. You can revisit any step or continue when ready.")


def render_circuit_lab(show_header: bool = True) -> None:
    if show_header:
        page_header(
            "Hands-on simulator",
            "Circuit lab",
            "Build a circuit, make a prediction, and compare it with the exact state. Every visual result maps directly to runnable Qiskit code.",
        )

    preset_col, qubit_col, noise_col = st.columns([1.5, 1, 1])
    with preset_col:
        preset_name = st.selectbox("Worked examples", list(PRESETS.keys()), index=1)
        if st.button("Load example  →", use_container_width=True):
            load_preset(preset_name)
            st.rerun()
    with qubit_col:
        qubits = st.selectbox("Number of qubits", [1, 2, 3, 4], index=st.session_state.num_qubits - 1)
        if qubits != st.session_state.num_qubits:
            set_qubit_count(qubits)
    with noise_col:
        st.toggle("Include device noise", key="noisy", help="Adds a simple depolarizing-noise model to sampled probabilities.")

    st.subheader("1. Build")
    operation = gate_controls("lab")
    if operation:
        st.session_state.gates.append(operation)
        sync_workspace_to_circuit()
        st.rerun()

    sequence = " → ".join(gate_label(g) for g in st.session_state.gates) or "No gates yet"
    st.caption(f"Current sequence: {sequence}")
    undo_col, clear_col, _spacer = st.columns([1, 1, 3])
    with undo_col:
        if st.button("↶  Undo last", use_container_width=True, disabled=not st.session_state.gates):
            st.session_state.gates = st.session_state.gates[:-1]
            sync_workspace_to_circuit()
            st.rerun()
    with clear_col:
        if st.button("Clear circuit", use_container_width=True, disabled=not st.session_state.gates):
            st.session_state.gates = []
            sync_workspace_to_circuit()
            st.rerun()

    engine = build_engine()
    probabilities = engine.get_probabilities(noisy=st.session_state.noisy)

    st.subheader("2. Observe")
    st.markdown(
        f"""
<div class="metric-row">
  <div class="metric-box"><div class="metric-label">Qubits</div><div class="metric-value">{st.session_state.num_qubits}</div></div>
  <div class="metric-box"><div class="metric-label">Circuit depth</div><div class="metric-value">{len(st.session_state.gates)}</div></div>
  <div class="metric-box"><div class="metric-label">Model</div><div class="metric-value">{'Noisy samples' if st.session_state.noisy else 'Ideal state'}</div></div>
</div>
        """,
        unsafe_allow_html=True,
    )

    circuit_col, probability_col = st.columns([1.2, 1], gap="large")
    with circuit_col:
        st.markdown("**Circuit diagram**")
        render_circuit(engine)
    with probability_col:
        st.markdown("**Measurement probabilities**")
        render_probabilities(probabilities)
        st.caption("Bit strings use Qiskit's display order. q0 is the rightmost bit.")

    st.subheader("3. Explain")
    st.markdown(
        f"<div class='callout'><strong>What the circuit says</strong><p>{html.escape(describe_circuit(st.session_state.gates, probabilities))}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("**Each qubit's arrow** — a shrunken arrow means the qubit is entangled or noisy")
    render_bloch_row(engine)

    with st.expander("View the exact statevector"):
        state = engine.get_statevector().data
        st.latex(statevector_latex(state, st.session_state.num_qubits))
        rows = []
        width = st.session_state.num_qubits
        for index, amplitude in enumerate(state):
            if abs(amplitude) > 1e-9:
                rows.append(f"|{index:0{width}b}⟩  amplitude={amplitude.real:+.4f}{amplitude.imag:+.4f}j  probability={abs(amplitude) ** 2:.4f}")
        st.code("\n".join(rows) or "All amplitudes are zero (unexpected).", language="text")

    with st.expander("View matching Qiskit code", expanded=True):
        st.code(engine.get_qiskit_code(), language="python")
        if st.button("Open this circuit in the code workspace  →", type="primary"):
            sync_workspace_to_circuit()
            navigate("Playground", "Qiskit code")


def statevector_latex(state: object, width: int) -> str:
    """Return a compact, readable ket expansion for Streamlit's KaTeX renderer."""
    terms = []
    for index, raw_amplitude in enumerate(state):
        amplitude = complex(raw_amplitude)
        if abs(amplitude) <= 1e-9:
            continue
        real = 0.0 if abs(amplitude.real) < 1e-9 else amplitude.real
        imaginary = 0.0 if abs(amplitude.imag) < 1e-9 else amplitude.imag
        ket = rf"|{index:0{width}b}\rangle"
        if imaginary == 0.0 and abs(real - 1.0) < 1e-9:
            terms.append(ket)
        elif imaginary == 0.0 and abs(real + 1.0) < 1e-9:
            terms.append(rf"-{ket}")
        elif imaginary == 0.0:
            terms.append(rf"({real:.4g}){ket}")
        elif real == 0.0:
            terms.append(rf"({imaginary:.4g}i){ket}")
        else:
            terms.append(rf"({real:.4g}{imaginary:+.4g}i){ket}")
    return r"|\psi\rangle = " + r" + ".join(terms)


def render_code_lab(show_header: bool = True) -> None:
    if show_header:
        page_header(
            "Qiskit workspace",
            "Code lab",
            "Write and run short Qiskit programs in a restricted teaching sandbox. The coach reviews the actual code and the last traceback—not a generic prompt.",
        )

    toolbar_left, toolbar_right = st.columns([1, 2])
    with toolbar_left:
        if st.button("Use the current circuit", use_container_width=True):
            sync_workspace_to_circuit()
            st.rerun()
    with toolbar_right:
        st.caption("Allowed: Qiskit, NumPy, Matplotlib, and pure Python. File, process, and network access are blocked.")

    editor_col, result_col = st.columns([1.2, 1], gap="large")
    with editor_col:
        st.markdown("**Editor**")
        editor_value = st.text_area(
            "Qiskit code",
            value=st.session_state.workspace_code,
            key="workspace_editor",
            height=420,
            label_visibility="collapsed",
        )
        st.session_state.workspace_code = editor_value
        run_col, review_col = st.columns(2)
        with run_col:
            run_clicked = st.button("Run code", type="primary", use_container_width=True)
        with review_col:
            review_clicked = st.button("Review code", use_container_width=True)

    if run_clicked:
        with st.spinner("Running in the teaching sandbox…"):
            st.session_state.last_result = execute_notebook_code(st.session_state.workspace_code)

    with result_col:
        st.markdown("**Output**")
        result = st.session_state.last_result
        if result is None:
            st.info("Run the program to see stdout, figures, and errors here.")
        elif result["success"]:
            st.success("Execution completed.")
            if result["stdout"]:
                st.code(result["stdout"], language="text")
            else:
                st.caption("The code ran but printed no text. Add a print statement or create a Matplotlib figure.")
            for figure in result["figures"]:
                st.image(figure, use_container_width=True)
        else:
            st.error("Execution failed. The coach has the traceback context below.")
            st.code(result.get("error") or result.get("stderr") or "Unknown error", language="text")

    if review_clicked:
        findings = review_qiskit_code(st.session_state.workspace_code)
        render_findings(findings)

    if st.session_state.last_result and not st.session_state.last_result["success"]:
        diagnosis = answer_tutor(
            "Debug and fix the last error",
            current_tutor_context(),
            use_model=True,
        )
        st.markdown("### First-pass diagnosis")
        st.markdown(diagnosis["reply"])

    render_code_coach()


def render_findings(findings: list[dict]) -> None:
    st.markdown("### Code review")
    if not findings:
        st.success("No obvious syntax or Qiskit-version issue found. Verify the physics by predicting the output.")
        return
    for item in findings:
        line = f" · line {item['line']}" if item.get("line") else ""
        label = f"{item['title']}{line}"
        if item["severity"] == "error":
            st.error(f"**{label}** — {item['detail']}")
        else:
            st.info(f"**{label}** — {item['detail']}")


def current_tutor_context() -> TutorContext:
    result = st.session_state.last_result or {}
    error = ""
    if result and not result.get("success", False):
        error = result.get("error") or result.get("stderr") or ""
    lessons = course_lessons()
    lesson = lessons[min(int(st.session_state.selected_lesson), len(lessons) - 1)]
    return TutorContext(
        code=st.session_state.workspace_code,
        execution_error=error,
        gates=[dict(gate) for gate in st.session_state.gates],
        num_qubits=st.session_state.num_qubits,
        lesson_title=lesson["title"],
    )


def render_code_coach() -> None:
    st.markdown("### Ask the code coach")
    st.caption("It receives the current circuit, lesson, code, and latest execution error. Do not paste secrets or access tokens.")

    prompts = []
    cols = st.columns(4)
    labels = [
        ("Explain my code", "Explain my code and connect each important line to the quantum state."),
        ("Review for issues", "Review my code for Qiskit mistakes and unclear learning output."),
        ("Debug last error", "Debug and fix the last error."),
        ("Give me an exercise", "Give me a focused next exercise based on the current lesson."),
    ]
    for column, (label, prompt) in zip(cols, labels):
        with column:
            if st.button(label, use_container_width=True, key=f"coach_{label}"):
                prompts.append(prompt)

    for message in st.session_state.coach_messages[-8:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_prompt = st.chat_input("Ask about the code, circuit, error, or lesson")
    prompt = typed_prompt or (prompts[0] if prompts else None)
    if prompt:
        st.session_state.coach_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Inspecting the learning context…"):
                answer = answer_tutor(prompt, current_tutor_context(), use_model=True)
            st.markdown(answer["reply"])
        st.session_state.coach_messages.append({"role": "assistant", "content": answer["reply"]})

    if st.session_state.coach_messages and st.button("Clear coach conversation"):
        st.session_state.coach_messages = []
        st.rerun()


def render_playground() -> None:
    page_header(
        "Explore freely",
        "Playground",
        "Use the same circuit in two views: build visually, then inspect or change the matching Qiskit program. Nothing here interrupts your lesson progress.",
    )
    pending_view = st.session_state.pop("pending_playground_view", None)
    if pending_view:
        st.session_state.playground_view = pending_view
    mode = st.radio(
        "Workspace",
        ["Circuit builder", "Qiskit code"],
        horizontal=True,
        label_visibility="collapsed",
        key="playground_view",
    )

    if mode == "Circuit builder":
        if st.session_state.active_challenge:
            render_active_challenge()
        render_circuit_lab(show_header=False)
    else:
        render_code_lab(show_header=False)


def render_active_challenge() -> None:
    exercise = PRACTICE[min(int(st.session_state.selected_practice), len(PRACTICE) - 1)]
    st.markdown(
        f"""
<div class="challenge-banner">
  <div><span>Optional challenge</span><strong>{html.escape(exercise['title'])}</strong></div>
  <p>{html.escape(exercise['goal'])}</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    action, dismiss = st.columns([1, 1])
    with action:
        check = st.button("Check this circuit", type="primary", use_container_width=True)
    with dismiss:
        if st.button("Leave challenge mode", use_container_width=True):
            st.session_state.active_challenge = False
            st.rerun()

    if not check:
        return
    if st.session_state.num_qubits != exercise["qubits"]:
        st.error(f"This challenge needs exactly {exercise['qubits']} qubit(s).")
        return
    actual = build_engine().get_probabilities()
    target = exercise["target"]
    states = set(actual) | set(target)
    max_error = max(abs(actual.get(state, 0.0) - target.get(state, 0.0)) for state in states)
    names = [gate["gate"] for gate in st.session_state.gates]
    required_ok = all(name in names for name in exercise.get("required", []))
    forbidden_ok = all(name not in names for name in exercise.get("forbidden", []))
    if max_error < 0.025 and required_ok and forbidden_ok:
        st.success("Challenge complete. Your circuit reaches the target and respects the gate constraints.")
    else:
        st.warning(f"Not yet. Hint: {exercise['hint']}")


def render_content_studio() -> None:
    page_header(
        "Creator tools",
        "Content studio",
        "Edit course copy without changing Python. Changes preview immediately in this browser session; export the JSON file to make them permanent in the repository or on Hugging Face Spaces.",
    )

    st.markdown(
        """
<div class="callout">
  <strong>How persistence works</strong>
  <p>Edits here are session-only. Download the configuration and replace <code>frontend/site_content.json</code> in the repository to publish them permanently. This prevents public visitors from rewriting your Space.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Site identity")
    name_col, tagline_col = st.columns(2)
    with name_col:
        brand_name = st.text_input("Site name", value=st.session_state.site_brand.get("name", "Qiskit Intuition"))
    with tagline_col:
        brand_tagline = st.text_input("Tagline", value=st.session_state.site_brand.get("tagline", ""))
    if st.button("Update site identity"):
        st.session_state.site_brand = {"name": brand_name.strip() or "Qiskit Intuition", "tagline": brand_tagline.strip()}
        st.success("Site identity updated for this session.")

    st.subheader("Lesson editor")
    lessons = course_lessons()
    lesson_index = st.selectbox(
        "Lesson to edit",
        range(len(lessons)),
        format_func=lambda index: f"{lessons[index]['number']}. {lessons[index]['title']}",
        key="studio_lesson_index",
    )
    lesson = lessons[lesson_index]

    with st.form(f"lesson_editor_{lesson_index}"):
        title = st.text_input("Title", value=lesson["title"])
        eyebrow = st.text_input("Section label", value=lesson["eyebrow"])
        duration = st.text_input("Estimated time", value=lesson["duration"])
        summary = st.text_area("Summary", value=lesson["summary"], height=90)
        objectives = st.text_area("Learning objectives — one per line", value="\n".join(lesson["objectives"]), height=130)
        explanation = st.text_area("Explanation — separate paragraphs with a blank line", value="\n\n".join(lesson["explanation"]), height=220)
        latex = st.text_input(
            "Formula (LaTeX)",
            value=lesson.get("latex", lesson["equation"]),
            help=r"Use KaTeX-compatible notation, for example: H|0\rangle = |+\rangle",
        )
        misconception = st.text_area("Common misconception", value=lesson["misconception"], height=100)
        checkpoint = st.text_area("Checkpoint question", value=lesson["checkpoint"], height=100)
        saved = st.form_submit_button("Save lesson in this session", type="primary")

    if saved:
        updated = dict(lesson)
        updated.update({
            "title": title.strip() or lesson["title"],
            "eyebrow": eyebrow.strip(),
            "duration": duration.strip(),
            "summary": summary.strip(),
            "objectives": [line.strip() for line in objectives.splitlines() if line.strip()],
            "explanation": [paragraph.strip() for paragraph in explanation.split("\n\n") if paragraph.strip()],
            "latex": latex.strip(),
            "misconception": misconception.strip(),
            "checkpoint": checkpoint.strip(),
        })
        new_lessons = deepcopy(lessons)
        new_lessons[lesson_index] = updated
        st.session_state.site_lessons = new_lessons
        st.success("Lesson saved. Open the learning path to preview it.")

    st.subheader("Import or export")
    export_payload = json.dumps(
        {"brand": st.session_state.site_brand, "lessons": course_lessons()},
        indent=2,
        ensure_ascii=False,
    )
    download_col, reset_col = st.columns(2)
    with download_col:
        st.download_button(
            "Download site_content.json",
            data=export_payload,
            file_name="site_content.json",
            mime="application/json",
            type="primary",
            use_container_width=True,
        )
    with reset_col:
        if st.button("Reset session to repository content", use_container_width=True):
            try:
                saved_content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
            except (OSError, ValueError, TypeError):
                saved_content = {}
            st.session_state.site_brand = saved_content.get("brand", {"name": "Qiskit Intuition", "tagline": "Quantum computing, built from first principles"})
            st.session_state.site_lessons = saved_content.get("lessons", deepcopy(LESSONS))
            st.rerun()

    uploaded = st.file_uploader("Import a site_content.json file", type=["json"])
    if uploaded is not None and st.button("Apply imported content"):
        try:
            imported = json.loads(uploaded.getvalue().decode("utf-8"))
            if not isinstance(imported.get("brand"), dict) or not isinstance(imported.get("lessons"), list) or not imported["lessons"]:
                raise ValueError("The file must contain a brand object and a non-empty lessons list.")
            st.session_state.site_brand = imported["brand"]
            st.session_state.site_lessons = imported["lessons"]
            st.success("Imported content applied to this session.")
        except (UnicodeDecodeError, ValueError, TypeError, KeyError) as exc:
            st.error(f"Could not import that file: {exc}")


def render_my_notebook() -> None:
    page_header(
        "Everything you've written",
        "My notebook",
        "Your predictions, explanations, margin notes and code from every lesson, in one place.",
    )
    data = notebook_store.snapshot(st.session_state)
    lessons = course_lessons()

    storage, backup = st.columns([1.3, 1], gap="large")
    with storage:
        if st.session_state.get("nb_storage_ok"):
            st.markdown("💾 **Saved automatically in this browser.** Come back any time on this device and pick up where you left off.")
        elif st.session_state.get("nb_hydrated"):
            st.markdown("⚠ **This browser won't let the page save locally** (common inside embedded pages). Download your notebook to keep it.")
        else:
            st.markdown("Connecting to this browser's storage…")
        st.caption("Nothing is sent to a server. Clearing your browser data erases the saved copy, so download a backup now and then.")
    with backup:
        st.download_button(
            "⬇  Download my notebook (.json)",
            data=notebook_store.dumps(data),
            file_name="quantum-lab-notebook.json",
            mime="application/json",
            type="primary",
            use_container_width=True,
        )
        st.download_button(
            "⬇  Download as a write-up (.md)",
            data=notebook_store.to_markdown(data, lessons),
            file_name="quantum-lab-notebook.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with st.expander("Restore a notebook or start fresh"):
        uploaded = st.file_uploader("Load a notebook file", type=["json"], key="nb_upload")
        if uploaded is not None and st.button("Restore this notebook", key="nb_restore"):
            restored = notebook_store.loads(uploaded.getvalue().decode("utf-8", errors="replace"))
            notebook_store.apply(st.session_state, notebook_store.merge(notebook_store.snapshot(st.session_state), restored))
            st.session_state.nb_toast = "Notebook restored."
            st.rerun()
        st.divider()
        confirm = st.checkbox("I want to erase everything in this notebook", key="nb_confirm_reset")
        if st.button("Start a fresh notebook", disabled=not confirm, key="nb_reset"):
            notebook_store.apply(st.session_state, notebook_store.empty())
            st.session_state.nb_toast = "Fresh notebook started."
            st.rerun()

    entries = [(index, lesson) for index, lesson in enumerate(lessons) if notebook_store.has_entry(data, lesson["id"])]
    if not entries:
        show_html('<p class="intro-note">Nothing written yet. Start lesson 1 — your predictions, notes and code will collect here.</p>')
        if st.button("Start lesson 1  →", type="primary", key="nb_start"):
            open_lesson(0)
        return

    for index, lesson in entries:
        lesson_id = lesson["id"]
        with st.container(key=f"nb-card-entry-{lesson_id}"):
            done = lesson_id in data["completed_lessons"]
            show_html(
                f'<div class="entry-head"><span>Lesson {index + 1}</span><strong>{html.escape(lesson["title"])}</strong>'
                f'{"<em>✓ written up</em>" if done else "<em>in progress</em>"}</div>'
            )
            quiz = lesson.get("quiz")
            answer = data["quiz_answers"].get(lesson_id)
            if quiz and answer is not None and answer < len(quiz["options"]):
                verdict = "✓" if answer == quiz["answer"] else "✗"
                show_html(
                    f'<p class="entry-line"><span>I predicted</span> {verdict} {html.escape(quiz["options"][answer])}</p>'
                )
            if lesson_id in data["reflections"]:
                show_html(f'<p class="entry-line"><span>I explained</span></p><p class="entry-hand">{html.escape(data["reflections"][lesson_id])}</p>')
            if lesson_id in data["notes"]:
                show_html(f'<div class="entry-note">{html.escape(data["notes"][lesson_id])}</div>')
            if lesson_id in data["code_attempts"]:
                label = "My code — solved ✓" if lesson_id in data["tasks_passed"] else "My code (not solved yet)"
                show_html(f'<p class="entry-line"><span>{label}</span></p>')
                st.code(data["code_attempts"][lesson_id], language="python")
            if st.button("Open this lesson", key=f"nb_open_{lesson_id}"):
                open_lesson(index, 0 if done else min(int(data["lesson_max_stage"].get(lesson_id, 0)), 5))


def footer() -> None:
    st.divider()
    st.caption("Intuition → prediction → experiment → math → Qiskit → explanation. Runs locally or on Hugging Face Spaces.")


init_state()
inject_education_theme(readable=st.session_state.reading_mode == "plain")
if st.session_state.pop("nb_restored", False):
    st.toast("Welcome back — your notebook was restored.", icon="📓")
if "nb_toast" in st.session_state:
    st.toast(st.session_state.pop("nb_toast"), icon="📓")
active_page = sidebar()

if active_page == "Course map":
    render_course_map()
elif active_page == "Learning path":
    render_learning_path()
elif active_page == "My notebook":
    render_my_notebook()
elif active_page == "Playground":
    render_playground()
else:
    render_content_studio()

footer()
notebook_store.sync_browser_storage()
