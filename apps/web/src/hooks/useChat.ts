import { useCallback } from 'react';
import { useChatStore, Message, Citation } from '@/store/chatStore';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

export function useChat() {
  const { messages, isGenerating, addMessage, appendTokenToLastMessage, appendCitationToLastMessage, setGenerating } = useChatStore();

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isGenerating) return;

    // Add user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      citations: [],
      timestamp: new Date(),
    };
    addMessage(userMessage);

    // Initial assistant message for streaming
    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      citations: [],
      timestamp: new Date(),
    };
    addMessage(assistantMessage);

    setGenerating(true);

    try {
      const token = localStorage.getItem('co_op_token');

      const response = await fetch(`${API_URL}/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          message: content,
          history: messages.filter(m => m.content).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.pipeThrough(new TextDecoderStream()).getReader();
      if (!reader) return;

      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += value;

        // Parse SSE chunks (Format: event: <type>\ndata: <json>\n\n)
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          if (!part.trim()) continue;

          const lines = part.split('\n');
          let eventName = 'message';
          let data = '';

          for (const line of lines) {
            if (line.startsWith('event:')) {
              eventName = line.substring(6).trim();
            } else if (line.startsWith('data:')) {
              data += line.substring(5).trim();
            }
          }

          if (!data) continue;

          try {
            const parsed = JSON.parse(data);
            if (eventName === 'token') {
              appendTokenToLastMessage(parsed.content || '');
            } else if (eventName === 'citation') {
              appendCitationToLastMessage(parsed as Citation);
            } else if (eventName === 'done') {
              // Stream complete
            }
          } catch (err) {
            console.error('Failed to parse SSE data', data, err);
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      appendTokenToLastMessage('\n\n[Error: Connection failed.]');
    } finally {
      setGenerating(false);
    }
  }, [messages, isGenerating, addMessage, appendTokenToLastMessage, appendCitationToLastMessage, setGenerating]);

  return { sendMessage, messages, isGenerating };
}
