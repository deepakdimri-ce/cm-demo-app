# Acme Multi-Tenant Invoice Service (`cm-demo-app`)

Sample Python 3 multi-tenant invoice microservice used to demonstrate **Google Cloud CodeMender (`cm`)** end-to-end:

- **`src/invoice_service.py`** — Multi-tenant SQLite invoice lookup & template loader API.
- **`tests/test_invoice_service.py`** — Offline unit test suite (`python3 -m unittest discover -s tests -v`).
- **`demo_exploit_check.py`** — Live verification script showing before/after exploitability.
- **`.codemender/command_policy.yaml`** — Project-level command policy denylist.
- **`hooks/pre-commit`** — Local Git pre-commit delta security gate (`cm find . --diff --staged`).
- **`.github/workflows/codemender.yml`** — GitHub Actions Pull Request diff scan, SARIF Code Scanning upload, and automated Fix-PR workflow powered by keyless Workload Identity Federation.

## Quick Commands

```bash
# 1. Run unit tests
python3 -m unittest discover -s tests -v

# 2. Check live exploitability (Before vs After patching)
PYTHONPATH=. python3 demo_exploit_check.py

# 3. Scan, verify, and patch with CodeMender
cm health --strict
cm find ./src
cm report
cm verify <FINDING_ID> -y
cm fix <FINDING_ID> -y
cm vcs diff
```
