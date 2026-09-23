import re
from datetime import datetime
from typing import Dict, Any

class IntakeAgent:
    """
    Agent 1 — Intake Agent
    Responsibilities:
    - Clean and normalize text
    - Extract customer ID, channel, and metadata
    - Produce standardized ticket dictionary
    """
    def process(self, raw_ticket: Dict[str, Any]) -> Dict[str, Any]:
        raw_message = raw_ticket.get("customer_message") or raw_ticket.get("description") or ""
        cleaned_message = re.sub(r'\s+', ' ', raw_message).strip()
        
        ticket_id = raw_ticket.get("ticket_id") or raw_ticket.get("id") or "TKT-1001"
        customer_id = raw_ticket.get("customer_id") or "CUST-9901"
        channel = raw_ticket.get("channel") or "web"
        timestamp = raw_ticket.get("timestamp") or datetime.utcnow().isoformat()
        
        return {
            "ticket_id": ticket_id,
            "title": raw_ticket.get("title") or cleaned_message[:60] + "...",
            "customer_message": cleaned_message,
            "customer_id": customer_id,
            "channel": channel,
            "timestamp": timestamp,
            "metadata": raw_ticket.get("metadata", {})
        }

intake_agent = IntakeAgent()
