import os
import runpy
import sys

# Set root directory in sys.path
ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# Transparently execute the decoupled frontend app
runpy.run_path(os.path.join(ROOT, "frontend", "streamlit_app.py"))
