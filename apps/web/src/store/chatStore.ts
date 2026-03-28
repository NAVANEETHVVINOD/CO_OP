import { create } from 'zustand';
import { Citation } from '@/types/api';
export type { Citation };

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations: Citation[];
  timestamp?: Date;
  created_at?: string;
};

interface ChatState {
  messages: Message[];
  isGenerating: boolean;
  addMessage: (message: Message) => void;
  appendTokenToLastMessage: (token: string) => void;
  appendCitationToLastMessage: (citation: Citation) => void;
  setGenerating: (status: boolean) => void;
  clearMessages: () => void;
  setMessages: (messages: Message[]) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isGenerating: false,
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  appendTokenToLastMessage: (token) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
      messages[messages.length - 1].content += token;
    }
    return { messages };
  }),
  appendCitationToLastMessage: (citation) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
      messages[messages.length - 1].citations.push(citation);
    }
    return { messages };
  }),
  setGenerating: (status) => set({ isGenerating: status }),
  clearMessages: () => set({ messages: [] }),
}));
