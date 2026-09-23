import pytest
from app.agents.intake import intake_agent
from app.agents.classifier import classifier_agent
from app.agents.rag_agent import rag_agent
from app.agents.decision import decision_agent
from app.agents.action import action_agent
from app.agents.verifier import verifier_agent

@pytest.mark.asyncio
async def test_intake_agent():
    raw_ticket = {
        "title": "Payment failed",
        "customer_message": "My payment failed three times  and money   was deducted. ",
        "customer_id": "CUST-1001"
    }
    result = intake_agent.process(raw_ticket)
    assert result["ticket_id"] is not None
    assert "money was deducted" in result["customer_message"]

@pytest.mark.asyncio
async def test_classifier_agent():
    ticket = {
        "title": "Payment failed",
        "customer_message": "Payment failed three times but money deducted",
        "channel": "web"
    }
    result = await classifier_agent.process(ticket)
    assert "category" in result
    assert "priority" in result
    assert "department" in result

@pytest.mark.asyncio
async def test_rag_agent():
    ticket = {"customer_message": "How do I process a refund?"}
    classification = {"category": "Refund"}
    result = await rag_agent.process(ticket, classification)
    assert "documents" in result
    assert "sources" in result

@pytest.mark.asyncio
async def test_decision_agent_high_risk():
    ticket = {
        "ticket_id": "TKT-1001",
        "customer_message": "Payment failed three times and $149 was deducted."
    }
    classification = {"category": "Refund", "priority": "High", "department": "Payments"}
    rag_docs = {"documents": [{"content": "Refund policy info"}]}
    
    result = await decision_agent.process(ticket, classification, rag_docs)
    assert result["decision"] in ["REQUEST_HUMAN_APPROVAL", "AUTO_REPLY", "ASSIGN_TICKET", "ESCALATE"]
    assert "risk_level" in result

@pytest.mark.asyncio
async def test_action_and_verification_agents():
    ticket = {"ticket_id": "TKT-1001", "customer_message": "Need refund"}
    classification = {"department": "Payments", "category": "Refund"}
    decision = {"decision": "REQUEST_HUMAN_APPROVAL", "reason": "High financial risk"}
    rag_docs = {"documents": [{"citation": "[1] refund_policy.md", "content": "Refund policy text"}]}

    action_result = await action_agent.process(ticket, classification, decision, rag_docs)
    assert "customer_response" in action_result

    ver_result = await verifier_agent.process(ticket, decision, action_result, rag_docs)
    assert "approved" in ver_result
