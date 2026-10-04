"""Run in-process Qiskit work on one long-lived thread.

Streamlit executes every rerun of a page on a fresh thread. Qiskit's Rust
extension (``qiskit._accelerate``) segfaulted when circuits were built from
those short-lived threads in turn (a crash reading thread-local state), taking
the whole app server down. Funnelling every in-process Qiskit call through
one dedicated worker thread avoids it.

Return plain Python / NumPy / Matplotlib objects from decorated functions:
Qiskit objects such as ``QuantumCircuit`` should not escape to other threads.
Learner code is unaffected — it runs in a separate process.
"""

from __future__ import annotations

import concurrent.futures
import functools
import threading

_THREAD_NAME = "qiskit-worker"
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix=_THREAD_NAME)


def on_qiskit_thread(fn):
    """Decorator: run ``fn`` on the dedicated Qiskit thread and wait for it."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if threading.current_thread().name.startswith(_THREAD_NAME):
            return fn(*args, **kwargs)  # already there; avoid deadlocking on ourselves
        return _EXECUTOR.submit(fn, *args, **kwargs).result()

    return wrapper
