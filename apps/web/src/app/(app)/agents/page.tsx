'use client';

import React, { useState, useEffect } from 'react';
import { Bot, Play, X, CheckCircle, Circle, Loader2 } from 'lucide-react';
import { PageHeader } from '@/components/shared/PageHeader';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { MonoId } from '@/components/shared/MonoId';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { apiFetch } from '@/lib/api';
import { AgentRun } from '@/types/api';
import { toast } from 'sonner';

interface Agent {
  id: string;
  name: string;
  description: string;
  status: string;
  type: string;
}

interface RunStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  message?: string;
  steps?: { label: string; done: boolean }[];
}

const MOCK_AGENTS: Agent[] = [
  { id: 'ingestion_agent', name: 'Ingestion Agent', description: 'Extracts text, splits into chunks, and indexes documents into the vector store.', status: 'active', type: 'pipeline' },
  { id: 'rag_agent', name: 'RAG Agent', description: 'Retrieves context chunks and synthesizes answers using the backend inference engine.', status: 'active', type: 'inference' },
  { id: 'summarization_agent', name: 'Summarization Agent', description: 'Produces structured summaries from a collection of related document chunks.', status: 'active', type: 'pipeline' },
  { id: 'audit_agent', name: 'Audit Agent', description: 'Monitors agent runs for anomalies and flags suspicious activity.', status: 'disabled', type: 'autonomous' },
];

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function AgentsPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(true);
  const [modalAgent, setModalAgent] = useState<Agent | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [activePollId, setActivePollId] = useState<string | null>(null);

  const fetchRuns = async () => {
    try {
      const res = await apiFetch('/v1/agents/runs');
      if (res.ok) setRuns(await res.json());
    } catch { /* silent */ } finally {
      setLoadingRuns(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  useEffect(() => {
    if (!activePollId) return;
    const interval = setInterval(async () => {
      try {
        const res = await apiFetch(`/v1/agents/runs/${activePollId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'completed') {
            setRunStatus({ status: 'completed', message: 'Agent run completed successfully.' });
            setActivePollId(null);
            fetchRuns();
            toast.success('Agent run completed');
          } else if (data.status === 'failed') {
            setRunStatus({ status: 'failed', message: data.error ?? 'Run failed unexpectedly.' });
            setActivePollId(null);
            toast.error('Agent run failed');
          }
        }
      } catch { /* silent */ }
    }, 2000);
    return () => clearInterval(interval);
  }, [activePollId]);

  const handleRun = async (agent: Agent) => {
    setModalAgent(agent);
    setRunStatus({ status: 'pending', message: 'Queuing...' });
    try {
      const res = await apiFetch(`/v1/agents/${agent.id}/run`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setActivePollId(data.run_id ?? data.id ?? null);
        setRunStatus({ status: 'running', message: 'Agent is running...', steps: [
          { label: 'Initialize', done: true },
          { label: 'Processing', done: false },
          { label: 'Finalizing', done: false },
        ] });
      } else {
        setRunStatus({ status: 'failed', message: `Failed to start agent (${res.status})` });
      }
    } catch {
      setRunStatus({ status: 'failed', message: 'Connection error. Backend may be offline.' });
    }
  };

  const closeModal = () => {
    setModalAgent(null);
    setRunStatus(null);
    setActivePollId(null);
  };

  return (
    <div>
      <PageHeader title="Agents" description="Manage and monitor your AI agent pipeline" badge={MOCK_AGENTS.filter(a => a.status === 'active').length} />

      <div className="grid grid-cols-2 gap-4 mb-8">
        {MOCK_AGENTS.map((agent) => (
          <div
            key={agent.id}
            className="rounded-xl p-5 flex flex-col gap-4"
            style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: agent.status === 'active' ? 'var(--accent-glow)' : 'var(--bg-surface)', border: '1px solid var(--border)' }}
                >
                  <Bot size={18} className={agent.status === 'active' ? 'text-accent' : 'text-muted'} />
                </div>
                <div>
                  <div className="text-[14px] font-semibold text-primary">{agent.name}</div>
                  <div className="font-mono text-[10px] text-muted">{agent.id}</div>
                </div>
              </div>
              <StatusBadge status={agent.status} />
            </div>
            <p className="text-sm text-secondary leading-relaxed">{agent.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-[10px] tracking-widest uppercase text-muted font-semibold">{agent.type}</span>
              <button
                disabled={agent.status !== 'active'}
                onClick={() => handleRun(agent)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-white"
                style={{
                  backgroundColor: agent.status === 'active' ? 'var(--accent)' : 'transparent',
                  border: agent.status === 'active' ? 'none' : '1px solid var(--border)',
                  color: agent.status === 'active' ? 'white' : 'var(--text-muted)',
                  cursor: agent.status !== 'active' ? 'not-allowed' : 'pointer',
                  opacity: agent.status !== 'active' ? 0.5 : 1,
                }}
              >
                <Play size={12} />
                Run
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Recent runs */}
      <div className="text-[10px] font-semibold tracking-widest uppercase text-muted mb-3">Recent Runs</div>
      {loadingRuns ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12 rounded-lg" style={{ backgroundColor: 'var(--bg-elevated)' }} />)}
        </div>
      ) : runs.length === 0 ? (
        <EmptyState icon={Bot} title="No runs yet" description="Run an agent above to see execution history here" />
      ) : (
        <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--border)' }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-elevated)' }}>
                {['Run ID', 'Agent', 'Status', 'Duration', 'Started'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} style={{ borderTop: '1px solid var(--border)' }}>
                  <td className="px-4 py-3"><MonoId id={run.id} chars={8} /></td>
                  <td className="px-4 py-3 text-[13px] text-secondary">{run.agent_id}</td>
                  <td className="px-4 py-3"><StatusBadge status={run.status} /></td>
                  <td className="px-4 py-3 font-mono text-[12px] text-muted">{run.duration_s ? `${run.duration_s.toFixed(1)}s` : '—'}</td>
                  <td className="px-4 py-3 text-[12px] text-muted">{relativeTime(run.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {modalAgent && (
        <>
          <div className="fixed inset-0 bg-black/60 z-40" onClick={closeModal} />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="rounded-xl p-6 w-full max-w-sm relative" style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
              <button onClick={closeModal} className="absolute top-4 right-4 text-muted hover:text-primary"><X size={16} /></button>
              <div className="flex items-center gap-3 mb-5">
                <Bot size={20} className="text-accent" />
                <div>
                  <div className="text-sm font-semibold text-primary">{modalAgent.name}</div>
                  <div className="text-xs text-muted font-mono">{modalAgent.id}</div>
                </div>
              </div>

              {runStatus && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2.5 mb-4">
                    {runStatus.status === 'pending' && <Loader2 size={18} className="text-muted animate-spin" />}
                    {runStatus.status === 'running' && <Loader2 size={18} className="text-accent animate-spin" />}
                    {runStatus.status === 'completed' && <CheckCircle size={18} className="text-green" />}
                    {runStatus.status === 'failed' && <X size={18} className="text-red" />}
                    <span className="text-sm text-secondary">{runStatus.message}</span>
                  </div>
                  {runStatus.steps?.map((step, i) => (
                    <div key={i} className="flex items-center gap-2.5 text-sm">
                      {step.done ? (
                        <CheckCircle size={15} className="text-green flex-shrink-0" />
                      ) : runStatus.status === 'running' && i === runStatus.steps!.findIndex(s => !s.done) ? (
                        <Loader2 size={15} className="text-accent animate-spin flex-shrink-0" />
                      ) : (
                        <Circle size={15} className="text-muted flex-shrink-0" />
                      )}
                      <span className={step.done ? 'text-secondary' : 'text-muted'}>{step.label}</span>
                    </div>
                  ))}
                  {(runStatus.status === 'completed' || runStatus.status === 'failed') && (
                    <button
                      onClick={closeModal}
                      className="w-full mt-3 py-2.5 rounded-lg text-sm font-medium text-white"
                      style={{ backgroundColor: 'var(--accent)' }}
                    >
                      Done
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
