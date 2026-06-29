# Demo PRD

## Run Metadata

- Run ID: e083f64f-0434-45c8-98f5-cd2eaf64463c
- Task ID: STORY-003
- Skill: fjsk-ai-governance-demo-skill
- Skill Version: 0.1.0-demo
- Synthetic Demo Input: true

## Purpose

This artifact is a lightweight PRD sample for fjsk-ai-work-governance trace and hash verification. It is not a formal business PRD.

## Input Basis

The input directory only contains the task envelope and README. No real business requirement package, field dictionary, workflow screenshot, or production data sample was provided.

Files:
- `README.md`

Excerpt:

```text
## README.md
# AI 作业输入材料
- Task ID: `STORY-003`
- Run ID: `e083f64f-0434-45c8-98f5-cd2eaf64463c`
- Work Type: `prd`
- Task Title: 工时报表 - 合同维度导出
当前目录用于放置本次 Codex / Skill 读取的任务输入材料。
如没有额外业务材料，Demo Skill 会明确标记 synthetic_demo_input=true，不会把技术样例伪装成真实业务输入。
```

## Demo Requirement

The governance demo should prove that an AI work run can produce registered artifacts, expose Skill audit evidence, record user usage quality, and allow later certificate or hash verification.

## Acceptance Criteria

1. The demo PRD, Skill audit report, and usage evaluation JSON are written to the declared output directory.
2. The usage evaluation JSON contains input quality, artifact quality, token productivity, and overall readiness fields.
3. Synthetic validation data is explicitly marked when real input material is not available.
4. The generated content is deterministic for the same command arguments and input files.

## Notes

This document is intentionally small so it can be used as a stable trace-server registration sample. The formal business plan for this run is `工时报表-合同维度导出-PRD.md`.
