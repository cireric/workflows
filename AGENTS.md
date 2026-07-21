# AGENTS.md — Project Rules

**项目上下文**：见 `README.md`（项目概述、工具链、开发命令、目录结构）。

本文档仅包含 agent 必须遵守的硬约束和规范。

## 运行环境约束

- **Python 3.13** — 系统 Python (3.9) 不满足版本要求，Makefile 使用 `python3.13` 创建 venv
- **必须使用 venv 虚拟环境** — 禁止全局安装依赖，禁止使用系统 Python，禁止在 venv 外运行 Python 脚本

## 编码规范

- 类型注解必须完整 — 禁止 `Any`、`# type: ignore`
- 错误处理必须可见 — 禁止空 `except` 块
- 单文件不超过 250 行纯逻辑代码
- 公共函数必须有 Google 风格 docstring
- 使用 `from __future__ import annotations` 作为每个 Python 文件首行
- `open()` 必须显式指定 `encoding="utf-8"` — 平台默认编码不一致
- 测试中创建临时文件使用 `tmp_path` fixture — 不污染项目目录
- TDD: 新模块先创建最小可导入骨架（签名 + `raise NotImplementedError`），再写测试，确保 Behavioral Red

## 约束

- 修改 `agents/` 或 `skills/` 下的 Markdown 文件后，运行 `make test` 确认结构测试通过

## Agent skills

### Issue tracker

Issues tracked as local markdown files under `.scratch/<feature>/`. No remote issue tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles using default label strings. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
