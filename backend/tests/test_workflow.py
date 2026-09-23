import pytest
from app.graph.workflow import agentflow_graph
from app.graph.routers import risk_router, verification_router

def test_risk_router_high_risk():
    state = {
        "decision": {
            "decision": "REQUEST_HUMAN_APPROVAL",
            "risk_level": "HIGH",
            "requires_approval": True
        }
    }
    route = risk_router(state)
    assert route == "human_approval"

def test_risk_router_low_risk():
    state = {
        "decision": {
            "decision": "AUTO_REPLY",
            "risk_level": "LOW",
            "requires_approval": False
        }
    }
    route = risk_router(state)
    assert route == "action_agent"

def test_verification_router_retry():
    state = {
        "verification": {"approved": False},
        "retry_count": 1
    }
    route = verification_router(state)
    assert route == "decision_agent"

def test_verification_router_max_retries():
    state = {
        "verification": {"approved": False},
        "retry_count": 3
    }
    route = verification_router(state)
    assert route == "escalate"
