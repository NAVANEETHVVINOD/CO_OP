'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Plus, MessageSquare, Trash2, ArrowUp, Bot, FileText, ChevronDown, ChevronRight } from 'lucide-react';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { apiFetch } from '@/lib/api';
import { Conversation, Message, Citation } from '@/types/api';
import { useChat } from '@/hooks/useChat';
import { useChatStore } from '@/store/chatStore';
import { cn } from '@/lib/utils';

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sendMessage, isGenerating: isStreaming } = useChat();
  const { messages, setMessages } = useChatStore();
  const [inputValue, setInputValue] = useState('');

  const fetchConversations = async () => {
    try {
      const res = await apiFetch('/v1/chat/conversations');
      if (res.ok) setConversations(await res.json());
    } catch { /* silent */ }
  };

  useEffect(() => {
    fetchConversations();

    const searchContext = sessionStorage.getItem('co_op_search_context');
    if (searchContext) {
      try {
        const result = JSON.parse(searchContext);
        setInputValue(`Regarding ${result.source_file}:\n\n"${result.text}"\n\n`);
        sessionStorage.removeItem('co_op_search_context');
      } catch { /* ignore */ }
    }
  }, []);

  useEffect(() => {
    if (!activeConversationId) {
      setMessages([]);
      return;
    }
    const loadMessages = async () => {
      setLoadingHistory(true);
      try {
        const res = await apiFetch(`/v1/chat/conversations/${activeConversationId}/messages`);
        if (res.ok) {
          const data = await res.json();
          setMessages(data.map((msg: Message) => ({
            id: msg.id,
            role: msg.role,
            content: msg.content,
            citations: msg.citations || [],
            created_at: msg.created_at,
          })));
        }
      } catch { /* silent */ } finally {
        setLoadingHistory(false);
      }
    };
    loadMessages();
  }, [activeConversationId, setMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = async () => {
    if (!inputValue.trim() || isStreaming) return;
    const text = inputValue.trim();
    setInputValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    await sendMessage(text);
    if (!activeConversationId) {
      setTimeout(fetchConversations, 1000);
    }
  };

  const handleDelete = async () => {
    if (!activeConversationId || !confirm('Delete this conversation?')) return;
    try {
      const res = await apiFetch(`/v1/chat/conversations/${activeConversationId}`, { method: 'DELETE' });
      if (res.ok) {
        setActiveConversationId(null);
        setMessages([]);
        fetchConversations();
      }
    } catch { /* silent */ }
  };

  const activeTitle = conversations.find(c => c.id === activeConversationId)?.title || 'New Conversation';

  return (
    <div
      className="flex h-full w-full -m-6"
      style={{ height: 'calc(100% + 3rem)' }}
    >
      {/* Left Panel */}
      <div
        className="flex-shrink-0 flex flex-col"
        style={{ width: '256px', backgroundColor: 'var(--bg-surface)', borderRight: '1px solid var(--border)' }}
      >
        <div className="h-12 px-4 flex items-center justify-between flex-shrink-0" style={{ borderBottom: '1px solid var(--border)' }}>
          <span className="text-[10px] text-muted tracking-widest uppercase font-semibold">Conversations</span>
          <button
            onClick={() => { setActiveConversationId(null); setMessages([]); }}
            className="text-muted hover:text-primary hover:bg-elevated rounded p-1 transition-colors"
          >
            <Plus size={15} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {conversations.length === 0 ? (
            <EmptyState icon={MessageSquare} title="No conversations" description="Start a new chat to begin" className="mt-8 scale-90" />
          ) : (
            conversations.map(conv => (
              <div
                key={conv.id}
                onClick={() => setActiveConversationId(conv.id)}
                className="px-4 py-3 cursor-pointer border-b relative transition-colors"
                style={{
                  borderBottomColor: 'var(--border)',
                  borderLeft: conv.id === activeConversationId ? '2px solid var(--accent)' : '2px solid transparent',
                  backgroundColor: conv.id === activeConversationId ? 'var(--accent-hover)' : 'transparent',
                }}
              >
                <div className="flex justify-between items-center mb-0.5">
                  <span className="text-[13px] font-medium text-primary truncate pr-2 flex-1">
                    {conv.title ? conv.title.slice(0, 28) : 'Untitled'}
                  </span>
                  <span className="text-[10px] bg-elevated rounded-full px-1.5 py-0.5 text-muted font-mono flex-shrink-0">
                    {conv.message_count}
                  </span>
                </div>
                <div className="text-[11px] text-muted">{relativeTime(conv.created_at)}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 flex items-center justify-between flex-shrink-0" style={{ borderBottom: '1px solid var(--border)' }}>
          <h2 className="text-sm font-medium text-primary truncate max-w-lg">{activeTitle}</h2>
          {activeConversationId && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted font-mono">{messages.length} msgs</span>
              <button
                onClick={handleDelete}
                className="text-muted hover:text-red-status p-1.5 rounded hover:bg-red-status/10 transition-colors"
              >
                <Trash2 size={15} />
              </button>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4 custom-scrollbar">
          {!activeConversationId && messages.length === 0 ? (
            <div className="h-full flex items-center justify-center mt-8">
              <EmptyState icon={Bot} title="Co-Op AI Assistant" description="Ask questions about your uploaded documents. Type a query below to begin." />
            </div>
          ) : loadingHistory ? (
            <div className="space-y-5">
              {[70, 50, 80].map((w, i) => (
                <div key={i} className={cn('flex', i % 2 === 0 ? 'justify-start' : 'justify-end')}>
                  <Skeleton className={`h-14 w-${w}`} style={{ width: `${w}%`, backgroundColor: 'var(--bg-elevated)', borderRadius: '12px' }} />
                </div>
              ))}
            </div>
          ) : (
            <>
              {messages.map((msg, i) => {
                const isLastStreaming = isStreaming && i === messages.length - 1 && msg.role === 'assistant';
                if (isLastStreaming) {
                  return (
                    <div key={msg.id || i} className="flex justify-start">
                      <div className="max-w-[75%] px-4 py-3 text-[14px] leading-relaxed shadow-sm rounded-2xl rounded-tl-sm"
                        style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
                        {msg.content.length === 0 ? (
                          <span className="text-muted italic text-sm">Searching knowledge base...</span>
                        ) : (
                          <div className="whitespace-pre-wrap">
                            {msg.content}
                            <span className="inline-block w-1.5 h-4 bg-primary ml-0.5 align-middle" style={{ animation: 'blink-cursor 0.6s step-end infinite' }} />
                          </div>
                        )}
                      </div>
                    </div>
                  );
                }
                return <MessageBubble key={msg.id || i} message={msg} />;
              })}
              <div ref={messagesEndRef} className="h-1" />
            </>
          )}
        </div>

        {/* Input */}
        <div className="flex-shrink-0 px-5 pb-5 pt-3" style={{ backgroundColor: 'var(--bg-base)' }}>
          <div className="relative max-w-4xl mx-auto">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputValue}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              disabled={isStreaming}
              placeholder="Ask anything about your documents... (Ctrl+Enter to send)"
              className="w-full text-sm text-primary placeholder:text-muted rounded-xl px-4 py-3.5 pr-14 resize-none custom-scrollbar disabled:opacity-50 transition-all"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                minHeight: '52px',
                maxHeight: '120px',
                outline: 'none',
              }}
              onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--accent)'; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}
            />
            <button
              onClick={handleSubmit}
              disabled={!inputValue.trim() || isStreaming}
              className={cn(
                'absolute right-3 bottom-3 w-8 h-8 rounded-lg flex items-center justify-center transition-all',
                inputValue.trim() && !isStreaming
                  ? 'text-white shadow-md hover:scale-105 active:scale-95'
                  : 'text-muted cursor-not-allowed'
              )}
              style={{
                backgroundColor: inputValue.trim() && !isStreaming ? 'var(--accent)' : 'var(--bg-elevated)',
                border: inputValue.trim() && !isStreaming ? 'none' : '1px solid var(--border)',
              }}
            >
              {isStreaming ? (
                <span className="w-4 h-4 border-2 border-muted border-t-transparent rounded-full" style={{ animation: 'spin 1s linear infinite' }} />
              ) : (
                <ArrowUp size={15} strokeWidth={2.5} />
              )}
            </button>
          </div>
          <p className="text-[11px] text-muted text-center mt-2">Answers are based on your uploaded documents only. AI can make mistakes.</p>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message | Record<string, unknown> }) {
  const isUser = (message as Message).role === 'user';
  const content = String((message as Message).content ?? '');
  const citations = ((message as Message).citations ?? []) as Citation[];

  return (
    <div className={cn('flex w-full', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn('max-w-[75%] px-4 py-3 text-[14px] leading-relaxed shadow-sm', isUser ? 'rounded-2xl rounded-tr-sm' : 'rounded-2xl rounded-tl-sm')}
        style={{
          backgroundColor: isUser ? 'var(--accent)' : 'var(--bg-elevated)',
          border: isUser ? 'none' : '1px solid var(--border)',
          color: isUser ? 'white' : 'var(--text-primary)',
        }}
      >
        <div className="whitespace-pre-wrap">{content}</div>
        {!isUser && citations.length > 0 && <CitationsBlock citations={citations} />}
      </div>
    </div>
  );
}

function CitationsBlock({ citations }: { citations: Citation[] }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="mt-3 pt-2" style={{ borderTop: '1px solid var(--border)' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-xs text-muted hover:text-secondary transition-colors font-medium tracking-wide"
      >
        {isOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
        Sources ({citations.length})
      </button>
      {isOpen && (
        <div className="mt-2 space-y-1.5">
          {citations.map((cite, i) => (
            <div key={i} className="rounded flex flex-col p-2 hover:border-accent/50 transition-colors"
              style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
              <div className="flex items-center gap-2 text-[11px] font-mono mb-1 text-secondary">
                <FileText size={11} className="text-muted" />
                <span className="truncate flex-1" title={cite.source}>{cite.source}</span>
                <span className="bg-elevated px-1 rounded text-muted">Pg {cite.page}</span>
                <span className="text-muted border-l border-dim pl-1">{(cite.score * 100).toFixed(0)}%</span>
              </div>
              {cite.content && <div className="text-[11px] text-muted line-clamp-2 px-1 italic">&ldquo;{cite.content}&rdquo;</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
