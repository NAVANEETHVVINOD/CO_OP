'use client';

import React, { useEffect, useState } from 'react';
import { FileText, MessageSquare, Database } from 'lucide-react';
import { PageHeader } from '@/components/shared/PageHeader';
import { StatusDot } from '@/components/shared/StatusDot';
import { apiFetch } from '@/lib/api';
import { HealthResponse } from '@/types/api';
import { Skeleton } from '@/components/ui/skeleton';
import { CreditWidget } from '@/components/dashboard/CreditWidget';
import { SimulationToggle } from '@/components/dashboard/SimulationToggle';
import { ProjectsWidget } from '@/components/dashboard/ProjectsWidget';
import { InvoicesWidget } from '@/components/dashboard/InvoicesWidget';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

const ACTIVITY_ROWS = [
  { time: '12:34:01', type: 'UPLOAD', detail: '8728e832 → READY', color: 'var(--status-green)' },
  { time: '12:31:44', type: 'SEARCH', detail: '"remote work policy"', color: 'var(--accent)' },
  { time: '12:29:10', type: 'CHAT', detail: 'conv_a1b2c3d4', color: '#A855F7' },
  { time: '12:15:00', type: 'UPLOAD', detail: 'd4027ec3 → READY', color: 'var(--status-green)' },
  { time: '12:00:00', type: 'SEARCH', detail: '"Q4 financial report"', color: 'var(--accent)' },
];

interface StatusCellProps {
  label: string;
  value: string;
  status?: 'healthy' | 'error' | 'warning' | 'unknown';
}

function StatusCell({ label, value, status = 'unknown' }: StatusCellProps) {
  return (
    <div className="rounded-lg p-3" style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
      <div className="text-[9px] text-muted tracking-widest uppercase mb-1 font-semibold">{label}</div>
      <div className="flex items-center gap-1.5">
        <StatusDot status={status} size="sm" />
        <span className="text-[13px] font-mono" style={{ color: status === 'healthy' ? 'var(--status-green)' : status === 'error' ? 'var(--status-red)' : 'var(--text-primary)' }}>
          {value}
        </span>
      </div>
    </div>
  );
}

function mapHealthStatus(val: string | undefined): 'healthy' | 'error' | 'unknown' {
  if (!val) return 'unknown';
  if (val === 'ok' || val === 'healthy' || val === 'connected') return 'healthy';
  if (val === 'error' || val === 'disconnected' || val === 'failed') return 'error';
  return 'unknown';
}

export default function DashboardPage() {
  const [docCount, setDocCount] = useState<number | null>(null);
  const [convCount, setConvCount] = useState<number | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [docsRes, convsRes] = await Promise.all([
          apiFetch('/v1/documents'),
          apiFetch('/v1/chat/conversations'),
        ]);
        if (docsRes.ok) {
          const docs = await docsRes.json();
          setDocCount(Array.isArray(docs) ? docs.length : 0);
        }
        if (convsRes.ok) {
          const convs = await convsRes.json();
          setConvCount(Array.isArray(convs) ? convs.length : 0);
        }
      } catch { /* ignore */ } finally {
        setLoading(false);
      }
    };

    const fetchHealth = () => {
      fetch(`${API_URL}/health`)
        .then(r => r.ok ? r.json() : null)
        .then((data: HealthResponse | null) => setHealth(data))
        .catch(() => setHealth(null));
    };

    fetchAll();
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <PageHeader title="Overview" description="System status and activity summary" />

      <div className="grid grid-cols-3 gap-6">
        {/* Left 2 cols */}
        <div className="col-span-2 space-y-6">
          {/* Stat Cards */}
          <div className="grid grid-cols-3 gap-5">
            {loading ? (
              <>
                <Skeleton className="h-28 rounded-xl bg-elevated" />
                <Skeleton className="h-28 rounded-xl bg-elevated" />
                <Skeleton className="h-28 rounded-xl bg-elevated" />
              </>
            ) : (
              <>
                {/* Documents */}
                <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] text-muted tracking-widest uppercase font-semibold">Documents</span>
                    <FileText size={18} className="text-muted" />
                  </div>
                  <div className="text-[36px] font-bold text-primary font-mono leading-none">{docCount ?? '—'}</div>
                  <div className="text-[12px] text-secondary mt-1.5">Indexed knowledge files</div>
                </div>
                {/* Stage 3: Projects Widget */}
                <ProjectsWidget />
                {/* Stage 3: Invoices Widget */}
                <InvoicesWidget />
                {/* Conversations */}
                <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] text-muted tracking-widest uppercase font-semibold">Conversations</span>
                    <MessageSquare size={18} className="text-muted" />
                  </div>
                  <div className="text-[36px] font-bold text-primary font-mono leading-none">{convCount ?? '—'}</div>
                  <div className="text-[12px] text-secondary mt-1.5">Chat histories stored</div>
                </div>
                {/* Vectors */}
                <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] text-muted tracking-widest uppercase font-semibold">Vectors</span>
                    <Database size={18} className="text-muted" />
                  </div>
                  <div className="text-[36px] font-bold text-primary font-mono leading-none">{docCount !== null ? `~${docCount * 40}` : '—'}</div>
                  <div className="text-[12px] text-secondary mt-1.5">Estimated embeddings</div>
                </div>
              </>
            )}
          </div>

          {/* Recent Activity */}
          <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
            <div className="text-[10px] font-semibold tracking-widest uppercase text-muted mb-4">Recent Activity</div>
            <div className="space-y-2">
              {ACTIVITY_ROWS.map((row, i) => (
                <div key={i} className="flex items-center gap-3 text-sm font-mono py-1.5 border-b border-dim last:border-0">
                  <span className="text-[11px] text-muted w-16 flex-shrink-0">{row.time}</span>
                  <span
                    className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: row.color + '22', color: row.color }}
                  >
                    {row.type}
                  </span>
                  <span className="text-[13px] text-secondary truncate">{row.detail}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 1 col */}
        <div className="col-span-1 space-y-4">
          <div className="rounded-xl p-5 h-fit" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
            <div className="text-[10px] font-semibold tracking-widest uppercase text-muted mb-4">System Snapshot</div>
            {loading ? (
              <div className="grid grid-cols-2 gap-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 rounded-lg bg-surface" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                <StatusCell label="Status" value="Connected" status="healthy" />
                <StatusCell label="Uptime" value="Live" status="healthy" />
                <StatusCell
                  label="Postgres"
                  value={health?.postgres ?? 'unknown'}
                  status={mapHealthStatus(health?.postgres)}
                />
                <StatusCell
                  label="Qdrant"
                  value={health?.qdrant ?? 'unknown'}
                  status={mapHealthStatus(health?.qdrant)}
                />
                <StatusCell
                  label="Redis"
                  value={health?.redis ?? 'unknown'}
                  status={mapHealthStatus(health?.redis)}
                />
                <StatusCell
                  label="MinIO"
                  value={health?.minio ?? 'unknown'}
                  status={mapHealthStatus(health?.minio)}
                />
              </div>
            )}
          </div>

          <p className="text-[11px] text-muted px-1">
            Backend: <span className="font-mono text-secondary">{API_URL}</span>
          </p>

          {/* Stage 3: Environment Toggle */}
          <SimulationToggle />

          {/* Stage 2: Token Budget Widget */}
          <CreditWidget />
        </div>
      </div>
    </div>
  );
}
