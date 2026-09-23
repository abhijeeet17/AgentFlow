import os
import sys
import asyncio

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import init_db, AsyncSessionLocal
from app.database.repositories import TicketRepository
from app.services.ticket_service import ticket_workflow_service

SAMPLE_TICKETS = [
    {
        "title": "Payment failed three times but money deducted",
        "description": "My payment failed three times during checkout, but $149.00 was deducted from my bank account. Please refund immediately.",
        "customer_id": "CUST-1001"
    },
    {
        "title": "How do I change my subscription plan?",
        "description": "I would like to upgrade my account from Starter to Enterprise plan. Where do I find the billing settings?",
        "customer_id": "CUST-1002"
    },
    {
        "title": "HTTP 500 Internal Server Error on API export",
        "description": "Whenever I try to export 50,000 analytics records via REST API, I get HTTP 500 server error response.",
        "customer_id": "CUST-1003"
    },
    {
        "title": "Unauthorized login attempt detected on account",
        "description": "I received an email alert about an unauthorized login attempt from an unknown IP address in Europe. Please lock my account.",
        "customer_id": "CUST-1004"
    },
    {
        "title": "Request for SAML 2.0 Single Sign-On integration",
        "description": "We are onboarding 200 users and need setup instructions for SAML 2.0 Okta integration.",
        "customer_id": "CUST-1005"
    },
    {
        "title": "Duplicate subscription renewal charge",
        "description": "I was charged twice on my credit card ($99.00 each) on Sept 1st for monthly renewal.",
        "customer_id": "CUST-1006"
    },
    {
        "title": "Feature Request: Export dashboard widgets to PDF",
        "description": "Can you add a button to export live dashboard charts directly to PDF reports?",
        "customer_id": "CUST-1007"
    },
    {
        "title": "API Rate Limit 429 Too Many Requests",
        "description": "Our automated ETL pipeline is hitting 429 rate limits during midnight batch runs.",
        "customer_id": "CUST-1008"
    },
    {
        "title": "Where can I find open API specification docs?",
        "description": "Is there a Swagger UI or Redoc documentation link for backend endpoints?",
        "customer_id": "CUST-1009"
    },
    {
        "title": "Bank chargeback notice for transaction #8812",
        "description": "Our bank issued a formal chargeback dispute for transaction #8812 due to billing misunderstanding.",
        "customer_id": "CUST-1010"
    }
]

async def seed():
    print("Initializing Database...")
    await init_db()

    async with AsyncSessionLocal() as session:
        print("Seeding sample tickets and running multi-agent workflows...")
        for data in SAMPLE_TICKETS:
            t = await TicketRepository.create(
                session,
                title=data["title"],
                description=data["description"],
                customer_id=data["customer_id"]
            )
            print(f"Created Ticket: {t.id} - '{t.title}'")
            
            # Execute workflow for first 3 tickets
            res = await ticket_workflow_service.run_ticket_workflow(session, t.id)
            print(f"  -> Workflow Status: {res['status']} (Run ID: {res['workflow_run_id']})")

    print("\nDatabase Seeding Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
