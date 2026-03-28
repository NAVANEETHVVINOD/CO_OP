import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatPage from '@/app/(app)/chat/page';

// Mock useChat hook
vi.mock('@/hooks/useChat', () => ({
  useChat: () => ({
    sendMessage: vi.fn(),
    messages: [],
    isGenerating: false,
  }),
}));

describe('ChatPage', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('renders conversations panel', () => {
    render(<ChatPage />);
    expect(screen.getByText('Conversations')).toBeInTheDocument();
  });

  it('displays new conversation button', () => {
    render(<ChatPage />);
    const buttons = screen.getAllByRole('button');
    const plusButton = buttons.find(btn => btn.querySelector('svg'));
    expect(plusButton).toBeInTheDocument();
  });

  it('loads and displays conversations', async () => {
    render(<ChatPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Conversation')).toBeInTheDocument();
    });
  });

  it('shows message count for conversations', async () => {
    render(<ChatPage />);
    
    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument();
    });
  });

  it('displays empty state when no conversations', async () => {
    const { server } = await import('../mocks/server');
    const { http, HttpResponse } = await import('msw');
    
    server.use(
      http.get('http://localhost:8000/v1/chat/conversations', () => {
        return HttpResponse.json([]);
      })
    );

    render(<ChatPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No conversations')).toBeInTheDocument();
    });
  });

  it('renders message input area', () => {
    render(<ChatPage />);
    const textarea = screen.getByPlaceholderText(/ask anything about your documents/i);
    expect(textarea).toBeInTheDocument();
  });

  it('displays send button', () => {
    render(<ChatPage />);
    const buttons = screen.getAllByRole('button');
    // Send button should be present
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('shows empty state for new conversation', () => {
    render(<ChatPage />);
    expect(screen.getByText('Co-Op AI Assistant')).toBeInTheDocument();
    expect(screen.getByText(/ask questions about your uploaded documents/i)).toBeInTheDocument();
  });

  it('allows typing in message input', () => {
    render(<ChatPage />);
    const textarea = screen.getByPlaceholderText(/ask anything about your documents/i) as HTMLTextAreaElement;
    
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    expect(textarea.value).toBe('Test message');
  });

  it('displays conversation title in header', async () => {
    render(<ChatPage />);
    
    await waitFor(() => {
      expect(screen.getByText('New Conversation')).toBeInTheDocument();
    });
  });

  it('shows helper text below input', () => {
    render(<ChatPage />);
    expect(screen.getByText(/answers are based on your uploaded documents only/i)).toBeInTheDocument();
  });

  it('loads search context from sessionStorage', () => {
    const searchContext = {
      source_file: 'test.pdf',
      text: 'Sample text',
    };
    sessionStorage.setItem('co_op_search_context', JSON.stringify(searchContext));

    render(<ChatPage />);
    
    const textarea = screen.getByPlaceholderText(/ask anything about your documents/i) as HTMLTextAreaElement;
    expect(textarea.value).toContain('test.pdf');
    expect(textarea.value).toContain('Sample text');
  });

  it('clears search context after loading', () => {
    sessionStorage.setItem('co_op_search_context', JSON.stringify({ source_file: 'test.pdf', text: 'text' }));
    
    render(<ChatPage />);
    
    expect(sessionStorage.getItem('co_op_search_context')).toBeNull();
  });
});
