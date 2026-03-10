# Example Ticket — For Calibration

This is what a good ticket looks like. Match this level of quality, specificity, and conciseness.

---

# API Rate Limiting

## Problem
The public API has no rate limiting. Any client can make unlimited requests, which risks service degradation under load and makes the platform vulnerable to abuse. Multiple customers have reported slow responses during peak hours.

## Approach
Implement token bucket rate limiting at the API gateway level with per-client limits stored in Redis. Use the gateway rather than per-endpoint middleware to avoid duplicating logic across services. Fall back to in-memory limits if Redis is unavailable — degraded rate limiting is better than none.

## Affected Services

| Service | Changes | Impact |
|---------|---------|--------|
| api-gateway | Rate limiting middleware, Redis integration | High |
| auth-service | Expose client tier info for dynamic limits | Low |
| redis | New key namespace for rate limit counters | Low |
| frontend-dashboard | Rate limit usage display for API consumers | Medium |

## Implementation Plan

### 1. api-gateway — Add rate limiting middleware
- **Why:** Centralizing at the gateway means all downstream services are protected without individual changes
- **Where:** `src/middleware/`, `src/config/`
- **What:** Add rate limiting middleware that checks token bucket counters in Redis before forwarding requests. Configure default limits (e.g., 100 req/min) with per-tier overrides. Return 429 with `Retry-After` header when exceeded.
- **Watch out:** Must handle Redis connection failures gracefully — fall back to in-memory counters, not open access

### 2. auth-service — Expose client tier information
- **Why:** Different API clients have different rate limit tiers (free, pro, enterprise). The gateway needs this info to apply the right limits.
- **Where:** `src/services/client-service.ts`, `src/routes/internal/`
- **What:** Add an internal endpoint that returns the rate limit tier for a given API key. Cache responses since tiers change infrequently.
- **Watch out:** This is an internal-only endpoint — must not be exposed publicly

### 3. frontend-dashboard — Usage display
- **Why:** API consumers need visibility into their current usage and limits
- **Where:** `src/pages/api-settings/`, `src/components/`
- **What:** Add a usage section to the API settings page showing current request count, limit, and reset time. Use the `/frontend-design` skill during implementation.
- **Watch out:** Usage data should be near-real-time but doesn't need to be exact — poll every 30s, not websocket

## Integration Points
- Gateway reads client tier from auth-service via internal API (cached)
- Gateway reads/writes rate counters to Redis
- Dashboard reads usage stats from a new gateway endpoint
- Rate limit headers (`X-RateLimit-Remaining`, `X-RateLimit-Reset`) are added to all API responses

## Edge Cases
- Redis goes down: fall back to in-memory token buckets per instance (less accurate but functional)
- Client has no tier assigned: apply default (lowest) tier limits
- Distributed counting: with multiple gateway instances, Redis provides shared state. In-memory fallback means per-instance limits (effectively multiplied by instance count)
- Clock skew between gateway instances: use Redis server time for bucket windows, not local time

## Testing Strategy
- **Unit:** Token bucket algorithm correctness, Redis fallback behavior
- **Integration:** Gateway → Redis → rate limit enforcement, gateway → auth-service tier lookup
- **Load:** Verify limits hold under concurrent requests from multiple clients
- **E2E:** Full flow from API request → 429 response → dashboard shows usage

## Notes
- Consider adding rate limit info to API documentation
- May want webhook notifications when clients approach their limits (future enhancement, not in this ticket)
