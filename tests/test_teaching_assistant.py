from backend.core.teaching_assistant import (
    TutorContext,
    answer_tutor,
    describe_circuit,
    explain_execution_error,
    review_qiskit_code,
)


def titles(findings):
    return {item["title"] for item in findings}


def test_review_detects_out_of_range_qubit():
    code = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(1)\nprint(qc)"
    assert "Qubit index is out of range" in titles(review_qiskit_code(code))


def test_review_detects_same_control_and_target():
    code = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.cx(0, 0)\nprint(qc)"
    assert "Two-qubit gate uses the same qubit twice" in titles(review_qiskit_code(code))


def test_review_flags_removed_execute_workflow():
    code = "from qiskit import execute\nresult = execute(qc, backend)\nprint(result)"
    assert "Removed execute() workflow" in titles(review_qiskit_code(code))


def test_review_accepts_current_bell_example():
    code = """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
state = Statevector.from_instruction(qc)
print(state.probabilities_dict())
"""
    errors = [item for item in review_qiskit_code(code) if item["severity"] == "error"]
    assert errors == []


def test_tutor_generates_current_qiskit_bell_code():
    answer = answer_tutor("Show me Qiskit code for a Bell state", use_model=False)
    assert "qc.h(0)" in answer["reply"]
    assert "qc.cx(0, 1)" in answer["reply"]
    assert "Statevector.from_instruction" in answer["reply"]


def test_tutor_uses_execution_error_context():
    context = TutorContext(
        code="from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(2)",
        execution_error="IndexError: index out of range",
    )
    answer = answer_tutor("Fix the last error", context=context, use_model=False)
    assert "valid indices" in answer["reply"]
    assert "line 3" in answer["reply"]


def test_tutor_walks_through_real_code_lines():
    context = TutorContext(
        code="from qiskit import QuantumCircuit\nqc = QuantumCircuit(1)\nqc.h(0)\nprint(qc)",
    )
    answer = answer_tutor("Explain my code", context=context, use_model=False)
    assert "Line 2" in answer["reply"]
    assert "All qubits start in |0>" in answer["reply"]
    assert "Line 3" in answer["reply"]
    assert "superposition" in answer["reply"]


def test_circuit_description_explains_interference():
    gates = [
        {"gate": "H", "target": 0},
        {"gate": "Z", "target": 0},
        {"gate": "H", "target": 0},
    ]
    description = describe_circuit(gates, {"0": 0.0, "1": 1.0})
    assert "hidden phase" in description
    assert "1: 100.0%" in description


def test_error_explanation_updates_aer_import():
    text = explain_execution_error("ImportError: cannot import name 'Aer' from 'qiskit'")
    assert "qiskit_aer" in text
