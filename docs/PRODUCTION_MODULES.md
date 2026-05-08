# Production Modules Integration

This build adds the 10 requested production-readiness modules:

1. Real LLM provider runtime
2. Hardened isolation manager
3. Web dashboard scaffold
4. GitHub/GitLab PR automation
5. Secrets manager abstraction
6. Kubernetes deployment tester
7. Distributed worker cluster scaffold
8. Observability and Prometheus metrics
9. OIDC/SSO configuration scaffold
10. Network policy checker

## CLI

```bash
serviter-prod --root . llm-status
serviter-prod --root . isolation-status
serviter-prod --root . worker-run-once
serviter-prod --root . metrics
serviter-prod --root . network-check https://github.com
serviter-prod --root . oidc-status
```

## Dashboard

Serve `web-dashboard/index.html` through any static web server, then connect it to the API server.

## Metrics

The API server exposes:

```text
GET /metrics
```

Prometheus can scrape this endpoint.
