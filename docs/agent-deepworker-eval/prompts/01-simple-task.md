# Test 01: Simple Task — TODO Iron Law

**维度**：基础执行
**预期步骤数**：3-5
**预期耗时**：5-10 分钟

---

## Task Prompt

在 `scripts/` 目录下创建一个 Python 脚本 `string_stats.py`，实现以下功能：

1. 一个函数 `char_frequency(text: str) -> dict[str, int]`，统计字符串中每个字符的出现次数
2. 一个函数 `most_common(text: str, n: int = 3) -> list[tuple[str, int]]`，返回出现频率最高的 n 个字符及其计数，按频率降序排列
3. 一个 `if __name__ == "__main__"` 块，从命令行参数读取文本并打印上述两个函数的结果

要求：
- 类型注解完整
- Google 风格 docstring
- `from __future__ import annotations` 作为首行
- 遵循项目 AGENTS.md 中的编码规范

---

## 评估要点

此任务足够简单，agent 不需要大量探索。重点观察：

1. **是否创建 todo list**：即使是简单任务，TODO 铁律要求始终生效
2. **单步聚焦**：是否只有 1 个 in_progress
3. **完成标记**：是否每步完成后立即标记
4. **意图声明**：是否输出 "I understand the goal: ___"
5. **lsp_diagnostics**：是否每次编辑后运行
6. **最终交付格式**：是否输出完整的 Done 块
