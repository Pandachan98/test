# AI Governance CI Gate

This repository includes a GitHub Actions gate for AI work governance.

## What It Checks

- Every `run_certificate.json` in the repository is verified.
- Artifact hashes in the certificate must match the current files.
- Certificate signature must be valid.
- Skill name and Skill version must match the expected governance contract.
- If an `output/` directory contains AI artifacts but no sibling `trace/run_certificate.json`, the check fails.

## Expected Package Shape

Commit each AI work package with this shape:

```text
<task-or-workspace>/
  output/
    demo_prd.md
    skill_audit_report.md
    skill_usage_evaluation.json
  trace/
    run_certificate.json
```

The local demo may also commit the larger `local_workspaces/...` tree. Both
forms are supported as long as the certificate hashes match the committed
artifact files.

## GitHub Branch Protection

To make this a real merge gate, protect `main` and require this status check:

```text
AI Governance Verifier / ai-governance-verifier
```

Without branch protection, the workflow still reports failures, but GitHub will
not block merges automatically.

## Production Secret

The demo verifier uses the local default secret unless `FJSK_TRACE_SECRET` is
set. In production, configure `FJSK_TRACE_SECRET` as a GitHub Actions secret and
make the trace service sign certificates with the same secret.
