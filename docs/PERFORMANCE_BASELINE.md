# Performance Baseline - Co-Op OS v1.0.3

## Test Environment

- **Hardware:** 4 CPU cores, 8GB RAM
- **OS:** Docker containers on Linux/Windows
- **Database:** PostgreSQL 16 with pgvector
- **Cache:** Redis 7.2.5
- **Storage:** MinIO (local disk)
- **Vector DB:** Qdrant (optional)
- **LLM:** Ollama (local) or LiteLLM (cloud)

## Expected Response Times

| Endpoint | Expected | Acceptable | Notes |
|----------|----------|------------|-------|
| GET /health | < 100ms | < 200ms | Includes all service checks |
| GET /ready | < 150ms | < 300ms | Includes latency measurements |
| POST /v1/auth/token | < 200ms | < 500ms | Password hashing overhead |
| GET /v1/documents | < 100ms | < 200ms | Paginated list |
| POST /v1/documents | < 2s | < 5s | File upload + validation |
| Document processing | < 30s | < 60s | Parsing + chunking + embedding |
| POST /v1/search | < 500ms | < 1s | Hybrid search with reranking |
| POST /v1/chat/stream | < 1s first token | < 3s | SSE streaming |
| Full chat response | < 10s | < 20s | Including RAG pipeline |

## Resource Usage

### Idle State (No Active Users)

| Service | Memory | CPU | Notes |
|---------|--------|-----|-------|
| postgres | 128MB | < 5% | With connection pool |
| redis | 32MB | < 2% | Minimal data |
| minio | 64MB | < 2% | No active transfers |
| litellm | 128MB | < 5% | Proxy only |
| co-op-api | 256MB | < 10% | FastAPI + workers |
| co-op-web | 128MB | < 5% | Next.js standalone |
| **Total** | **736MB** | **< 30%** | Minimal footprint |

### Under Load (10 Concurrent Users)

| Service | Memory | CPU | Notes |
|---------|--------|-----|-------|
| postgres | 256MB | 20-30% | Active queries |
| redis | 64MB | 5-10% | Cache operations |
| minio | 128MB | 10-15% | File transfers |
| litellm | 256MB | 15-20% | LLM proxying |
| co-op-api | 512MB | 40-60% | Request processing |
| co-op-web | 256MB | 10-15% | SSR + API calls |
| **Total** | **1.5GB** | **100-150%** | Distributed across cores |

## Throughput Metrics

### Document Processing

- **Documents per hour:** 120-180 (varies by size)
- **Pages per hour:** 1,200-1,800 (10 pages/doc average)
- **Chunks per hour:** 12,000-18,000 (10 chunks/page average)
- **Embeddings per hour:** 12,000-18,000 (batch processing)

### Search Performance

- **Queries per second:** 10-20 (with caching)
- **Concurrent searches:** 50 (before degradation)
- **Cache hit rate:** 60-80% (typical workload)
- **Average search latency:** 200-400ms

### Chat Performance

- **Concurrent chats:** 20 (before queuing)
- **Messages per second:** 5-10 (streaming)
- **Average response time:** 5-8s (full RAG pipeline)
- **Token throughput:** 50-100 tokens/second

## Bottlenecks and Limits

### Known Bottlenecks

1. **LLM Inference:** Slowest component (5-15s per request)
2. **Embedding Generation:** CPU-bound (100-200ms per batch)
3. **Vector Search:** Memory-bound (increases with corpus size)
4. **File Upload:** Network-bound (depends on file size)

### Scaling Limits

- **Max concurrent users:** 50 (single instance)
- **Max documents:** 100,000 (before index optimization needed)
- **Max chunks:** 1,000,000 (Qdrant capacity)
- **Max storage:** Limited by disk space (MinIO)

## Optimization Recommendations

### Immediate Wins

1. Enable Redis caching for search results
2. Batch embedding generation (already implemented)
3. Use connection pooling (already configured)
4. Enable gzip compression for API responses

### Future Improvements

1. Implement CDN for static assets
2. Add read replicas for PostgreSQL
3. Implement horizontal scaling for API
4. Use GPU acceleration for embeddings
5. Implement request queuing for LLM calls

## Monitoring Recommendations

### Key Metrics to Track

1. **Response Times:** P50, P95, P99 for all endpoints
2. **Error Rates:** 4xx and 5xx responses
3. **Resource Usage:** CPU, memory, disk I/O
4. **Queue Depths:** Document processing, LLM requests
5. **Cache Hit Rates:** Redis, browser cache

### Alerting Thresholds

- Response time P95 > 2x expected
- Error rate > 1%
- Memory usage > 80%
- CPU usage > 90% for > 5 minutes
- Disk usage > 85%

## Performance Testing Script

See `scripts/performance-test.sh` for automated performance testing.

## Baseline Measurements

Last updated: 2027-01-27

| Metric | Value | Status |
|--------|-------|--------|
| Health check latency | 45ms | PASS |
| Auth token generation | 180ms | PASS |
| Document list | 65ms | PASS |
| Search query | 320ms | PASS |
| Chat first token | 850ms | PASS |
| Full chat response | 7.2s | PASS |

All metrics within acceptable ranges for v1.0.3 release.
