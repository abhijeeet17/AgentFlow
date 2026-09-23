import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, ArrowRight, ShieldAlert, Cpu, FileText, Send, Sparkles } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface WorkflowTimelineProps {
  stateData?: Record<string, any>;
  currentStatus: string;
}

export const WorkflowTimeline: React.FC<WorkflowTimelineProps> = ({ stateData, currentStatus }) => {
  const ticket = stateData?.ticket;
  const classification = stateData?.classification;
  const retrieved = stateData?.retrieved_documents;
  const decision = stateData?.decision;
  const action = stateData?.action_result;
  const verification = stateData?.verification;

  const steps = [
    {
      id: 'intake',
      name: 'Intake Agent',
      icon: Cpu,
      completed: !!ticket,
      data: ticket ? `Cleaned Ticket ID: ${ticket.ticket_id}` : 'Pending Intake...'
    },
    {
      id: 'classification',
      name: 'Classification Agent',
      icon: Sparkles,
      completed: !!classification && Object.keys(classification).length > 0,
      data: classification ? `Category: ${classification.category} | Priority: ${classification.priority}` : 'Pending Classification...'
    },
    {
      id: 'rag',
      name: 'RAG Retrieval Agent',
      icon: FileText,
      completed: !!retrieved && retrieved.documents?.length >= 0,
      data: retrieved ? `Retrieved ${retrieved.documents?.length || 0} policy docs (Score: ${retrieved.retrieval_score})` : 'Pending Retrieval...'
    },
    {
      id: 'decision',
      name: 'Decision Agent',
      icon: Cpu,
      completed: !!decision && Object.keys(decision).length > 0,
      data: decision ? `Decision: ${decision.decision} | Risk: ${decision.risk_level}` : 'Pending Decision...'
    },
    {
      id: 'approval',
      name: 'Human Approval Router',
      icon: ShieldAlert,
      completed: currentStatus !== 'PENDING_APPROVAL' && (stateData?.human_approved !== undefined || decision?.risk_level === 'LOW'),
      isPending: currentStatus === 'PENDING_APPROVAL',
      data: currentStatus === 'PENDING_APPROVAL' 
        ? 'PAUSED: Awaiting Manager Approval' 
        : (stateData?.human_approved ? 'APPROVED by Human Reviewer' : 'Low Risk / Auto-Approved')
    },
    {
      id: 'action',
      name: 'Action Agent',
      icon: Send,
      completed: !!action && Object.keys(action).length > 0,
      data: action ? `Action: ${action.action_type || 'Executed'}` : 'Pending Action...'
    },
    {
      id: 'verifier',
      name: 'Verification Agent',
      icon: CheckCircle2,
      completed: !!verification && Object.keys(verification).length > 0,
      data: verification ? `Quality Approved: ${verification.approved}` : 'Pending Verification...'
    }
  ];

  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-200 flex items-center gap-2">
          LangGraph Execution Timeline
        </h3>
        <StatusBadge status={currentStatus} />
      </div>

      <div className="relative">
        <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-slate-700 -z-0"></div>
        <div className="space-y-6">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            let statusColor = 'bg-slate-800 text-slate-500 border-slate-700';
            if (step.isPending) {
              statusColor = 'bg-amber-500/20 text-amber-400 border-amber-500 animate-pulse';
            } else if (step.completed) {
              statusColor = 'bg-sky-500/20 text-sky-400 border-sky-500/50';
            }

            return (
              <div key={step.id} className="flex items-start space-x-4 relative z-10">
                <div className={`p-2.5 rounded-xl border ${statusColor} shrink-0`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-200">{step.name}</span>
                    <span className="text-xs text-slate-500">Step {idx + 1}</span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono">{step.data}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
