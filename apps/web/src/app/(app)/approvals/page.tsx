'use client';

import React, { useState, useEffect } from 'react';
import { CheckSquare, CheckCircle, XCircle, AlertTriangle, User, Shield, Loader2 } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { toast } from 'sonner';

interface Approval {
  id: string;
  action_type: string;
  description: string;
  proposed_by: string;
  parameters: Record<string, unknown>;
  evidence?: string[];
  created_at: string;
  priority?: 'low' | 'medium' | 'high';
}

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      const res = await apiFetch('/v1/approvals');
      if (res.ok) setApprovals(await res.json());
    } catch { /* silent */ } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchApprovals(); }, []);

  const handleDecision = async (id: string, decision: 'approve' | 'reject') => {
    setActionInProgress(id);
    try {
      const res = await apiFetch(`/v1/approvals/${id}/${decision}`, { method: 'POST' });
      if (res.ok) {
        setApprovals(prev => prev.filter(a => a.id !== id));
        toast.success(decision === 'approve' ? 'Action approved' : 'Action rejected');
      } else {
        toast.error(`Failed to ${decision} action`);
      }
    } catch {
      toast.error('Connection error');
    } finally {
      setActionInProgress(null);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 text-primary">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Approvals</h1>
          <p className="text-secondary">Human-in-the-loop action queue — review agent-proposed actions.</p>
        </div>
        {approvals.length > 0 && (
          <div className="px-3 py-1 bg-accent/10 text-accent rounded-full text-xs font-bold border border-accent/20">
            {approvals.length} PENDING
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 rounded-xl p-4 bg-accent/5 border border-accent/10">
        <div className="p-2 bg-accent/10 rounded-lg text-accent">
          <Shield size={20} />
        </div>
        <div className="flex-1">
          <div className="text-sm font-bold text-primary">Autonomous Safety Protocol</div>
          <p className="text-xs text-secondary mt-0.5">
            Agents require explicit authorization for actions involving external communication or financial commitments.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-surface border border-dim animate-pulse" />
          ))}
        </div>
      ) : approvals.length === 0 ? (
        <div className="border border-dim rounded-xl p-16 text-center bg-surface flex flex-col items-center">
          <div className="w-20 h-20 bg-green-status/10 rounded-full flex items-center justify-center mb-6">
            <CheckSquare className="h-10 w-10 text-green-status opacity-40" />
          </div>
          <h3 className="text-xl font-bold text-primary">Your inbox is clear</h3>
          <p className="text-secondary mt-2 max-w-sm">No actions currently require manual intervention. Your agents are operating within approved constraints.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {approvals.map((approval) => {
            const isHigh = approval.priority === 'high';
            return (
              <div
                key={approval.id}
                className="rounded-xl overflow-hidden bg-surface border border-dim hover:border-accent/30 transition-all shadow-sm group"
              >
                <div className={`p-1 h-1 ${isHigh ? 'bg-red-status' : 'bg-accent/20'}`} />
                
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-accent bg-accent/10 px-2 py-0.5 rounded">
                          {approval.action_type}
                        </span>
                        {isHigh && (
                          <span className="text-[10px] font-bold uppercase tracking-widest text-red-status bg-red-status/10 px-2 py-0.5 rounded flex items-center gap-1">
                            <AlertTriangle size={10} /> HIGH PRIORITY
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-bold text-primary">{approval.description}</h3>
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-[11px] text-muted mb-1">REQ-{approval.id.split('-')[0].toUpperCase()}</div>
                      <div className="flex items-center gap-1.5 text-[11px] text-muted justify-end">
                        <User size={10} /> {approval.proposed_by}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    {approval.parameters && Object.keys(approval.parameters).length > 0 && (
                      <div className="rounded-lg bg-elevated/40 border border-dim p-4">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-muted mb-3">Action Data</div>
                        <div className="space-y-2">
                          {Object.entries(approval.parameters).map(([k, v]) => (
                            <div key={k} className="flex justify-between items-center text-xs">
                              <span className="text-muted font-mono">{k}</span>
                              <span className="text-secondary font-medium">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {approval.evidence && approval.evidence.length > 0 && (
                      <div className="rounded-lg bg-elevated/40 border border-dim p-4">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-muted mb-3">Evidence Chain</div>
                        <div className="space-y-2">
                          {approval.evidence.map((e, index) => (
                            <div key={index} className="flex items-start gap-2 text-xs text-secondary">
                              <div className="w-4 h-4 rounded-full bg-accent/10 text-accent flex items-center justify-center flex-shrink-0 text-[10px] mt-0.5">
                                {index + 1}
                              </div>
                              <p>{e}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-6 border-t border-dim">
                    <span className="text-[11px] text-muted">Proposed {relativeTime(approval.created_at)}</span>
                    <div className="flex items-center gap-3">
                      <button
                        disabled={actionInProgress === approval.id}
                        onClick={() => handleDecision(approval.id, 'reject')}
                        className="flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-bold text-red-status hover:bg-red-status/10 transition-all disabled:opacity-50"
                      >
                        <XCircle size={16} />
                        Reject
                      </button>
                      <button
                        disabled={actionInProgress === approval.id}
                        onClick={() => handleDecision(approval.id, 'approve')}
                        className="flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-bold bg-green-status text-white hover:bg-green-status/90 transition-all disabled:opacity-50 shadow-lg shadow-green-status/20"
                      >
                        {actionInProgress === approval.id ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle size={16} />}
                        Approve Action
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
