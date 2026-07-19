# Test 05: Interaction Constraint Identification — PLAN Stage

**维度**：交互约束识别
**预期步骤数**：6-10
**预期耗时**：10-20 分钟

---

## Task Prompt

在 `scripts/` 目录下创建 `file_filter.py`，实现文件过滤工具：

1. 函数 `load_rules(path: str) -> list[dict]`：从 JSON 文件加载过滤规则列表
   - 每条规则: `{"pattern": str, "action": "include"|"exclude"}`
2. 函数 `filter_files(files: list[str], rules: list[dict]) -> list[str]`：返回匹配 include 规则的文件
   - 规则按顺序应用，先匹配到的规则决定文件的命运
3. 函数 `categorize(files: list[str], rules: list[dict]) -> dict[str, list[str]]`：将文件按匹配的 include 规则分组
   - 返回 `{rule_pattern: [matched_files]}`
4. 函数 `summarize(categories: dict[str, list[str]]) -> dict[str, int]`：统计每个分类的文件数量
   - 返回 `{rule_pattern: count}`

要求：
- 类型注解完整，Google 风格 docstring
- `from __future__ import annotations` 作为首行
- 添加对应的测试文件 `tests/test_file_filter.py`

---

## 评估要点

> **维度重叠说明**：`categorize` 的匹配语义未在 prompt 中明确说明（首匹配优先？全匹配？），这本身是一个歧义。维度 5（交互约束识别）评估 agent 是否在 PLAN 阶段识别该语义并推导其与 `filter_files` 的一致性。如果 agent 在 Intent Declaration 的 Ambiguity scan 中识别了该歧义，维度 4（歧义处理）也应给分。两个维度在此测试上存在天然重叠，评分时分别从各自角度评估。

此任务设计了一个**函数间语义不一致陷阱**——`filter_files` 和 `categorize` 对规则匹配顺序的语义不同：

**隐藏陷阱**：
- 提示词中 `filter_files` 的子项说明了"规则按顺序应用，先匹配到的规则决定文件的命运"
- 但 `categorize` 只说"按匹配的 include 规则分组"，未说明匹配语义——agent 需要自己推导
- 自然推导：`categorize` 也会按顺序匹配，一个文件归入第一个匹配的分类
- 陷阱：当规则有 `"*.py" → include` 和 `"test_*.py" → include"` 时，`categorize` 会把 `test_*.py` 归入 `*.py` 分类而非 `test_*.py` 分类（因为 `*.py` 先匹配）
- 但 `filter_files` 中 `"test_*.py" → include` 会先于 `"*.py"` 匹配（如果 `test_*.py` 规则在前），所以两个函数的匹配优先级语义可能不一致
- 用户期望 `test_*.py` 有独立的分类计数，但 `summarize` 的结果与预期不符

**直觉度分析**：
- 显式数据流（rules → filter_files → categorize → summarize）：~90% agent 会推导出
- 语义不一致识别：~30-50% agent 会在 PLAN 阶段识别（提示词未暴露 categorize 匹配语义，需要推理发现）
- 目标直觉度：30-50%，根据测试反馈调整

重点观察：

1. **Deep Ambiguity Scan (cross-function)**：DISCOVER 阶段的 Deep Ambiguity Scan cross-function semantic consistency 检查是否识别了 `filter_files` 与 `categorize` 对匹配顺序的语义不一致
2. **端到端场景声明**：agent 是否在 PLAN Goal 中声明了 `load_rules → filter_files → categorize → summarize` 的端到端场景
3. **交互约束识别**：agent 是否在 PLAN 阶段识别了 `filter_files` 与 `categorize` 对匹配顺序的语义不一致
4. **PLAN 阶段修正**：识别约束后是否在 PLAN 中调整了实现路径或增加了验证步骤
5. **端到端场景质量**：场景是否覆盖了 `filter_files → categorize` 的组合路径（非直觉的组合）
6. **如果未识别**：QA GATE 是否暴露问题，诊断是否正确（understanding error → understanding incomplete）

预期行为：
- A 级：Deep Ambiguity Scan cross-function 检查识别匹配语义不一致 → PLAN Goal 包含完整端到端场景 → 识别交互约束 → 调整实现路径
- B 级：有端到端场景但未识别语义不一致，执行中发现问题并修正
- C 级：端到端场景只覆盖单个函数的独立使用，未识别交互约束
- D 级：无端到端场景声明，从未识别交互约束
