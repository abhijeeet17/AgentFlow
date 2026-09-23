from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.llm.factory import get_llm_provider

class DecisionSchema(BaseModel):
    decision: str = Field(description="Action decision: AUTO_REPLY, ASSIGN_TICKET, ESCALATE, REQUEST_HUMAN_APPROVAL, CLOSE_TICKET")
    reason: str = Field(description="Clear explanation for the decision without exposing hidden COT")
    risk_level: str = Field(description="Risk Level: LOW, MEDIUM, HIGH")
    requires_approval: bool = Field(description="True if human approval is required before execution")
    recommended_action: str = Field(description="Specific recommended action summary")

class DecisionAgent:
    """
    Agent 4 — Decision Agent
    Responsibilities:
    - Analyze ticket, classification, and RAG context.
    - Determine action decision and risk level.
    - Identify whether human approval is required (e.g. refunds > $100, security incidents, financial disputes).
    """
    def __init__(self):
        self.llm = get_llm_provider()

    async def process(
        self,
        ticket: Dict[str, Any],
        classification: Dict[str, Any],
        retrieved_documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        prompt = (
            f"Analyze the ticket and determine the appropriate action.\n"
            f"Ticket ID: {ticket.get('ticket_id')}\n"
            f"Customer Message: {ticket.get('customer_message')}\n"
            f"Category: {classification.get('category')}\n"
            f"Priority: {classification.get('priority')}\n"
            f"Department: {classification.get('department')}\n"
            f"Retrieved Documents Count: {len(retrieved_documents.get('documents', []))}\n\n"
            f"Rules:\n"
            f"1. Any financial disputes, payment failure with money deducted, or refund requests require REQUEST_HUMAN_APPROVAL with risk_level HIGH.\n"
            f"2. Security breaches or account lockouts require REQUEST_HUMAN_APPROVAL or ESCALATE with risk_level HIGH.\n"
            f"3. General documentation or standard technical questions with clear RAG matches can be AUTO_REPLY with risk_level LOW.\n"
            f"4. Complex technical issues without direct automated fix should be ASSIGN_TICKET with risk_level MEDIUM."
        )
        system_prompt = "You are a senior support decision agent. Determine the action, risk level, and reasoning."

        result: DecisionSchema = await self.llm.generate_structured(
            prompt=prompt,
            response_model=DecisionSchema,
            system_prompt=system_prompt
        )
        return result.model_dump()

decision_agent = DecisionAgent()
