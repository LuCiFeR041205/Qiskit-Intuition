import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure we are able to import from the root project directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()

from backend.routers import agents, execute, simulate

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

extra_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + extra_origins,
    allow_origin_regex=r"https://.*\.hf\.space",
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
