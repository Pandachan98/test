# Demo PRD

## Run Metadata

- Run ID: dc1d4cfd-b4ba-4a4d-93f7-99887272de45
- Task ID: STORY-001
- Skill: fjsk-ai-governance-demo-skill
- Skill Version: 0.1.0-demo
- Synthetic Demo Input: true

## Purpose

This artifact is a lightweight PRD sample for fjsk-ai-work-governance trace and hash verification. It is not a formal business PRD.

## Input Basis

The current workspace contains only task-space scaffolding and no real business input package, so this run is treated as a marked technical validation sample.

Files:
- `README.md` (task-space scaffold only; not treated as real business input)

Excerpt:

```text
## synthetic_demo_request.md
Technical validation sample: generate a PRD artifact for "驾驶舱车辆图层实时刷新" and keep the output clearly marked as synthetic demo input because no real business materials were provided in input/.
```

## Demo Requirement

The governance demo should prove that an AI work run can produce registered artifacts, expose Skill audit evidence, record user usage quality, and allow later certificate or hash verification.

## Acceptance Criteria

1. The demo PRD, Skill audit report, and usage evaluation JSON are written to the declared output directory.
2. The usage evaluation JSON contains input quality, artifact quality, token productivity, and overall readiness fields.
3. Synthetic validation data is explicitly marked when real input material is not available.
4. The generated content is deterministic for the same command arguments and input files.

## Notes

This document is intentionally small so it can be used as a stable trace-server registration sample.
