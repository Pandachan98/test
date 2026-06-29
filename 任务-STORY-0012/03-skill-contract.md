# Skill 合同

- Skill 名称：`fjsk-ai-governance-demo-skill`
- Skill 版本：`0.1.0-demo`
- 输入目录：`input/`
- 正式产物目录：`output/`
- 过程记录目录：`trace/`

## 必交付文件

- `output/skill_audit_report.md`
- `output/skill_usage_evaluation.json`

## 动态业务产物

业务产物按当前任务主题生成，不固定为 demo 文件名。示例：

- `output/<业务主题>-PRD.md`
- `output/<业务主题>-测试用例.md`
- `output/<业务主题>-设计说明.md`

所有 `output/` 下 `.md` / `.json` 正式产物都会被登记进 `trace/run_certificate.json` 并计算 SHA256。

## 签发后审计文件

- `trace/skill-invocation.json`
- `trace/conversation-retrospective.md`
- `trace/conversation-context.md`
- `trace/conversation-context.json`
- `trace/final-response.md`
- `trace/conversation-log.jsonl`
- `trace/tool-calls.jsonl`
- `trace/session-summary.json`
- `trace/input-snapshot-manifest.json`
- `trace/output-snapshot-manifest.json`
- `trace/run_certificate.json`
- `trace/verifier-report.json`
- `trace/verifier-report.md`

## 入库前校验

`apps/verifier/verify_ai_run.py` 会重新计算当前产物 hash，并和 `run_certificate.json` 中登记的 hash 对比。任何产物或凭证被手动改动，都必须在入库前被拦截。
