'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { TopBar } from '@/components/layout/TopBar';
import { apiFetch } from '@/lib/api';
import { Toaster } from '@/components/ui/sonner';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [verifying, setVerifying] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('co_op_token');
      if (!token) {
        router.replace('/login');
        return;
      }

      try {
        const res = await apiFetch('/v1/auth/me');
        if (!res.ok) {
          localStorage.removeItem('co_op_token');
          router.replace('/login');
        } else {
          setVerifying(false);
        }
      } catch (err) {
        localStorage.removeItem('co_op_token');
        router.replace('/login');
      }
    };

    checkAuth();
  }, [router]);

  if (verifying) {
    return (
      <div className="min-h-screen bg-base flex flex-col items-center justify-center">
        <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-base">
      <AppSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
      <Toaster />
    </div>
  );
}
