from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from agents.router_agent import (
    classify_intent,
    route_and_respond,
    AGENT_META
)
from agents.composer_agent import explain_composer_action
from agents.feynman_agent import explain_concept
from agents.qiskit_engineer import generate_code
from agents.socratic_tutor import generate_problem
from agents.base_agent import generate_stream

router = APIRouter()

class ExplainRequest(BaseModel):
    concept: str

class CoachRequest(BaseModel):
    latest_gate: str
    qubit: int
    full_circuit_desc: str
    eli5_mode: bool = False

class EvaluateRequest(BaseModel):
    user_answer: str
    checkpoint: str

class RouteRequest(BaseModel):
    user_message: str
    eli5_mode: bool = False

def stream_sse(generator):
    for chunk in generator:
        if chunk:
            yield f"data: {chunk}\n\n"

@router.post("/explain")
async def explain(req: ExplainRequest):
    try:
        generator = explain_concept(req.concept)
        return StreamingResponse(stream_sse(generator), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coach")
async def coach(req: CoachRequest):
    try:
        generator = explain_composer_action(req.latest_gate, req.qubit, req.full_circuit_desc, eli5_mode=req.eli5_mode)
        return StreamingResponse(stream_sse(generator), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate")
async def evaluate(req: EvaluateRequest):
    try:
        eval_prompt = """
You are A.C.E. (Advanced Conceptual Explainer) acting as the Socratic Evaluator.
The user (Explorer) has answered a checkpoint question in their quantum learning lab.
Analyze their answer in the context of the checkpoint question:
Checkpoint question: {checkpoint}
User's Answer: {user_answer}

Provide graded feedback: explain whether their conceptual understanding is correct, partially correct, or needs refinement.
Keep the feedback highly encouraging, warm, socratic (helping them build physical intuition), and sophisticated in your British AI persona.
Keep the response under 150 words. Additionally, focus on the physics and computational concepts, and avoid generic or vague statements. 
Use analogies and examples where appropriate to clarify concepts.
"""
        formatted_prompt = eval_prompt.format(checkpoint=req.checkpoint, user_answer=req.user_answer)
        generator = generate_stream(
            system_prompt="You are a sophisticated, polite, and encouraging British AI Socratic Evaluator.",
            user_prompt=formatted_prompt
        )
        return StreamingResponse(stream_sse(generator), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/route")
async def route_agent(req: RouteRequest):
    try:
        intent = classify_intent(req.user_message)
        meta = AGENT_META.get(intent, AGENT_META["general"])
        
        async def route_stream():
            # First send metadata as an 'intent' event
            yield f"event: intent\ndata: {json.dumps({'intent': intent, 'name': meta['name'], 'avatar': meta['avatar'], 'description': meta['description']})}\n\n"
            
            # Then stream chunks
            _, response_stream = route_and_respond(req.user_message, intent=intent, eli5_mode=req.eli5_mode)
            for chunk in response_stream:
                if chunk:
                    yield f"event: chunk\ndata: {chunk}\n\n"
                    
        return StreamingResponse(route_stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CodeRequest(BaseModel):
    concept: str
    analogy: str

class StreamRequest(BaseModel):
    system_prompt: str
    user_prompt: str

@router.post("/code")
async def generate_code_endpoint(req: CodeRequest):
    try:
        generator = generate_code(req.concept, req.analogy)
        return StreamingResponse(stream_sse(generator), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/challenge")
async def challenge(req: ExplainRequest):
    try:
        generator = generate_problem(req.concept)
        return StreamingResponse(stream_sse(generator), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_generic(req: StreamRequest):
    try:
        generator = generate_stream(req.system_prompt, req.user_prompt)
        return StreamingResponse(stream_sse(generator), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
