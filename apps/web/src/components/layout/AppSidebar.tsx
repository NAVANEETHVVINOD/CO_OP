'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  MessageSquare,
  FileText,
  Search,
  Bot,
  CheckSquare,
  LayoutDashboard,
  TrendingUp,
  Settings,
  LogOut,
  Briefcase,
  Receipt,
} from 'lucide-react';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

interface NavItemProps {
  href: string;
  icon: React.ElementType;
  label: string;
  badge?: React.ReactNode;
  comingSoon?: boolean;
  redCount?: number;
}

function NavItem({ href, icon: Icon, label, badge, comingSoon, redCount }: NavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname.startsWith(href + '/');

  if (comingSoon) {
    return (
      <div className="flex items-center gap-2.5 px-4 py-2.5 cursor-not-allowed opacity-40">
        <Icon size={16} className="text-muted flex-shrink-0" />
        <span className="text-[13px] text-secondary flex-1">{label}</span>
        {badge}
      </div>
    );
  }

  return (
    <Link
      href={href}
      className="flex items-center gap-2.5 px-4 py-2.5 transition-colors relative"
      style={{
        borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
        backgroundColor: isActive ? 'var(--accent-hover)' : 'transparent',
        color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.04)';
          e.currentTarget.style.color = 'var(--text-primary)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.color = 'var(--text-secondary)';
        }
      }}
    >
      <Icon size={16} className="flex-shrink-0" />
      <span className="text-[13px] flex-1 font-medium">{label}</span>
      {redCount !== undefined && redCount > 0 && (
        <span className="text-[10px] font-bold rounded-full px-1.5 py-0.5 min-w-[18px] text-center text-white"
          style={{ backgroundColor: 'var(--status-red)' }}>
          {redCount}
        </span>
      )}
      {badge}
    </Link>
  );
}

const Phase2Badge = () => (
  <span className="text-[9px] font-semibold tracking-widest uppercase px-1.5 py-0.5 rounded bg-elevated border border-dim text-muted">
    P2
  </span>
);

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-4 pt-5 pb-1">
      <span className="text-[10px] font-semibold tracking-widest uppercase text-muted">{children}</span>
    </div>
  );
}

export function AppSidebar() {
  const router = useRouter();
  const [approvalCount, setApprovalCount] = useState(0);
  const [userEmail, setUserEmail] = useState('admin@co-op.local');
  const [userInitials, setUserInitials] = useState('AD');

  useEffect(() => {
    const token = localStorage.getItem('co_op_token');
    if (!token) return;

    // Fetch approval count
    fetch(`${API_URL}/v1/approvals`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : [])
      .then((data: unknown[]) => setApprovalCount(data.length))
      .catch(() => setApprovalCount(0));

    // Fetch current user
    fetch(`${API_URL}/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : null)
      .then((data: { email?: string } | null) => {
        if (data?.email) {
          setUserEmail(data.email);
          const parts = data.email.split('@')[0].split('.');
          setUserInitials(parts.map((p: string) => p[0]?.toUpperCase() ?? '').join('').slice(0, 2));
        }
      })
      .catch(() => {});
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('co_op_token');
    router.push('/login');
  };

  return (
    <div
      className="flex flex-col flex-shrink-0 h-screen"
      style={{
        width: '240px',
        backgroundColor: 'var(--bg-surface)',
        borderRight: '1px solid var(--border)',
      }}
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b border-dim">
        <div className="text-[18px] font-bold text-primary tracking-tight">CO_OP</div>
        <div className="text-[9px] tracking-[0.15em] text-muted mt-0.5 uppercase">GATEWAY DASHBOARD</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto custom-scrollbar py-2">
        <SectionLabel>Knowledge</SectionLabel>
        <NavItem href="/dashboard" icon={LayoutDashboard} label="Dashboard" />
        <NavItem href="/chat" icon={MessageSquare} label="Chat" />
        <NavItem href="/documents" icon={FileText} label="Documents" />
        <NavItem href="/search" icon={Search} label="Search" />

        <SectionLabel>Automation</SectionLabel>
        <NavItem href="/agents" icon={Bot} label="Agents" />
        <NavItem href="/approvals" icon={CheckSquare} label="Approvals" redCount={approvalCount} />

        <SectionLabel>Operations</SectionLabel>
        <NavItem href="/projects" icon={Briefcase} label="Projects" />
        <NavItem href="/finance" icon={Receipt} label="Invoices" />

        <SectionLabel>Analytics</SectionLabel>
        <NavItem href="/analytics" icon={TrendingUp} label="Analytics" comingSoon badge={<Phase2Badge />} />

        <SectionLabel>Settings</SectionLabel>
        <NavItem href="/admin" icon={Settings} label="Admin" />
      </nav>

      {/* User card */}
      <div className="px-4 py-3 border-t border-dim">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0"
            style={{ backgroundColor: 'var(--accent)' }}
          >
            {userInitials}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[12px] text-secondary truncate">{userEmail}</div>
            <div className="text-[10px] text-muted">admin</div>
          </div>
          <button
            onClick={handleLogout}
            className="text-muted hover:text-red-status p-1 rounded hover:bg-red-status/10 transition-colors flex-shrink-0"
            title="Sign out"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default AppSidebar;
