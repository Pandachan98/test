# Codex 执行说明

你正在处理丰匠 AI 作业治理 Demo 的正式任务空间。

请按顺序执行：

1. 先阅读 `00-task-fingerprint.json`，确认 `runId`、`taskId`、`workType`、`outputDir`、`traceDir`。
2. 再阅读 `01-job-context.md`，确认任务背景和目录边界。
3. 使用 `fjsk-ai-governance-demo-skill`，版本口径为 `0.1.0-demo`。
4. 正式产物只写入 `output/`。业务产物可按任务主题命名，例如 `<业务主题>-PRD.md`、`<业务主题>-测试用例.md`、`<业务主题>-设计说明.md`。
5. 过程记录、凭证、校验报告只写入 `trace/`。
6. 不允许跳过审计文件，不允许只生成业务 PRD 而缺少 Skill 审计报告或使用质量评估 JSON。
7. 完成后更新 `04-submit-checklist.md`，把已完成项改为 `[x]`，未完成项保留 `[ ]` 和原因。

## 作业完成后的强制动作

你完成所有 `output/` 产物后，必须调用本地服务签发证据链：

```bash
curl -X POST http://127.0.0.1:8765/api/ai-governance/complete-codex-work \
  -H "Content-Type: application/json" \
  -d '{"runId":"dc1d4cfd-b4ba-4a4d-93f7-99887272de45"}'
```

如果你无法执行 curl，请明确提示用户回到任务系统页面点击：

“完成 Codex 作业并签发凭证”。

未签发凭证前，本次作业不得视为完成。

如需要演示兜底生成，可由页面点击“生成演示产物”，该按钮会通过本地服务调用项目内 Python 脚本完成同一 workspace 的产物、凭证和校验报告生成。
