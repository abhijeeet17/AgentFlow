export interface Ticket {
  id: string;
  customer_id?: string;
  title: string;
  description: string;
  category?: string;
  priority?: string;
  status: string;
  assigned_team?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkflowRun {
  id: string;
  ticket_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  state_data?: Record<string, any>;
}

export interface Approval {
  id: string;
  workflow_run_id: string;
  risk_level: string;
  reason: string;
  status: string;
  approved_by?: string;
  decision_notes?: string;
  created_at: string;
  resolved_at?: string;
}

export interface AgentPerformance {
  agent_name: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  success_rate: number;
  avg_latency_ms: number;
  retries_count: number;
}

export interface AgentRunLog {
  id: string;
  workflow_run_id: string;
  agent_name: string;
  status: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  duration_ms: number;
  error?: string;
  retry_count: number;
  created_at: string;
}
