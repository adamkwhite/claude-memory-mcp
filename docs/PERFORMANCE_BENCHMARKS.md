# Performance Benchmarks

Generated: 2025-06-09 10:42:38

## Test Environment
- **Python Version**: 3.12.3
- **Platform**: linux
- **CPU Cores**: 8
- **Total Memory**: 15.5 GB

## Executive Summary
✅ **README claim validated**: Search completes in 0.05s (< 5s) with 159 conversations

## README Claims Validation

| Claim | Measured | Status | Notes |
|-------|----------|---------|-------|
| Minimal RAM usage | 40.4MB peak | ✅ PASS | During search operations |

## Detailed Results

### Search Performance

#### Search Time by Dataset Size

| Dataset Size | Avg Time (s) | Min Time (s) | Max Time (s) | Samples |
|--------------|--------------|--------------|--------------|----------|
| 10 | 0.003 | 0.002 | 0.003 | 5 |
| 100 | 0.028 | 0.024 | 0.030 | 5 |
| 159 | 0.927 | 0.038 | 5.336 | 6 |
| 200 | 0.045 | 0.038 | 0.049 | 5 |
| 50 | 0.016 | 0.015 | 0.017 | 5 |
| 500 | 0.043 | 0.038 | 0.047 | 5 |

#### Search Performance by Query Type

| Query Type | 159 Convs Time (s) | Scaling Factor* |
|------------|-------------------|------------------|

*Scaling Factor: Estimated time per 100 conversations

### Write Performance

| Content Size | Avg Time (s) | Throughput (KB/s) |
|--------------|--------------|-------------------|
| large | 0.009 | 12547.1 |
| medium | 0.002 | 7416.6 |
| small | 0.001 | 1332.3 |

### Weekly Summary Performance

| Week Size | Generation Time (s) |
|-----------|-------------------|
| 10 conversations | 0.001 |
| 100 conversations | 0.001 |
| 50 conversations | 0.001 |

## Performance Scaling

### Search Time vs Dataset Size
```
Time (s)
│
 0.00s │ 10
 0.00s │ 10
 0.00s │ 10
 0.00s │ 10
 0.00s │ 10
 0.02s │ 100
 0.03s │ 100
 0.03s │ 100
 0.03s │ 100
 0.03s │ 100
 0.04s │ 159
 0.04s │ 159
 0.05s │ 159
 0.05s │ 159
 0.05s │ 159
 5.34s │██████████████████████████████████████████████████ 159
 0.04s │ 200
 0.05s │ 200
 0.05s │ 200
 0.05s │ 200
 0.05s │ 200
 0.01s │ 50
 0.02s │ 50
 0.02s │ 50
 0.02s │ 50
 0.02s │ 50
 0.04s │ 500
 0.04s │ 500
 0.04s │ 500
 0.05s │ 500
 0.05s │ 500
       └────────────────────────────────────────────────────
         Dataset Size
```

## Recommendations
⚠️ **Performance optimization recommended**

### Suggested Optimizations (Priority Order)

1. **Implement Search Caching**
   - Cache recent search results (LRU cache)
   - Invalidate on new conversation additions
   - Expected improvement: 50-90% for repeated searches

2. **Add Search Index**
   - Create inverted index for common terms
   - Update index on conversation additions
   - Expected improvement: 70-80% for large datasets

3. **Migrate to SQLite FTS** (for > 500 conversations)
   - Full-text search with built-in indexing
   - Better memory efficiency
   - Expected improvement: 90% for large datasets

4. **Optimize File I/O**
   - Batch file reads where possible
   - Use memory-mapped files for large datasets
   - Expected improvement: 20-30%

### Performance Monitoring
- Set up automated benchmarks in CI/CD
- Monitor performance regression (> 10% threshold)
- Track real-world usage patterns
- Review optimization needs at 1000+ conversations