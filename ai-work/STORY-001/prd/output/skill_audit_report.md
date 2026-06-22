# Skill Audit Report

## Run Metadata

- Run ID: 9d6a1cb3-28e7-4175-92f8-59f8536b646d
- Task ID: STORY-001
- Skill: fjsk-ai-governance-demo-skill
- Skill Version: 0.1.0-demo
- Synthetic Demo Input: true

## Audit Scope

This report audits the Demo Skill execution shape for fjsk-ai-work-governance. It checks whether the run produced the required artifacts and whether the input basis is clearly represented.

## Input Materials

- `synthetic_demo_request.md` (30 estimated input tokens)

## Execution Steps

1. Parse command arguments.
2. Read input materials from the input directory in deterministic path order.
3. Fall back to marked technical validation sample content when no real input material is present.
4. Render the demo PRD and audit report.
5. Generate `skill_usage_evaluation.json` with the planned governance metrics.

## Coverage

- Business artifact sample: covered by `demo_prd.md`.
- Skill audit sample: covered by this report.
- Usage quality metrics: covered by `skill_usage_evaluation.json`.
- Synthetic input disclosure: present; synthetic_demo_input=true

## Risks And Follow-Up

- Replace the synthetic sample with real task materials before business review.
- Keep the synthetic marker in all technical validation records.
