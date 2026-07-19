# Security & Hardening Policy

## Overview
This document outlines the security measures, rate limiting, and optimization strategies employed within the AI Storytelling Workspace API and Frontend.

## Backend Security (FastAPI)

### Rate Limiting
- A custom IP-based `RateLimitMiddleware` has been added to prevent API abuse.
- By default, requests are limited to 100 requests per minute per IP.
- The AI Provider API calls also utilize a token bucket rate limiter in `core/rate_limiter.py` to prevent runaway costs from upstream LLM services (e.g., OpenAI, Anthropic).

### Cross-Origin Resource Sharing (CORS)
- Removed custom unsafe CORS headers middleware.
- Only utilizing FastAPI's official `CORSMiddleware` with explicit configuration bound by environment variables (`CORS_ORIGINS`).

### Injection Prevention
- All database interactions use SQLAlchemy ORM or the `session.execute` pattern with parameterized queries, preventing SQL injection natively.

## Performance Optimizations

### N+1 Query Fixes
- `get_project_stats` API has been optimized to execute SQL aggregations (`func.count`, `func.sum`) directly at the database level rather than fetching nested related rows or returning placeholders.

### Frontend (Angular)
- Bundle sizes are constrained by Angular CLI budgets (Warning: 500kB, Error: 1MB).
- Strict AOT and Optimization are utilized.
- Component lazy-loading is natively implemented (`app.routes.ts` uses `loadChildren`).
