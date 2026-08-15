"""Context-aware quantum and Qiskit teaching support.

The deterministic path is intentionally useful on its own so the public
Hugging Face Space does not need a paid model key.  When GEMINI_API_KEY is
configured, the same structured context can be sent to Gemini for a more
open-ended response; failures always fall back to the local coach.
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TutorContext:
    code: str = ""
    execution_error: str = ""
    gates: list[dict[str, Any]] = field(default_factory=list)
    num_qubits: int = 1
    lesson_title: str = ""


TOPICS = {
    "qubit": (
        "A qubit is a two-level quantum system described by amplitudes for |0> and |1>. "
        "Those amplitudes can carry relative phase, so a qubit is richer than a classical random bit."
    ),
    "measurement": (
        "Measurement returns one classical sample. The statevector describes the exact ideal state before "
        "measurement; repeated shots estimate the probabilities predicted by that state."
    ),
    "superposition": (
        "Superposition means multiple basis-state amplitudes are present in one quantum state. Its useful "
        "feature is interference: later gates can make amplitudes add or cancel."
    ),
    "phase": (
        "Relative phase is the angle between amplitudes. A phase gate can leave the current 0/1 probabilities "
        "unchanged, then a mixing gate such as H converts that phase difference into visible probability."
    ),
    "entanglement": (
        "Entanglement is a joint state that cannot be split into independent states for each qubit. In a Bell "
        "state, the pair is pure even though either qubit viewed alone is maximally mixed."
    ),
    "bloch": (
        "The Bloch sphere represents one qubit: the poles are |0> and |1>, latitude controls the probability "
        "balance, and longitude represents relative phase. A mixed single-qubit state lies inside the sphere."
    ),
    "noise": (
        "Shot noise is ordinary sampling variation. Device noise comes from imperfect gates, readout, and "
        "decoherence. Compare both with an ideal simulation before judging a hardware result."
    ),
}


TEMPLATES = {
    "bell": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(2)
qc.h(0)          # Put q0 into superposition
qc.cx(0, 1)      # Correlate q1 with q0

state = Statevector.from_instruction(qc)
print(qc.draw(output="text"))
print(state.probabilities_dict())
""",
    "superposition": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(1)
qc.h(0)

state = Statevector.from_instruction(qc)
print(qc.draw(output="text"))
print(state.probabilities_dict())
""",
    "interference": """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(1)
qc.h(0)          # Create two amplitude paths
qc.z(0)          # Flip the phase of the |1> path
qc.h(0)          # Recombine the paths

state = Statevector.from_instruction(qc)
print(qc.draw(output="text"))
print(state.probabilities_dict())
""",
    "measurement": """from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

simulator = AerSimulator()
compiled = transpile(qc, simulator)
counts = simulator.run(compiled, shots=1024).result().get_counts()
print(counts)
""",
    "rotation": """import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(1)
qc.ry(np.pi / 3, 0)  # P(0) = cos^2(pi/6) = 0.75

state = Statevector.from_instruction(qc)
print(state.probabilities_dict())
""",
}


def _line(node: ast.AST) -> int | None:
    return getattr(node, "lineno", None)


def review_qiskit_code(code: str) -> list[dict[str, Any]]:
    """Return concrete, line-aware findings for common Qiskit mistakes."""
    findings: list[dict[str, Any]] = []
    if not code.strip():
        return [{
            "severity": "info",
            "line": None,
            "title": "No code to review",
            "detail": "Paste a Qiskit example or load one from the circuit lab.",
        }]

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [{
            "severity": "error",
            "line": exc.lineno,
            "title": "Python syntax error",
            "detail": f"{exc.msg}. Check the code around line {exc.lineno} before debugging the quantum logic.",
        }]

    circuit_sizes: dict[str, int] = {}
    measured_names: set[str] = set()
    has_output = False
    has_qiskit_import = False

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names]
            module = node.module if isinstance(node, ast.ImportFrom) else ""
            if module == "qiskit" or any(name.startswith("qiskit") for name in names):
                has_qiskit_import = True

        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func = node.value.func
            if (
                isinstance(func, ast.Name)
                and func.id == "QuantumCircuit"
                and node.value.args
                and isinstance(node.value.args[0], ast.Constant)
                and isinstance(node.value.args[0].value, int)
            ):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        circuit_sizes[target.id] = node.value.args[0].value

        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name) and node.func.id in {"print", "display"}:
            has_output = True

        if isinstance(node.func, ast.Name) and node.func.id == "execute":
            findings.append({
                "severity": "error",
                "line": _line(node),
                "title": "Removed execute() workflow",
                "detail": "Qiskit 1.x removed the old execute() shortcut. Transpile the circuit, then call backend.run(...).",
            })

        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            owner = node.func.value
            owner_name = owner.id if isinstance(owner, ast.Name) else None

            if method == "bind_parameters":
                findings.append({
                    "severity": "error",
                    "line": _line(node),
                    "title": "Deprecated parameter binding",
                    "detail": "Use assign_parameters(...) in current Qiskit.",
                })

            if method in {"draw", "probabilities_dict", "get_counts"}:
                has_output = True

            if method in {"measure", "measure_all"} and owner_name:
                measured_names.add(owner_name)

            if owner_name in circuit_sizes:
                n_qubits = circuit_sizes[owner_name]
                qargs: list[tuple[int, int | None]] = []
                if method in {"h", "x", "y", "z", "s", "sdg", "t", "tdg"} and node.args:
                    qargs.append((0, _constant_int(node.args[0])))
                elif method in {"rx", "ry", "rz"} and len(node.args) > 1:
                    qargs.append((1, _constant_int(node.args[1])))
                elif method in {"cx", "cz", "swap"} and len(node.args) > 1:
                    qargs.extend([(0, _constant_int(node.args[0])), (1, _constant_int(node.args[1]))])

                for _, qubit in qargs:
                    if qubit is not None and not 0 <= qubit < n_qubits:
                        findings.append({
                            "severity": "error",
                            "line": _line(node),
                            "title": "Qubit index is out of range",
                            "detail": f"{owner_name} has {n_qubits} qubit(s), so valid indices are 0 through {n_qubits - 1}; this call uses {qubit}.",
                        })

                if method in {"cx", "cz", "swap"} and len(node.args) > 1:
                    first, second = _constant_int(node.args[0]), _constant_int(node.args[1])
                    if first is not None and first == second:
                        findings.append({
                            "severity": "error",
                            "line": _line(node),
                            "title": "Two-qubit gate uses the same qubit twice",
                            "detail": f"{method.upper()} needs two different qubits for control/target or its two operands.",
                        })

            if method == "from_instruction" and node.args and isinstance(node.args[0], ast.Name):
                circuit_name = node.args[0].id
                if circuit_name in measured_names:
                    findings.append({
                        "severity": "error",
                        "line": _line(node),
                        "title": "Statevector requested after measurement",
                        "detail": "Create the Statevector from the unmeasured circuit, or copy the circuit before adding measurements.",
                    })

    if "from qiskit import Aer" in code or re.search(r"\bAer\.get_backend", code):
        findings.append({
            "severity": "error",
            "line": None,
            "title": "Aer import needs updating",
            "detail": "Install qiskit-aer and use `from qiskit_aer import AerSimulator`.",
        })

    if not has_qiskit_import and ("QuantumCircuit" in code or re.search(r"\bqc\.", code)):
        findings.append({
            "severity": "error",
            "line": 1,
            "title": "Missing Qiskit import",
            "detail": "Add `from qiskit import QuantumCircuit` before creating the circuit.",
        })

    if not has_output:
        findings.append({
            "severity": "suggestion",
            "line": None,
            "title": "Make the result observable",
            "detail": "Print the text circuit and either inspect a Statevector or run measured shots so the learner can verify the prediction.",
        })

    return _deduplicate(findings)


def _constant_int(node: ast.AST) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def _deduplicate(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    unique = []
    for item in findings:
        key = (item["title"], item.get("line"), item["detail"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def explain_execution_error(error: str) -> str:
    clean = (error or "").strip()
    lower = clean.lower()
    if not clean:
        return "No execution error was provided. Run the code first, then ask me to inspect the exact failure."
    if "index out of range" in lower or "indexerror" in lower:
        return "A gate or measurement refers to a qubit/classical bit that the circuit does not contain. Check the size passed to QuantumCircuit and remember that indexing starts at 0."
    if "no module named" in lower:
        module = re.search(r"No module named ['\"]([^'\"]+)", clean, re.IGNORECASE)
        name = module.group(1) if module else "that package"
        return f"Python cannot import `{name}` in this environment. For Aer simulation, the package name is `qiskit-aer` and the import is `from qiskit_aer import AerSimulator`."
    if "cannot import name 'aer'" in lower or "cannot import name \"aer\"" in lower:
        return "Aer moved out of the main Qiskit package. Use `from qiskit_aer import AerSimulator`, then transpile and run the circuit on that simulator."
    if "nameerror" in lower or "is not defined" in lower:
        return "A name is being used before it is imported or assigned. Find the final `NameError` line, then check spelling and execution order for that variable."
    if "syntax error" in lower or "syntaxerror" in lower:
        return "Python could not parse the code. Fix the first reported line before interpreting any Qiskit behavior; the real mistake is often an unclosed bracket or missing colon just above it."
    if "security restriction" in lower:
        return "The teaching sandbox blocked an operation that can access the computer or network. Keep the example to Qiskit, NumPy, Matplotlib, and pure Python calculations."
    return "Read the last line of the traceback first: it names the exception and usually the immediate cause. Then inspect the first line in your own code mentioned above it."


def describe_circuit(gates: list[dict[str, Any]], probabilities: dict[str, float] | None = None) -> str:
    if not gates:
        return "The circuit is empty, so every qubit remains in |0>. Add one gate and predict the change before checking the chart."

    names = [str(g.get("gate", "?")).upper() for g in gates]
    observations = [f"The circuit has {len(gates)} operation{'s' if len(gates) != 1 else ''}: " + " -> ".join(names) + "."]
    if names == ["H"]:
        observations.append("H creates equal |0> and |1> amplitudes from |0>, so the expected probabilities are 50% and 50%.")
    elif names[-3:] == ["H", "Z", "H"]:
        observations.append("The middle Z changes relative phase; the final H turns that hidden phase into a deterministic |1> outcome.")
    elif "CNOT" in names and "H" in names[: names.index("CNOT")]:
        observations.append("Because a control qubit was put in superposition before CNOT, the circuit can create entanglement rather than a simple conditional bit flip.")
    elif names[-1] in {"Z", "S", "T", "RZ"}:
        observations.append("The final gate primarily changes phase. The measurement bars may not move until another gate converts phase into interference.")

    if probabilities:
        likely = [(state, p) for state, p in probabilities.items() if p > 0.01]
        likely.sort(key=lambda item: item[1], reverse=True)
        rendered = ", ".join(f"{state}: {p:.1%}" for state, p in likely[:4])
        observations.append(f"The non-negligible ideal outcomes are {rendered}.")
    return " ".join(observations)


def answer_tutor(message: str, context: TutorContext | None = None, use_model: bool = True) -> dict[str, Any]:
    """Answer a learner with circuit/code context and a useful next action."""
    context = context or TutorContext()
    message = (message or "").strip()[:4000]
    context.code = (context.code or "")[:12000]
    context.execution_error = (context.execution_error or "")[-6000:]

    if use_model and os.getenv("GEMINI_API_KEY"):
        model_reply = _answer_with_gemini(message, context)
        if model_reply:
            return {"reply": model_reply, "provider": "gemini", "findings": review_qiskit_code(context.code) if context.code else []}

    reply, findings = _answer_locally(message, context)
    return {"reply": reply, "provider": "local", "findings": findings}


def _answer_locally(message: str, context: TutorContext) -> tuple[str, list[dict[str, Any]]]:
    lower = message.lower()
    findings = review_qiskit_code(context.code) if context.code else []

    if context.execution_error and any(word in lower for word in ("error", "fix", "debug", "failed", "wrong")):
        diagnosis = explain_execution_error(context.execution_error)
        review = _format_findings(findings)
        return (
            f"**What failed**\n\n{diagnosis}\n\n"
            f"**Code checks**\n\n{review}\n\n"
            "**Next step**\n\nFix the first error listed, run the code again, and use the new traceback only if it still fails."
        ), findings

    if context.code and any(word in lower for word in ("review", "inspect", "explain my code", "fix my code", "code help")):
        review = _format_findings(findings)
        purpose = _infer_code_purpose(context.code)
        walkthrough = _walkthrough_code(context.code)
        return (
            f"**What this code is doing**\n\n{purpose}\n\n"
            f"**Walkthrough**\n\n{walkthrough}\n\n"
            f"**Review**\n\n{review}\n\n"
            "**Next step**\n\nWrite down the expected basis-state probabilities before running it, then compare that prediction with the output."
        ), findings

    template_key = _template_key(lower)
    if template_key and any(word in lower for word in ("code", "build", "write", "show", "example", "implement", "circuit")):
        concept = TOPICS.get("entanglement" if template_key == "bell" else template_key, "This example uses current Qiskit syntax.")
        return (
            f"{concept}\n\n```python\n{TEMPLATES[template_key].rstrip()}\n```\n\n"
            "**Check your understanding:** predict the probability dictionary before running the code."
        ), findings

    if any(phrase in lower for phrase in ("current circuit", "my circuit", "what did i build", "explain circuit")):
        return describe_circuit(context.gates), findings

    for key, explanation in TOPICS.items():
        if key in lower or (key == "phase" and any(term in lower for term in ("z gate", "s gate", "rz"))):
            experiment = _topic_experiment(key)
            return f"{explanation}\n\n**Try this:** {experiment}", findings

    if any(word in lower for word in ("next", "practice", "exercise", "challenge")):
        lesson = f" for **{context.lesson_title}**" if context.lesson_title else ""
        return (
            f"Here is a focused exercise{lesson}: build H-Z-H on one qubit without looking at the result first. "
            "Predict the final state, run it, then remove the Z gate and explain why the answer changes.\n\n"
            "If that is already easy, create a Bell state and explain why only 00 and 11 appear."
        ), findings

    return (
        "I can help with a specific quantum concept, review the code in the workspace, explain the current circuit, "
        "or diagnose the last execution error.\n\n"
        "Try asking: `Why does H-Z-H end at |1>?`, `Review my code`, or `Fix the last error`."
    ), findings


def _format_findings(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "No obvious Qiskit or Python issue was found. The next check is whether the circuit's output matches your physical prediction."
    lines = []
    for item in findings[:6]:
        location = f" (line {item['line']})" if item.get("line") else ""
        lines.append(f"- **{item['title']}**{location}: {item['detail']}")
    return "\n".join(lines)


def _infer_code_purpose(code: str) -> str:
    lower = code.lower()
    if ".cx(" in lower and ".h(" in lower:
        return "It prepares a superposition and then uses a controlled operation, most likely to study Bell-state correlation or entanglement."
    if "aersimulator" in lower or ".measure(" in lower or ".measure_all(" in lower:
        return "It builds a measured circuit and samples classical counts from a simulator."
    if "statevector" in lower:
        return "It builds an ideal circuit and inspects its exact pre-measurement statevector or probabilities."
    if any(gate in lower for gate in (".rx(", ".ry(", ".rz(")):
        return "It uses parameterized rotations to control amplitude and/or relative phase."
    return "It creates a Qiskit circuit. Add an explicit statevector, probability, circuit drawing, or sampled-count output to make the learning goal testable."


def _walkthrough_code(code: str) -> str:
    notes: list[str] = []
    for line_number, raw_line in enumerate(code.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("from qiskit", "import qiskit")):
            notes.append(f"- **Line {line_number}:** imports the Qiskit tool used later; importing alone does not create or run a circuit.")
            continue
        circuit_match = re.search(r"(\w+)\s*=\s*QuantumCircuit\((\d+)(?:\s*,\s*(\d+))?\)", line)
        if circuit_match:
            classical = f" and {circuit_match.group(3)} classical bit(s)" if circuit_match.group(3) else ""
            notes.append(f"- **Line {line_number}:** creates `{circuit_match.group(1)}` with {circuit_match.group(2)} qubit(s){classical}. All qubits start in |0>.")
            continue
        gate_match = re.search(r"\.(h|x|y|z|s|t|rx|ry|rz|cx|cz|swap)\((.*)\)", line, re.IGNORECASE)
        if gate_match:
            gate = gate_match.group(1).upper()
            args = gate_match.group(2)
            physics = {
                "H": "mixes |0> and |1> amplitudes and can create superposition",
                "X": "swaps the |0> and |1> amplitudes",
                "Y": "performs a bit flip together with a phase change",
                "Z": "changes relative phase without moving immediate 0/1 probability",
                "S": "adds a quarter-turn of phase to the |1> amplitude",
                "T": "adds an eighth-turn of phase to the |1> amplitude",
                "RX": "rotates the qubit around the Bloch-sphere x axis",
                "RY": "rotates around y and directly changes the 0/1 probability balance",
                "RZ": "rotates relative phase around z",
                "CX": "flips the target when the control is |1>; with a superposed control it can entangle the pair",
                "CZ": "adds phase to the |11> branch",
                "SWAP": "exchanges the states of two qubits",
            }[gate]
            notes.append(f"- **Line {line_number}:** `{gate}({args})` {physics}.")
            continue
        if "Statevector.from_instruction" in line:
            notes.append(f"- **Line {line_number}:** evaluates the exact ideal state before measurement; this is not sampled shot data.")
            continue
        if ".measure" in line:
            notes.append(f"- **Line {line_number}:** maps quantum measurement results into classical bits for shot-based execution.")
            continue
        if "transpile(" in line:
            notes.append(f"- **Line {line_number}:** rewrites the circuit for the selected simulator or hardware target.")
            continue
        if ".run(" in line:
            notes.append(f"- **Line {line_number}:** executes the prepared circuit; `shots` controls how many samples are collected.")
            continue
        if line.startswith("print("):
            notes.append(f"- **Line {line_number}:** exposes a result so you can compare the program with your prediction.")

    return "\n".join(notes[:12]) or "The code is valid Python, but I could not identify a Qiskit circuit operation to walk through."


def _template_key(lower: str) -> str | None:
    if "bell" in lower or "entangl" in lower:
        return "bell"
    if "interference" in lower or ("hzh" in lower) or "h-z-h" in lower:
        return "interference"
    if "measure" in lower or "shots" in lower or "counts" in lower:
        return "measurement"
    if "rotation" in lower or "ry" in lower:
        return "rotation"
    if "superposition" in lower or "hadamard" in lower:
        return "superposition"
    return None


def _topic_experiment(topic: str) -> str:
    return {
        "qubit": "prepare |0>, apply RY(pi/3), and verify that P(0)=0.75.",
        "measurement": "run the same H circuit with 100 shots and 10,000 shots; compare how close each distribution is to 50/50.",
        "superposition": "apply H once, inspect the probabilities, then apply H again and explain the return to |0>.",
        "phase": "compare H-H with H-Z-H. The middle Z changes only phase at first, but the final H exposes it.",
        "entanglement": "build H on q0 followed by CNOT(0,1), then verify that only 00 and 11 have non-zero probability.",
        "bloch": "apply RY(pi/2), then RZ(pi/2), and track which coordinates change while the 0/1 probabilities stay fixed.",
        "noise": "run the Bell circuit in ideal and noisy modes and compare the probability assigned to 01 and 10.",
    }[topic]


def _answer_with_gemini(message: str, context: TutorContext) -> str | None:
    try:
        from google import genai

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        prompt = f"""You are the code coach inside an introductory Qiskit course.
Be technically precise, concise, and educational. Never use a fictional persona or praise filler.
When code is present, cite relevant line numbers, explain the physics intent, and propose current Qiskit 1.x code.
When an error is present, diagnose the first actionable cause. End with one verification step.

Current lesson: {context.lesson_title or 'not specified'}
Qubits: {context.num_qubits}
Circuit gates: {context.gates}
Code:
{context.code or '[none]'}
Last execution error:
{context.execution_error or '[none]'}

Learner question: {message}
"""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
        )
        text = getattr(response, "text", "")
        return text.strip() if text else None
    except Exception:  # noqa: BLE001 - provider failures must fall back locally
        return None
