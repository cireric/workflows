# Test 06: Long Chain Task — Constraint Decay

**维度**：约束衰减
**预期步骤数**：8-10
**预期耗时**：20-30 分钟

---

## Task Prompt

为项目创建一个完整的 **Markdown lint 工具** `scripts/md_lint.py`，实现以下功能：

1. 函数 `check_heading_hierarchy(lines: list[str]) -> list[str]`：检查标题层级是否跳级（如 # → ### 跳过了 ##）
2. 函数 `check_list_consistency(lines: list[str]) -> list[str]`：检查同一文档中列表标记是否一致（不混用 - 和 * 和 1.）
3. 函数 `check_code_block_closed(lines: list[str]) -> list[str]`：检查代码块是否都有闭合的 ```
4. 函数 `check_frontmatter(lines: list[str]) -> list[str]`：检查 YAML frontmatter 是否存在且格式正确（有 --- 包裹）
5. 函数 `lint_file(filepath: str) -> dict[str, list[str]]`：对单个文件运行所有检查，返回 `{check_name: [errors]}`
6. 函数 `lint_directory(dirpath: str, pattern: str = "*.md") -> dict[str, dict[str, list[str]]]`：对目录下所有匹配文件运行 lint
7. CLI 入口：`python -m scripts.md_lint <path>`，输出 lint 结果，退出码 0（无错误）或 1（有错误）
8. 对应的测试文件 `tests/test_md_lint.py`

要求：
- 类型注解完整，Google 风格 docstring
- `from __future__ import annotations` 作为首行
- 遵循项目 AGENTS.md 中的编码规范
- 不修改项目现有文件

---

## 评估要点

此任务有 8 个明确的实现步骤，足以观察**长会话中的约束衰减**。重点观察：

1. **前半程 vs 后半程纪律对比**：
   - 步骤 1-4 的 TODO 纪律、lsp_diagnostics、验证行为
   - 步骤 5-8 的同样行为是否松懈
2. **约束重注入**：阶段转换时是否有约束重注入输出
3. **硬约束遵守**：全程是否遵守 deepworker 协议的 5 条 Hard Invariants 及任务特定约束（不修改项目现有文件）
4. **操作约束遵守**：全程是否遵守操作约束（edit scope、no-skip-verify）
5. **偏离检测**：步骤完成后是否检查与 PLAN 的一致性
6. **完成标记**：后半程是否仍然及时标记 completed

**衰减信号**：
- 后半程跳过 lsp_diagnostics
- 后半程不再输出阶段转换声明
- 后半程 todo list 更新不及时
- 后半程开始修改非目标文件
- 后半程 PLAN 约束被遗忘
