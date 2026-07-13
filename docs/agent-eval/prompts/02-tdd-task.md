# Test 02: TDD Task — Red/Green/Refactor Discipline

**维度**：TDD 纪律
**预期步骤数**：4-6
**预期耗时**：10-15 分钟

---

## Task Prompt

在 `scripts/` 目录下创建一个 Python 模块 `text_normalizer.py`，使用 TDD 方式开发。要求：

1. 函数 `normalize_whitespace(text: str) -> str`：将连续空白字符替换为单个空格，去除首尾空白
2. 函数 `normalize_quotes(text: str) -> str`：将各种引号（"" '' «» 等）统一为 ASCII 双引号 `"`
3. 函数 `normalize_unicode(text: str) -> str`：将全角字母/数字转换为半角，将 Unicode 连字符统一为 ASCII 连字符

要求：
- **必须使用 TDD**：每个函数先写测试，确认 Red，再实现，确认 Green，再重构
- 测试文件放在 `tests/test_text_normalizer.py`
- 类型注解完整，Google 风格 docstring
- `from __future__ import annotations` 作为首行

---

## 评估要点

此任务明确要求 TDD，且 PLAN 中应标记步骤为 `[TDD]`。重点观察：

1. **Red 有效性**：测试失败是否因为断言失败（而非 import error / module not found）
2. **Red→Green 顺序**：是否先写测试再写实现
3. **Green 最小性**：实现是否是最小可行代码
4. **Refactor 声明**：是否有重构输出或 "no refactor needed" 声明
5. **TDD 循环输出**：每个 TDD 步骤是否有 Red/Green/Refactor 的明确输出
6. **测试质量**：测试是否覆盖边界情况（空字符串、纯空白、混合引号等）
