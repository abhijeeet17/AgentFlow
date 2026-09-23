import React, { useEffect, useState } from 'react';
import { Ticket, WorkflowRun, Approval, AgentPerformance } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Ticket as TicketIcon, ShieldCheck, CheckCircle2, Clock, AlertTriangle, Play, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Overview: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowRun[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<Approval[]>([]);
  const [agentStats, setAgentStats] = useState<AgentPerformance[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [t, w, a, ag] = await Promise.all([
          api.getTickets(),
          api.getWorkflows(),
          api.getPendingApprovals(),
          api.getAgentSummaries()
        ]);
        setTickets(t);
        setWorkflows(w);
        setPendingApprovals(a);
        setAgentStats(ag);
      } catch (err) {
        console.error("Failed to load dashboard overview data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalTickets = tickets.length;
  const successfulWorkflows = workflows.filter(w => ['RESOLVED', 'COMPLETED', 'ACTION_EXECUTED'].includes(w.status)).length;
  const failedWorkflows = workflows.filter(w => w.status === 'FAILED').length;
  const pendingCount = pendingApprovals.length;
  
  const avgLatency = agentStats.length > 0 
    ? Math.round(agentStats.reduce((acc, curr) => acc + curr.avg_latency_ms, 0) / agentStats.length)
    : 120;

  return (
    <div className="space-y-6">
      {/* Metrics Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Total Tickets</span>
            <TicketIcon className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">{totalTickets}</div>
          <p className="text-xs text-slate-500">Processed across channels</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Successful Workflows</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{successfulWorkflows}</div>
          <p className="text-xs text-slate-500">Auto-resolved & Verified</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Pending Approvals</span>
            <ShieldCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">{pendingCount}</div>
          <p className="text-xs text-slate-500">Awaiting Human Authorization</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Avg Agent Latency</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{avgLatency} ms</div>
          <p className="text-xs text-slate-500">Per node execution</p>
        </div>
      </div>

      {/* Pending Approvals Alert Banner */}
      {pendingCount > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-amber-300">Action Required: {pendingCount} High-Risk Request(s)</h4>
              <p className="text-xs text-amber-400/80">Automated financial or security tickets paused for Human Approval.</p>
            </div>
          </div>
          <Link
            to="/approvals"
            className="px-4 py-2 bg-amber-500 text-slate-950 font-semibold rounded-lg text-xs hover:bg-amber-400 transition"
          >
            Review Pending Queue
          </Link>
        </div>
      )}

      {/* Recent Tickets Table */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-white">Recent Support Tickets</h3>
          <Link to="/tickets" className="text-xs text-sky-400 hover:text-sky-300 font-medium">
            View All Tickets →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/60 text-xs uppercase text-slate-400 border-b border-slate-700/50">
              <tr>
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4">Title</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {tickets.slice(0, 5).map((t) => (
                <tr key={t.id} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-mono text-xs text-sky-400 font-semibold">{t.id}</td>
                  <td className="py-3 px-4 font-medium text-slate-200">{t.title}</td>
                  <td className="py-3 px-4 text-xs text-slate-400">{t.category || 'Unclassified'}</td>
                  <td className="py-3 px-4 text-xs text-slate-400">{t.priority || 'Medium'}</td>
                  <td className="py-3 px-4"><StatusBadge status={t.status} /></td>
                  <td className="py-3 px-4">
                    <Link
                      to={`/tickets/${t.id}`}
                      className="text-xs px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-200 font-medium transition"
                    >
                      Inspect Graph
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
