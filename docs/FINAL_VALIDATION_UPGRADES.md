# Final 7 Validation Upgrades

This build adds:

1. Path-safe deployment checks
2. Real LLM workflow validation harness
3. Docker/Kubernetes trial scripts
4. Development default scanner
5. Security review toolkit
6. Full workflow runner
7. Monitoring and backup validator

## Commands

```bash
serviter-final --root . deployment-check
serviter-final --root . llm-workflow-check
serviter-final --root . defaults-scan
serviter-final --root . security-review
serviter-final --root . full-workflow "analyze project"
serviter-final --root . metrics-check
serviter-final --root . backup-create
```

## Trial scripts

```bash
scripts/trial_docker_compose.sh
scripts/trial_kubernetes.sh
```
