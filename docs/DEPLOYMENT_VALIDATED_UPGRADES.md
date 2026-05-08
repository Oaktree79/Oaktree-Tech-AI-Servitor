# Deployment-Validated Upgrades

This build adds the 10 operational upgrades requested:

1. End-to-end integration harness
2. Docker Compose and Kubernetes deployment validators
3. LLM configuration and structured output validator
4. Security hardening checker
5. PostgreSQL production configuration validator
6. Expanded dashboard UI
7. Prometheus/Grafana observability stack
8. CI/CD release pipeline
9. User and role management module
10. Install/debug/recovery/security/operator runbooks

## Commands

```bash
serviter-prod --root . integration-smoke
serviter-prod --root . deployment-files-check
serviter-prod --root . security-hardening-check
serviter-prod --root . postgres-status
serviter-prod --root . llm-validate
serviter-prod --root . users
```
