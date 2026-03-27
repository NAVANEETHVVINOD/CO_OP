'use client';

import React, { useState, useEffect } from 'react';
import { Receipt, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

export function InvoicesWidget() {
  const [total, setTotal] = useState<number>(0);

  useEffect(() => {
    const token = localStorage.getItem('co_op_token');
    fetch(`${API_URL}/v1/invoices`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        const sum = Array.isArray(data) ? data.reduce((acc: number, inv: any) => acc + (inv.amount || 0), 0) : 0;
        setTotal(sum);
      })
      .catch(() => setTotal(0));
  }, []);

  return (
    <div className="rounded-xl p-5 bg-surface border border-dim space-y-4">
      <div className="flex items-center justify-between">
        <div className="p-2 rounded-lg bg-green-status/10 text-green-status">
          <Receipt size={18} />
        </div>
        <Link href="/finance" className="text-muted hover:text-accent transition-colors">
          <ArrowUpRight size={18} />
        </Link>
      </div>
      <div>
        <div className="text-[10px] font-bold uppercase tracking-widest text-muted">Billed Amount</div>
        <div className="text-2xl font-bold font-mono">${total.toFixed(2)}</div>
      </div>
    </div>
  );
}
