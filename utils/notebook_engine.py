import io
import sys
import contextlib
import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def execute_notebook_code(code_string):
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    existing_figs = set(plt.get_fignums())
    
    exec_globals = {
        '__builtins__': __builtins__,
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
