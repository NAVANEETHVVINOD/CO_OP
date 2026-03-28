import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from '@/hooks/useChat';
import { useChatStore } from '@/store/chatStore';

// Mock env
vi.mock('@/lib/env', () => ({
  env: {
    API_URL: 'http://localhost:8000',
  },
}));

// Mock fetch for SSE streaming
const createMockSSEResponse = (events: Array<{ event: string; data: any }>) => {
  const encoder = new TextEncoder();
  let eventIndex = 0;

  const stream = new ReadableStream({
    start(controller) {
      const sendNextEvent = () => {
        if (eventIndex < events.length) {
          const { event, data } = events[eventIndex];
          const sseData = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
          controller.enqueue(encoder.encode(sseData));
          eventIndex++;
          setTimeout(sendNextEvent, 10);
        } else {
          controller.close();
        }
      };
      sendNextEvent();
    },
  });

  return {
    ok: true,
    body: stream,
  };
};

describe('useChat', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
    vi.clearAllMocks();
    // Reset store state
    useChatStore.setState({ messages: [], isGenerating: false });
  });

  it('returns sendMessage function and state', () => {
    const { result } = renderHook(() => useChat());
    
    expect(result.current.sendMessage).toBeInstanceOf(Function);
    expect(result.current.messages).toEqual([]);
    expect(result.current.isGenerating).toBe(false);
  });

  it('does not send message when content is empty', async () => {
    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('');
    });
    
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('does not send message when already generating', async () => {
    useChatStore.setState({ isGenerating: true });
    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test');
    });
    
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('adds user message to store', async () => {
    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'token', data: { content: 'Hello' } },
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test message');
    });

    await waitFor(() => {
      const messages = useChatStore.getState().messages;
      const userMessage = messages.find(m => m.role === 'user');
      expect(userMessage).toBeDefined();
      expect(userMessage?.content).toBe('test message');
    });
  });

  it('adds assistant message placeholder', async () => {
    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'token', data: { content: 'Hello' } },
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test');
    });

    await waitFor(() => {
      const messages = useChatStore.getState().messages;
      const assistantMessage = messages.find(m => m.role === 'assistant');
      expect(assistantMessage).toBeDefined();
    });
  });

  it('sets generating state during request', async () => {
    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'token', data: { content: 'Hello' } },
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    let generatingDuringRequest = false;
    
    await act(async () => {
      const promise = result.current.sendMessage('test');
      // Check state during request
      await waitFor(() => {
        generatingDuringRequest = useChatStore.getState().isGenerating;
      });
      await promise;
    });

    expect(generatingDuringRequest).toBe(true);
    expect(useChatStore.getState().isGenerating).toBe(false);
  });

  it('handles token events from SSE stream', async () => {
    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'token', data: { content: 'Hello' } },
        { event: 'token', data: { content: ' world' } },
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test');
    });

    await waitFor(() => {
      const messages = useChatStore.getState().messages;
      const assistantMessage = messages.find(m => m.role === 'assistant');
      expect(assistantMessage?.content).toBe('Hello world');
    });
  });

  it('handles citation events from SSE stream', async () => {
    const citation = {
      source: 'test.pdf',
      page: 1,
      score: 0.95,
      content: 'test content',
    };

    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'citation', data: citation },
        { event: 'token', data: { content: 'Answer' } },
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test');
    });

    await waitFor(() => {
      const messages = useChatStore.getState().messages;
      const assistantMessage = messages.find(m => m.role === 'assistant');
      expect(assistantMessage?.citations).toHaveLength(1);
      expect(assistantMessage?.citations[0]).toEqual(citation);
    });
  });

  it('includes authorization header when token exists', async () => {
    localStorage.setItem('co_op_token', 'test-token');
    
    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test');
    });

    await waitFor(() => {
      const callArgs = (global.fetch as any).mock.calls[0];
      expect(callArgs[1].headers['Authorization']).toBe('Bearer test-token');
    });
  });

  it('sends message history in request', async () => {
    useChatStore.setState({
      messages: [
        { id: '1', role: 'user', content: 'previous', citations: [], timestamp: new Date() },
        { id: '2', role: 'assistant', content: 'response', citations: [], timestamp: new Date() },
      ],
    });

    (global.fetch as any).mockResolvedValueOnce(
      createMockSSEResponse([
        { event: 'done', data: {} },
      ])
    );

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('new message');
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining('"history"'),
        })
      );
    });
  });

  it('handles connection errors gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useChat());
    
    await act(async () => {
      await result.current.sendMessage('test');
    });

    await waitFor(() => {
      const messages = useChatStore.getState().messages;
      const assistantMessage = messages.find(m => m.role === 'assistant');
      expect(assistantMessage?.content).toContain('[Error: Connection failed.]');
      expect(useChatStore.getState().isGenerating).toBe(false);
    });
  });

  it('handles malformed SSE data gracefully', async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('event: token\ndata: invalid-json\n\n'));
        controller.close();
      },
    });

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      body: stream,
    });

    const { result } = renderHook(() => useChat());
    
    // Should not throw
    await act(async () => {
      await result.current.sendMessage('test');
    });

    await waitFor(() => {
      expect(useChatStore.getState().isGenerating).toBe(false);
    });
  });
});
