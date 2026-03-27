'use client';

import React from 'react';
import { cn } from '@/lib/utils';

type StatusType = 'healthy' | 'ok' | 'error' | 'warning' | 'pending' | 'unknown';
type SizeType = 'sm' | 'md';

interface StatusDotProps {
  status: StatusType;
  size?: SizeType;
  className?: string;
}

export function StatusDot({ status, size = 'md', className }: StatusDotProps) {
  // Backward compatibility: 'ok' maps to 'healthy', 'pending' maps to 'warning'
  const normalizedStatus = status === 'ok' ? 'healthy' : status === 'pending' ? 'warning' : status;

  const sizeClasses = {
    sm: 'w-1.5 h-1.5', // 6px
    md: 'w-2 h-2',     // 8px
  };

  const colorClasses: Record<StatusType, string> = {
    healthy: 'bg-status-green',
    ok: 'bg-status-green', // Mapped to healthy
    error: 'bg-status-red',
    warning: 'bg-status-amber',
    pending: 'bg-status-amber', // Mapped to warning
    unknown: 'bg-text-muted',
  };

  const animated = normalizedStatus === 'healthy' || normalizedStatus === 'warning';

  return (
    <span
      className={cn(
        'inline-block rounded-full flex-shrink-0 transition-colors duration-200',
        sizeClasses[size],
        colorClasses[normalizedStatus], // Use normalizedStatus for color
        animated && 'animate-pulse-dot',
        className
      )}
    />
  );
}

export default StatusDot;
