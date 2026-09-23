import React, { useEffect, useState } from 'react';
import { AgentRunLog } from '../types';
import { api } from '../services/api';
import { Terminal, Search, Clock, Cpu } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export const Logs: React.FC = () => {
  const [logs, setLogs] = useState<AgentRunLog[]>([]);
  const [filterAgent, setFilterAgent] = useState<string>('');

  useEffect(() => {
    loadLogs();
  }, []);

  async function loadLogs() {
    try {
      const data = await api.getAllLogs();
      setLogs(data);
    } catch (err) {
      console.error(err);
    }
  }

  const filteredLogs = logs.filter(
    l => !filterAgent || l.agent_name.toLowerCase().includes(filterAgent.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Terminal className="w-6 h-6 text-indigo-400" />
            Agent Execution Logs & Traceability
          </h2>
          <p className="text-xs text-slate-400">LLMOps structured audit log for every agent node execution</p>
        </div>

        <input
          type="text"
          placeholder="Filter logs by agent name..."
          value={filterAgent}
          onChange={(e) => setFilterAgent(e.target.value)}
          className="bg-slate-800/80 border border-slate-700/60 rounded-xl px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
        />
      </div>

      <div className="space-y-3 font-mono text-xs">
        {filteredLogs.map((log) => (
          <div key={log.id} className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-3">
                <span className="font-semibold text-sky-400">{log.agent_name}</span>
                <span className="text-[11px] text-slate-500">Run ID: {log.workflow_run_id}</span>
              </div>
              <div className="flex items-center space-x-3">
                <StatusBadge status={log.status} />
                <span className="text-slate-400">{Math.round(log.duration_ms)} ms</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px]">
              <div>
                <span className="text-slate-500 block mb-1">Input Context:</span>
                <pre className="bg-slate-950/60 p-2.5 rounded-lg text-slate-300 overflow-x-auto max-h-36">
                  {log.input_data ? JSON.stringify(log.input_data, null, 2) : 'N/A'}
                </pre>
              </div>

              <div>
                <span className="text-slate-500 block mb-1">Output Result:</span>
                <pre className="bg-slate-950/60 p-2.5 rounded-lg text-slate-300 overflow-x-auto max-h-36">
                  {log.output_data ? JSON.stringify(log.output_data, null, 2) : log.error || 'N/A'}
                </pre>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
