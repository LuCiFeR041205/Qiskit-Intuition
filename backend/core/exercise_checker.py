"""Auto-check learner Qiskit code against a reference solution.

The learner's program must leave a ``QuantumCircuit`` in a variable named
``qc``. Both programs run in the sandbox with a short epilogue that reports the
circuit's exact state and operation counts, which are then compared.
"""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np

from backend.core.notebook_engine import execute_notebook_code

MARKER = "<<QI-CHECK>>"

EPILOGUE = f"""

import json as _qi_json
from qiskit import QuantumCircuit as _QiCircuit
from qiskit.quantum_info import Statevector as _QiState
if not isinstance(qc, _QiCircuit):
    raise TypeError("`qc` must be a QuantumCircuit")
_qi_circ = qc.remove_final_measurements(inplace=False)
_qi_state = _QiState(_qi_circ)
print("{MARKER}" + _qi_json.dumps({{
    "amps": [[float(a.real), float(a.imag)] for a in _qi_state.data],
    "ops": {{str(k): int(v) for k, v in qc.count_ops().items()}},
}}))
"""


def strip_check_output(stdout: str) -> str:
    """Remove the checker's machine-readable line from learner-visible output."""
    return "\n".join(line for line in stdout.splitlines() if not line.startswith(MARKER))


def run_and_inspect(code: str) -> dict:
    """Run ``code`` and return {"ok", "amps", "ops", "stdout", "error"}."""
    result = execute_notebook_code(code + EPILOGUE)
    stdout = result.get("stdout", "")
    payload = None
    for line in stdout.splitlines():
        if line.startswith(MARKER):
            payload = json.loads(line[len(MARKER):])
    if not result.get("success") or payload is None:
        error = result.get("error") or result.get("stderr") or "The program did not finish."
        if "name 'qc' is not defined" in error:
            error = "Store your circuit in a variable named `qc` so it can be checked."
        return {"ok": False, "error": error, "stdout": strip_check_output(stdout)}
    amps = np.array([complex(re, im) for re, im in payload["amps"]])
    return {"ok": True, "amps": amps, "ops": payload["ops"], "stdout": strip_check_output(stdout), "error": None}


@lru_cache(maxsize=64)
def _reference(solution: str) -> dict:
    return run_and_inspect(solution)


def _probabilities(amps: np.ndarray) -> np.ndarray:
    return np.abs(amps) ** 2


def check_code_task(code: str, task: dict) -> dict:
    """Compare learner code with ``task["solution"]``.

    ``task["match"]`` is ``"state"`` (default, equal up to global phase) or
    ``"probs"`` (equal measurement distribution). ``task["required_ops"]`` lists
    Qiskit operation names (``"h"``, ``"cx"``...) the learner must use.
    """
    learner = run_and_inspect(code)
    if not learner["ok"]:
        return {"passed": False, "message": learner["error"], "stdout": learner.get("stdout", "")}

    reference = _reference(task["solution"])
    if not reference["ok"]:
        return {"passed": False, "message": "The reference solution failed to run.", "stdout": learner["stdout"]}

    if learner["amps"].shape != reference["amps"].shape:
        want = int(np.log2(len(reference["amps"])))
        have = int(np.log2(len(learner["amps"])))
        return {
            "passed": False,
            "message": f"Your circuit has {have} qubit(s); this task needs {want}.",
            "stdout": learner["stdout"],
        }

    missing = [op for op in task.get("required_ops", []) if op not in learner["ops"]]
    if missing:
        return {
            "passed": False,
            "message": "Use " + ", ".join(f"`{op}`" for op in missing) + " in your circuit for this task.",
            "stdout": learner["stdout"],
        }

    if task.get("match", "state") == "probs":
        distance = 0.5 * float(np.sum(np.abs(_probabilities(learner["amps"]) - _probabilities(reference["amps"]))))
        passed = distance < 0.03
        detail = "measurement probabilities"
    else:
        fidelity = float(np.abs(np.vdot(reference["amps"], learner["amps"])) ** 2)
        passed = fidelity > 0.99
        detail = f"state (fidelity {fidelity:.3f})"

    if passed:
        message = f"Correct — your circuit matches the target {detail}."
    else:
        width = int(np.log2(len(learner["amps"])))
        have = _probabilities(learner["amps"])
        want = _probabilities(reference["amps"])
        rows = [
            f"|{i:0{width}b}⟩ yours {have[i]:.0%} · target {want[i]:.0%}"
            for i in range(len(have))
            if have[i] > 1e-6 or want[i] > 1e-6
        ]
        message = f"Not yet — the {detail.split(' (')[0]} differs. " + "; ".join(rows)
        if task.get("match", "state") == "state" and np.allclose(have, want, atol=0.02):
            message += ". The probabilities agree, so the difference is a relative phase."
    return {"passed": passed, "message": message, "stdout": learner["stdout"]}
