"""Restricted teaching sandbox for learner-written Qiskit code.

Two layers of protection:

1. Static AST checks: only allowlisted modules may be imported, dangerous
   builtins are unavailable, and dunder / module-escape attribute access is
   rejected before anything runs.
2. Process isolation: code runs in a fresh Python process with a wall-clock timeout,
   so infinite loops or runaway simulations cannot hang the app.

Pure-Python sandboxing is best-effort; do not expose this to untrusted users
without an additional OS-level boundary (container, seccomp, etc.).
"""

import ast
import contextlib
import io
import os
import pickle
import subprocess
import sys
import tempfile
import traceback

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "qiskit-intuition-mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

DEFAULT_TIMEOUT_SECONDS = 15
MAX_OUTPUT_CHARS = 20_000
MAX_FIGURES = 8
# Extra memory a learner program may allocate beyond the interpreter's own
# footprint. Stops one heavy program from exhausting a small shared host.
MEMORY_HEADROOM_BYTES = 1024 ** 3
# Keep numerical libraries single-threaded so concurrent learners share CPUs fairly.
_SINGLE_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "RAYON_NUM_THREADS": "1",
}

# Only these top-level packages may be imported by learner code.
ALLOWED_MODULES = {
    "qiskit", "qiskit_aer", "numpy", "matplotlib", "math", "cmath", "random",
    "itertools", "functools", "collections", "fractions", "decimal", "statistics",
    "typing", "dataclasses", "copy", "string", "re", "operator", "json", "time",
}

BLOCKED_CALLS = {
    "eval", "exec", "compile", "open", "__import__", "getattr", "setattr",
    "delattr", "globals", "locals", "vars", "breakpoint", "input",
}

# Attribute names that reach the OS, the interpreter, or the filesystem
# (e.g. ``matplotlib.os`` or ``np.loadtxt``).
BLOCKED_ATTRS = {
    "os", "sys", "subprocess", "shutil", "socket", "importlib", "builtins",
    "pathlib", "io", "ctypes", "pickle", "marshal", "signal", "threading",
    "multiprocessing", "system", "popen", "spawn", "fork",
    "load", "loads", "loadtxt", "genfromtxt", "fromfile", "tofile", "memmap",
    "save", "savez", "savez_compressed", "savetxt", "savefig", "ctypeslib",
}

# Dunder attributes learners legitimately read.
ALLOWED_DUNDERS = {"__name__", "__doc__", "__version__", "__init__", "__len__"}

BLOCKED_KEYWORDS = {"filename", "file", "fname"}

_orig_import = __import__


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level or name.split(".")[0] not in ALLOWED_MODULES:
        raise ImportError(f"Security Restriction: Module '{name}' is not available in the sandbox.")
    return _orig_import(name, globals, locals, fromlist, level)


SAFE_BUILTINS = {
    "__import__": _safe_import,
    "__build_class__": __build_class__,
    "__name__": "__sandbox__",
    "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
    "callable": callable, "chr": chr, "complex": complex, "dict": dict,
    "divmod": divmod, "enumerate": enumerate, "filter": filter, "float": float,
    "format": format, "frozenset": frozenset, "hasattr": hasattr, "hash": hash,
    "hex": hex, "int": int, "isinstance": isinstance, "issubclass": issubclass,
    "iter": iter, "len": len, "list": list, "map": map, "max": max, "min": min,
    "next": next, "object": object, "oct": oct, "ord": ord, "pow": pow,
    "print": print, "property": property, "range": range, "repr": repr,
    "reversed": reversed, "round": round, "set": set, "slice": slice,
    "sorted": sorted, "staticmethod": staticmethod, "classmethod": classmethod,
    "str": str, "sum": sum, "super": super, "tuple": tuple, "type": type, "zip": zip,
    "True": True, "False": False, "None": None,
    "Exception": Exception, "ArithmeticError": ArithmeticError,
    "AssertionError": AssertionError, "AttributeError": AttributeError,
    "ImportError": ImportError, "IndexError": IndexError, "KeyError": KeyError,
    "NameError": NameError, "NotImplementedError": NotImplementedError,
    "RuntimeError": RuntimeError, "StopIteration": StopIteration,
    "TypeError": TypeError, "ValueError": ValueError,
    "ZeroDivisionError": ZeroDivisionError,
}


def validate_code_safety(code_string: str):
    """Return an error message if the code uses anything outside the sandbox, else None."""
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return f"Syntax Error: {e.msg} at line {e.lineno}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_MODULES:
                    return f"Security Restriction: Importing '{alias.name}' is not available in the sandbox."
        elif isinstance(node, ast.ImportFrom):
            if node.level or not node.module or node.module.split(".")[0] not in ALLOWED_MODULES:
                return f"Security Restriction: Importing from '{node.module}' is not available in the sandbox."
            for alias in node.names:
                if alias.name in BLOCKED_ATTRS:
                    return f"Security Restriction: Importing '{alias.name}' is prohibited in the sandbox."
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                return f"Security Restriction: Function '{node.func.id}()' is prohibited in the sandbox."
            for kw in node.keywords:
                if kw.arg in BLOCKED_KEYWORDS:
                    return f"Security Restriction: Writing files ('{kw.arg}=') is prohibited in the sandbox."
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            is_dunder = attr.startswith("__") and attr.endswith("__")
            if attr in BLOCKED_ATTRS or (is_dunder and attr not in ALLOWED_DUNDERS):
                return f"Security Restriction: Accessing '{attr}' is prohibited in the sandbox."
        elif isinstance(node, ast.Name):
            if node.id.startswith("__") and node.id not in ALLOWED_DUNDERS:
                return f"Security Restriction: Name '{node.id}' is prohibited in the sandbox."

    return None


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + f"\n... output truncated after {MAX_OUTPUT_CHARS} characters"


def _figure_to_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    return buf.getvalue()


def _run(code_string: str) -> dict:
    """Execute code in the current process and return a picklable result."""
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    existing_figs = set(plt.get_fignums())

    # A single namespace so functions defined by the learner can see
    # module-level names (separate globals/locals breaks closures).
    namespace = {
        "__builtins__": SAFE_BUILTINS,
        "__name__": "__sandbox__",
        "np": np,
        "qiskit": qiskit,
        "QuantumCircuit": QuantumCircuit,
        "Statevector": Statevector,
        "plt": plt,
    }

    # Print numpy scalars as plain numbers (numpy 2 shows np.float64(...)).
    with contextlib.suppress(Exception):
        np.set_printoptions(legacy="1.25")

    success = True
    error_message = None
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        try:
            exec(compile(code_string, "<sandbox>", "exec"), namespace)
        except MemoryError:
            success = False
            error_message = (
                f"Memory limit: the program tried to use more than about {MEMORY_HEADROOM_BYTES // 1024 ** 3} GB. "
                "Use fewer qubits or shots, or smaller arrays. (Each extra qubit doubles a statevector's size.)"
            )
        except Exception:
            success = False
            error_message = _truncate(traceback.format_exc())

    figures = []
    for num in sorted(set(plt.get_fignums()) - existing_figs):
        fig = plt.figure(num)
        if len(figures) < MAX_FIGURES:
            try:
                figures.append(_figure_to_png(fig))
            except Exception:
                pass
        plt.close(num)

    return {
        "success": success,
        "stdout": _truncate(stdout_buffer.getvalue()),
        "stderr": _truncate(stderr_buffer.getvalue()),
        "error": error_message,
        "figures": figures,
    }


def _failure(message: str) -> dict:
    return {"success": False, "stdout": "", "stderr": message, "error": message, "figures": []}


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def execute_notebook_code(code_string, timeout: float = DEFAULT_TIMEOUT_SECONDS):
    """Validate and run learner code in a fresh, time-limited Python process.

    A new interpreter per run (rather than ``fork``) is deliberate: forking the
    multi-threaded app server deadlocks once Qiskit's Rust thread pool has been
    used (e.g. by ``transpile``), and a fresh process never inherits app state.

    Returns a dict with ``success``, ``stdout``, ``stderr``, ``error`` and
    ``figures`` (a list of PNG images as bytes).
    """
    security_violation = validate_code_safety(code_string)
    if security_violation:
        return _failure(security_violation)

    env = {**os.environ, **_SINGLE_THREAD_ENV}
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [_PROJECT_ROOT, env.get("PYTHONPATH")]))
    with tempfile.TemporaryDirectory(prefix="qi-sandbox-") as workdir:
        result_path = os.path.join(workdir, "result.pickle")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "backend.core.notebook_engine", result_path, str(timeout)],
                input=code_string,
                text=True,
                capture_output=True,
                timeout=timeout,
                cwd=workdir,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return _failure(
                f"Timeout: execution exceeded {timeout:g} seconds and was stopped. "
                "Check for infinite loops or reduce the number of shots/qubits."
            )
        try:
            with open(result_path, "rb") as handle:
                return pickle.load(handle)
        except (OSError, EOFError, pickle.UnpicklingError):
            detail = (completed.stderr or "").strip()[-2000:]
            return _failure("The sandbox process exited unexpectedly (possibly out of memory).\n" + detail)


def _current_address_space() -> int | None:
    try:
        with open("/proc/self/status", encoding="ascii") as status:
            for line in status:
                if line.startswith("VmSize:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError):
        pass
    return None


def _limit_memory(timeout: float) -> None:
    """Cap this process at its current size plus MEMORY_HEADROOM_BYTES (POSIX only)."""
    try:
        import resource
    except ImportError:  # Windows: rely on the timeout alone
        return
    current = _current_address_space()
    if current is not None:
        limit = current + MEMORY_HEADROOM_BYTES
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    cpu = int(timeout) + 2
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))


def _worker_main(result_path: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> None:
    code_string = sys.stdin.read()
    try:
        _limit_memory(timeout)
        result = _run(code_string)
    except Exception:
        result = _failure(traceback.format_exc())
    with open(result_path, "wb") as handle:
        pickle.dump(result, handle)


if __name__ == "__main__":
    _worker_main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_TIMEOUT_SECONDS)
