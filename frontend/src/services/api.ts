import { Ticket, WorkflowRun, Approval, AgentPerformance, AgentRunLog } from '../types';

const API_BASE = '/api';

export const api = {
  async getTickets(): Promise<Ticket[]> {
    const res = await fetch(`${API_BASE}/tickets`);
    if (!res.ok) throw new Error('Failed to fetch tickets');
    return res.json();
  },

  async getTicket(id: string): Promise<Ticket> {
    const res = await fetch(`${API_BASE}/tickets/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch ticket ${id}`);
    return res.json();
  },

  async createTicket(data: { title: string; description: string; customer_id?: string }): Promise<Ticket> {
    const res = await fetch(`${API_BASE}/tickets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create ticket');
    return res.json();
  },

  async runWorkflow(ticketId: string): Promise<{ workflow_run_id: string; status: string; state: any }> {
    const res = await fetch(`${API_BASE}/workflows/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticket_id: ticketId }),
    });
    if (!res.ok) throw new Error('Failed to run workflow');
    return res.json();
  },

  async getWorkflows(): Promise<WorkflowRun[]> {
    const res = await fetch(`${API_BASE}/workflows`);
    if (!res.ok) throw new Error('Failed to fetch workflows');
    return res.json();
  },

  async getWorkflowRun(runId: string): Promise<WorkflowRun> {
    const res = await fetch(`${API_BASE}/workflows/${runId}`);
    if (!res.ok) throw new Error(`Failed to fetch workflow run ${runId}`);
    return res.json();
  },

  async getPendingApprovals(): Promise<Approval[]> {
    const res = await fetch(`${API_BASE}/approvals/pending`);
    if (!res.ok) throw new Error('Failed to fetch pending approvals');
    return res.json();
  },

  async respondToApproval(approvalId: string, approved: boolean, notes?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/approvals/${approvalId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved, notes, approved_by: 'Dashboard User' }),
    });
    if (!res.ok) throw new Error('Failed to respond to approval');
    return res.json();
  },

  async getAgentSummaries(): Promise<AgentPerformance[]> {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to fetch agent summaries');
    return res.json();
  },

  async getAllLogs(): Promise<AgentRunLog[]> {
    const res = await fetch(`${API_BASE}/logs`);
    if (!res.ok) throw new Error('Failed to fetch agent logs');
    return res.json();
  },

  async getWorkflowLogs(runId: string): Promise<AgentRunLog[]> {
    const res = await fetch(`${API_BASE}/runs/${runId}/logs`);
    if (!res.ok) throw new Error(`Failed to fetch logs for workflow ${runId}`);
    return res.json();
  }
};
