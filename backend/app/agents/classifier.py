from typing import Dict, Any
from pydantic import BaseModel, Field
from app.llm.factory import get_llm_provider

class ClassificationSchema(BaseModel):
    category: str = Field(description="Category: Billing, Technical Issue, Account, Refund, Security, Feature Request, General Question")
    priority: str = Field(description="Priority: Low, Medium, High, Urgent")
    sentiment: str = Field(description="Sentiment: Positive, Neutral, Negative")
    complexity: str = Field(description="Complexity: Low, Moderate, High")
    department: str = Field(description="Target Department: Payments, Technical Support, Security, Account Team, Product")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    summary: str = Field(description="Brief summary of the issue")

class ClassificationAgent:
    """
    Agent 2 — Classification Agent
    Responsibilities:
    - Classify ticket into category, priority, sentiment, complexity, and target department.
    - Return structured JSON object.
    """
    def __init__(self):
        self.llm = get_llm_provider()

    async def process(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"Classify the following customer support ticket:\n"
            f"Title: {ticket.get('title')}\n"
            f"Customer Message: {ticket.get('customer_message')}\n"
            f"Channel: {ticket.get('channel')}"
        )
        system_prompt = (
            "You are an expert customer support classifier. Analyze the ticket content and return a JSON classification."
        )

        result: ClassificationSchema = await self.llm.generate_structured(
            prompt=prompt,
            response_model=ClassificationSchema,
            system_prompt=system_prompt
        )
        return result.model_dump()

classifier_agent = ClassificationAgent()
