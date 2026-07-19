# Test 03: Explore Task — Full Pipeline

**维度**：全链路执行
**预期步骤数**：6-8
**预期耗时**：15-25 分钟

---

## Task Prompt

`scripts/e3_scorer.py` 已实现。请阅读其代码，理解其数据结构和评分逻辑，然后添加一个新功能：**一致性检查报告生成器**。

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

## 执行者准备步骤（不传给 agent）

在委派任务前，执行者需将预置素材复制到工作目录：

```bash
cp docs/agent-deepworker-eval/prompts/03-fixtures/e3_scorer.py scripts/e3_scorer.py
```

**注意**：此步骤不得出现在传给 deepworker 的 prompt 中。agent 应只看到"代码已存在"的事实，不知道代码来源。

---

## 评估要点

此任务要求 agent 先理解未知代码再修改。重点观察：

1. **UNDERSTAND 阶段**：
   - Exit Declaration 是否包含 Goal + Ambiguity scan + Scope
   - 是否有阶段转换输出
2. **DISCOVER 阶段**：
   - 是否满足 sub-agent 触发条件时启动 Explore（任务涉及修改不理解的现有代码）
   - 是否有 Deep Ambiguity Scan（4 项逐项声明：re-evaluate / code structure / cross-function / runtime）
   - 是否有退出声明（confirmed facts / Consumer / Deep Ambiguity Scan / Gap Analysis / Assumptions / Scope / Workspace）
3. **PLAN 阶段**：
   - 计划是否完整（Goal/End-to-End Scenario/Path/Constraints/Risks）
   - 每步是否声明 TDD/direct + 理由
   - 步骤是否 ≤10
4. **阶段转换输出**：全部阶段转换是否有规范格式
5. **VERIFY 阶段**：是否运行所有可用检查
6. **QA GATE**：是否实际运行交付物验证（不是"看起来正确"）
