from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

class AgentState(TypedDict):
    ticket: Dict[str, Any]
    classification: Dict[str, Any]
    retrieved_documents: Dict[str, Any]
    decision: Dict[str, Any]
    action_result: Dict[str, Any]
    verification: Dict[str, Any]
    errors: Annotated[List[str], operator.add]
    retry_count: int
    status: str
    workflow_run_id: str
    human_approved: Optional[bool]
    approval_notes: Optional[str]
