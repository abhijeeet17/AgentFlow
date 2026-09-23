import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_and_ready_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.get("/health")
        assert res1.status_code == 200
        assert res1.json()["status"] == "healthy"

        res2 = await ac.get("/ready")
        assert res2.status_code == 200
        assert "llm_provider" in res2.json()

@pytest.mark.asyncio
async def test_tickets_api_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create ticket
        payload = {
            "title": "Test Ticket",
            "description": "Test ticket description for API verification",
            "customer_id": "CUST-999"
        }
        res = await ac.post("/api/tickets", json=payload)
        assert res.status_code == 201
        ticket_data = res.json()
        assert ticket_data["title"] == payload["title"]

        # Get tickets list
        list_res = await ac.get("/api/tickets")
        assert list_res.status_code == 200
        assert len(list_res.json()) > 0
