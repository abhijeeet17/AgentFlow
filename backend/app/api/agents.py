from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import AgentRunRepository
from app.schemas.agent import AgentPerformanceSummary

router = APIRouter(prefix="/agents", tags=["Agents"])

AGENT_NAMES = [
    "intake_agent",
    "classification_agent",
    "rag_retrieval_agent",
    "decision_agent",
    "action_agent",
    "verification_agent"
]

@router.get("", response_model=List[AgentPerformanceSummary])
async def list_agent_summaries(db: AsyncSession = Depends(get_db)):
    logs = await AgentRunRepository.list_all_logs(db, limit=500)
    
    stats: Dict[str, Dict[str, Any]] = {
        name: {
            "agent_name": name,
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_duration": 0.0,
            "retries_count": 0
        } for name in AGENT_NAMES
    }

    for log in logs:
        name = log.agent_name
        if name not in stats:
            stats[name] = {
                "agent_name": name,
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_duration": 0.0,
                "retries_count": 0
            }
        
        s = stats[name]
        s["total_executions"] += 1
        if log.status == "SUCCESS":
            s["successful_executions"] += 1
        else:
            s["failed_executions"] += 1
        s["total_duration"] += log.duration_ms
        s["retries_count"] += log.retry_count

    summaries = []
    for name, s in stats.items():
        total = s["total_executions"]
        succ = s["successful_executions"]
        rate = round((succ / total) * 100, 1) if total > 0 else 100.0
        avg_lat = round(s["total_duration"] / total, 2) if total > 0 else 0.0

        summaries.append(AgentPerformanceSummary(
            agent_name=name,
            total_executions=total,
            successful_executions=succ,
            failed_executions=s["failed_executions"],
            success_rate=rate,
            avg_latency_ms=avg_lat,
            retries_count=s["retries_count"]
        ))
    return summaries

@router.get("/{agent_name}", response_model=AgentPerformanceSummary)
async def get_agent_summary(agent_name: str, db: AsyncSession = Depends(get_db)):
    summaries = await list_agent_summaries(db)
    for s in summaries:
        if s.agent_name.lower() == agent_name.lower():
            return s
    raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found.")
