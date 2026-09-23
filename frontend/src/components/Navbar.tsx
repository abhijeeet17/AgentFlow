import React from 'react';
import { Bot, ShieldAlert, Cpu, Activity } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header className="h-16 bg-slate-800/80 backdrop-blur-md border-b border-slate-700/60 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-tr from-sky-600 to-indigo-600 rounded-xl shadow-lg shadow-sky-500/20">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
            AgentFlow
            <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30 font-mono">
              v1.0.0
            </span>
          </h1>
          <p className="text-xs text-slate-400">Multi-Agent Business Workflow Automation</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-900/60 rounded-lg border border-slate-700/50 text-xs text-slate-300">
          <Activity className="w-4 h-4 text-emerald-400 animate-pulse" />
          <span>System Healthy</span>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-900/60 rounded-lg border border-slate-700/50 text-xs text-slate-300">
          <Cpu className="w-4 h-4 text-sky-400" />
          <span>LangGraph Engine</span>
        </div>
      </div>
    </header>
  );
};
