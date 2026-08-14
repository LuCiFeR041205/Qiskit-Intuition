"""Tests for the sandbox execution core in the FastAPI backend layout."""
from backend.core.notebook_engine import execute_notebook_code


def test_simple_execution():
    result = execute_notebook_code("print('hello from sandbox')")
    assert result["success"] is True
    assert "hello from sandbox" in result["stdout"]


def test_qiskit_runs_in_sandbox():
    code = (
        "from qiskit import QuantumCircuit\n"
        "qc = QuantumCircuit(1)\n"
        "qc.h(0)\n"
        "print(qc.num_qubits)\n"
    )
    result = execute_notebook_code(code)
    assert result["success"] is True
    assert "1" in result["stdout"]


def test_error_is_captured():
    result = execute_notebook_code("raise ValueError('boom')")
    assert result["success"] is False
    assert "boom" in result["error"]
