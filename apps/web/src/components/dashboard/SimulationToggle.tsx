'use client';

import React, { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Info } from 'lucide-react';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

export function SimulationToggle() {
  const [isSimulated, setIsSimulated] = useState<boolean | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('co_op_token');
    fetch(`${API_URL}/health`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setIsSimulated(data.simulation_mode || false);
      })
      .catch(() => setIsSimulated(false));
  }, []);

  const toggleMode = async () => {
    const nextMode = !isSimulated;
    // Note: In a real app we'd have a POST endpoint. 
    // For now, we'll just mock the behavior as if it's set in env.
    // If the user wants to persist this, they should update the .env file.
    setIsSimulated(nextMode);
  };

  if (isSimulated === null) return null;

  return (
    <div className="rounded-xl p-5 bg-surface border border-dim space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold uppercase tracking-widest text-muted">Agent Environment</span>
          <div className="group relative">
            <Info size={12} className="text-muted cursor-help" />
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-elevated border border-dim rounded-lg text-[10px] text-secondary opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              Simulation mode uses synthetic data for proposals and invoices. Disable for live execution.
            </div>
          </div>
        </div>
        <button 
          onClick={toggleMode}
          className={`transition-colors ${isSimulated ? 'text-accent' : 'text-muted'}`}
        >
          {isSimulated ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
        </button>
      </div>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full animate-pulse ${isSimulated ? 'bg-accent' : 'bg-green-status'}`} />
        <span className="text-[13px] font-medium">
          {isSimulated ? 'Simulation Active' : 'Live Mode (Production)'}
        </span>
      </div>
    </div>
  );
}
