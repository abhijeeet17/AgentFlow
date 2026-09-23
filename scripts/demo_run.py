import os
import sys
import asyncio
import json

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import init_db, AsyncSessionLocal
from app.database.repositories import TicketRepository, ApprovalRepository
from app.rag.ingestion import ingest_knowledge_base
from app.services.ticket_service import ticket_workflow_service

async def run_demo():
    print("================================================================================")
    print("                AGENTFLOW MULTI-AGENT WORKFLOW DEMONSTRATION                   ")
    print("================================================================================")
    
    # 1. Initialize DB and RAG Knowledge Base
    await init_db()
    kb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base"))
    chunks = ingest_knowledge_base(kb_path)
    print(f"\n[1/5] RAG Pipeline Ready: Ingested {chunks} policy chunks into ChromaDB.")

    # 2. Submit High-Risk Customer Ticket
    async with AsyncSessionLocal() as db:
        print("\n[2/5] Submitting Customer Ticket...")
        ticket = await TicketRepository.create(
            db,
            title="Payment failed three times but money deducted",
            description="My payment failed three times during checkout, but $149.00 was deducted from my bank account. Please help.",
            customer_id="CUST-DEMO-99"
        )
        print(f"      Ticket Created: ID = {ticket.id}")
        print(f"      Customer Message: '{ticket.description}'")

        # 3. Execute LangGraph Multi-Agent Workflow
        print("\n[3/5] Launching LangGraph Multi-Agent Graph...")
        res = await ticket_workflow_service.run_ticket_workflow(db, ticket.id)
        
        wf_id = res["workflow_run_id"]
        status = res["status"]
        state = res["state"]

        print(f"\n      --- Agent Node Outputs ---")
        print(f"      • Intake Agent: Ticket Normalized ({state.get('ticket', {}).get('ticket_id')})")
        print(f"      • Classification Agent: Category = {state.get('classification', {}).get('category')}, Priority = {state.get('classification', {}).get('priority')}, Department = {state.get('classification', {}).get('department')}")
        print(f"      • RAG Agent: Retrieved {len(state.get('retrieved_documents', {}).get('documents', []))} docs from ChromaDB (Score = {state.get('retrieved_documents', {}).get('retrieval_score')})")
        print(f"      • Decision Agent: Decision = {state.get('decision', {}).get('decision')}, Risk Level = {state.get('decision', {}).get('risk_level')}")
        print(f"      • Decision Rationale: {state.get('decision', {}).get('reason')}")

        if status == "PENDING_APPROVAL":
            print("\n[4/5] ⚠️ Risk Router Interrupted: High Risk Detected! Workflow PAUSED for Human Approval.")
            pending = await ApprovalRepository.list_pending(db)
            approval = [a for a in pending if a.workflow_run_id == wf_id][0]
            print(f"      Approval ID: {approval.id} | Reason: {approval.reason}")

            # 4. Simulate Human Manager Approval
            print("\n[5/5] Simulating Human Manager Approval (POST /api/approvals/{id})...")
            resume_res = await ticket_workflow_service.resume_after_approval(
                session=db,
                approval_id=approval.id,
                approved=True,
                notes="Verified bank statement details and authorized refund."
            )
            
            final_state = resume_res["state"]
            print(f"\n      ✅ Workflow Resumed & Completed!")
            print(f"      • Action Agent Output:")
            print(f"        Action Type: {final_state.get('action_result', {}).get('action_type')}")
            print(f"        Assigned Team: {final_state.get('action_result', {}).get('assigned_team')}")
            print(f"      • Generated Customer Response:")
            print(f"--------------------------------------------------------------------------------")
            print(final_state.get('action_result', {}).get('customer_response'))
            print(f"--------------------------------------------------------------------------------")
            print(f"      • Verification Agent: Approved = {final_state.get('verification', {}).get('approved')} (Confidence = {final_state.get('verification', {}).get('confidence')})")

    print("\n================================================================================")
    print("                    DEMONSTRATION COMPLETED SUCCESSFULLY                        ")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(run_demo())
