from __future__ import annotations

from fastapi import APIRouter, Depends

from src.entrypoints.api.v1.schemas import AgentQueryRequest, AgentQueryResponse
from src.entrypoints.api.main import get_agent_service

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(payload: AgentQueryRequest, agent=Depends(get_agent_service)) -> AgentQueryResponse:
    result = await agent.run(payload.query)
    return AgentQueryResponse(answer=result["answer"], error=result.get("error"))
