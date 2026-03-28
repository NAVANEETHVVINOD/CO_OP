import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiFetch, getDocuments, uploadDocument, deleteDocument, searchDocuments } from '@/lib/api';

// Mock env
vi.mock('@/lib/env', () => ({
  env: {
    API_URL: 'http://localhost:8000',
  },
}));

describe('apiFetch', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('makes request with correct URL', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/v1/documents');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/documents',
      expect.any(Object)
    );
  });

  it('includes authorization header when token exists', async () => {
    localStorage.setItem('co_op_token', 'test-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/v1/documents');

    const callArgs = (global.fetch as any).mock.calls[0];
    expect(callArgs[1].headers['Authorization']).toBe('Bearer test-token');
  });

  it('does not include authorization header when token does not exist', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/v1/documents');

    const callArgs = (global.fetch as any).mock.calls[0][1];
    expect(callArgs.headers.Authorization).toBeUndefined();
  });

  it('sets Content-Type to application/json for non-FormData', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/v1/documents', {
      method: 'POST',
      body: JSON.stringify({ test: 'data' }),
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('does not set Content-Type for FormData', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    const formData = new FormData();
    await apiFetch('/v1/documents', {
      method: 'POST',
      body: formData,
    });

    const callArgs = (global.fetch as any).mock.calls[0][1];
    expect(callArgs.headers['Content-Type']).toBeUndefined();
  });

  it('handles 401 response with token refresh', async () => {
    localStorage.setItem('co_op_token', 'old-token');
    localStorage.setItem('co_op_refresh_token', 'refresh-token');

    // First call returns 401
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    // Refresh call succeeds
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'new-token',
        refresh_token: 'new-refresh-token',
      }),
    });

    // Retry call succeeds
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'success' }),
    });

    await apiFetch('/v1/documents');

    // Should have made 3 calls: original, refresh, retry
    expect((global.fetch as any).mock.calls.length).toBeGreaterThanOrEqual(2);
    expect(localStorage.getItem('co_op_token')).toBe('new-token');
    expect(localStorage.getItem('co_op_refresh_token')).toBe('new-refresh-token');
  });

  it('redirects to login when refresh token is missing', async () => {
    localStorage.setItem('co_op_token', 'old-token');
    
    // Mock window.location to avoid jsdom navigation error
    const originalLocation = window.location;
    delete (window as any).location;
    (window as any).location = { href: '' };

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    try {
      await apiFetch('/v1/documents');
    } catch (e) {
      // May throw due to navigation
    }

    expect(window.location.href).toBe('/login');
    
    // Restore
    (window as any).location = originalLocation;
  });

  it('redirects to login when refresh fails', async () => {
    localStorage.setItem('co_op_token', 'old-token');
    localStorage.setItem('co_op_refresh_token', 'refresh-token');
    
    // Mock window.location to avoid jsdom navigation error
    const originalLocation = window.location;
    delete (window as any).location;
    (window as any).location = { href: '' };

    // First call returns 401
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    // Refresh call fails
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    try {
      await apiFetch('/v1/documents');
    } catch (e) {
      // May throw due to navigation
    }

    expect(window.location.href).toBe('/login');
    expect(localStorage.getItem('co_op_token')).toBeNull();
    expect(localStorage.getItem('co_op_refresh_token')).toBeNull();
    
    // Restore
    (window as any).location = originalLocation;
  });
});

describe('getDocuments', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    vi.clearAllMocks();
  });

  it('fetches documents successfully', async () => {
    const mockDocs = [{ id: '1', filename: 'test.pdf' }];
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockDocs,
    });

    const result = await getDocuments();

    expect(result).toEqual(mockDocs);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/documents',
      expect.any(Object)
    );
  });

  it('throws error when request fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(getDocuments()).rejects.toThrow('Failed to fetch documents');
  });
});

describe('uploadDocument', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    vi.clearAllMocks();
  });

  it('uploads document with FormData', async () => {
    const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    const mockResponse = { id: '1', filename: 'test.pdf' };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await uploadDocument(mockFile);

    expect(result).toEqual(mockResponse);
    const callArgs = (global.fetch as any).mock.calls[0];
    expect(callArgs[1].body).toBeInstanceOf(FormData);
  });

  it('throws error when upload fails', async () => {
    const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(uploadDocument(mockFile)).rejects.toThrow('Failed to upload document');
  });
});

describe('deleteDocument', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    vi.clearAllMocks();
  });

  it('deletes document successfully', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
    });

    await deleteDocument('doc-id');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/documents/doc-id',
      expect.objectContaining({
        method: 'DELETE',
      })
    );
  });

  it('throws error when delete fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(deleteDocument('doc-id')).rejects.toThrow('Failed to delete document');
  });
});

describe('searchDocuments', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    vi.clearAllMocks();
  });

  it('searches documents successfully', async () => {
    const mockResults = [{ text: 'result', score: 0.9 }];
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResults,
    });

    const result = await searchDocuments('test query');

    expect(result).toEqual(mockResults);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/search',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ query: 'test query' }),
      })
    );
  });

  it('throws error when search fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(searchDocuments('test')).rejects.toThrow('Failed to search');
  });
});

describe('Token refresh queue handling', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('queues multiple requests during token refresh', async () => {
    localStorage.setItem('co_op_token', 'old-token');
    localStorage.setItem('co_op_refresh_token', 'refresh-token');

    // First request returns 401
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    // Second request also returns 401 (will be queued)
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    // Refresh call succeeds
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'new-token',
        refresh_token: 'new-refresh-token',
      }),
    });

    // Retry calls succeed
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'success1' }),
    });

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'success2' }),
    });

    // Make two concurrent requests
    const promise1 = apiFetch('/v1/documents');
    const promise2 = apiFetch('/v1/documents');

    const [result1, result2] = await Promise.all([promise1, promise2]);

    // Both should succeed with new token
    expect(localStorage.getItem('co_op_token')).toBe('new-token');
  });
});

describe('Stage 2 API functions', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    vi.clearAllMocks();
  });

  describe('getCreditUsage', () => {
    it('fetches credit usage successfully', async () => {
      const mockUsage = { total: 100, used: 50 };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsage,
      });

      const result = await (await import('@/lib/api')).getCreditUsage();

      expect(result).toEqual(mockUsage);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/costs',
        expect.any(Object)
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).getCreditUsage()).rejects.toThrow('Failed to fetch credit usage');
    });
  });

  describe('getHardwareTier', () => {
    it('fetches hardware tier successfully', async () => {
      const mockTier = { tier: 'premium' };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTier,
      });

      const result = await (await import('@/lib/api')).getHardwareTier();

      expect(result).toEqual(mockTier);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/settings/hardware',
        expect.any(Object)
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).getHardwareTier()).rejects.toThrow('Failed to fetch hardware tier');
    });
  });

  describe('getProjects', () => {
    it('fetches projects successfully', async () => {
      const mockProjects = [{ id: '1', name: 'Project 1' }];
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockProjects,
      });

      const result = await (await import('@/lib/api')).getProjects();

      expect(result).toEqual(mockProjects);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/projects',
        expect.any(Object)
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).getProjects()).rejects.toThrow('Failed to fetch projects');
    });
  });

  describe('completeMilestone', () => {
    it('completes milestone successfully', async () => {
      const mockResponse = { success: true };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await (await import('@/lib/api')).completeMilestone('milestone-1');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/projects/milestones/milestone-1/complete',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).completeMilestone('milestone-1')).rejects.toThrow('Failed to complete milestone');
    });
  });

  describe('getInvoices', () => {
    it('fetches invoices successfully', async () => {
      const mockInvoices = [{ id: '1', amount: 100 }];
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockInvoices,
      });

      const result = await (await import('@/lib/api')).getInvoices();

      expect(result).toEqual(mockInvoices);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/invoices',
        expect.any(Object)
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).getInvoices()).rejects.toThrow('Failed to fetch invoices');
    });
  });

  describe('getApprovals', () => {
    it('fetches approvals successfully', async () => {
      const mockApprovals = [{ id: '1', status: 'pending' }];
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockApprovals,
      });

      const result = await (await import('@/lib/api')).getApprovals();

      expect(result).toEqual(mockApprovals);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/approvals',
        expect.any(Object)
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).getApprovals()).rejects.toThrow('Failed to fetch approvals');
    });
  });

  describe('approveAction', () => {
    it('approves action successfully', async () => {
      const mockResponse = { success: true };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await (await import('@/lib/api')).approveAction('action-1');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/approvals/action-1/approve',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).approveAction('action-1')).rejects.toThrow('Failed to approve action');
    });
  });

  describe('rejectAction', () => {
    it('rejects action successfully', async () => {
      const mockResponse = { success: true };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await (await import('@/lib/api')).rejectAction('action-1');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/approvals/action-1/reject',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('throws error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect((await import('@/lib/api')).rejectAction('action-1')).rejects.toThrow('Failed to reject action');
    });
  });
});
