"""Tests for the sandbox execution core in the FastAPI backend layout."""
import pytest

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


def test_functions_see_module_level_names():
    code = "import math\ndef f():\n    return math.pi\nprint(round(f(), 2))\n"
    result = execute_notebook_code(code)
    assert result["success"] is True, result["error"]
    assert "3.14" in result["stdout"]


def test_figures_are_returned_as_png_bytes():
    result = execute_notebook_code("plt.plot([0, 1], [1, 0])\n")
    assert result["success"] is True
    assert len(result["figures"]) == 1
    assert result["figures"][0].startswith(b"\x89PNG")


def test_infinite_loop_times_out():
    result = execute_notebook_code("while True:\n    pass\n", timeout=1)
    assert result["success"] is False
    assert "Timeout" in result["error"]


@pytest.mark.parametrize(
    "code",
    [
        "import importlib",
        "import io",
        "import matplotlib\nmatplotlib.os.getcwd()",
        "np.loadtxt('/etc/hostname')",
        "().__class__.__base__",
        "from qiskit import sys",
        "qc = QuantumCircuit(1)\nqc.draw(output='text', filename='x.txt')",
    ],
)
def test_escape_attempts_are_blocked(code):
    result = execute_notebook_code(code)
    assert result["success"] is False
    assert "Security Restriction" in result["error"]


def test_memory_hungry_program_is_stopped_with_a_clear_message():
    result = execute_notebook_code("big = np.ones(600_000_000)\nprint(big.sum())\n")
    assert result["success"] is False
    assert "Memory limit" in result["error"]


def test_normal_qiskit_program_fits_within_the_memory_cap():
    code = (
        "from qiskit import QuantumCircuit, transpile\n"
        "from qiskit_aer import AerSimulator\n"
        "qc = QuantumCircuit(12)\n"
        "qc.h(range(12))\n"
        "qc.measure_all()\n"
        "sim = AerSimulator()\n"
        "print(len(sim.run(transpile(qc, sim), shots=200).result().get_counts()) > 1)\n"
    )
    result = execute_notebook_code(code)
    assert result["success"] is True, result["error"]
    assert "True" in result["stdout"]
