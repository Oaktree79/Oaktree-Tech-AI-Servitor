# Debugging Runbook

1. Check service health: `GET /health`
2. Check metrics: `GET /metrics`
3. Check task list: `serviter . tasks`
4. Run one worker cycle: `serviter . run-once`
5. Inspect SQLite DB: `.serviter/serviter.db`
6. Run production checks: `serviter-prod --root . llm-status`
