from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import WorkflowRepository
from app.services.ticket_service import ticket_workflow_service
from app.schemas.workflow import WorkflowRunRequest, WorkflowRunResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.post("/run")
async def run_workflow(payload: WorkflowRunRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await ticket_workflow_service.run_ticket_workflow(db, payload.ticket_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.get("", response_model=List[WorkflowRunResponse])
async def list_workflows(limit: int = 50, db: AsyncSession = Depends(get_db)):
    runs = await WorkflowRepository.list_runs(db, limit=limit)
    return runs

@router.get("/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await WorkflowRepository.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Workflow run {run_id} not found")
    return run
