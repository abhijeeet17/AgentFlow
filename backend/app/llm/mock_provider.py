import json
from typing import Optional, Type
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider

class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider for out-of-the-box dry runs, offline testing,
    and keyless environments. Intelligently matches prompts to construct appropriate responses.
    """
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()
        if "response" in prompt_lower or "draft" in prompt_lower:
            return "Dear Customer,\n\nThank you for reaching out to AgentFlow Support. We have received your query regarding your transaction/account. According to our documentation, failed transactions are automatically reconciled within 24 hours. If your balance has not updated, our Payments team will inspect your transaction ID.\n\nBest regards,\nAgentFlow Support Team"
        return "Mock LLM text output generated successfully."

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None
    ) -> BaseModel:
        prompt_lower = prompt.lower()
        model_name = response_model.__name__.lower()

        # 1. Classification Agent Output
        if "classif" in model_name:
            category = "Billing"
            priority = "High"
            sentiment = "Negative"
            department = "Payments"
            confidence = 0.92

            if any(kw in prompt_lower for kw in ["slow", "bug", "500", "technical", "error"]):
                category = "Technical Issue"
                department = "Technical Support"
                priority = "Medium"
                sentiment = "Neutral"
            elif any(kw in prompt_lower for kw in ["password", "hack", "login", "security", "unauthorized"]):
                category = "Security"
                department = "Security"
                priority = "Urgent"
                sentiment = "Negative"
            elif any(kw in prompt_lower for kw in ["refund", "deducted", "payment failed", "chargeback"]):
                category = "Refund"
                department = "Payments"
                priority = "High"
                sentiment = "Negative"
            elif any(kw in prompt_lower for kw in ["feature", "add"]):
                category = "Feature Request"
                department = "Product"
                priority = "Low"
                sentiment = "Positive"

            data = {
                "category": category,
                "priority": priority,
                "sentiment": sentiment,
                "complexity": "Moderate",
                "department": department,
                "confidence": confidence,
                "summary": "Customer reported an issue requiring investigation."
            }
            return response_model.model_validate(data)

        # 2. Decision Agent Output
        if "decision" in model_name:
            if any(kw in prompt_lower for kw in ["refund", "deducted", "failed three times", "chargeback", "security", "hacked", "financial dispute"]):
                data = {
                    "decision": "REQUEST_HUMAN_APPROVAL",
                    "reason": "Potential financial dispute or sensitive payment adjustment requires human approval as per policy.",
                    "risk_level": "HIGH",
                    "requires_approval": True,
                    "recommended_action": "Verify bank statement details and authorize refund."
                }
            else:
                data = {
                    "decision": "AUTO_REPLY",
                    "reason": "Standard inquiry with clear knowledge base match.",
                    "risk_level": "LOW",
                    "requires_approval": False,
                    "recommended_action": "Send automated customer reply with relevant documentation."
                }
            return response_model.model_validate(data)

        # 3. Action Agent Output
        if "action" in model_name:
            data = {
                "action_type": "DRAFT_RESPONSE",
                "customer_response": (
                    "Hello,\n\nWe apologize for the inconvenience caused. "
                    "Based on our policy (Refund Policy - Page 1), failed payments where money was deducted "
                    "are auto-reversed by payment gateways within 24 to 48 hours. "
                    "Our Payments team is monitoring your ticket.\n\n"
                    "Sources:\n[1] refund_policy.md - Section 2\n[2] payment_policy.md - Section 1"
                ),
                "assigned_team": "Payments",
                "status_update": "PENDING_APPROVAL",
                "execution_details": {"email_sent": False, "slack_notified": True}
            }
            return response_model.model_validate(data)

        # 4. Verification Agent Output
        if "verifi" in model_name:
            data = {
                "approved": True,
                "issues": [],
                "confidence": 0.95,
                "explanation": "Action aligns with company policies and retrieved documentation."
            }
            return response_model.model_validate(data)

        # Fallback default instantiation using model fields
        field_defaults = {}
        for field_name, field in response_model.model_fields.items():
            field_type = field.annotation
            if field_type == str:
                field_defaults[field_name] = "mock_value"
            elif field_type == bool:
                field_defaults[field_name] = True
            elif field_type == int or field_type == float:
                field_defaults[field_name] = 1.0
            elif field_type == list or getattr(field_type, '__origin__', None) == list:
                field_defaults[field_name] = []
            elif field_type == dict or getattr(field_type, '__origin__', None) == dict:
                field_defaults[field_name] = {}
            else:
                field_defaults[field_name] = None

        return response_model.model_validate(field_defaults)
