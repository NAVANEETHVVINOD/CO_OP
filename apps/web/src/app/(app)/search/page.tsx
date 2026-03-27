'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, SearchX, FileText } from 'lucide-react';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { apiFetch } from '@/lib/api';
import { SearchResult } from '@/types/api';

function highlightText(text: string, query: string): string {
  if (!query.trim()) return text;
  const words = query.trim().split(/\s+/).map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const regex = new RegExp(`(${words.join('|')})`, 'gi');
  return text.replace(regex, '<mark class="bg-amber-400/30 text-amber-300 rounded px-0.5">$1</mark>');
}

const RESULT_COUNTS = [3, 5, 10, 20];
const MODES = [
  { label: 'Semantic', alpha: 0.9 },
  { label: 'Balanced', alpha: 0.7 },
  { label: 'Keyword', alpha: 0.3 },
];

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(5);
  const [modeIndex, setModeIndex] = useState(0);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    const start = Date.now();
    try {
      const res = await apiFetch('/v1/search', {
        method: 'POST',
        body: JSON.stringify({ query: query.trim(), top_k: topK, alpha: MODES[modeIndex].alpha }),
      });
      if (res.ok) {
        const data = await res.json();
        setResults(Array.isArray(data) ? data : (data.results ?? []));
      }
    } catch { setResults([]); } finally {
      setSearchTime(Date.now() - start);
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleUseInChat = (result: SearchResult) => {
    sessionStorage.setItem('co_op_search_context', JSON.stringify(result));
    router.push('/chat');
  };

  return (
    <div>
      <PageHeader title="Knowledge Search" description="Search across all indexed documents" />

      {/* Search bar */}
      <div className="max-w-2xl mx-auto mt-2 mb-6">
        <div className="relative">
          <Search size={18} className="text-muted absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search your knowledge base..."
            className="w-full pl-12 pr-28 py-3.5 text-sm text-primary rounded-xl transition-colors"
            style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
          />
          <button
            onClick={handleSearch}
            disabled={!query.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 rounded-lg text-sm font-medium text-white transition-opacity"
            style={{ backgroundColor: 'var(--accent)', opacity: (!query.trim() || loading) ? 0.6 : 1 }}
          >
            Search
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-7 text-sm">
        <div className="flex items-center gap-2 text-muted">
          <span className="text-xs">Results:</span>
          <select
            value={topK}
            onChange={e => setTopK(Number(e.target.value))}
            className="bg-elevated border-dim rounded text-sm text-secondary px-2 py-1"
            style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}
          >
            {RESULT_COUNTS.map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-1">
          {MODES.map((m, i) => (
            <button
              key={m.label}
              onClick={() => setModeIndex(i)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              style={{
                backgroundColor: modeIndex === i ? 'var(--accent)' : 'var(--bg-elevated)',
                color: modeIndex === i ? 'white' : 'var(--text-secondary)',
                border: modeIndex === i ? 'none' : '1px solid var(--border)',
              }}
            >
              {m.label}
            </button>
          ))}
        </div>
        {searched && !loading && searchTime !== null && (
          <span className="text-xs text-muted ml-auto font-mono">
            {results.length} results in {searchTime}ms
          </span>
        )}
      </div>

      {/* Results */}
      {!searched ? (
        <EmptyState
          icon={Search}
          title="Search your knowledge base"
          description="Upload and index documents, then search here with natural-language queries"
        />
      ) : loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" style={{ backgroundColor: 'var(--bg-elevated)' }} />
          ))}
        </div>
      ) : results.length === 0 ? (
        <EmptyState
          icon={SearchX}
          title="No results found"
          description={`No documents match "${query}". Try different keywords or upload more documents.`}
        />
      ) : (
        <div className="space-y-3">
          {results.map((result, i) => (
            <div
              key={i}
              className="rounded-xl p-5 transition-all"
              style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--border-bright)')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <FileText size={14} className="text-muted flex-shrink-0" />
                  <span className="text-[13px] font-mono text-secondary">{result.source_file}</span>
                  <span className="text-muted text-xs">·</span>
                  <span className="text-[13px] text-muted">Page {result.page_number}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[11px] font-mono text-muted">Score: {result.score.toFixed(2)}</span>
                  <button
                    onClick={() => handleUseInChat(result)}
                    className="text-xs font-medium hover:underline"
                    style={{ color: 'var(--accent)' }}
                  >
                    Use in Chat →
                  </button>
                </div>
              </div>
              <p
                className="text-sm text-primary line-clamp-3 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: highlightText(result.text, query) }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
