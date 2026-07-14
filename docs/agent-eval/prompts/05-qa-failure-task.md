# Test 05: QA Failure Task — Failure Recovery

**维度**：失败恢复
**预期步骤数**：6-10（含恢复循环）
**预期耗时**：15-25 分钟

---

## Task Prompt

在 `scripts/` 目录下创建 `time_range.py`，实现时间范围计算工具：

1. 函数 `parse_time(s: str) -> tuple[int, int]`：解析时间字符串为 `(hours, minutes)` 元组
   - 接受格式：`"HH:MM"`（24 小时制），如 `"09:30"` → `(9, 30)`
   - 无效格式抛出 `ValueError`
2. 函数 `format_time(t: tuple[int, int]) -> str`：将 `(hours, minutes)` 元组格式化为字符串
   - 输出格式：`"HH:MM"`（24 小时制，零填充），如 `(9, 30)` → `"09:30"`
3. 函数 `time_diff(start: str, end: str) -> str`：计算两个时间之间的差值
   - 返回格式：`"Xh Ym"`，如 `time_diff("09:00", "11:30")` → `"2h 30m"`
4. 函数 `add_minutes(time: str, minutes: int) -> str`：在给定时间上增加分钟数
   - 跨日自动回绕（如 23:00 + 120min → 01:00），如 `add_minutes("22:30", 90)` → `"00:00"`

要求：
- 类型注解完整，Google 风格 docstring
- `from __future__ import annotations` 作为首行
- 添加对应的测试文件 `tests/test_time_range.py`

---

## 评估要点

此任务设计了一个**运行时类型不匹配陷阱**——需求本身在函数间引入了类型矛盾：

**隐藏陷阱——`add_minutes` 需要处理跨日回绕，但 `parse_time` 返回的 `(hours, minutes)` 元组无法表达跨日信息**：

1. Agent 按需求字面实现后，`add_minutes` 内部会调用 `parse_time` 得到 `(hours, minutes)`，加上分钟数后得到新的 `(hours, minutes)`
2. 跨日回绕计算：`hours = (hours + extra_hours) % 24` — 这在逻辑上正确
3. **但 QA GATE 会发现一个问题**：`add_minutes` 内部将 `parse_time` 返回的 `(22, 30)` 加 90 分钟后，得到 `(0, 0)`，然后调用 `format_time((0, 0))` 得到 `"00:00"` — 这**看起来**正确
4. **真正的陷阱**：当 `add_minutes` 的结果需要再传给 `time_diff` 时，`time_diff` 期望的是同一天内的时间差。`time_diff("22:30", "00:00")` 按简单实现会得到 `"-22h 30m"` 而非 `"1h 30m"`——因为 `parse_time("00:00")` 得到 `(0, 0)`，而 `parse_time("22:30")` 得到 `(22, 30)`，简单减法得到负数

**为什么这个陷阱更可靠**：

1. **会导致运行时错误/错误输出**：`time_diff("22:30", "00:00")` 返回负值或异常，不是"语义不够好"而是"功能直接出错"
2. **不依赖 agent 遗漏边界情况**：即使 agent 考虑了跨日回绕，也很可能只在 `add_minutes` 中处理，而不会意识到 `time_diff` 也需要处理跨日场景
3. **触发路径自然**：QA GATE 的 surface verification 会尝试所有函数的组合使用，自然会调用 `time_diff` 与 `add_minutes` 的组合
4. **失败类型是 understanding error**：agent 按需求分别实现了每个函数，但需求没有说明 `time_diff` 需要处理跨日场景——这是对需求理解不完整，不是实现 bug

重点观察：

1. **QA GATE 失败是否被检测**：agent 是否在 surface verification 中测试了 `time_diff` 与 `add_minutes` 的组合
2. **失败诊断**：是否诊断为 understanding error（需求未说明跨日场景，但函数间组合使用时暴露了问题）而非 implementation error
3. **恢复路由**：understanding error → DISCOVER（重新理解需求，认识到函数间的隐含交互约束）而非直接 EXECUTE
4. **回溯声明**：如果返回 DISCOVER，是否有 "→ Returning to DISCOVER" 声明
5. **安全网**：如果修复后仍不满意，是否升级到 Oracle/用户

**预期行为**：
- A 级：QA GATE 测试 `time_diff("22:30", "00:00")` → 发现负值/错误 → 诊断为 understanding error → 回溯到 DISCOVER → 认识到 `time_diff` 需要处理跨日场景 → 修复 → 重新 QA GATE → 通过
- B 级：QA GATE 发现问题但诊断为 implementation error → 直接 EXECUTE 修复（添加跨日处理）→ 仍能修复
- C 级：QA GATE 未测试 `time_diff` 与 `add_minutes` 的组合（"看起来正确"即通过），或发现后无诊断直接重试
- D 级：跳过 QA GATE 或失败后放弃
