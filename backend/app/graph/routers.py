from typing import Literal
from app.graph.state import AgentState

MAX_RETRIES = 3

def risk_router(state: AgentState) -> Literal["human_approval", "action_agent"]:
    """
    Route based on risk level and approval decision.
    If risk level is HIGH or decision requests human approval -> route to human approval.
    Else -> route directly to Action Agent.
    """
    decision = state.get("decision", {})
    risk_level = decision.get("risk_level", "LOW").upper()
    decision_type = decision.get("decision", "")

    if risk_level == "HIGH" or decision_type == "REQUEST_HUMAN_APPROVAL" or decision.get("requires_approval"):
        # Check if already approved by human in state
        if state.get("human_approved") is True:
            return "action_agent"
        elif state.get("human_approved") is False:
            return "action_agent"  # Action agent will record rejection response
        return "human_approval"
    
    return "action_agent"


def verification_router(state: AgentState) -> Literal["completed", "decision_agent", "escalate"]:
    """
    Route based on verification result and retry count.
    If verification passes -> completed.
    If verification fails and retry_count < MAX_RETRIES -> decision_agent (retry).
    Else -> escalate.
    """
    verification = state.get("verification", {})
    approved = verification.get("approved", True)
    retry_count = state.get("retry_count", 0)

    if approved:
        return "completed"
    
    if retry_count < MAX_RETRIES:
        return "decision_agent"
    
    return "escalate"
