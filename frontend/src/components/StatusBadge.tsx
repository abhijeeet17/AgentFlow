import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const s = status.toUpperCase();
  let color = 'bg-slate-700/50 text-slate-300 border-slate-600';

  if (['RESOLVED', 'COMPLETED', 'SUCCESS', 'APPROVED'].includes(s)) {
    color = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  } else if (['PENDING_APPROVAL', 'PENDING'].includes(s)) {
    color = 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse';
  } else if (['FAILED', 'REJECTED', 'HIGH', 'URGENT'].includes(s)) {
    color = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  } else if (['PROCESSING', 'RUNNING'].includes(s)) {
    color = 'bg-sky-500/10 text-sky-400 border-sky-500/30';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${color}`}>
      {status}
    </span>
  );
};
