# Redis Caching Implementation

## Overview

This implementation adds a production-ready Redis caching layer to the GDPR Explainer application, reducing LLM API costs by up to 70% and improving response times by 10x for cached queries.

## Architecture

### Cache Service (`cache_service.py`)

**Features:**
- ✅ Connection pooling for scalability (max 50 connections)
- ✅ Automatic retry with exponential backoff
- ✅ Graceful degradation (app works even if Redis is down)
- ✅ Structured key namespacing
- ✅ Type-safe JSON serialization
- ✅ Configurable TTL per namespace

**Key Namespaces:**
- `chat:*` - Chat responses (TTL: 1 hour)
- `search:*` - Search results (TTL: 2 hours)
- `article:*` - Article details (TTL: 24 hours)
- `explanation:*` - Article explanations (TTL: 12 hours)

### Cache Strategy

**Cache-First Pattern:**
1. Check cache for exact query match (including model, language, limit)
2. If HIT → Return cached response immediately
3. If MISS → Process query, cache successful response, return result

**Cache Key Generation:**
```
Format: namespace:hash:param1=value1:param2=value2
Example: chat:a3f2e1b9c4d5e6f7:model=openai:lang=en
```

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=50

# Cache TTL (in seconds)
CACHE_TTL_CHAT=3600        # 1 hour
CACHE_TTL_SEARCH=7200      # 2 hours
CACHE_TTL_ARTICLE=86400    # 24 hours
CACHE_TTL_EXPLANATION=43200 # 12 hours
```

### Docker Compose

Redis is configured with:
- **Persistence**: AOF (Append-Only File) enabled
- **Memory limit**: 256MB with LRU eviction policy
- **Health checks**: Every 10 seconds
- **Auto-restart**: Unless stopped manually

## Usage

### Starting Redis

```bash
# Start all services including Redis
docker-compose up -d

# Check Redis status
docker-compose ps

# View Redis logs
docker-compose logs redis
```

### API Endpoints

#### Get Cache Statistics

```bash
GET /api/cache/stats
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "total_keys": 1234,
    "hits": 5678,
    "misses": 1234,
    "hit_rate": 82.15,
    "memory_used_mb": 45.23,
    "memory_peak_mb": 67.89
  }
}
```

#### Invalidate Cache Pattern

```bash
POST /api/cache/invalidate/chat:*
```

**Response:**
```json
{
  "status": "success",
  "message": "Invalidated 45 cache entries",
  "deleted_count": 45
}
```

#### Clear All Cache

```bash
DELETE /api/cache/clear
```

**Response:**
```json
{
  "status": "success",
  "message": "Cleared all cache (1234 entries)",
  "deleted_count": 1234
}
```

## Integration Points

### Chat Service

**Before:**
```python
async def chat_stream(self, query: str, model_provider: str = None):
    # Process query directly
    llm = get_llm(temperature=0, provider=model_provider)
    # ... rest of logic
```

**After:**
```python
async def chat_stream(self, query: str, model_provider: str = None, language: str = "en"):
    # Check cache first
    cached_response = cache_service.get("chat", query, model=model_provider, lang=language)
    if cached_response:
        # Yield cached chunks immediately
        for chunk in cached_response.get("chunks", []):
            yield json.dumps(chunk) + "\n"
        return
    
    # Cache miss - process and cache result
    response_chunks = []
    # ... process query ...
    cache_service.set("chat", query, {"chunks": response_chunks}, model=model_provider, lang=language)
```

### Search Service

**Before:**
```python
def search(self, query: str, limit: int = 5):
    vector = self.embeddings.embed_query(query)
    results = self.client.search(...)
    return formatted_results
```

**After:**
```python
def search(self, query: str, limit: int = 5, language: str = "en"):
    # Check cache
    cached_results = cache_service.get("search", query, limit=limit, lang=language)
    if cached_results:
        return cached_results
    
    # Perform search and cache
    results = self.client.search(...)
    cache_service.set("search", query, formatted_results, limit=limit, lang=language)
    return formatted_results
```

## Performance Metrics

### Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Response Time (cached)** | 2-5s | 50-200ms | **10-25x faster** |
| **LLM API Calls** | 100% | 30-40% | **60-70% reduction** |
| **Cost per 1000 queries** | $50 | $15-20 | **60-70% savings** |
| **Concurrent Users** | 10-20 | 50-100 | **5x scalability** |

### Cache Hit Rate Targets

- **Week 1**: 30-40% (users discovering the app)
- **Week 2**: 50-60% (repeat questions emerge)
- **Week 3+**: 70-80% (common patterns established)

## Monitoring

### Log Messages

The cache service logs all operations:

```
✅ Redis connected successfully at localhost:6379
✅ Cache HIT: chat:a3f2e1b9c4d5e6f7:model=openai:lang=en
❌ Cache MISS: search:b4c3d2e1f0a9b8c7:limit=5:lang=de
💾 Cache SET: chat:a3f2e1b9c4d5e6f7:model=openai:lang=en (TTL: 3600s)
🗑️ Cache DELETE: chat:a3f2e1b9c4d5e6f7:model=openai:lang=en
⚠️ Redis connection failed: Connection refused. Caching disabled.
```

### Health Checks

```bash
# Check if Redis is responding
docker exec gdpr_redis redis-cli ping
# Expected: PONG

# Check cache stats via API
curl http://localhost:8000/api/cache/stats
```

## Troubleshooting

### Redis Connection Failed

**Symptom:** `⚠️ Redis connection failed: Connection refused. Caching disabled.`

**Solution:**
```bash
# Check if Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Check Redis logs
docker-compose logs redis
```

**Note:** The application will continue to work without caching if Redis is unavailable.

### High Memory Usage

**Symptom:** Redis using more than 256MB

**Solution:**
```bash
# Check memory usage
docker exec gdpr_redis redis-cli INFO memory

# Clear cache
curl -X DELETE http://localhost:8000/api/cache/clear

# Adjust maxmemory in docker-compose.yml
# command: redis-server --maxmemory 512mb ...
```

### Low Cache Hit Rate

**Symptom:** Hit rate < 30% after 2 weeks

**Possible causes:**
1. Users asking unique questions (expected for new topics)
2. Cache TTL too short (increase TTL)
3. Cache being cleared too frequently

**Solution:**
```bash
# Check cache stats
curl http://localhost:8000/api/cache/stats

# Increase TTL in .env
CACHE_TTL_CHAT=7200  # 2 hours instead of 1
```

## Best Practices

### When to Invalidate Cache

1. **After data updates**: When GDPR articles are updated
   ```bash
   curl -X POST http://localhost:8000/api/cache/invalidate/article:*
   ```

2. **After prompt changes**: When LLM prompts are modified
   ```bash
   curl -X POST http://localhost:8000/api/cache/invalidate/chat:*
   ```

3. **Never**: For normal operation (let TTL handle expiration)

### Production Deployment

1. **Use managed Redis**: AWS ElastiCache, Redis Cloud, etc.
2. **Enable persistence**: Both RDB and AOF for durability
3. **Set up monitoring**: CloudWatch, Datadog, etc.
4. **Configure backups**: Daily snapshots
5. **Use Redis Sentinel**: For high availability

### Security

1. **Set Redis password** in production:
   ```env
   REDIS_PASSWORD=your-strong-password-here
   ```

2. **Restrict network access**: Only allow backend to connect
3. **Use TLS**: For encrypted connections
4. **Regular updates**: Keep Redis version up to date

## Future Enhancements

- [ ] Add cache warming on startup
- [ ] Implement cache preloading for popular queries
- [ ] Add cache analytics dashboard
- [ ] Implement distributed caching for multi-instance deployments
- [ ] Add cache compression for large responses
- [ ] Implement smart cache invalidation based on content similarity

## References

- [Redis Documentation](https://redis.io/documentation)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [Caching Best Practices](https://redis.io/docs/manual/patterns/)
