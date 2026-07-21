# workflows

AI Agent 工作流项目——设计自定义 agents / skills / commands 的 Python 脚本驱动框架。

## 运行环境

- **Python 3.13** — 系统 Python (3.9) 不满足版本要求，Makefile 使用 `python3.13` 创建 venv
- **必须使用 venv 虚拟环境** — 激活方式：`source .venv/bin/activate` 或通过 Makefile

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

- 类型注解完整 — 禁止 `Any`、`# type: ignore`
- 错误处理可见 — 禁止空 `except` 块
- 单文件不超过 250 行纯逻辑代码
- 公共函数必须有 Google 风格 docstring
- `from __future__ import annotations` 作为每个 Python 文件首行
- TDD: 新模块先创建最小可导入骨架（签名 + `raise NotImplementedError`），再写测试，确保 Behavioral Red
