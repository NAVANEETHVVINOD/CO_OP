'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
  className?: string;
}

const STATUS_MAP: Record<string, { bg: string; text: string; border?: string; animate?: boolean }> = {
  // Green states
  READY: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  active: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  healthy: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  connected: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  indexed: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  completed: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  approved: { bg: 'rgba(34,197,94,0.15)', text: '#22C55E' },
  // Amber states (animated dots)
  PENDING: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  processing: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  INDEXING: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  indexing: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  running: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  pending: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  uploading: { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B', animate: true },
  // Red states
  FAILED: { bg: 'rgba(239,68,68,0.15)', text: '#EF4444' },
  error: { bg: 'rgba(239,68,68,0.15)', text: '#EF4444' },
  failed: { bg: 'rgba(239,68,68,0.15)', text: '#EF4444' },
  rejected: { bg: 'rgba(239,68,68,0.15)', text: '#EF4444' },
  // Gray/dashed states
  'coming-soon': { bg: '#1A1A26', text: '#475569', border: '1px dashed #2A2A3A' },
  'phase-2': { bg: '#1A1A26', text: '#475569', border: '1px dashed #2A2A3A' },
  disabled: { bg: '#1A1A26', text: '#475569', border: '1px dashed #2A2A3A' },
};

export function StatusBadge({ status, size = 'sm', className }: StatusBadgeProps) {
  const config = STATUS_MAP[status] ?? STATUS_MAP[status?.toLowerCase() ?? ''] ?? {
    bg: '#1A1A26',
    text: '#475569',
  };

  const px = size === 'sm' ? '3px 7px' : '4px 10px';
  const fontSize = size === 'sm' ? '10px' : '11px';

  return (
    <span
      className={cn('inline-flex items-center gap-1 rounded-full font-semibold tracking-wider uppercase whitespace-nowrap', className)}
      style={{
        backgroundColor: config.bg,
        color: config.text,
        border: config.border ?? 'none',
        padding: px,
        fontSize,
      }}
    >
      {status?.toUpperCase()}
      {config.animate && (
        <span className="inline-flex gap-0.5 ml-0.5">
          <span className="w-1 h-1 rounded-full bg-current animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1 h-1 rounded-full bg-current animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1 h-1 rounded-full bg-current animate-bounce" style={{ animationDelay: '300ms' }} />
        </span>
      )}
    </span>
  );
}

export default StatusBadge;
