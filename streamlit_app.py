import os
import sys
import asyncio
import json
import time
import pandas as pd
import streamlit as st

# Configure Python path for Streamlit Cloud and local execution
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.config import settings
from app.database.database import init_db, AsyncSessionLocal
from app.database.repositories import (
    TicketRepository, WorkflowRepository, AgentRunRepository, ApprovalRepository
)
from app.services.ticket_service import ticket_workflow_service
from app.rag.ingestion import ingest_knowledge_base

# Page Configuration
st.set_page_config(
    page_title="AgentFlow — Multi-Agent Workflow Automation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stApp { background-color: #0f172a; }
    .css-1d3con0 { background-color: #1e293b; }
    .stMetric { background-color: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 12px; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 8px; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #0369a1; }
</style>
""", unsafe_allow_html=True)

# Helper function to run async DB calls in Streamlit
def run_async(coro):
    return asyncio.run(coro)

# Initialize Database and RAG on first run
@st.cache_resource
def setup_environment():
    run_async(init_db())
    kb_path = os.path.abspath(os.path.join(current_dir, "knowledge_base"))
    chunks = ingest_knowledge_base(kb_path)
    return chunks

try:
    setup_environment()
except Exception as e:
    pass

# Header
st.title("🤖 AgentFlow — Multi-Agent Workflow Automation")
st.caption("Intelligent Multi-Agent Platform powered by LangGraph, RAG (ChromaDB), FastAPI, and Human-in-the-Loop Routing")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ System Status")
    st.markdown(f"**LLM Provider**: `{settings.LLM_PROVIDER.upper()}`")
    st.markdown(f"**Database**: `PostgreSQL / SQLite ORM`")
    st.markdown(f"**Vector Store**: `ChromaDB Persistent`")
    st.markdown(f"**Orchestrator**: `LangGraph v0.2`")
    st.divider()
    
    st.subheader("🚀 Quick Actions")
    if st.button("🌱 Seed Sample Tickets"):
        async def seed():
            async with AsyncSessionLocal() as db:
                from scripts.seed_database import SAMPLE_TICKETS
                for data in SAMPLE_TICKETS[:3]:
                    t = await TicketRepository.create(db, data["title"], data["description"], data["customer_id"])
                    await ticket_workflow_service.run_ticket_workflow(db, t.id)
        run_async(seed())
        st.success("Sample tickets & workflows seeded!")
        st.rerun()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview & Submit Ticket", 
    "🛡️ Human Approvals Queue", 
    "🧬 LangGraph Workflow Timeline", 
    "📈 Agent Performance", 
    "📜 Execution Audit Logs"
])

# ==============================================================================
# TAB 1: OVERVIEW & SUBMIT TICKET
# ==============================================================================
with tab1:
    col1, col2, col3, col4 = st.columns(4)

    async def get_overview_metrics():
        async with AsyncSessionLocal() as db:
            tickets = await TicketRepository.list_all(db, limit=100)
            workflows = await WorkflowRepository.list_runs(db, limit=100)
            pending = await ApprovalRepository.list_pending(db)
            return tickets, workflows, pending

    tickets, workflows, pending = run_async(get_overview_metrics())

    resolved_count = len([w for w in workflows if w.status in ["RESOLVED", "COMPLETED", "ACTION_EXECUTED"]])
    pending_count = len(pending)

    col1.metric("Total Tickets", len(tickets), delta="Processed")
    col2.metric("Auto-Resolved Workflows", resolved_count, delta="Verified")
    col3.metric("Pending Human Approvals", pending_count, delta="High Risk", delta_color="inverse")
    col4.metric("Active Agents", "6 Specialized Agents", delta="LangGraph")

    st.divider()

    st.subheader("➕ Submit New Customer Ticket")
    with st.form("new_ticket_form"):
        title = st.text_input("Ticket Title", placeholder="e.g. Payment failed three times but money deducted")
        description = st.text_area("Customer Message", placeholder="My payment failed three times during checkout, but money was deducted...")
        customer_id = st.text_input("Customer ID", value="CUST-9901")
        submitted = st.form_submit_button("🚀 Submit & Launch Multi-Agent Workflow")

        if submitted and title and description:
            async def process_ticket():
                async with AsyncSessionLocal() as db:
                    t = await TicketRepository.create(db, title, description, customer_id)
                    res = await ticket_workflow_service.run_ticket_workflow(db, t.id)
                    return t, res

            with st.spinner("Executing LangGraph Agents (Intake -> Classifier -> RAG -> Decision -> Action -> Verifier)..."):
                ticket_obj, wf_res = run_async(process_ticket())
            
            st.success(f"Ticket {ticket_obj.id} submitted! Status: {wf_res['status']}")
            st.rerun()

    st.subheader("📋 Recent Tickets")
    if tickets:
        ticket_data = [{
            "Ticket ID": t.id,
            "Title": t.title,
            "Category": t.category or "Unclassified",
            "Priority": t.priority or "Medium",
            "Department": t.assigned_team or "Unassigned",
            "Status": t.status,
            "Created At": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for t in tickets]
        st.dataframe(pd.DataFrame(ticket_data), use_container_width=True)

# ==============================================================================
# TAB 2: HUMAN APPROVALS QUEUE
# ==============================================================================
with tab2:
    st.subheader("🛡️ Pending Human Approvals Queue")
    st.caption("High-risk financial or security tickets paused by LangGraph risk router awaiting human manager authorization.")

    async def get_pending_details():
        async with AsyncSessionLocal() as db:
            p_list = await ApprovalRepository.list_pending(db)
            return p_list

    pending_approvals = run_async(get_pending_details())

    if not pending_approvals:
        st.info("✅ No pending approvals! All workflow runs are auto-processed or already resolved.")
    else:
        for appr in pending_approvals:
            with st.container():
                st.markdown(f"### ⚠️ Approval Required: `{appr.id}`")
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**Workflow Run ID**: `{appr.workflow_run_id}`")
                    st.write(f"**Risk Level**: `{appr.risk_level}`")
                    st.write(f"**Decision Reason**: {appr.reason}")
                    notes = st.text_input(f"Decision Notes for {appr.id}", placeholder="Statement verified, authorizing refund...", key=f"notes_{appr.id}")

                with c2:
                    st.write("")
                    st.write("")
                    btn_approve = st.button("✅ Approve Action", key=f"app_{appr.id}")
                    btn_reject = st.button("❌ Reject Action", key=f"rej_{appr.id}")

                    if btn_approve or btn_reject:
                        is_approved = True if btn_approve else False
                        async def handle_appr():
                            async with AsyncSessionLocal() as db:
                                await ticket_workflow_service.resume_after_approval(db, appr.id, is_approved, notes)
                        
                        with st.spinner("Resuming LangGraph state execution..."):
                            run_async(handle_appr())
                        st.success(f"Approval decision recorded! Action executed.")
                        st.rerun()
            st.divider()

# ==============================================================================
# TAB 3: WORKFLOW TIMELINE
# ==============================================================================
with tab3:
    st.subheader("🧬 LangGraph Workflow Timeline & State Inspection")

    async def get_all_workflows():
        async with AsyncSessionLocal() as db:
            return await WorkflowRepository.list_runs(db, limit=50)

    wf_runs = run_async(get_all_workflows())
    if wf_runs:
        run_ids = [w.id for w in wf_runs]
        selected_run_id = st.selectbox("Select Workflow Run to Inspect", run_ids)

        selected_wf = next((w for w in wf_runs if w.id == selected_run_id), None)
        if selected_wf and selected_wf.state_data:
            state = selected_wf.state_data

            c1, c2, c3 = st.columns(3)
            c1.metric("Status", selected_wf.status)
            c2.metric("Duration", f"{round(selected_wf.duration_ms or 0, 2)} ms")
            c3.metric("Ticket ID", selected_wf.ticket_id)

            st.subheader("Step Execution Sequence")
            st.markdown("""
            1. **Intake Agent**: Cleaned text & extracted metadata
            2. **Classification Agent**: Categorized category, priority & department
            3. **RAG Retrieval Agent**: Retrieved policy chunks from ChromaDB
            4. **Decision Agent**: Determined action decision & risk level
            5. **Risk Router & Human Approval**: Paused or routed based on risk
            6. **Action Agent**: Formatted customer response with document citations
            7. **Verification Agent**: Groundedness and safety verification
            """)

            with st.expander("🔍 Inspect Full LangGraph State Object JSON"):
                st.json(state)
            
            if state.get("action_result", {}).get("customer_response"):
                st.subheader("📄 Generated Customer Response")
                st.code(state["action_result"]["customer_response"], language="markdown")

# ==============================================================================
# TAB 4: AGENT PERFORMANCE
# ==============================================================================
with tab4:
    st.subheader("📈 Agent Performance & Latency Analytics")

    async def get_agent_metrics():
        async with AsyncSessionLocal() as db:
            return await AgentRunRepository.list_all_logs(db, limit=500)

    all_logs = run_async(get_agent_metrics())
    if all_logs:
        df_logs = pd.DataFrame([{
            "Agent": l.agent_name,
            "Status": l.status,
            "Duration (ms)": l.duration_ms,
            "Retry Count": l.retry_count,
            "Timestamp": l.created_at
        } for l in all_logs])

        # Summary Table
        summary = df_logs.groupby("Agent").agg(
            Executions=("Status", "count"),
            Avg_Latency_ms=("Duration (ms)", "mean"),
            Retries=("Retry Count", "sum")
        ).reset_index()

        st.dataframe(summary, use_container_width=True)

        # Bar chart
        st.subheader("Average Latency per Agent (ms)")
        st.bar_chart(summary, x="Agent", y="Avg_Latency_ms")

# ==============================================================================
# TAB 5: EXECUTION LOGS
# ==============================================================================
with tab5:
    st.subheader("📜 LLMOps Execution Audit Stream")

    if all_logs:
        for log in all_logs[:20]:
            with st.expander(f"📌 [{log.created_at.strftime('%H:%M:%S')}] {log.agent_name} - {log.status} ({round(log.duration_ms, 2)} ms)"):
                st.write(f"**Workflow Run ID**: `{log.workflow_run_id}`")
                st.write("**Input Context**:")
                st.json(log.input_data or {})
                st.write("**Output Result**:")
                st.json(log.output_data or {})
                if log.error:
                    st.error(f"Error: {log.error}")
