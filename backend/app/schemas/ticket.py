from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TicketCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Payment failed three times but money deducted"})
    description: str = Field(..., json_schema_extra={"example": "My payment failed three times but money was deducted from my bank account. Please help."})
    customer_id: Optional[str] = Field(default="CUST-9901")
    channel: Optional[str] = Field(default="web")

class TicketResponse(BaseModel):
    id: str
    customer_id: Optional[str]
    title: str
    description: str
    category: Optional[str]
    priority: Optional[str]
    status: str
    assigned_team: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
