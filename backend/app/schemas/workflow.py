from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class WorkflowRunRequest(BaseModel):
    ticket_id: str

class WorkflowRunResponse(BaseModel):
    id: str
    ticket_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    state_data: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
