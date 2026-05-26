from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ..core.notebook_engine import execute_notebook_code

router = APIRouter()

class ExecuteRequest(BaseModel):
    code: str

def fig_to_base64(fig):
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str
    except Exception:
        return ""

@router.post("/execute")
async def execute(req: ExecuteRequest):
    try:
        result = execute_notebook_code(req.code)
        
        figures_b64 = []
        for fig in result.get('figures', []):
            fig_b64 = fig_to_base64(fig)
            if fig_b64:
                figures_b64.append(fig_b64)
                
        return {
            "success": result.get("success", False),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "error": result.get("error", None),
            "figures": figures_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
