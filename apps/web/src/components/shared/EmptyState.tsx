'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center text-center py-12 px-6', className)}>
      <div className="w-16 h-16 rounded-2xl bg-elevated border border-dim flex items-center justify-center mb-4">
        <Icon size={28} className="text-muted" />
      </div>
      <h3 className="text-sm font-semibold text-secondary mb-1.5">{title}</h3>
      <p className="text-xs text-muted max-w-[240px] leading-relaxed">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-5 px-4 py-2 text-sm font-medium rounded-lg border border-accent text-accent hover:bg-accent-hover transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
