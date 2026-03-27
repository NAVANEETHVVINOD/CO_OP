'use client';

import React, { useState, useEffect } from 'react';
import { Briefcase, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

export function ProjectsWidget() {
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    const token = localStorage.getItem('co_op_token');
    fetch(`${API_URL}/v1/projects`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setCount(Array.isArray(data) ? data.length : 0))
      .catch(() => setCount(0));
  }, []);

  return (
    <div className="rounded-xl p-5 bg-surface border border-dim space-y-4">
      <div className="flex items-center justify-between">
        <div className="p-2 rounded-lg bg-accent/10 text-accent">
          <Briefcase size={18} />
        </div>
        <Link href="/projects" className="text-muted hover:text-accent transition-colors">
          <ArrowUpRight size={18} />
        </Link>
      </div>
      <div>
        <div className="text-[10px] font-bold uppercase tracking-widest text-muted">Active Projects</div>
        <div className="text-2xl font-bold font-mono">{count}</div>
      </div>
    </div>
  );
}
