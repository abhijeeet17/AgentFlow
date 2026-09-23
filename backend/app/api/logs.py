from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import AgentRunRepository
from app.schemas.agent import AgentRunResponse

router = APIRouter(prefix="", tags=["Logs"])

@router.get("/runs/{run_id}/logs", response_model=List[AgentRunResponse])
async def get_workflow_logs(run_id: str, db: AsyncSession = Depends(get_db)):
    logs = await AgentRunRepository.get_logs_for_workflow(db, run_id)
    return logs

@router.get("/logs", response_model=List[AgentRunResponse])
async def list_all_agent_logs(limit: int = 100, db: AsyncSession = Depends(get_db)):
    logs = await AgentRunRepository.list_all_logs(db, limit=limit)
    return logs
