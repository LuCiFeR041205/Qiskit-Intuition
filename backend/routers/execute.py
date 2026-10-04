from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from ..core.notebook_engine import execute_notebook_code

router = APIRouter()

class ExecuteRequest(BaseModel):
    code: str

@router.post("/execute")
async def execute(req: ExecuteRequest):
    try:
        result = execute_notebook_code(req.code)
        
        figures_b64 = [base64.b64encode(png).decode("ascii") for png in result.get("figures", [])]
                
        return {
            "success": result.get("success", False),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "error": result.get("error", None),
            "figures": figures_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
