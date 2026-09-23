from typing import Dict, Any
from pydantic import BaseModel, Field
from app.llm.factory import get_llm_provider
from app.integrations.slack import slack_integration
from app.integrations.email import email_integration

class ActionSchema(BaseModel):
    action_type: str = Field(description="Action executed: DRAFT_RESPONSE, ASSIGN_DEPARTMENT, ESCALATE_TICKET, REJECT_ACTION")
    customer_response: str = Field(description="Professional response formatted for customer with RAG citations")
    assigned_team: str = Field(description="Department assigned")
    status_update: str = Field(description="New ticket status: RESOLVED, PENDING_APPROVAL, ESCALATED, IN_PROGRESS")
    execution_details: Dict[str, Any] = Field(description="Metadata regarding notifications sent")

class ActionAgent:
    """
    Agent 5 — Action Agent
    Responsibilities:
    - Perform selected action (draft response, assign ticket, escalate, send notifications).
    - Format citations from retrieved documents.
    """
    def __init__(self):
        self.llm = get_llm_provider()

    async def process(
        self,
        ticket: Dict[str, Any],
        classification: Dict[str, Any],
        decision: Dict[str, Any],
        retrieved_documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        docs = retrieved_documents.get("documents", [])
        sources_text = "\n".join([f"- {d.get('citation', '')}: {d.get('content', '')[:150]}" for d in docs])

        prompt = (
            f"Generate an action result for ticket {ticket.get('ticket_id')}.\n"
            f"Customer Message: {ticket.get('customer_message')}\n"
            f"Decision: {decision.get('decision')}\n"
            f"Reasoning: {decision.get('reason')}\n"
            f"Department: {classification.get('department')}\n"
            f"Retrieved Documentation:\n{sources_text}\n\n"
            f"Draft a helpful, polite customer response containing source citations if applicable."
        )
        system_prompt = "You are an action execution agent. Generate customer response and update details."

        result: ActionSchema = await self.llm.generate_structured(
            prompt=prompt,
            response_model=ActionSchema,
            system_prompt=system_prompt
        )
        
        # Trigger integrations (Slack / Email) asynchronously or mock
        action_dict = result.model_dump()
        
        # Send notifications
        slack_result = await slack_integration.send_notification(
            f"Ticket {ticket.get('ticket_id')} [{classification.get('category')}] -> Action: {decision.get('decision')}"
        )
        email_result = await email_integration.send_email(
            to_email=ticket.get("customer_id", "customer@example.com"),
            subject=f"Update regarding your ticket {ticket.get('ticket_id')}",
            body=action_dict["customer_response"]
        )
        
        action_dict["execution_details"] = {
            "slack_notified": slack_result,
            "email_sent": email_result
        }

        return action_dict

action_agent = ActionAgent()
