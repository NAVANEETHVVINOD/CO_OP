'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { UploadCloud, FileText, Trash2, Eye, X, ExternalLink } from 'lucide-react';
import { PageHeader } from '@/components/shared/PageHeader';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { MonoId } from '@/components/shared/MonoId';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { apiFetch } from '@/lib/api';
import { Document } from '@/types/api';
import { toast } from 'sonner';
import { env } from '@/lib/env';

const API_URL = env.API_URL;

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const TYPE_COLORS: Record<string, string> = {
  pdf: '#EF4444', docx: '#3B82F6', txt: '#6B7280', md: '#A855F7',
};

export default function DocumentsPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [pollingIds, setPollingIds] = useState<Set<string>>(new Set());
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [dragging, setDragging] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await apiFetch('/v1/documents');
      if (res.ok) {
        const data = await res.json();
        setDocuments(Array.isArray(data) ? data : []);
      }
    } catch { /* silent */ } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Polling logic
  useEffect(() => {
    if (pollingIds.size === 0) return;
    const interval = setInterval(async () => {
      const ids = Array.from(pollingIds);
      for (const id of ids) {
        try {
          const res = await apiFetch(`/v1/documents/${id}/status`);
          if (res.ok) {
            const data = await res.json();
            const newStatus = data.status as Document['status'];
            setDocuments(prev => prev.map(d => d.id === id ? { ...d, status: newStatus, chunk_count: data.chunk_count ?? d.chunk_count } : d));
            if (newStatus === 'READY') {
              setPollingIds(prev => { const s = new Set(prev); s.delete(id); return s; });
              toast.success('Document indexed — ready to search');
            } else if (newStatus === 'FAILED') {
              setPollingIds(prev => { const s = new Set(prev); s.delete(id); return s; });
              toast.error('Indexing failed — check document format');
            }
          }
        } catch { /* silent */ }
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [pollingIds]);

  const uploadFile = async (file: File) => {
    if (file.size > 50 * 1024 * 1024) {
      toast.error(`File too large: ${file.name} exceeds 50MB`);
      return;
    }
    const allowed = ['.pdf', '.docx', '.txt', '.md'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowed.includes(ext)) {
      toast.error(`Unsupported file type: ${file.name}`);
      return;
    }

    const token = typeof window !== 'undefined' ? localStorage.getItem('co_op_token') : '';
    const formData = new FormData();
    formData.append('file', file);

    try {
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) setUploadProgress(Math.round((e.loaded / e.total) * 100));
        };
        xhr.onload = async () => {
          setUploadProgress(null);
          if (xhr.status >= 200 && xhr.status < 300) {
            const newDoc: Document = JSON.parse(xhr.responseText);
            setDocuments(prev => [newDoc, ...prev]);
            setPollingIds(prev => new Set(prev).add(newDoc.id));
            toast.success('Document uploaded — indexing in progress');
            resolve();
          } else {
            reject(new Error('Upload failed'));
          }
        };
        xhr.onerror = () => { setUploadProgress(null); reject(new Error('Network error')); };
        xhr.open('POST', `${API_URL}/v1/documents`);
        if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        xhr.send(formData);
      });
    } catch {
      toast.error(`Failed to upload ${file.name}`);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    Array.from(e.dataTransfer.files).forEach(uploadFile);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    Array.from(e.target.files ?? []).forEach(uploadFile);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDelete = async (doc: Document) => {
    if (!confirm(`Delete "${doc.filename}"? This removes all indexed chunks.`)) return;
    try {
      const res = await apiFetch(`/v1/documents/${doc.id}`, { method: 'DELETE' });
      if (res.ok) {
        setDocuments(prev => prev.filter(d => d.id !== doc.id));
        if (selectedDoc?.id === doc.id) setSelectedDoc(null);
        toast.success('Document deleted');
      } else {
        toast.error('Failed to delete document');
      }
    } catch { toast.error('Failed to delete document'); }
  };

  const readyDocs = documents.filter(d => d.status === 'READY').length;

  return (
    <div className="relative">
      <PageHeader
        title="Knowledge Base"
        badge={readyDocs}
        description={`${documents.length} documents · ${readyDocs} indexed`}
        actions={
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white"
            style={{ backgroundColor: 'var(--accent)' }}
          >
            <UploadCloud size={15} />
            Upload
          </button>
        }
      />

      {/* Upload zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onClick={() => fileInputRef.current?.click()}
        className="relative rounded-xl p-10 text-center cursor-pointer transition-colors mb-6 overflow-hidden"
        style={{
          border: `2px dashed ${dragging ? 'var(--accent)' : 'var(--border)'}`,
          backgroundColor: dragging ? 'var(--accent-hover)' : 'transparent',
        }}
      >
        <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.docx,.txt,.md" multiple onChange={handleFileInput} />
        <UploadCloud size={36} className="text-muted mx-auto mb-3" />
        <p className="text-secondary text-sm font-medium">Drop files here or click to browse</p>
        <p className="text-muted text-xs mt-1">Supports: PDF, DOCX, TXT, MD · Max 50MB</p>

        {uploadProgress !== null && (
          <div className="absolute inset-0 flex flex-col items-center justify-center" style={{ backgroundColor: 'rgba(10,10,15,0.85)' }}>
            <div className="text-sm text-secondary mb-3 font-medium">Uploading... {uploadProgress}%</div>
            <div className="w-48 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--border)' }}>
              <div className="h-full rounded-full transition-all" style={{ backgroundColor: 'var(--accent)', width: `${uploadProgress}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" style={{ backgroundColor: 'var(--bg-elevated)' }} />)}
        </div>
      ) : documents.length === 0 ? (
        <EmptyState icon={FileText} title="No documents yet" description="Upload your first document to begin building your knowledge base." action={{ label: 'Upload Document', onClick: () => fileInputRef.current?.click() }} />
      ) : (
        <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--border)' }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-elevated)' }}>
                <th className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold">Name</th>
                <th className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold w-20">Type</th>
                <th className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold w-24">Size</th>
                <th className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold w-28">Status</th>
                <th className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold w-20">Chunks</th>
                <th className="text-left px-4 py-3 text-[10px] text-muted tracking-widest uppercase font-semibold w-28">Uploaded</th>
                <th className="px-4 py-3 w-20"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => {
                const ext = doc.filename.split('.').pop()?.toLowerCase() ?? '';
                const color = TYPE_COLORS[ext] ?? '#6B7280';
                return (
                  <tr
                    key={doc.id}
                    className="cursor-pointer transition-colors"
                    style={{ borderTop: '1px solid var(--border)' }}
                    onClick={() => setSelectedDoc(doc)}
                    onMouseEnter={e => (e.currentTarget.style.backgroundColor = 'rgba(26,26,38,0.7)')}
                    onMouseLeave={e => (e.currentTarget.style.backgroundColor = '')}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5">
                        <span className="w-5 h-5 rounded text-white text-[9px] font-bold flex items-center justify-center flex-shrink-0" style={{ backgroundColor: color }}>
                          {ext.toUpperCase().slice(0, 2)}
                        </span>
                        <span className="text-primary text-[13px] truncate max-w-xs" title={doc.filename}>{doc.filename}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={ext} /></td>
                    <td className="px-4 py-3 font-mono text-[12px] text-muted">{formatFileSize(doc.file_size)}</td>
                    <td className="px-4 py-3"><StatusBadge status={doc.status} /></td>
                    <td className="px-4 py-3 font-mono text-[12px] text-muted">{doc.chunk_count > 0 ? doc.chunk_count : '—'}</td>
                    <td className="px-4 py-3 text-[12px] text-muted">{relativeTime(doc.created_at)}</td>
                    <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                      <div className="flex items-center gap-2">
                        <button onClick={() => setSelectedDoc(doc)} className="text-muted hover:text-accent transition-colors p-1"><Eye size={14} /></button>
                        <button onClick={() => handleDelete(doc)} className="text-muted hover:text-red-status transition-colors p-1"><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Slide-over panel */}
      {selectedDoc && (
        <>
          <div className="fixed inset-0 bg-black/50 z-40" onClick={() => setSelectedDoc(null)} />
          <div
            className="fixed inset-y-0 right-0 z-50 flex flex-col animate-slide-right"
            style={{ width: '320px', backgroundColor: 'var(--bg-surface)', borderLeft: '1px solid var(--border)', boxShadow: '-8px 0 24px rgba(0,0,0,0.4)' }}
          >
            <div className="h-14 px-5 flex items-center justify-between flex-shrink-0" style={{ borderBottom: '1px solid var(--border)' }}>
              <div className="flex items-center gap-2">
                <FileText size={16} className="text-muted" />
                <span className="text-sm font-medium text-primary truncate max-w-[200px]">{selectedDoc.filename}</span>
              </div>
              <button onClick={() => setSelectedDoc(null)} className="text-muted hover:text-primary p-1 rounded"><X size={16} /></button>
            </div>
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {[
                { label: 'ID', value: <MonoId id={selectedDoc.id} /> },
                { label: 'Filename', value: <span className="text-primary text-sm font-mono">{selectedDoc.filename}</span> },
                { label: 'File Size', value: <span className="text-primary font-mono">{formatFileSize(selectedDoc.file_size)}</span> },
                { label: 'Chunks', value: <span className="text-primary font-mono">{selectedDoc.chunk_count > 0 ? selectedDoc.chunk_count : '—'}</span> },
                { label: 'Status', value: <StatusBadge status={selectedDoc.status} size="md" /> },
                { label: 'Uploaded', value: <span className="text-muted font-mono text-sm">{new Date(selectedDoc.created_at).toLocaleString()}</span> },
              ].map(({ label, value }) => (
                <div key={label} className="flex flex-col gap-1">
                  <span className="text-[10px] tracking-widest uppercase text-muted font-semibold">{label}</span>
                  <div className="text-sm">{value}</div>
                </div>
              ))}
            </div>
            <div className="p-5" style={{ borderTop: '1px solid var(--border)' }}>
              <button
                onClick={() => router.push('/chat')}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-colors text-white"
                style={{ backgroundColor: 'var(--accent)' }}
              >
                <ExternalLink size={14} />
                Chat with this document
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
