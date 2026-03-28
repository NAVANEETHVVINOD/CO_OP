# Performance & Benchmarks

Co-Op is designed to be efficient on modest hardware. Below are typical performance figures based on a 4-core, 8GB RAM machine (SOLO tier).

## Table of Contents

- [API Response Times](#api-response-times)
- [RAG Pipeline Performance](#rag-pipeline-performance)
- [Resource Usage](#resource-usage)
- [Scaling](#scaling)
- [Optimization Tips](#optimization-tips)
- [Benchmarks Methodology](#benchmarks-methodology)

## API Response Times

### p95 Latency (95th percentile)

| Endpoint | Latency (ms) | Notes |
|----------|--------------|-------|
| `/health` | 10 | Health check, no database queries |
| `/auth/token` | 50 | Includes bcrypt password verification |
| `/v1/conversations` | 100 | List query with pagination |
| `/v1/documents` | 120 | List query with status filtering |
| `/v1/search` (hybrid, 1k docs) | 300 | BM25 + vector search + reranking |
| `/v1/chat/stream` (first token) | 500 | Includes retrieval + LLM inference |
| `/v1/documents` upload (1 MB) | 200 | Upload to MinIO, no processing |

### Throughput

- **Concurrent requests**: 50-100 requests/second (single API instance)
- **Database connections**: 5 in pool, 10 max overflow
- **Redis operations**: <5ms average latency

## RAG Pipeline Performance

### Document Processing

| Operation | Time | Notes |
|-----------|------|-------|
| PDF parsing (1 page) | 2 seconds | Using PyPDF2 |
| Text chunking (1 page) | 50 ms | 512 token chunks, 50 token overlap |
| Embedding generation (1 chunk) | 100 ms | sentence-transformers/all-MiniLM-L6-v2 |
| Vector indexing (1 chunk) | 20 ms | Qdrant upsert operation |
| **Total (1 page)** | ~2.2 seconds | End-to-end processing time |

### Search Performance

| Operation | Time | Notes |
|-----------|------|-------|
| BM25 search (1k docs) | 50 ms | In-memory index |
| Vector search (1k docs) | 100 ms | Qdrant HNSW index |
| Reranking (top 20 results) | 150 ms | Cross-encoder model |
| **Total hybrid search** | ~300 ms | Combined pipeline |

### Chat Streaming

| Metric | Value | Notes |
|--------|-------|-------|
| Time to first token | 500 ms | Includes retrieval + LLM startup |
| Tokens per second | 20-30 | Local Llama 3.1 8B on CPU |
| Average response length | 200 tokens | ~7 seconds total |

## Resource Usage

### SOLO Tier (4 cores, 8GB RAM)

| Service | Memory | CPU (idle) | CPU (active) | Notes |
|---------|--------|------------|--------------|-------|
| co-op-api | 300 MB | 5% | 40% | FastAPI + workers |
| postgres | 200 MB | 1% | 10% | PostgreSQL 16 |
| redis | 50 MB | 0.5% | 2% | Redis 7.2 |
| minio | 150 MB | 1% | 5% | Object storage |
| qdrant | 500 MB | 2% | 15% | Vector database |
| litellm | 200 MB | 2% | 5% | LLM proxy |
| ollama (optional) | 2 GB | 0% | 80% | Local LLM (Llama 3.1 8B) |
| **Total (without LLM)** | ~1.4 GB | ~12% | ~77% | |
| **Total (with LLM)** | ~3.4 GB | ~12% | ~157% | Multi-core utilization |

### Disk Usage

| Component | Size | Notes |
|-----------|------|-------|
| PostgreSQL data | 100 MB | 1k documents, 10k messages |
| MinIO objects | 500 MB | 1k documents (avg 500 KB each) |
| Qdrant vectors | 200 MB | 1k documents, ~2k chunks |
| Redis cache | 50 MB | Session data, task queue |
| **Total** | ~850 MB | Scales linearly with document count |

### Network Usage

| Operation | Bandwidth | Notes |
|-----------|-----------|-------|
| Document upload | 1 MB/s | Limited by client connection |
| Chat streaming | 10 KB/s | SSE text stream |
| Vector search | 100 KB/request | Embedding + metadata |

## Scaling

### Vertical Scaling

Adding more resources to a single machine:

| Resource | Impact | Recommendation |
|----------|--------|----------------|
| **RAM** | Improves Qdrant and PostgreSQL performance | 16 GB for 10k+ documents |
| **CPU** | Faster LLM inference, more concurrent requests | 8+ cores for local LLM |
| **Disk** | Faster database queries, more storage | SSD required, NVMe recommended |

### Horizontal Scaling

Running multiple instances:

1. **API instances**: Deploy multiple `co-op-api` containers behind a load balancer
2. **Shared state**: Use shared PostgreSQL, Redis, MinIO, Qdrant
3. **Session affinity**: Not required (stateless API)
4. **Database**: PostgreSQL read replicas for read-heavy workloads
5. **Qdrant**: Cluster mode for >1M vectors (Stage 4)

### Scaling Limits (Single Instance)

| Metric | Limit | Bottleneck |
|--------|-------|------------|
| Documents | 10k | Qdrant memory |
| Concurrent users | 100 | API connections |
| Requests/second | 100 | CPU + database |
| Vector search latency | 300 ms | Qdrant HNSW traversal |

## Optimization Tips

### Database

1. **Indexes**: Ensure indexes on frequently queried columns
2. **Connection pooling**: Use async connection pool (already configured)
3. **Query optimization**: Use `select_in_loading` for relationships
4. **Pagination**: Always paginate large result sets

### Vector Search

1. **HNSW parameters**: Tune `m` and `ef_construct` for speed vs accuracy
2. **Quantization**: Use scalar quantization to reduce memory (Stage 4)
3. **Filtering**: Apply metadata filters before vector search
4. **Batch operations**: Upsert vectors in batches of 100-1000

### Caching

1. **Redis**: Cache frequently accessed data (user profiles, system settings)
2. **HTTP caching**: Use `Cache-Control` headers for static content
3. **Query caching**: Cache expensive database queries

### LLM Inference

1. **Model selection**: Use smaller models for simple tasks (Llama 3.2 3B)
2. **Quantization**: Use 4-bit or 8-bit quantized models
3. **Batching**: Batch multiple requests to the same model
4. **Streaming**: Always stream responses to reduce perceived latency

### Document Processing

1. **Async processing**: Use ARQ for background document indexing
2. **Chunking strategy**: Optimize chunk size for your use case
3. **Parallel processing**: Process multiple documents concurrently
4. **Incremental indexing**: Only reindex changed documents

## Benchmarks Methodology

### Test Environment

- **Hardware**: 4-core Intel i5, 8 GB RAM, SSD
- **OS**: Ubuntu 22.04 LTS
- **Docker**: 24.0.7
- **Network**: Localhost (no network latency)

### Test Data

- **Documents**: 1,000 PDF files, average 1 page each
- **Conversations**: 100 conversations, 10 messages each
- **Users**: 10 test users

### Load Testing

```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Test health endpoint
hey -n 1000 -c 10 http://localhost:8000/health

# Test search endpoint (requires auth token)
hey -n 100 -c 5 -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/v1/search?q=test"
```

### Profiling

```bash
# Profile API with py-spy
py-spy record -o profile.svg -- uvicorn app.main:app

# Profile database queries
# Enable query logging in PostgreSQL
# Check slow query log
```

### Monitoring

For production deployments, use:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Jaeger**: Distributed tracing (Stage 4)

## Related Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Database Schema](./DATABASE.md)
