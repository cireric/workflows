# AGENTS.md — Project Rules

## 项目概述

Python 脚本驱动的 AI Agent 工作流项目，用于设计自定义 agents / skills / commands。

## 运行环境

- **Python 3.13** — 系统 Python (3.9) 不满足版本要求，Makefile 使用 `python3.13` 创建 venv
- **必须使用 venv 虚拟环境** — 禁止全局安装依赖，禁止使用系统 Python
- 激活方式：`source .venv/bin/activate` 或通过 Makefile（`make install` 自动创建 venv）

## 工具链

| 用途 | 工具 | 配置位置 |
|---|---|---|
| 包管理 / 依赖 | venv + pip | `pyproject.toml` |
| 构建后端 | hatchling | `pyproject.toml [build-system]` |
| Lint + Format | Ruff | `pyproject.toml [tool.ruff]` |
| 类型检查 | mypy (strict) | `pyproject.toml [tool.mypy]` |
| 测试 | pytest + pytest-asyncio | `pyproject.toml [tool.pytest]` |
| Git hooks | pre-commit | `.pre-commit-config.yaml` |
| 任务运行 | Makefile | `Makefile` |

## 开发命令

```bash
make install    # 创建 venv + 安装依赖 + 注册 pre-commit hooks
make lint       # ruff check
make format     # ruff format
make typecheck  # mypy
make test       # pytest
make clean      # 清理 venv 和缓存
```

## 目录结构

```
agents/       # Agent 定义（Markdown）
commands/     # 命令定义
docs/         # 文档、研究笔记、提示词模板
  notes/
  prompts/
  research/
scripts/      # Python 脚本
skills/       # Skill 定义（每个 skill 一个目录，含 SKILL.md）
tests/        # 测试
```

## 编码规范

- 类型注解必须完整 — 禁止 `Any`、`# type: ignore`
- 错误处理必须可见 — 禁止空 `except` 块
- 单文件不超过 250 行纯逻辑代码
- 公共函数必须有 Google 风格 docstring
- 使用 `from __future__ import annotations` 作为每个 Python 文件首行

## 约束

- 禁止在 venv 外运行 Python 脚本
- 禁止提交 `.env` 文件（仅提交 `.env.example`）
- 禁止提交 IDE 配置（`.idea/`、`.vscode/`）
- 修改 `agents/` 或 `skills/` 下的 Markdown 文件后，运行 `make test` 确认结构测试通过

## Agent skills

### Issue tracker

Issues tracked as local markdown files under `.scratch/<feature>/`. No remote issue tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles using default label strings. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
