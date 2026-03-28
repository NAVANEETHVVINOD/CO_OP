import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DocumentsPage from '@/app/(app)/documents/page';

// Mock toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('DocumentsPage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders page header with title', () => {
    render(<DocumentsPage />);
    expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
  });

  it('displays upload button', () => {
    render(<DocumentsPage />);
    expect(screen.getByRole('button', { name: /upload/i })).toBeInTheDocument();
  });

  it('shows upload zone with instructions', () => {
    render(<DocumentsPage />);
    expect(screen.getByText(/drop files here or click to browse/i)).toBeInTheDocument();
    expect(screen.getByText(/supports: pdf, docx, txt, md/i)).toBeInTheDocument();
  });

  it('loads and displays documents', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
      expect(screen.getByText('report.docx')).toBeInTheDocument();
    });
  });

  it('displays document status badges', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('READY')).toBeInTheDocument();
      expect(screen.getByText('INDEXING')).toBeInTheDocument();
    });
  });

  it('shows document file sizes', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('1000.0 KB')).toBeInTheDocument();
      expect(screen.getByText('500.0 KB')).toBeInTheDocument();
    });
  });

  it('displays chunk counts for indexed documents', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      const table = screen.getByRole('table');
      expect(table).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('10')).toBeInTheDocument();
    });
  });

  it('shows empty state when no documents', async () => {
    const { server } = await import('../mocks/server');
    const { http, HttpResponse } = await import('msw');
    
    server.use(
      http.get('http://localhost:8000/v1/documents', () => {
        return HttpResponse.json([]);
      })
    );

    render(<DocumentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No documents yet')).toBeInTheDocument();
      expect(screen.getByText(/upload your first document/i)).toBeInTheDocument();
    });
  });

  it('opens detail panel when document is clicked', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    const row = screen.getByText('test.pdf').closest('tr');
    if (row) {
      fireEvent.click(row);
    }

    await waitFor(() => {
      // Panel should show document details
      const panels = screen.getAllByText('test.pdf');
      expect(panels.length).toBeGreaterThan(1);
    });
  });

  it('shows delete button for each document', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button');
      const trashButtons = deleteButtons.filter(btn => 
        btn.querySelector('svg')
      );
      expect(trashButtons.length).toBeGreaterThan(0);
    });
  });

  it('displays document count in header badge', async () => {
    render(<DocumentsPage />);
    
    await waitFor(() => {
      // Should show count of READY documents
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  it('handles file input change', async () => {
    render(<DocumentsPage />);
    
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input?.accept).toBe('.pdf,.docx,.txt,.md');
    expect(input?.multiple).toBe(true);
  });
});
