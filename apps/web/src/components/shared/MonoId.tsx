'use client';

import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MonoIdProps {
  id: string;
  chars?: number;
  className?: string;
}

export function MonoId({ id, chars = 8, className }: MonoIdProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(id).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  const shortened = id.slice(0, chars);

  return (
    <span
      className={cn('inline-flex items-center gap-1 group', className)}
      title={id}
    >
      <span className="font-mono text-[12px] text-muted tracking-tight">
        {shortened}
      </span>
      <button
        onClick={handleCopy}
        className="opacity-0 group-hover:opacity-100 transition-opacity text-muted hover:text-secondary p-0.5 rounded"
        title="Copy full ID"
      >
        {copied ? (
          <Check size={12} className="text-green" />
        ) : (
          <Copy size={12} />
        )}
      </button>
    </span>
  );
}

export default MonoId;
