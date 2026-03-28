export interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: 'PENDING' | 'INDEXING' | 'READY' | 'FAILED'
  chunk_count: number
  created_at: string
  error_message?: string
}

export interface Conversation {
  id: string
  title: string
  message_count: number
  created_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  created_at: string
}

export interface Citation {
  source: string
  page: number
  score: number
  content?: string
}

export interface SearchResult {
  document_id: string
  text: string
  score: number
  source_file: string
  page_number: number
}

export interface AgentRun {
  id: string
  agent_id: string
  agent_type?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input_payload?: Record<string, unknown>
  output_payload?: Record<string, unknown>
  started_at?: string
  created_at: string
  completed_at?: string
  duration_s?: number
  token_cost_usd?: number
  error?: string
}

export interface HealthResponse {
  status: string
  postgres: string
  redis: string
  qdrant: string
  minio?: string
}
