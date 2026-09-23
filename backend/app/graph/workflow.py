import time
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import AgentState
from app.graph.routers import risk_router, verification_router
from app.agents.intake import intake_agent
from app.agents.classifier import classifier_agent
from app.agents.rag_agent import rag_agent
from app.agents.decision import decision_agent
from app.agents.action import action_agent
from app.agents.verifier import verifier_agent
from app.monitoring.logger import agent_logger
from app.monitoring.metrics import metrics_manager
from app.database.database import AsyncSessionLocal
from app.database.repositories import AgentRunRepository

logger = logging.getLogger(__name__)

async def persist_agent_log(
    workflow_run_id: str,
    agent_name: str,
    status: str,
    duration_ms: float,
    input_data: Dict[str, Any] = None,
    output_data: Dict[str, Any] = None,
    retry_count: int = 0,
    error: str = None
):
    try:
        async with AsyncSessionLocal() as db:
            await AgentRunRepository.log_run(
                session=db,
                workflow_run_id=workflow_run_id,
                agent_name=agent_name,
                status=status,
                input_data=input_data,
                output_data=output_data,
                duration_ms=duration_ms,
                error=error,
                retry_count=retry_count
            )
    except Exception as ex:
        logger.error(f"Failed to persist agent run log to DB: {ex}")

# Node 1: Intake
async def node_intake(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    run_id = state.get("workflow_run_id", "RUN-0")
    try:
        cleaned_ticket = intake_agent.process(state["ticket"])
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="intake_agent",
            status="SUCCESS",
            duration_ms=duration,
            input_data=state["ticket"],
            output_data=cleaned_ticket
        )
        await persist_agent_log(run_id, "intake_agent", "SUCCESS", duration, state["ticket"], cleaned_ticket)
        metrics_manager.record_agent_latency("intake_agent", duration)
        return {"ticket": cleaned_ticket, "status": "INTAKE_COMPLETED"}
    except Exception as e:
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="intake_agent",
            status="FAILED",
            duration_ms=duration,
            error=str(e)
        )
        await persist_agent_log(run_id, "intake_agent", "FAILED", duration, error=str(e))
        return {"errors": [f"Intake Error: {str(e)}"], "status": "FAILED"}


# Node 2: Classifier
async def node_classifier(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    run_id = state.get("workflow_run_id", "RUN-0")
    try:
        cls_result = await classifier_agent.process(state["ticket"])
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="classification_agent",
            status="SUCCESS",
            duration_ms=duration,
            input_data=state["ticket"],
            output_data=cls_result
        )
        await persist_agent_log(run_id, "classification_agent", "SUCCESS", duration, state["ticket"], cls_result)
        metrics_manager.record_agent_latency("classification_agent", duration)
        return {"classification": cls_result, "status": "CLASSIFIED"}
    except Exception as e:
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="classification_agent",
            status="FAILED",
            duration_ms=duration,
            error=str(e)
        )
        await persist_agent_log(run_id, "classification_agent", "FAILED", duration, error=str(e))
        return {"errors": [f"Classification Error: {str(e)}"], "status": "FAILED"}


# Node 3: RAG Retrieval
async def node_rag(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    run_id = state.get("workflow_run_id", "RUN-0")
    try:
        rag_result = await rag_agent.process(state["ticket"], state.get("classification", {}))
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="rag_retrieval_agent",
            status="SUCCESS",
            duration_ms=duration,
            input_data={"ticket": state["ticket"], "classification": state.get("classification")},
            output_data={"sources": rag_result.get("sources"), "doc_count": len(rag_result.get("documents", []))}
        )
        await persist_agent_log(run_id, "rag_retrieval_agent", "SUCCESS", duration, {"classification": state.get("classification")}, rag_result)
        metrics_manager.record_agent_latency("rag_retrieval_agent", duration)
        return {"retrieved_documents": rag_result, "status": "RAG_COMPLETED"}
    except Exception as e:
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="rag_retrieval_agent",
            status="FAILED",
            duration_ms=duration,
            error=str(e)
        )
        await persist_agent_log(run_id, "rag_retrieval_agent", "FAILED", duration, error=str(e))
        return {"errors": [f"RAG Error: {str(e)}"], "status": "FAILED"}


# Node 4: Decision
async def node_decision(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    run_id = state.get("workflow_run_id", "RUN-0")
    try:
        dec_result = await decision_agent.process(
            ticket=state["ticket"],
            classification=state.get("classification", {}),
            retrieved_documents=state.get("retrieved_documents", {})
        )
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="decision_agent",
            status="SUCCESS",
            duration_ms=duration,
            input_data={"classification": state.get("classification")},
            output_data=dec_result
        )
        await persist_agent_log(run_id, "decision_agent", "SUCCESS", duration, {"classification": state.get("classification")}, dec_result)
        metrics_manager.record_agent_latency("decision_agent", duration)
        return {"decision": dec_result, "status": "DECISION_MADE"}
    except Exception as e:
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="decision_agent",
            status="FAILED",
            duration_ms=duration,
            error=str(e)
        )
        await persist_agent_log(run_id, "decision_agent", "FAILED", duration, error=str(e))
        return {"errors": [f"Decision Error: {str(e)}"], "status": "FAILED"}


# Node 5: Human Approval Interrupt Node
async def node_human_approval(state: AgentState) -> Dict[str, Any]:
    logger.info(f"Workflow {state.get('workflow_run_id')} paused for Human Approval.")
    return {"status": "PENDING_APPROVAL"}


# Node 6: Action
async def node_action(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    run_id = state.get("workflow_run_id", "RUN-0")
    try:
        if state.get("human_approved") is False:
            act_result = {
                "action_type": "REJECT_ACTION",
                "customer_response": "Your request was reviewed by our human operations team and was rejected as per policy limits.",
                "assigned_team": state.get("classification", {}).get("department", "Support"),
                "status_update": "REJECTED",
                "execution_details": {"approved_by": "Human Reviewer", "decision": "REJECTED"}
            }
        else:
            act_result = await action_agent.process(
                ticket=state["ticket"],
                classification=state.get("classification", {}),
                decision=state.get("decision", {}),
                retrieved_documents=state.get("retrieved_documents", {})
            )
        
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="action_agent",
            status="SUCCESS",
            duration_ms=duration,
            input_data={"decision": state.get("decision")},
            output_data=act_result
        )
        await persist_agent_log(run_id, "action_agent", "SUCCESS", duration, {"decision": state.get("decision")}, act_result)
        metrics_manager.record_agent_latency("action_agent", duration)
        return {"action_result": act_result, "status": "ACTION_EXECUTED"}
    except Exception as e:
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="action_agent",
            status="FAILED",
            duration_ms=duration,
            error=str(e)
        )
        await persist_agent_log(run_id, "action_agent", "FAILED", duration, error=str(e))
        return {"errors": [f"Action Error: {str(e)}"], "status": "FAILED"}


# Node 7: Verification
async def node_verifier(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    run_id = state.get("workflow_run_id", "RUN-0")
    try:
        ver_result = await verifier_agent.process(
            ticket=state["ticket"],
            decision=state.get("decision", {}),
            action_result=state.get("action_result", {}),
            retrieved_documents=state.get("retrieved_documents", {})
        )
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="verification_agent",
            status="SUCCESS",
            duration_ms=duration,
            input_data={"action_type": state.get("action_result", {}).get("action_type")},
            output_data=ver_result
        )
        await persist_agent_log(run_id, "verification_agent", "SUCCESS", duration, {"action_type": state.get("action_result", {}).get("action_type")}, ver_result)
        metrics_manager.record_agent_latency("verification_agent", duration)
        
        new_retry_count = state.get("retry_count", 0)
        if not ver_result.get("approved"):
            new_retry_count += 1

        final_status = "COMPLETED" if ver_result.get("approved") else "VERIFICATION_FAILED"
        return {
            "verification": ver_result,
            "retry_count": new_retry_count,
            "status": final_status
        }
    except Exception as e:
        duration = (time.time() - t0) * 1000
        agent_logger.log_agent_execution(
            run_id=run_id,
            agent_name="verification_agent",
            status="FAILED",
            duration_ms=duration,
            error=str(e)
        )
        await persist_agent_log(run_id, "verification_agent", "FAILED", duration, error=str(e))
        return {"errors": [f"Verification Error: {str(e)}"], "status": "FAILED"}


# Node 8: Escalation Fallback Node
async def node_escalate(state: AgentState) -> Dict[str, Any]:
    logger.warning(f"Workflow {state.get('workflow_run_id')} escalated after max retries or verification failures.")
    return {"status": "ESCALATED"}


# Build LangGraph
def build_agentflow_graph():
    builder = StateGraph(AgentState)

    # Add Nodes
    builder.add_node("intake_agent", node_intake)
    builder.add_node("classification_agent", node_classifier)
    builder.add_node("rag_agent", node_rag)
    builder.add_node("decision_agent", node_decision)
    builder.add_node("human_approval", node_human_approval)
    builder.add_node("action_agent", node_action)
    builder.add_node("verification_agent", node_verifier)
    builder.add_node("escalate", node_escalate)

    # Add Edges
    builder.add_edge(START, "intake_agent")
    builder.add_edge("intake_agent", "classification_agent")
    builder.add_edge("classification_agent", "rag_agent")
    builder.add_edge("rag_agent", "decision_agent")

    # Risk Router Conditional Edge
    builder.add_conditional_edges(
        "decision_agent",
        risk_router,
        {
            "human_approval": "human_approval",
            "action_agent": "action_agent"
        }
    )

    builder.add_edge("human_approval", "action_agent")
    builder.add_edge("action_agent", "verification_agent")

    # Verification Conditional Edge
    builder.add_conditional_edges(
        "verification_agent",
        verification_router,
        {
            "completed": END,
            "decision_agent": "decision_agent",
            "escalate": "escalate"
        }
    )

    builder.add_edge("escalate", END)

    # Compile with memory saver checkpointer & interrupt on human approval node
    checkpointer = MemorySaver()
    compiled_graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_approval"]
    )
    return compiled_graph

agentflow_graph = build_agentflow_graph()
