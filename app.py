import runpy
import sys
import os

# Set root directory in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Transparently execute the decoupled frontend app
runpy.run_path("frontend/streamlit_app.py")
