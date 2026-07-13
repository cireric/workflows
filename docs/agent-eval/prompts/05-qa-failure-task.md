# Test 05: QA Failure Task — Failure Recovery

**维度**：失败恢复
**预期步骤数**：6-10（含恢复循环）
**预期耗时**：15-25 分钟

---

## Task Prompt

在 `scripts/` 目录下创建 `csv_analyzer.py`，实现以下功能：

1. 函数 `load_csv(filepath: str) -> list[dict[str, str]]`：读取 CSV 文件，返回字典列表（第一行为 header）
2. 函数 `filter_rows(data: list[dict[str, str]], column: str, value: str) -> list[dict[str, str]]`：按列值过滤行
3. 函数 `aggregate(data: list[dict[str, str]], column: str, operation: str) -> float`：对指定列执行聚合操作（sum/avg/min/max）

**隐藏陷阱**：
- `aggregate` 函数需要将字符串值转为 float，但 CSV 数据可能包含非数值——这个边界情况**不在需求中明确说明**
- 正确实现应该处理 `ValueError`，返回有意义的错误或跳过非数值行
- 如果 agent 不处理这个边界情况，QA GATE 的表面验证（用包含非数值的测试数据运行）会失败

---

## 评估要点

此任务设计了一个**隐藏的 QA GATE 失败触发器**。agent 的初始实现很可能不处理非数值边界情况，导致 QA GATE 失败。重点观察：

1. **QA GATE 失败是否被检测**：agent 是否实际运行了交付物（而不是"看起来正确"）
2. **失败诊断**：是否区分 understanding error（需求理解错误）vs implementation error（实现缺陷）
3. **恢复路由**：是否按正确路径恢复（implementation error → EXECUTE）
4. **回溯声明**：如果返回 DISCOVER，是否有 "→ Returning to DISCOVER" 声明
5. **安全网**：如果多次失败，是否升级到 Oracle/用户

**预期行为**：
- A 级：QA GATE 检测到非数值问题 → 诊断为 implementation error → 修复 → 重新 QA GATE → 通过
- B 级：QA GATE 检测到问题但诊断不够精确 → 仍能修复
- C 级：QA GATE 未检测问题（"看起来正确"即通过）或检测后无诊断直接重试
- D 级：跳过 QA GATE 或失败后放弃
