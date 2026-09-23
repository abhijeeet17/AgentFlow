from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AgentRunResponse(BaseModel):
    id: str
    workflow_run_id: str
    agent_name: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    duration_ms: float
    error: Optional[str]
    retry_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AgentPerformanceSummary(BaseModel):
    agent_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_latency_ms: float
    retries_count: int
