'use client';

import React, { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Bell } from 'lucide-react';
import { StatusDot } from '@/components/shared/StatusDot';
import { HealthResponse } from '@/types/api';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

const BREADCRUMB_MAP: Record<string, string> = {
  '/': 'Home',
  '/dashboard': 'Dashboard',
  '/chat': 'Chat',
  '/documents': 'Knowledge Base',
  '/search': 'Search',
  '/agents': 'Agents',
  '/approvals': 'Approvals',
  '/workflows': 'Workflows',
  '/analytics': 'Analytics',
  '/admin': 'Administration',
  '/debug': 'Debug',
  '/logs': 'Logs',
};

export function TopBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [userInitials, setUserInitials] = useState('AD');

  const breadcrumb = BREADCRUMB_MAP[pathname] ?? pathname.split('/').filter(Boolean).map(
    (p) => p.charAt(0).toUpperCase() + p.slice(1)
  ).join(' › ');

  useEffect(() => {
    const checkHealth = () => {
      fetch(`${API_URL}/health`)
        .then((r) => r.ok ? r.json() : null)
        .then((data: HealthResponse | null) => setHealth(data))
        .catch(() => setHealth(null));
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('co_op_token');
    if (!token) return;
    fetch(`${API_URL}/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : null)
      .then((data: { email?: string } | null) => {
        if (data?.email) {
          const parts = data.email.split('@')[0].split('.');
          setUserInitials(parts.map((p: string) => p[0]?.toUpperCase() ?? '').join('').slice(0, 2));
        }
      })
      .catch(() => {});
  }, []);

  const isHealthy = health?.status === 'ok' || health?.status === 'healthy';

  return (
    <div
      className="flex items-center justify-between px-6 flex-shrink-0"
      style={{
        height: '52px',
        backgroundColor: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      {/* Left — Breadcrumb */}
      <div className="text-[14px] text-secondary font-medium">
        {breadcrumb}
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        {/* Health indicator */}
        <button
          onClick={() => router.push('/admin')}
          className="flex items-center gap-1.5 text-[13px] text-secondary hover:text-primary transition-colors"
        >
          <StatusDot status={health === null ? 'unknown' : isHealthy ? 'healthy' : 'error'} size="sm" />
          <span>{health === null ? 'Connecting...' : isHealthy ? 'Healthy' : 'Issues'}</span>
        </button>

        {/* Bell */}
        <button className="text-muted hover:text-secondary transition-colors p-1">
          <Bell size={17} />
        </button>

        {/* User Avatar */}
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center text-white text-[11px] font-semibold cursor-pointer"
          style={{ backgroundColor: 'var(--accent)' }}
        >
          {userInitials}
        </div>
      </div>
    </div>
  );
}

export default TopBar;
