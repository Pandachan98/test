# Trace 详情报告

- Run ID: `9d6a1cb3-28e7-4175-92f8-59f8536b646d`
- Task ID: `STORY-001`
- Work Type: `prd`
- Skill: `fjsk-ai-governance-demo-skill@0.1.0-demo`
- Status: `completed`
- Started At: `2026-06-22T07:10:59+00:00`
- Ended At: `2026-06-22T07:10:59+00:00`
- Certificate: `demo_repo/requirements/STORY-001/prd/trace/run_certificate.json`

## 事件时间线

| 时间 | 事件 | 摘要 |
| --- | --- | --- |
| `2026-06-22T07:10:59+00:00` | `launcher.start` | {"context_path": "/Users/starry/Desktop/工作文件/原型制作/智能体平台/fjsk-ai-work-governance/demo_repo/requirements/STORY-001/prd/... |
| `2026-06-22T07:10:59+00:00` | `codex_simulator.started` | {"input_dir": "/Users/starry/Desktop/工作文件/原型制作/智能体平台/fjsk-ai-work-governance/demo_repo/requirements/STORY-001/prd/inp... |
| `2026-06-22T07:10:59+00:00` | `codex_simulator.prompt_summary` | {"summary": "Generate a governance-chain demo PRD, Skill audit report, and usage evaluation for a formal AI work run."} |
| `2026-06-22T07:10:59+00:00` | `codex_simulator.completed` | {"artifacts": [{"artifact_id": "0d04ad12-03af-4fb7-9230-ec2bc228368e", "artifact_type": "business", "created_at": "20... |
| `2026-06-22T07:10:59+00:00` | `launcher.finish` | {"requested_certificate_path": "/Users/starry/Desktop/工作文件/原型制作/智能体平台/fjsk-ai-work-governance/demo_repo/requirements/... |

## 登记产物

| 类型 | 路径 | SHA-256 |
| --- | --- | --- |
| `business` | `demo_repo/requirements/STORY-001/prd/output/demo_prd.md` | `742f6f2d0a78c3205ee91be80cded611242156832d843898b024478ea71ca816` |
| `skill_audit` | `demo_repo/requirements/STORY-001/prd/output/skill_audit_report.md` | `e5530183890b7f07dc7ca9053b54169ec080ccb1453551de3a219760c042d481` |
| `usage_evaluation` | `demo_repo/requirements/STORY-001/prd/output/skill_usage_evaluation.json` | `d8c249882ad6a48595bedd33d54bd1ce3396904956d4793872be80ea2dd072c7` |

## Skill 使用质量评估

- Source: `demo_repo/requirements/STORY-001/prd/output/skill_usage_evaluation.json`
- Delivery Readiness: `risk`
- Usage Level: `beginner`
- Quality / 1k Tokens: `5.39`

## 凭证摘要

- Trace Server: `fjsk-local-trace-server-v1`
- Issued At: `2026-06-22T07:10:59+00:00`
- Signature: `a7ad8cbfb4343cbec23571f5d9f3b5e4f6b503419a2a583f1bef822d191dcfa0`
