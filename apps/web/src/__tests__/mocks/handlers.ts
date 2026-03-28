import { http, HttpResponse } from 'msw';

const API_URL = 'http://localhost:8000';

export const handlers = [
  // Health endpoint
  http.get(`${API_URL}/health`, () => {
    return HttpResponse.json({
      status: 'ok',
      postgres: 'connected',
      redis: 'connected',
      qdrant: 'connected',
      minio: 'connected',
    });
  }),

  // Documents endpoints
  http.get(`${API_URL}/v1/documents`, () => {
    return HttpResponse.json([
      {
        id: 'doc-1',
        filename: 'test.pdf',
        file_type: 'pdf',
        file_size: 1024000,
        status: 'READY',
        chunk_count: 10,
        created_at: new Date().toISOString(),
      },
      {
        id: 'doc-2',
        filename: 'report.docx',
        file_type: 'docx',
        file_size: 512000,
        status: 'INDEXING',
        chunk_count: 0,
        created_at: new Date().toISOString(),
      },
    ]);
  }),

  http.post(`${API_URL}/v1/documents`, async () => {
    return HttpResponse.json({
      id: 'doc-new',
      filename: 'uploaded.pdf',
      file_type: 'pdf',
      file_size: 2048000,
      status: 'PENDING',
      chunk_count: 0,
      created_at: new Date().toISOString(),
    });
  }),

  http.delete(`${API_URL}/v1/documents/:id`, () => {
    return HttpResponse.json({ success: true });
  }),

  http.get(`${API_URL}/v1/documents/:id/status`, () => {
    return HttpResponse.json({
      status: 'READY',
      chunk_count: 10,
    });
  }),

  // Conversations endpoints
  http.get(`${API_URL}/v1/chat/conversations`, () => {
    return HttpResponse.json([
      {
        id: 'conv-1',
        title: 'Test Conversation',
        message_count: 5,
        created_at: new Date().toISOString(),
      },
    ]);
  }),

  http.get(`${API_URL}/v1/chat/conversations/:id/messages`, () => {
    return HttpResponse.json([
      {
        id: 'msg-1',
        conversation_id: 'conv-1',
        role: 'user',
        content: 'Hello',
        citations: [],
        created_at: new Date().toISOString(),
      },
      {
        id: 'msg-2',
        conversation_id: 'conv-1',
        role: 'assistant',
        content: 'Hi there!',
        citations: [],
        created_at: new Date().toISOString(),
      },
    ]);
  }),

  http.delete(`${API_URL}/v1/chat/conversations/:id`, () => {
    return HttpResponse.json({ success: true });
  }),

  // Search endpoint
  http.post(`${API_URL}/v1/search`, async () => {
    return HttpResponse.json([
      {
        document_id: 'doc-1',
        text: 'This is a test search result with relevant content.',
        score: 0.95,
        source_file: 'test.pdf',
        page_number: 1,
      },
      {
        document_id: 'doc-1',
        text: 'Another relevant passage from the document.',
        score: 0.87,
        source_file: 'test.pdf',
        page_number: 2,
      },
    ]);
  }),
];
