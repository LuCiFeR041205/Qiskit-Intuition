import io
import os
import sys
import ast
import tempfile
import contextlib
import traceback

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "qiskit-intuition-mpl"))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Disallowed modules and functions for educational sandbox safety
BLOCKED_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket", "http", "urllib", "requests",
    "pty", "posix", "ctypes", "pickle", "shelve", "builtins", "signal",
    "_thread", "threading", "multiprocessing", "asyncio", "pathlib", "tempfile"
}

BLOCKED_CALLS = {
    "eval", "exec", "compile", "open", "__import__", "getattr", "setattr", "delattr"
}

BLOCKED_ATTRS = {
    "__subclasses__", "__bases__", "__globals__", "__code__", "__builtins__"
}

orig_import = __import__

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_module = name.split('.')[0]
    if root_module in BLOCKED_MODULES:
        raise ImportError(f"Security Restriction: Module '{name}' is prohibited in the sandbox.")
    return orig_import(name, globals, locals, fromlist, level)

SAFE_BUILTINS = {
    '__import__': safe_import,
    'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
    'complex': complex, 'dict': dict, 'enumerate': enumerate, 'filter': filter,
    'float': float, 'format': format, 'hex': hex, 'int': int,
    'isinstance': isinstance, 'issubclass': issubclass, 'iter': iter,
    'len': len, 'list': list, 'map': map, 'max': max, 'min': min,
    'next': next, 'oct': oct, 'ord': ord, 'pow': pow, 'print': print,
    'range': range, 'reversed': reversed, 'round': round, 'set': set,
    'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
    'tuple': tuple, 'type': type, 'zip': zip,
    'True': True, 'False': False, 'None': None,
    'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
    'IndexError': IndexError, 'KeyError': KeyError, 'ZeroDivisionError': ZeroDivisionError,
}

def validate_code_safety(code_string: str):
    """
    Statically analyzes code AST to prevent dangerous imports, filesystem/process
    access, or code injection while allowing valid Qiskit and scientific code.
    """
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return f"Syntax Error: {e.msg} at line {e.lineno}"

    for node in ast.walk(tree):
        # 1. Block prohibited imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split('.')[0]
                if root_module in BLOCKED_MODULES:
                    return f"Security Restriction: Importing '{alias.name}' is prohibited in the sandbox."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split('.')[0]
                if root_module in BLOCKED_MODULES:
                    return f"Security Restriction: Importing from '{node.module}' is prohibited in the sandbox."

        # 2. Block prohibited function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                return f"Security Restriction: Function '{node.func.id}()' is prohibited in the sandbox."

        # 3. Block introspection escape attempts
        elif isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_ATTRS:
                return f"Security Restriction: Accessing '{node.attr}' is prohibited in the sandbox."

    return None

def execute_notebook_code(code_string):
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    existing_figs = set(plt.get_fignums())

    # Pre-execution AST security validation
    security_violation = validate_code_safety(code_string)
    if security_violation:
        return {
            'success': False,
            'stdout': '',
            'stderr': security_violation,
            'error': security_violation,
            'figures': []
        }

    exec_globals = {
        '__builtins__': SAFE_BUILTINS,
        'np': np,
        'qiskit': qiskit,
        'QuantumCircuit': QuantumCircuit,
        'Statevector': Statevector,
        'plt': plt,
    }
    exec_locals = {}

    success = True
    error_message = None

    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        try:
            exec(code_string, exec_globals, exec_locals)
        except Exception as e:
            success = False
            error_message = traceback.format_exc()

    stdout_output = stdout_buffer.getvalue()
    stderr_output = stderr_buffer.getvalue()

    new_figs = []
    current_figs = set(plt.get_fignums())
    created_fig_nums = current_figs - existing_figs

    for num in current_figs:
        fig = plt.figure(num)
        if num in created_fig_nums:
            new_figs.append(fig)
        plt.close(num)

    return {
        'success': success,
        'stdout': stdout_output,
        'stderr': stderr_output,
        'error': error_message,
        'figures': new_figs
    }
