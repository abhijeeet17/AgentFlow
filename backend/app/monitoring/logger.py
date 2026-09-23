import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agentflow.observability")

class AgentLogger:
    @staticmethod
    def log_agent_execution(
        run_id: str,
        agent_name: str,
        status: str,
        duration_ms: float,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        error: Optional[str] = None,
        model: Optional[str] = "mock-model"
    ):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": run_id,
            "agent": agent_name,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "retry_count": retry_count,
            "model": model,
            "error": error,
            "input_summary": str(input_data)[:200] if input_data else None,
            "output_summary": str(output_data)[:200] if output_data else None
        }
        logger.info(f"AGENT_EXECUTION: {json.dumps(log_record)}")

agent_logger = AgentLogger()
