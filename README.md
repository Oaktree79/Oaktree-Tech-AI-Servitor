# AI Serviter Closed-Loop Autonomous Build

This build integrates the previous autonomous scaffold plus all 9 additional autonomy upgrades.

## 9 added upgrades

1. **Real LLM execution loop**
   - `ClosedLoopCodingAgent`
   - structured JSON patch parser
   - patch → test → security scan → rollback/repair loop

2. **Hardened sandbox scaffold**
   - `DockerSandbox`
   - network disabled by default
   - memory and PID limits
   - dropped Linux capabilities

3. **Policy engine**
   - path allowlists/blocklists
   - risk scoring
   - auto-apply thresholds

4. **Observation loop**
   - file observer service mode
   - automatically submits tasks when watched files change

5. **Self-correction loop**
   - repair wrapper for failed test/security output

6. **Production auth additions**
   - RBAC permissions
   - audit log module

7. **Deployment hardening**
   - Kubernetes manifests
   - secret examples
   - backup script

8. **Human override controls**
   - pause/resume system
   - cancel task support

9. **Git integration**
   - status/diff
   - branch creation
   - commit all
   - PR command instructions

## Quick start

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"

python -m pytest -q
serviter . analyze
serviter . submit "analyze project"
serviter . run-once
```

## API server

```bash
export SERVITER_ADMIN_PASSWORD="change-me"
serviter-service --root . --mode api --host 127.0.0.1 --port 8765
```

## Worker

```bash
serviter-service --root . --mode worker
```

## Observer

```bash
serviter-service --root . --mode observer
```

## Closed-loop behavior

By default the LLM provider is dry-run, so it will not create real edits. To enable real model patching, configure an OpenAI-compatible provider and require structured JSON output:

```json
{
  "summary": "what changed",
  "edits": [
    {
      "path": "relative/file.py",
      "after": "complete file content"
    }
  ],
  "test_command": ["python", "-m", "pytest", "-q"]
}
```

## Safety

This is now a closed-loop autonomous scaffold, but production use still requires:
- a real secret manager
- hardened worker isolation
- network egress policy
- human approvals for medium/high risk changes
- monitoring and backups


## ISO / VM / Installer Packaging Integration

The uploaded solution architecture was integrated as an installer-media module.

Create an ISO tree:

```bash
cd python
serviter .. create-iso-tree --out ../AI_SERVITER_ISO --name "AI Serviter"
```

Build an ISO if an ISO builder is installed:

```bash
serviter .. build-iso --tree ../AI_SERVITER_ISO --out ../AI_SERVITER.iso
```

Optional GUI:

```bash
python -m pip install -e ".[gui]"
serviter-gui
```

See `docs/ISO_OS_INTEGRATION.md`.

Note: this is a Rufus-readable installer/data ISO scaffold. A true bootable OS ISO requires a bootloader and OS image.


## Certificate Inventory Integration

This build now includes certificate CSV inventory management.

```bash
cd python
serviter .. cert-report ../data/certificates.csv
serviter .. cert-import ../data/certificates.csv
serviter .. cert-search ../data/certificates.csv example
```

API:
- `GET /certificates/latest`
- `POST /certificates/import`


## Production Modules

This build includes the 10 requested production modules.

```bash
cd python
serviter-prod --root . llm-status
serviter-prod --root . isolation-status
serviter-prod --root . metrics
serviter-prod --root . network-check https://github.com
```

See `docs/PRODUCTION_MODULES.md`.


## Deployment-Validated Operational Upgrades

This build adds the final 10 operational modules.

```bash
cd python
serviter-prod --root . integration-smoke
serviter-prod --root . deployment-files-check
serviter-prod --root . security-hardening-check
serviter-prod --root . postgres-status
serviter-prod --root . llm-validate
```

Runbooks are in `docs/runbooks/`.


## Final Validation Modules

```bash
cd python
serviter-final --root .. deployment-check
serviter-final --root .. defaults-scan
serviter-final --root .. security-review
serviter-final --root .. full-workflow "analyze project"
serviter-final --root .. backup-create
```

See `docs/FINAL_VALIDATION_UPGRADES.md`.


## One-Click Installer Productization

```bash
bash installer/linux/install_one_click.sh
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File installer\windows\install_one_click.ps1
```

See `docs/ONE_CLICK_INSTALLER.md`.
