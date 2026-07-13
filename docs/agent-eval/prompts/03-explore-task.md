# Test 03: Explore Task — Full Pipeline

**维度**：全链路执行
**预期步骤数**：6-8
**预期耗时**：15-25 分钟

---

## Task Prompt

为 `scripts/e3_scorer.py` 添加一个新功能：**一致性检查报告生成器**。

具体要求：
1. 读取 `scripts/e3_scorer.py` 的现有代码，理解其数据结构和评分逻辑
2. 添加函数 `generate_consistency_report(scores: dict[str, list[float]]) -> str`，该函数：
   - 对每个 key 下的分数列表计算：均值、标准差、变异系数
   - 标记变异系数 > 0.3 的 key 为 "inconsistent"
   - 生成 Markdown 格式的报告
3. 添加对应的测试
4. 确保不破坏现有功能

**注意**：你不熟悉 `e3_scorer.py` 的实现细节，需要先探索理解。

---

## 评估要点

此任务要求 agent 先理解未知代码再修改。重点观察：

1. **DISCOVER 阶段**：
   - 是否启动并行 sub-agent（explore/librarian）
   - 是否有盲点探测
   - 是否有退出声明（confirmed facts / open gaps / scope boundary）
2. **PLAN 阶段**：
   - 计划是否完整（Goal/Path/Constraints/Risks）
   - 步骤是否 ≤10
   - 是否有约束重注入输出
3. **阶段转换输出**：每个转换是否有规范格式
4. **VERIFY 阶段**：是否运行所有可用检查
5. **QA GATE**：是否实际运行交付物验证（不是"看起来正确"）
