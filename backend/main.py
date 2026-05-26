import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure we are able to import from the root project directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()

from backend.routers import simulate, execute, agents

app = FastAPI(
    title="Qiskit Intuition Lab API",
    description="Decoupled backend service for quantum simulation, code execution, and educational AI agents.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
        "api_key_configured": bool(os.environ.get("GEMINI_API_KEY"))
    }
