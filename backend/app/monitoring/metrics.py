try:
    from prometheus_client import Counter, Histogram, Gauge

    WORKFLOW_EXECUTIONS = Counter('agentflow_workflow_executions_total', 'Total workflow executions', ['status'])
    AGENT_LATENCY = Histogram('agentflow_agent_latency_seconds', 'Agent execution latency in seconds', ['agent_name'])
    ACTIVE_WORKFLOWS = Gauge('agentflow_active_workflows', 'Number of currently active workflows')
    PENDING_APPROVALS = Gauge('agentflow_pending_approvals', 'Number of pending human approvals')
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    WORKFLOW_EXECUTIONS = None
    AGENT_LATENCY = None
    ACTIVE_WORKFLOWS = None
    PENDING_APPROVALS = None

class MetricsManager:
    @staticmethod
    def record_workflow_execution(status: str):
        if PROMETHEUS_AVAILABLE and WORKFLOW_EXECUTIONS:
            WORKFLOW_EXECUTIONS.labels(status=status).inc()

    @staticmethod
    def record_agent_latency(agent_name: str, duration_ms: float):
        if PROMETHEUS_AVAILABLE and AGENT_LATENCY:
            AGENT_LATENCY.labels(agent_name=agent_name).observe(duration_ms / 1000.0)

metrics_manager = MetricsManager()
