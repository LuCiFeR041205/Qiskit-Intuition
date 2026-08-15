"""Public learning experience for Qiskit Intuition.

The app runs as a single Streamlit process on Hugging Face Spaces. Simulation,
safe code execution, and tutoring all have in-process paths, so a separate API
server is optional rather than required.
"""

from __future__ import annotations

import html
import json
import math
import os
from copy import deepcopy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import matplotlib.pyplot as plt
import streamlit as st

from backend.core.notebook_engine import execute_notebook_code
from backend.core.quantum_engine import QuantumEngine
from backend.core.teaching_assistant import (
    TutorContext,
    answer_tutor,
    describe_circuit,
    review_qiskit_code,
)
from frontend.education_theme import inject_education_theme
from frontend.learning_content import LESSONS, PRACTICE, PRESETS

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


def init_state() -> None:
    try:
        saved_content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        saved_content = {}

    default_brand = {
        "name": "Qiskit Intuition",
        "tagline": "Quantum computing, built from first principles",
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
    preset = PRESETS[name]
    st.session_state.num_qubits = preset["qubits"]
    st.session_state.gates = [dict(gate) for gate in preset["gates"]]
    st.session_state.noisy = False
    sync_workspace_to_circuit()


def sync_workspace_to_circuit() -> None:
    st.session_state.workspace_code = build_engine().get_qiskit_code()
    st.session_state.last_result = None


def sidebar() -> str:
    brand = st.session_state.site_brand
    brand_name = html.escape(str(brand.get("name", "Qiskit Intuition")))
    brand_tagline = html.escape(str(brand.get("tagline", "Quantum computing, built from first principles")))
    st.sidebar.markdown(
        f"""
<div class="brand">
  <div class="brand-mark">Q</div>
  <div class="brand-name">{brand_name}</div>
  <div class="brand-subtitle">{brand_tagline}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "Navigation",
        ["Course", "Circuit lab", "Code lab", "Practice", "Content studio"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()
    st.sidebar.caption("COURSE PROGRESS")
    lesson_index = int(st.session_state.selected_lesson)
    lessons = course_lessons()
    lesson_index = min(lesson_index, len(lessons) - 1)
    st.sidebar.progress((lesson_index + 1) / len(lessons))
    st.sidebar.caption(f"Lesson {lesson_index + 1} of {len(lessons)}")

    st.sidebar.divider()
    if os.getenv("GEMINI_API_KEY"):
        coach_label = "Model-enhanced coach"
    else:
        coach_label = "Built-in code coach"
    st.sidebar.markdown(
        f"""
<div class="status-note"><span class="status-dot"></span>{coach_label}</div>
<p style="font-size:.74rem;color:#aebdc6;line-height:1.5;margin-top:.5rem;">
Simulation, lessons, and code review work without a separate server or API key.
</p>
        """,
        unsafe_allow_html=True,
    )
    return page


def page_header(eyebrow: str, title: str, intro: str) -> None:
    st.markdown(f'<div class="eyebrow">{html.escape(eyebrow)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-intro">{html.escape(intro)}</div>', unsafe_allow_html=True)


def render_course() -> None:
    lessons = course_lessons()
    lesson_titles = [f"{item['number']}. {item['title']}" for item in lessons]
    selected = st.selectbox(
        "Choose a lesson",
        range(len(LESSONS)),
        index=int(st.session_state.selected_lesson),
        format_func=lambda index: lesson_titles[index],
    )
    st.session_state.selected_lesson = selected
    lesson = lessons[selected]

    page_header(lesson["eyebrow"], lesson["title"], lesson["summary"])
    st.markdown(
        f"""
<div class="lesson-meta">
  <span class="meta-pill">Lesson {lesson['number']} of {len(lessons)}</span>
  <span class="meta-pill">{html.escape(lesson['duration'])}</span>
  <span class="meta-pill">Includes a lab</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.5, 1], gap="large")
    with left:
        st.subheader("The core idea")
        for paragraph in lesson["explanation"]:
            st.write(paragraph)
        st.latex(lesson.get("latex") or lesson["equation"])

    with right:
        objectives = "".join(f"<li>{html.escape(item)}</li>" for item in lesson["objectives"])
        st.markdown(
            f"""
<div class="content-card">
  <strong>By the end, you can…</strong>
  <ul class="objective-list">{objectives}</ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="callout warning">
  <strong>Common misconception</strong>
  <p>{html.escape(lesson['misconception'])}</p>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Test the idea")
    st.markdown(
        """
<div class="step-row"><div class="step-number">1</div><div><strong>Predict</strong><br>Write down what you expect before running the circuit.</div></div>
<div class="step-row"><div class="step-number">2</div><div><strong>Build</strong><br>Load the worked example, then change one gate at a time.</div></div>
<div class="step-row"><div class="step-number">3</div><div><strong>Explain</strong><br>Use amplitudes or joint probabilities—not just an analogy—to explain the result.</div></div>
        """,
        unsafe_allow_html=True,
    )

    action, prompt = st.columns([1, 2], gap="large")
    with action:
        if st.button(f"Load “{lesson['preset']}” in the lab  →", type="primary", use_container_width=True):
            load_preset(lesson["preset"])
            st.success("Example loaded. Open Circuit lab from the navigation.")
    with prompt:
        st.markdown(
            f"""
<div class="callout">
  <strong>Checkpoint</strong>
  <p>{html.escape(lesson['checkpoint'])}</p>
</div>
            """,
            unsafe_allow_html=True,
        )

    previous, next_col = st.columns(2)
    with previous:
        if selected > 0 and st.button("←  Previous lesson", use_container_width=True):
            st.session_state.selected_lesson = selected - 1
            st.rerun()
    with next_col:
        if selected < len(lessons) - 1 and st.button("Next lesson  →", use_container_width=True):
            st.session_state.selected_lesson = selected + 1
            st.rerun()


def render_circuit_lab() -> None:
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
            st.session_state.num_qubits = qubits
            st.session_state.gates = [
                gate for gate in st.session_state.gates
                if gate["target"] < qubits and (gate.get("control") is None or gate["control"] < qubits)
            ]
            sync_workspace_to_circuit()
            st.rerun()
    with noise_col:
        st.toggle("Include device noise", key="noisy", help="Adds a simple depolarizing-noise model to sampled probabilities.")

    st.subheader("1. Build")
    gate_col, target_col, parameter_col, add_col = st.columns([1.2, 1, 1.2, 0.9])
    with gate_col:
        gate_name = st.selectbox("Gate", ["H", "X", "Y", "Z", "S", "T", "RX", "RY", "RZ", "CNOT"])
    with target_col:
        target = st.selectbox("Target", list(range(st.session_state.num_qubits)), format_func=lambda q: f"q{q}")
    control = None
    angle = None
    with parameter_col:
        if gate_name == "CNOT":
            valid_controls = [q for q in range(st.session_state.num_qubits) if q != target]
            if valid_controls:
                control = st.selectbox("Control", valid_controls, format_func=lambda q: f"q{q}")
            else:
                st.selectbox("Control", ["Add another qubit"], disabled=True)
        elif gate_name in {"RX", "RY", "RZ"}:
            angle_pi = st.slider("Angle (× pi)", -2.0, 2.0, 0.5, 0.05)
            angle = angle_pi * math.pi
        else:
            st.selectbox("Parameter", ["None"], disabled=True)
    with add_col:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        can_add = gate_name != "CNOT" or control is not None
        add_clicked = st.button("＋  Add gate", type="primary", use_container_width=True, disabled=not can_add)

    if add_clicked:
        operation = {"gate": gate_name, "target": target, "control": control}
        if angle is not None:
            operation["angle"] = angle
        st.session_state.gates.append(operation)
        sync_workspace_to_circuit()
        st.rerun()

    sequence = " -> ".join(g["gate"] for g in st.session_state.gates) or "No gates yet"
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
    angles = engine.run_simulation()

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
        figure = engine.get_circuit_figure()
        st.pyplot(figure, clear_figure=True, use_container_width=True)
        plt.close(figure)
    with probability_col:
        st.markdown("**Measurement probabilities**")
        render_probabilities(probabilities)
        st.caption("Bit strings use Qiskit's display order. q0 is the rightmost bit.")

    st.subheader("3. Explain")
    st.markdown(
        f"<div class='callout'><strong>What the circuit says</strong><p>{html.escape(describe_circuit(st.session_state.gates, probabilities))}</p></div>",
        unsafe_allow_html=True,
    )

    with st.expander("Inspect single-qubit state readouts"):
        cols = st.columns(st.session_state.num_qubits)
        for qubit, data in angles.items():
            with cols[qubit]:
                radius = data["purity"]
                label = "pure" if radius > 0.98 else "mixed / entangled"
                st.metric(f"q{qubit}", label)
                st.caption(f"x {data['x']:.3f} · y {data['y']:.3f} · z {data['z']:.3f}")
                st.caption(f"Bloch radius {radius:.3f}")

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
        if st.button("Open this circuit in the Code lab  →", type="primary"):
            sync_workspace_to_circuit()
            st.success("Code lab updated.")


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


def render_probabilities(probabilities: dict[str, float]) -> None:
    rows = []
    for state, probability in probabilities.items():
        pct = max(0.0, min(100.0, probability * 100.0))
        rows.append(
            f"""
<div class="prob-row">
  <div class="prob-label">|{html.escape(state)}⟩</div>
  <div class="prob-track"><div class="prob-fill" style="width:{pct:.3f}%"></div></div>
  <div class="prob-value">{probability:.1%}</div>
</div>
            """
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_code_lab() -> None:
    page_header(
        "Qiskit workspace",
        "Code lab",
        "Write and run short Qiskit programs in a restricted teaching sandbox. The coach reviews the actual code and the last traceback—not a generic prompt.",
    )

    toolbar_left, toolbar_right = st.columns([1, 2])
    with toolbar_left:
        if st.button("Load code from Circuit lab", use_container_width=True):
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
                st.pyplot(figure, use_container_width=True)
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


def render_practice() -> None:
    page_header(
        "Deliberate practice",
        "Practice",
        "Each exercise has one observable target. Build it in the Circuit lab, then return here to check the current circuit.",
    )

    selected = st.selectbox(
        "Exercise",
        range(len(PRACTICE)),
        index=int(st.session_state.selected_practice),
        format_func=lambda index: f"{index + 1}. {PRACTICE[index]['title']}",
    )
    st.session_state.selected_practice = selected
    exercise = PRACTICE[selected]

    st.markdown(
        f"""
<div class="lesson-meta">
  <span class="meta-pill">{html.escape(exercise['level'])}</span>
  <span class="meta-pill">{exercise['qubits']} qubit{'s' if exercise['qubits'] != 1 else ''}</span>
</div>
<div class="content-card">
  <strong>Goal</strong>
  <p>{html.escape(exercise['goal'])}</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Show one hint"):
        st.write(exercise["hint"])

    start_col, check_col = st.columns(2)
    with start_col:
        if st.button("Start with an empty circuit", use_container_width=True):
            st.session_state.num_qubits = exercise["qubits"]
            st.session_state.gates = []
            sync_workspace_to_circuit()
            st.success("Workspace prepared. Open Circuit lab to build your answer.")
    with check_col:
        check_clicked = st.button("Check current circuit", type="primary", use_container_width=True)

    if check_clicked:
        if st.session_state.num_qubits != exercise["qubits"]:
            st.error(f"This exercise requires exactly {exercise['qubits']} qubit(s).")
            return
        engine = build_engine()
        actual = engine.get_probabilities()
        target = exercise["target"]
        states = set(actual) | set(target)
        max_error = max(abs(actual.get(state, 0.0) - target.get(state, 0.0)) for state in states)
        names = [gate["gate"] for gate in st.session_state.gates]
        required_ok = all(name in names for name in exercise.get("required", []))
        forbidden_ok = all(name not in names for name in exercise.get("forbidden", []))

        if max_error < 0.025 and required_ok and forbidden_ok:
            st.success("Correct. The circuit reaches the target distribution and satisfies the gate constraints.")
            lessons = course_lessons()
            st.markdown(f"**Explain it:** {lessons[min(selected + 1, len(lessons) - 1)]['checkpoint']}")
        else:
            st.warning("Not there yet. Compare the target and current probabilities, then change one gate.")
            comparison = []
            for state in sorted(states):
                comparison.append(f"|{state}>  target {target.get(state, 0.0):.1%}  ·  current {actual.get(state, 0.0):.1%}")
            st.code("\n".join(comparison), language="text")
            if not required_ok:
                st.caption("The solution has not used every required gate yet.")
            if not forbidden_ok:
                st.caption("The circuit uses a gate that this exercise excludes.")


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
        st.success("Lesson saved. Open Course to preview it.")

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


def footer() -> None:
    st.divider()
    st.caption("Built for learning: predict first, simulate second, explain third. Compatible with local Streamlit and Hugging Face Spaces.")


inject_education_theme()
init_state()
active_page = sidebar()

if active_page == "Course":
    render_course()
elif active_page == "Circuit lab":
    render_circuit_lab()
elif active_page == "Code lab":
    render_code_lab()
elif active_page == "Practice":
    render_practice()
else:
    render_content_studio()

footer()
