import React, { useEffect, useState } from 'react';
import { AgentPerformance } from '../types';
import { api } from '../services/api';
import { Cpu, CheckCircle2, Clock, RotateCcw } from 'lucide-react';

export const Agents: React.FC = () => {
  const [agents, setAgents] = useState<AgentPerformance[]>([]);

  useEffect(() => {
    loadAgents();
  }, []);

  async function loadAgents() {
    try {
      const data = await api.getAgentSummaries();
      setAgents(data);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-6 h-6 text-sky-400" />
          Agent Performance & Latency Metrics
        </h2>
        <p className="text-xs text-slate-400">Monitoring execution stats, success rates, and retry counts across all 6 agents</p>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400 border-b border-slate-700/50">
            <tr>
              <th className="py-3.5 px-4">Agent Name</th>
              <th className="py-3.5 px-4">Total Executions</th>
              <th className="py-3.5 px-4">Success Rate</th>
              <th className="py-3.5 px-4">Failed</th>
              <th className="py-3.5 px-4">Avg Latency</th>
              <th className="py-3.5 px-4">Retries</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {agents.map((ag) => (
              <tr key={ag.agent_name} className="hover:bg-slate-800/40">
                <td className="py-3.5 px-4 font-semibold text-slate-200 flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-sky-400"></div>
                  <span>{ag.agent_name}</span>
                </td>
                <td className="py-3.5 px-4 text-xs text-slate-300 font-mono">{ag.total_executions}</td>
                <td className="py-3.5 px-4">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    {ag.success_rate}%
                  </span>
                </td>
                <td className="py-3.5 px-4 text-xs text-rose-400 font-mono">{ag.failed_executions}</td>
                <td className="py-3.5 px-4 text-xs text-slate-300 font-mono">{ag.avg_latency_ms} ms</td>
                <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">{ag.retries_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
