from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.llm.factory import get_llm_provider

class VerificationSchema(BaseModel):
    approved: bool = Field(description="True if verification passes; False if failed")
    issues: List[str] = Field(description="List of identified issues or hallucination warnings")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    explanation: str = Field(description="Verification summary explanation")

class VerificationAgent:
    """
    Agent 6 — Verification Agent
    Responsibilities:
    - Verify that response is grounded in retrieved documents.
    - Check safety, required fields, and correct action routing.
    - If verification fails, signal retry or escalation.
    """
    def __init__(self):
        self.llm = get_llm_provider()

    async def process(
        self,
        ticket: Dict[str, Any],
        decision: Dict[str, Any],
        action_result: Dict[str, Any],
        retrieved_documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        prompt = (
            f"Verify the support action and response for ticket {ticket.get('ticket_id')}.\n"
            f"Customer Query: {ticket.get('customer_message')}\n"
            f"Decision: {decision.get('decision')}\n"
            f"Drafted Response: {action_result.get('customer_response')}\n"
            f"Retrieved Documents Count: {len(retrieved_documents.get('documents', []))}\n\n"
            f"Check:\n"
            f"1. Is the customer response polite and supported by knowledge base?\n"
            f"2. Are there any false or hallucinated promises?\n"
            f"3. Are required fields present?"
        )
        system_prompt = "You are a quality assurance and verification agent. Validate the generated action."

        result: VerificationSchema = await self.llm.generate_structured(
            prompt=prompt,
            response_model=VerificationSchema,
            system_prompt=system_prompt
        )
        return result.model_dump()

verifier_agent = VerificationAgent()
