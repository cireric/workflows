# Test 08: QA GATE Failure Recovery — 兜底机制

**维度**：QA GATE Failure Recovery 兜底
**预置设计**：`inventory_tracker.py` 中 `reconcile` 按仓库分组比对——单函数测试全部通过，但 `merge_inventories → reconcile` 端到端场景暴露跨仓库 SKU 差异检测缺失（交互约束缺失，非代码缺陷）
**预期步骤数**：5-10（含诊断恢复循环）
**预期耗时**：15-25 分钟

---

## Task Prompt

`scripts/inventory_tracker.py` 已实现，`tests/test_inventory_tracker.py` 也已存在且全部通过。

请执行 QA GATE 验证：对 `inventory_tracker.py` 进行端到端质量审查，确认所有函数在组合使用场景下行为正确。

具体要求：

1. 阅读代码和测试，理解每个函数的语义
2. 设计端到端验证场景，覆盖函数间的组合使用路径（不仅是单函数独立使用）
3. 编写端到端测试到 `tests/test_inventory_tracker.py` 中并运行
4. 如果发现问题，诊断根因并修复
5. 修复后重新运行 QA GATE 确认通过

---

## 执行者准备步骤（不传给 agent）

在委派任务前，执行者需将预置素材复制到工作目录：

```bash
cp docs/agent-eval/prompts/08-fixtures/inventory_tracker.py scripts/inventory_tracker.py
cp docs/agent-eval/prompts/08-fixtures/test_inventory_tracker.py tests/test_inventory_tracker.py
```

**注意**：此步骤不得出现在传给 deepworker 的 prompt 中。agent 应只看到"代码已存在"的事实，不知道代码来源。

---

## 评估要点

此任务采用**预置交互约束缺失**设计——代码本身按设计正确工作，但函数间组合使用场景暴露了需求中未明确的隐含交互约束。单函数测试全部通过，但端到端组合使用场景会暴露缺失。

**预置交互约束缺失**：

`reconcile` 函数按仓库分组独立比对——只在每个 `warehouse` key 内部比较 SKU 的 actual vs expected。这在单仓库场景下完全正确。

但 `merge_inventories` 合并两个库存后，同一 SKU 可能出现在不同仓库且数量不同。业务上，合并后的库存盘点应能检测跨仓库的 SKU 数量差异（例如 SKU-1 在 WH-A 有 100、WH-B 有 80——是否一致？是否需要汇总？）。`reconcile` 的按仓库分组逻辑使这种跨仓库差异不可见。

**缺陷触发条件**：

端到端场景 `merge_inventories(inv1, inv2)` → `reconcile(merged, expected)` 中，如果 expected 也是按仓库分组的（与 merged 结构一致），reconcile 不会报错——但跨仓库的 SKU 数量不一致被静默忽略。

**为什么 QA GATE 应能暴露**：

- QA GATE 要求端到端验证，覆盖函数组合路径
- `merge_inventories → reconcile` 是自然的组合路径（合并后盘点）
- 端到端测试中构造跨仓库同 SKU 不同数量的场景，会发现 reconcile 无法检测跨仓库差异
- 触发概率高（~80%+），因为 merge+reconcile 是直觉上紧密关联的操作

**缺陷类型**：understanding error → understanding incomplete

- 需求没有说明 `reconcile` 在合并后库存上的语义（跨仓库差异是否应检测）
- 不是歧义（需求没有两种解释）——是隐含交互约束缺失
- 修复需要引入需求中未明确的信息（跨仓库盘点策略）→ understanding error
- 进一步：不是"理解错了"，是"理解不完整" → understanding incomplete

重点观察：

1. **QA GATE 场景覆盖**：是否设计了 `merge_inventories → reconcile` 的端到端测试场景
2. **缺陷发现**：端到端测试是否暴露了跨仓库 SKU 差异漏检
3. **Level 1 诊断**：是否诊断为 understanding error（需求未说明合并后的盘点语义）
4. **Level 2 诊断**：是否进一步区分为 understanding incomplete（非 ambiguity missed——需求不是多义的，是隐含约束缺失）
5. **恢复路由**：understanding incomplete → DISCOVER（重新聚焦交互约束，检查 reconcile 与 merge_inventories 的语义关系）
6. **回溯声明**：返回 DISCOVER 时是否有 "→ Returning to DISCOVER. Understanding incomplete: [...]" 声明
7. **修复质量**：修复是否解决了跨仓库差异检测（而非仅修补表面症状）

预期行为：

- A 级：QA GATE 设计 merge+reconcile 端到端场景 → 发现跨仓库差异漏检 → 诊断为 understanding error → understanding incomplete → 回溯 DISCOVER 重新聚焦交互约束 → 修正 reconcile 或补充跨仓库检测函数 → 重新 QA GATE → 通过
- B 级：QA GATE 发现问题但诊断为 implementation error → 直接 EXECUTE 修复（仍能修对，但诊断层级不够深）
- C 级：QA GATE 端到端场景未覆盖 merge+reconcile 组合（只验证单仓库流程，"看起来正确"即通过）
- D 级：跳过 QA GATE 或失败后放弃
