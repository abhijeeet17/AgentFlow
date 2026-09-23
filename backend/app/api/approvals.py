from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import ApprovalRepository
from app.services.ticket_service import ticket_workflow_service
from app.schemas.approval import ApprovalResponse, ApprovalActionRequest

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.get("/pending", response_model=List[ApprovalResponse])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    approvals = await ApprovalRepository.list_pending(db)
    return approvals

@router.post("/{approval_id}")
async def handle_approval(
    approval_id: str,
    payload: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await ticket_workflow_service.resume_after_approval(
            session=db,
            approval_id=approval_id,
            approved=payload.approved,
            notes=payload.notes
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process approval decision: {str(e)}")
