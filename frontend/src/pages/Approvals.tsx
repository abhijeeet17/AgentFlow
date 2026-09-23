import React, { useEffect, useState } from 'react';
import { Approval } from '../types';
import { api } from '../services/api';
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [notes, setNotes] = useState<{ [key: string]: string }>({});
  const [processing, setProcessing] = useState<string | null>(null);

  useEffect(() => {
    loadApprovals();
  }, []);

  async function loadApprovals() {
    try {
      const data = await api.getPendingApprovals();
      setApprovals(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDecision(approvalId: string, approved: boolean) {
    setProcessing(approvalId);
    try {
      await api.respondToApproval(approvalId, approved, notes[approvalId] || '');
      await loadApprovals();
    } catch (err) {
      console.error(err);
    } finally {
      setProcessing(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-amber-400" />
          Human Approval Queue
        </h2>
        <p className="text-xs text-slate-400">High-risk financial or security tickets paused for Human-in-the-Loop approval</p>
      </div>

      {approvals.length === 0 ? (
        <div className="bg-slate-800/40 border border-slate-700/60 rounded-xl p-12 text-center space-y-3">
          <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
          <h3 className="text-base font-semibold text-white">No Pending Approvals</h3>
          <p className="text-xs text-slate-400">All workflow runs are auto-processed or already resolved.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {approvals.map((appr) => (
            <div key={appr.id} className="bg-slate-800/80 border border-amber-500/30 rounded-2xl p-6 space-y-4 shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                  <span className="text-xs font-mono text-slate-400">Approval ID: {appr.id}</span>
                </div>
                <StatusBadge status={appr.risk_level} />
              </div>

              <div className="space-y-1">
                <div className="text-xs text-slate-400">Workflow Run ID</div>
                <div className="font-mono text-sm text-sky-400 font-semibold">{appr.workflow_run_id}</div>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 font-mono">
                <span className="text-amber-400 font-semibold">Reason: </span>
                {appr.reason}
              </div>

              <div className="space-y-2">
                <label className="block text-xs text-slate-400">Decision Notes (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Bank statement verified, authorizing refund..."
                  value={notes[appr.id] || ''}
                  onChange={(e) => setNotes({ ...notes, [appr.id]: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => handleDecision(appr.id, true)}
                  disabled={processing === appr.id}
                  className="flex-1 flex items-center justify-center space-x-2 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-emerald-500/20 transition"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Action</span>
                </button>
                <button
                  onClick={() => handleDecision(appr.id, false)}
                  disabled={processing === appr.id}
                  className="flex-1 flex items-center justify-center space-x-2 py-2.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-rose-500/20 transition"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Action</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
