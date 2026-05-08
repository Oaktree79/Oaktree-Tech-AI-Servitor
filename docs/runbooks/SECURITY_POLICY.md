# Security Policy

- Never expose the API without TLS and authentication.
- Replace development secrets before deployment.
- Run autonomous workers in Docker/Kubernetes isolation.
- Require approvals for medium/high risk tasks.
- Use a production secret manager.
- Use PostgreSQL for multi-worker environments.
