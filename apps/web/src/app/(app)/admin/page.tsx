'use client';

import React, { useState, useEffect } from 'react';
import { Users, Settings, Info, UserPlus, RefreshCw } from 'lucide-react';
import { PageHeader } from '@/components/shared/PageHeader';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { StatusDot } from '@/components/shared/StatusDot';
import { MonoId } from '@/components/shared/MonoId';
import { Skeleton } from '@/components/ui/skeleton';
import { apiFetch } from '@/lib/api';
import { HealthResponse } from '@/types/api';
import { toast } from 'sonner';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

interface AppUser {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

type TabId = 'users' | 'system' | 'about';

const TABS: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: 'users', label: 'Users', icon: Users },
  { id: 'system', label: 'System', icon: Settings },
  { id: 'about', label: 'About', icon: Info },
];

const TECH_STACK = [
  { name: 'Next.js 14', role: 'Frontend framework', status: 'active' },
  { name: 'FastAPI', role: 'Backend REST API', status: 'active' },
  { name: 'PostgreSQL', role: 'Persistent storage', status: 'active' },
  { name: 'Qdrant', role: 'Vector database', status: 'active' },
  { name: 'Redis', role: 'Cache & task queue', status: 'active' },
  { name: 'MinIO', role: 'Object storage', status: 'active' },
];

function mapHealthStatus(val: string | undefined): 'healthy' | 'error' | 'unknown' {
  if (!val) return 'unknown';
  if (val === 'ok' || val === 'healthy' || val === 'connected') return 'healthy';
  return 'error';
}

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<TabId>('users');
  const [users, setUsers] = useState<AppUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await apiFetch('/v1/users');
        if (res.ok) setUsers(await res.json());
      } catch { /* silent */ } finally {
        setLoadingUsers(false);
      }
    };
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) setHealth(await res.json());
      } catch { /* silent */ } finally {
        setLoadingHealth(false);
      }
    };
    fetchUsers();
    fetchHealth();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail.trim()) return;
    setInviting(true);
    try {
      const res = await apiFetch('/v1/users/invite', {
        method: 'POST',
        body: JSON.stringify({ email: inviteEmail, role: 'user' }),
      });
      if (res.ok) {
        toast.success(`Invitation sent to ${inviteEmail}`);
        setInviteEmail('');
        const res2 = await apiFetch('/v1/users');
        if (res2.ok) setUsers(await res2.json());
      } else {
        toast.error('Failed to send invite');
      }
    } catch { toast.error('Connection error'); } finally {
      setInviting(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      const res = await apiFetch(`/v1/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify({ role: newRole }),
      });
      if (res.ok) {
        setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
        toast.success('Role updated');
      }
    } catch { toast.error('Failed to update role'); }
  };

  const handleDeactivate = async (userId: string) => {
    if (!confirm('Deactivate this user?')) return;
    try {
      const res = await apiFetch(`/v1/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: false }),
      });
      if (res.ok) {
        setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: false } : u));
        toast.success('User deactivated');
      }
    } catch { toast.error('Failed to deactivate user'); }
  };

  const systemChecks = [
    { label: 'API Gateway', status: health?.status === 'ok' ? 'healthy' : 'error', value: health?.status ?? 'unknown' },
    { label: 'PostgreSQL', status: mapHealthStatus(health?.postgres), value: health?.postgres ?? 'unknown' },
    { label: 'Qdrant Vector DB', status: mapHealthStatus(health?.qdrant), value: health?.qdrant ?? 'unknown' },
    { label: 'Redis Cache', status: mapHealthStatus(health?.redis), value: health?.redis ?? 'unknown' },
    { label: 'MinIO Storage', status: mapHealthStatus(health?.minio), value: health?.minio ?? 'unknown' },
  ] as const;

  return (
    <div>
      <PageHeader title="Administration" description="Manage users, review system health, and configure the platform" />

      {/* Tabs */}
      <div className="flex gap-1 mb-6 p-1 rounded-xl" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', width: 'fit-content' }}>
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                backgroundColor: isActive ? 'var(--bg-base)' : 'transparent',
                border: isActive ? '1px solid var(--border)' : '1px solid transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              <Icon size={15} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Users tab */}
      {activeTab === 'users' && (
        <div>
          {/* Invite form */}
          <form onSubmit={handleInvite} className="flex gap-3 mb-6">
            <input
              type="email"
              value={inviteEmail}
              onChange={e => setInviteEmail(e.target.value)}
              placeholder="colleague@company.com"
              className="flex-1 px-3 py-2.5 text-sm rounded-lg text-primary placeholder:text-muted"
              style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
            />
            <button
              type="submit"
              disabled={inviting || !inviteEmail}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium text-white"
              style={{ backgroundColor: 'var(--accent)', opacity: inviting ? 0.7 : 1 }}
            >
              <UserPlus size={15} />
              Invite
            </button>
          </form>

          {loadingUsers ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" style={{ backgroundColor: 'var(--bg-elevated)' }} />)}
            </div>
          ) : (
            <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--border)' }}>
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-elevated)' }}>
                    {['ID', 'Email', 'Role', 'Status', 'Joined', 'Actions'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} style={{ borderTop: '1px solid var(--border)' }}>
                      <td className="px-4 py-3"><MonoId id={user.id} chars={8} /></td>
                      <td className="px-4 py-3 text-[13px] text-secondary">{user.email}</td>
                      <td className="px-4 py-3">
                        <select
                          value={user.role}
                          onChange={e => handleRoleChange(user.id, e.target.value)}
                          className="text-xs rounded px-2 py-1 transition-colors"
                          style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}
                        >
                          <option value="admin">admin</option>
                          <option value="user">user</option>
                          <option value="viewer">viewer</option>
                        </select>
                      </td>
                      <td className="px-4 py-3"><StatusBadge status={user.is_active ? 'active' : 'disabled'} /></td>
                      <td className="px-4 py-3 text-[12px] text-muted font-mono">{new Date(user.created_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3">
                        {user.is_active && (
                          <button onClick={() => handleDeactivate(user.id)} className="text-xs text-muted hover:text-red-status transition-colors">
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* System tab */}
      {activeTab === 'system' && (
        <div>
          {loadingHealth ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-xl" style={{ backgroundColor: 'var(--bg-elevated)' }} />)}
            </div>
          ) : (
            <div className="space-y-3">
              {systemChecks.map(({ label, status, value }) => (
                <div key={label} className="flex items-center justify-between rounded-xl px-5 py-4" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center gap-3">
                    <StatusDot status={status} />
                    <span className="text-sm text-primary font-medium">{label}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted">{value}</span>
                    <StatusBadge status={status === 'healthy' ? 'healthy' : 'error'} />
                  </div>
                </div>
              ))}
              <button
                onClick={() => { setLoadingHealth(true); fetch(`${API_URL}/health`).then(r => r.ok ? r.json() : null).then(setHealth).finally(() => setLoadingHealth(false)); }}
                className="flex items-center gap-2 text-sm text-muted hover:text-accent transition-colors mt-4"
              >
                <RefreshCw size={13} />
                Refresh Now
              </button>
            </div>
          )}
        </div>
      )}

      {/* About tab */}
      {activeTab === 'about' && (
        <div className="space-y-5">
          <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
            <div className="text-[10px] font-semibold tracking-widest uppercase text-muted mb-3">Version</div>
            <div className="flex gap-4 text-sm">
              <div><span className="text-muted mr-2">Release:</span><span className="font-mono text-primary">1.0.0-alpha</span></div>
              <div><span className="text-muted mr-2">Branch:</span><span className="font-mono text-primary">main</span></div>
              <div><span className="text-muted mr-2">License:</span><span className="font-mono text-primary">Apache 2.0</span></div>
            </div>
          </div>

          <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
            <div className="text-[10px] font-semibold tracking-widest uppercase text-muted mb-3">Technology Stack</div>
            <div className="space-y-2">
              {TECH_STACK.map(({ name, role }) => (
                <div key={name} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div>
                    <span className="text-sm font-medium text-primary">{name}</span>
                    <span className="text-xs text-muted ml-3">{role}</span>
                  </div>
                  <StatusBadge status="active" />
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
            <div className="text-[10px] font-semibold tracking-widest uppercase text-muted mb-2">Backend</div>
            <p className="text-sm text-secondary">
              Running at{' '}
              <span className="font-mono text-accent">{API_URL}</span>
              {' — '}Stubbed inference mode (no LLM API key).
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
