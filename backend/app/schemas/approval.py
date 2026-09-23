from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ApprovalActionRequest(BaseModel):
    approved: bool
    approved_by: Optional[str] = "Admin"
    notes: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: str
    workflow_run_id: str
    risk_level: str
    reason: str
    status: str
    approved_by: Optional[str]
    decision_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
