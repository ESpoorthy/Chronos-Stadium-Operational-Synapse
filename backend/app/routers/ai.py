from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.agents.core import engine
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/ai", tags=["AI Engine"])

class ScenarioRequest(BaseModel):
    scenario: str
    stadium_data: dict

class SimulationResponse(BaseModel):
    futures: List[dict]
    messages: List[str]

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: ScenarioRequest):
    try:
        initial_state = {
            "messages": [HumanMessage(content=request.scenario)],
            "scenario": request.scenario,
            "stadium_data": request.stadium_data,
            "simulated_futures": []
        }
        
        # In a real app we'd await this if we use an async engine
        result = engine.invoke(initial_state)
        
        # Extract string messages for API response
        messages = [msg.content for msg in result.get("messages", [])]
        
        return SimulationResponse(
            futures=result.get("simulated_futures", []),
            messages=messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
