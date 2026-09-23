import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Ticket, WorkflowRun, AgentRunLog } from '../types';
import { api } from '../services/api';
import { WorkflowTimeline } from '../components/WorkflowTimeline';
import { StatusBadge } from '../components/StatusBadge';
import { ArrowLeft, Play, Terminal, ShieldAlert, Cpu, FileText } from 'lucide-react';

export const WorkflowDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [workflowRun, setWorkflowRun] = useState<WorkflowRun | null>(null);
  const [logs, setLogs] = useState<AgentRunLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);

  useEffect(() => {
    if (id) loadTicketDetails(id);
  }, [id]);

  async function loadTicketDetails(ticketId: string) {
    try {
      const t = await api.getTicket(ticketId);
      setTicket(t);

      const allWfs = await api.getWorkflows();
      const run = allWfs.find(w => w.ticket_id === ticketId);
      if (run) {
        setWorkflowRun(run);
        const l = await api.getWorkflowLogs(run.id);
        setLogs(l);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunGraph() {
    if (!id) return;
    setRunning(true);
    try {
      await api.runWorkflow(id);
      await loadTicketDetails(id);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  }

  if (loading) return <div className="p-8 text-center text-slate-400">Loading workflow state...</div>;
  if (!ticket) return <div className="p-8 text-center text-slate-400">Ticket not found.</div>;

  const stateData = workflowRun?.state_data || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link to="/tickets" className="p-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-3">
              Ticket {ticket.id}
              <StatusBadge status={ticket.status} />
            </h2>
            <p className="text-xs text-slate-400">{ticket.title}</p>
          </div>
        </div>

        <button
          onClick={handleRunGraph}
          disabled={running}
          className="flex items-center space-x-2 px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-sky-500/20 transition"
        >
          <Play className="w-4 h-4" />
          <span>{running ? 'Running Graph...' : 'Re-trigger Workflow'}</span>
        </button>
      </div>

      {/* Grid details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Workflow Visual Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <WorkflowTimeline stateData={stateData} currentStatus={ticket.status} />

          {/* Generated Customer Response */}
          {stateData.action_result?.customer_response && (
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-6 space-y-3">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <FileText className="w-4 h-4 text-sky-400" />
                Action Agent Output (Customer Response)
              </h3>
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                {stateData.action_result.customer_response}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: State Inspection & Logs */}
        <div className="space-y-6">
          {/* Metadata Card */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-slate-200">Ticket Details</h3>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex justify-between border-b border-slate-700/40 pb-1.5">
                <span className="text-slate-400">Customer ID</span>
                <span className="font-mono">{ticket.customer_id || 'N/A'}</span>
              </div>
              <div className="flex justify-between border-b border-slate-700/40 pb-1.5">
                <span className="text-slate-400">Category</span>
                <span className="font-semibold">{ticket.category || 'Unclassified'}</span>
              </div>
              <div className="flex justify-between border-b border-slate-700/40 pb-1.5">
                <span className="text-slate-400">Priority</span>
                <span className="font-semibold">{ticket.priority || 'Medium'}</span>
              </div>
              <div className="flex justify-between border-b border-slate-700/40 pb-1.5">
                <span className="text-slate-400">Assigned Department</span>
                <span className="font-semibold">{ticket.assigned_team || 'Unassigned'}</span>
              </div>
            </div>
          </div>

          {/* Agent Logs */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-indigo-400" />
              Node Logs ({logs.length})
            </h3>
            <div className="space-y-2 max-h-80 overflow-y-auto text-xs font-mono pr-1">
              {logs.map((log) => (
                <div key={log.id} className="p-2.5 bg-slate-900/80 border border-slate-800 rounded-lg space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sky-400">{log.agent_name}</span>
                    <span className="text-[10px] text-slate-500">{Math.round(log.duration_ms)}ms</span>
                  </div>
                  <div className="text-[11px] text-slate-400 truncate">{log.output_data ? JSON.stringify(log.output_data) : log.error || 'SUCCESS'}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
