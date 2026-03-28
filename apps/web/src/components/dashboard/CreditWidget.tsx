'use client';

import React, { useEffect, useState } from 'react';
import { Zap } from 'lucide-react';
import { apiFetch } from '@/lib/api';

interface CreditData {
  today: {
    total_tokens: number;
    total_cost: number;
    usage_pct: number;
  };
  all_time: {
    total_tokens: number;
    total_cost: number;
  };
  daily_limit: number;
}

function getBarColor(pct: number) {
  if (pct >= 90) return 'var(--status-red, #EF4444)';
  if (pct >= 70) return 'var(--status-yellow, #F59E0B)';
  return 'var(--status-green, #22C55E)';
}

export function CreditWidget() {
  const [data, setData] = useState<CreditData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCredits = async () => {
      try {
        const res = await apiFetch('/v1/costs');
        if (res.ok) {
          setData(await res.json());
        }
      } catch {
        // ignore — widget is non-critical
      } finally {
        setLoading(false);
      }
    };

    fetchCredits();
    const interval = setInterval(fetchCredits, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const pct = data?.today?.usage_pct ?? 0;
  const barColor = getBarColor(pct);
  const todayTokens = data?.today?.total_tokens ?? 0;
  const dailyLimit = data?.daily_limit ?? 100_000;
  const todayCost = data?.today?.total_cost ?? 0;

  return (
    <div
      className="rounded-xl p-5"
      style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-[10px] font-semibold tracking-widest uppercase text-muted">
          Token Budget
        </span>
        <Zap size={16} className="text-muted" />
      </div>

      {loading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-3 rounded-full bg-surface" />
          <div className="h-4 rounded bg-surface w-1/2" />
        </div>
      ) : (
        <>
          {/* Progress bar */}
          <div className="w-full h-3 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-surface)' }}>
            <div
              className="h-full rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.min(100, pct)}%`, backgroundColor: barColor }}
            />
          </div>

          {/* Stats */}
          <div className="flex items-baseline justify-between mt-3">
            <div>
              <span className="text-[20px] font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                {todayTokens.toLocaleString()}
              </span>
              <span className="text-[11px] text-muted ml-1">
                / {dailyLimit.toLocaleString()}
              </span>
            </div>
            <span className="text-[11px] font-mono" style={{ color: barColor }}>
              {pct.toFixed(1)}%
            </span>
          </div>

          <div className="text-[11px] text-muted mt-1">
            Today&apos;s cost: <span className="font-mono text-secondary">${todayCost.toFixed(4)}</span>
          </div>

          {data?.all_time && (
            <div className="text-[10px] text-muted mt-2 pt-2" style={{ borderTop: '1px solid var(--border)' }}>
              All-time: {data.all_time.total_tokens.toLocaleString()} tokens (${data.all_time.total_cost.toFixed(4)})
            </div>
          )}
        </>
      )}
    </div>
  );
}
