import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Ticket, GitFork, ShieldCheck, Cpu, Terminal } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/tickets', label: 'Tickets', icon: Ticket },
    { to: '/approvals', label: 'Human Approvals', icon: ShieldCheck },
    { to: '/agents', label: 'Agent Performance', icon: Cpu },
    { to: '/logs', label: 'Execution Logs', icon: Terminal },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Platform Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800 text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-300">RAG Knowledge Base</div>
        <p className="text-[11px] text-slate-500">ChromaDB Persistent Store Active</p>
      </div>
    </aside>
  );
};
