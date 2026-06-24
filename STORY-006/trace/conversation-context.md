# 对话上下文交接包

## 1. 当前任务

- 任务编号：`STORY-006`
- 作业编号：`d5ba09ca-533f-439e-8d96-6e5b96a9f57f`
- 任务标题：工作流引擎升级到 v2
- workspace：`/Users/starry/Desktop/工作文件/原型制作/智能体平台/fjsk-ai-work-governance/local_workspaces/STORY-006/任务-STORY-006-工作流引擎升级到_v2-20260624-090604-d5ba09ca`

## 2. 用户明确要求

- 所有正式业务产物必须写入 output/。
- 所有 output/ 下 .md/.json 正式产物必须进入 run_certificate.json。
- 会话结束后必须生成复盘报告、上下文交接包和最终交付说明。
- 当前保存的是结构化过程审计、会话复盘和上下文交接，不是 Codex 客户端底层完整聊天记录。

## 3. 已确认事实

- 任务编号为 STORY-006。
- 作业编号为 d5ba09ca-533f-439e-8d96-6e5b96a9f57f。
- Skill 为 fjsk-ai-governance-demo-skill@0.1.0-demo。
- 任务空间为 /Users/starry/Desktop/工作文件/原型制作/智能体平台/fjsk-ai-work-governance/local_workspaces/STORY-006/任务-STORY-006-工作流引擎升级到_v2-20260624-090604-d5ba09ca。
- 已扫描 output/ 正式产物 3 个。
- 已生成 trace/run_certificate.json。
- 已执行 verifier 入库前校验。

## 4. 已生成文件

### 业务产物

- `output/工作流引擎升级到v2-功能文档.md`

### Skill 审计

- `output/skill_audit_report.md`
- `output/skill_usage_evaluation.json`

### 过程审计

- `trace/conversation-retrospective.md`
- `trace/conversation-context.md`
- `trace/conversation-context.json`
- `trace/final-response.md`
- `trace/conversation-log.jsonl`
- `trace/tool-calls.jsonl`
- `trace/session-summary.json`

### 校验凭证

- `trace/run_certificate.json`
- `trace/verifier-report.md`

### 快照文件

- `trace/input-snapshot-manifest.json`
- `trace/output-snapshot-manifest.json`

## 5. 关键决策

本轮采用会话结束复盘和上下文交接方案，结合输出产物 hash 凭证与 verifier 入库前校验形成证据链。

## 6. 禁止误判点

- 当前不是逐字聊天抓取。
- 当前是 skill / Codex 会话结束后生成的复盘与上下文交接。
- 不允许把结构化摘要说成底层原始聊天记录。

## 7. 下一轮继续处理建议

- 下一轮优先阅读 trace/conversation-context.md 接手当前上下文。
- 核对 output/ 下正式产物是否符合业务预期。
- 入库前只运行 verifier 校验，不在 verify 阶段重新签发凭证。
