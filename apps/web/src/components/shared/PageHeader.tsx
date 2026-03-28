'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: string | number;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, description, badge, actions, className }: PageHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between pb-5 mb-6 border-b border-dim', className)}>
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-primary">{title}</h1>
          {badge !== undefined && badge !== null && (
            <span className="px-2 py-0.5 text-xs font-mono font-medium rounded-md bg-elevated border border-dim text-muted">
              {badge}
            </span>
          )}
        </div>
        {description && (
          <p className="text-sm text-muted mt-1">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex items-center gap-3">
          {actions}
        </div>
      )}
    </div>
  );
}

export default PageHeader;
