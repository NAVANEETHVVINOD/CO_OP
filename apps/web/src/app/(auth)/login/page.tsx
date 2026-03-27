'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState(env.DEFAULT_EMAIL);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await fetch(`${API_URL}/v1/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('co_op_token', data.access_token);
        localStorage.setItem('co_op_refresh_token', data.refresh_token);
        router.replace('/dashboard');
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch {
      setError('Unable to connect to server. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center"
      style={{ backgroundColor: 'var(--bg-base)' }}
    >
      {/* Logo */}
      <div className="text-center mb-10">
        <div className="text-[32px] font-bold text-primary tracking-tight">Co-Op</div>
        <div className="text-[14px] text-muted mt-1">Enterprise AI Operating System</div>
      </div>

      {/* Card */}
      <div
        className="rounded-xl p-8"
        style={{
          width: '400px',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border)',
        }}
      >
        <div className="text-[12px] tracking-widest text-muted uppercase mb-6 font-semibold">
          Sign In
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[12px] text-secondary mb-1.5 font-medium">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@co-op.local"
              required
              className="w-full px-3 py-2.5 text-sm rounded-lg text-primary placeholder:text-muted"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
              }}
            />
          </div>

          <div>
            <label className="block text-[12px] text-secondary mb-1.5 font-medium">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-3 py-2.5 text-sm rounded-lg text-primary placeholder:text-muted"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
              }}
            />
          </div>

          {error && (
            <div className="text-[13px] text-red-status bg-red-status/10 border border-red-status/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg text-[14px] font-semibold text-white transition-all flex items-center justify-center gap-2 mt-2"
            style={{
              backgroundColor: 'var(--accent)',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading && (
              <span
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                style={{ animation: 'spin 1s linear infinite' }}
              />
            )}
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          <p className="text-[11px] text-muted text-center pt-1">
            Default credentials: {env.DEFAULT_EMAIL} / {env.DEFAULT_PASSWORD}
          </p>

          <p className="text-[12px] text-muted text-center pt-2">
            Don't have an account?{' '}
            <Link href="/signup" className="text-accent hover:underline">
              Sign up
            </Link>
          </p>
        </form>
      </div>

      {/* Footer */}
      <p className="text-[11px] text-muted mt-8">
        Self-hosted · Open source · Apache 2.0
      </p>
    </div>
  );
}
