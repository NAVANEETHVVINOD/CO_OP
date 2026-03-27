import { env } from './env';

const API_URL = env.API_URL;

let isRefreshing = false;
let refreshQueue: ((token: string) => void)[] = [];

export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  let token = null;
  if (typeof window !== 'undefined') {
    token = localStorage.getItem('co_op_token');
  }
  
  const headers: RequestInit['headers'] = {
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const endpoint = url.startsWith('http') ? url : `${API_URL}${url.startsWith('/') ? url : `/${url}`}`;

  const res = await fetch(endpoint, {
    ...options,
    headers,
  });
  
  if (res.status === 401 && typeof window !== 'undefined') {
    const refreshToken = localStorage.getItem('co_op_refresh_token');
    
    if (!refreshToken) {
      window.location.href = '/login';
      return res;
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        refreshQueue.push((newToken: string) => {
          options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${newToken}`
          };
          resolve(apiFetch(url, options));
        });
      });
    }

    isRefreshing = true;

    try {
      const refreshRes = await fetch(`${API_URL}/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        const newToken = data.access_token;
        const newRefreshToken = data.refresh_token;
        
        localStorage.setItem('co_op_token', newToken);
        localStorage.setItem('co_op_refresh_token', newRefreshToken);
        
        // Notify all queued requests
        refreshQueue.forEach((cb) => cb(newToken));
        refreshQueue = [];
        isRefreshing = false;
        
        // Retry original request
        options.headers = {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        };
        return apiFetch(url, options);
      } else {
        localStorage.removeItem('co_op_token');
        localStorage.removeItem('co_op_refresh_token');
        window.location.href = '/login';
        throw new Error('Session expired');
      }
    } catch (err) {
      isRefreshing = false;
      refreshQueue = [];
      localStorage.removeItem('co_op_token');
      localStorage.removeItem('co_op_refresh_token');
      window.location.href = '/login';
      throw err;
    }
  }
  
  return res;
}

export async function getDocuments() {
  const res = await apiFetch('/v1/documents');
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  // apiFetch will handle NOT setting Content-Type for FormData
  const res = await apiFetch('/v1/documents', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload document');
  return res.json();
}

export async function deleteDocument(id: string) {
  const res = await apiFetch(`/v1/documents/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete document');
}

export async function searchDocuments(query: string) {
  const res = await apiFetch('/v1/search', {
    method: 'POST',
    body: JSON.stringify({ query })
  });
  if (!res.ok) throw new Error('Failed to search');
  return res.json();
}

// --- Stage 2 additions ---

export async function getCreditUsage() {
  const res = await apiFetch('/v1/costs');
  if (!res.ok) throw new Error('Failed to fetch credit usage');
  return res.json();
}

export async function getHardwareTier() {
  const res = await apiFetch('/v1/settings/hardware');
  if (!res.ok) throw new Error('Failed to fetch hardware tier');
  return res.json();
}

export async function getProjects() {
  const res = await apiFetch('/v1/projects');
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function completeMilestone(milestoneId: string) {
  const res = await apiFetch(`/v1/projects/milestones/${milestoneId}/complete`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to complete milestone');
  return res.json();
}

export async function getInvoices() {
  const res = await apiFetch('/v1/invoices');
  if (!res.ok) throw new Error('Failed to fetch invoices');
  return res.json();
}

export async function getApprovals() {
  const res = await apiFetch('/v1/approvals');
  if (!res.ok) throw new Error('Failed to fetch approvals');
  return res.json();
}

export async function approveAction(id: string) {
  const res = await apiFetch(`/v1/approvals/${id}/approve`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to approve action');
  return res.json();
}

export async function rejectAction(id: string) {
  const res = await apiFetch(`/v1/approvals/${id}/reject`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to reject action');
  return res.json();
}

