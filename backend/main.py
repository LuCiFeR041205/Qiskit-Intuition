import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure we are able to import from the root project directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()

from backend.routers import simulate, execute, agents  # noqa: E402

app = FastAPI(
    title="Qiskit Intuition Lab API",
    description="Decoupled backend service for quantum simulation, code execution, and offline educational helpers.",
    version="1.0.0"
)

# Configure CORS - Restrict to trusted local origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(simulate.router, tags=["simulation"])
app.include_router(execute.router, tags=["execution"])
app.include_router(agents.router, prefix="/agent", tags=["agents"])

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "offline_ai": True
    }
