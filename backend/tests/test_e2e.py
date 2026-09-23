import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_end_to_end_high_risk_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create a High-Risk payment failure ticket
        ticket_payload = {
            "title": "Payment failed three times but money deducted",
            "description": "My payment failed three times during checkout, but money was deducted from my bank account. Please help.",
            "customer_id": "CUST-E2E"
        }
        ticket_res = await ac.post("/api/tickets", json=ticket_payload)
        assert ticket_res.status_code == 201
        ticket_id = ticket_res.json()["id"]

        # 2. Run Workflow
        wf_res = await ac.post("/api/workflows/run", json={"ticket_id": ticket_id})
        assert wf_res.status_code == 200
        wf_data = wf_res.json()
        wf_run_id = wf_data["workflow_run_id"]

        # 3. If paused at PENDING_APPROVAL, fetch pending approvals
        if wf_data["status"] == "PENDING_APPROVAL":
            pending_res = await ac.get("/api/approvals/pending")
            assert pending_res.status_code == 200
            pending_list = pending_res.json()
            assert len(pending_list) > 0
            
            target_approval = None
            for appr in pending_list:
                if appr["workflow_run_id"] == wf_run_id:
                    target_approval = appr
                    break

            assert target_approval is not None

            # 4. Submit Human Approval
            approval_id = target_approval["id"]
            action_res = await ac.post(
                f"/api/approvals/{approval_id}",
                json={"approved": True, "approved_by": "Senior Auditor", "notes": "Statement verified, refund authorized."}
            )
            assert action_res.status_code == 200
            assert action_res.json()["status"] in ["RESOLVED", "COMPLETED"]

        # 5. Verify Execution Logs
        logs_res = await ac.get(f"/api/runs/{wf_run_id}/logs")
        assert logs_res.status_code == 200
        logs = logs_res.json()
        assert len(logs) >= 3
