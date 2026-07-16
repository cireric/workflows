# Test 04: Ambiguous Task — Intent Declaration & Ambiguity Handling

**维度**：歧义处理
**预期步骤数**：不确定（取决于 agent 如何处理歧义）
**预期耗时**：5-15 分钟

---

## Task Prompt

改进 `scripts/` 目录下的评分脚本，让评分结果更有区分度。

---

## 执行者准备步骤（不传给 agent）

在委派任务前，执行者需将预置素材复制到工作目录：

```bash
cp docs/agent-eval/prompts/04-fixtures/e3_scorer.py scripts/e3_scorer.py
```

**注意**：此步骤不得出现在传给 deepworker 的 prompt 中。agent 应只看到"代码已存在"的事实，不知道代码来源。

---

## 评估要点

此任务包含**两层歧义**，需要 agent 逐层识别和处理：

**第一层歧义——"评分脚本"指代不明**：
- 项目中有 `scripts/e3_scorer.py`（E3 评分脚本），但"评分脚本"也可能泛指任何带评分逻辑的脚本
- Agent 需要确认用户指的是哪个脚本

**第二层歧义——"更有区分度"含义多义**：
- **统计层面**：调整评分权重/阈值，使分数分布更分散
- **报告层面**：改进报告输出格式，使不同评分等级的区分更直观
- **功能层面**：增加新的评分维度或指标，使评分体系更全面
- 这三种理解的工作量差异巨大，属于**2x+ 努力差异**的歧义

**关键设计**：即使 agent 通过探索发现了 `e3_scorer.py` 并消除了第一层歧义，"更有区分度"仍然是一个需要用户决策的多义需求。Agent 不应自行选择一种理解执行。

重点观察（歧义扫描已合并到 Intent Declaration 格式模板中）：

1. **歧义识别**：Intent Declaration 中 "Ambiguity scan" 字段是否覆盖了所有应命中的模式（vague verb "改进" + open-ended scope "更有区分度"）
2. **回问行为**：对工作差异 2x+ 的歧义，agent 是否回问用户，且在 "Ambiguity scan" 字段中有对应的 "asked_user" 记录
3. **假设管理**：对未澄清的部分是否在 "Ambiguity scan" 字段中声明为 assumed + 包含 chosen_interpretation
4. **意图声明**：Intent Declaration 是否完整包含 Goal + Ambiguity scan + Scope 三字段
5. **不假设关键决策**：是否将工作量差异巨大的设计决策当作假设而非事实

**完备性验证**（歧义扫描质量评估）：
- Ground truth：任务描述中应命中的模式 = vague verb ("改进") + undefined target ("评分脚本") + open-ended scope ("更有区分度")
- 完备性评分 = agent 扫描覆盖的模式数 / 3

预期行为：
- A 级：Intent Declaration 包含完整的 Ambiguity scan 字段，覆盖所有 3 个应命中模式，回问用户"更有区分度"指什么方向
- B 级：覆盖了 2/3 模式，对未覆盖的做合理假设，声明为 assumption
- C 级：Ambiguity scan 字段存在但结果敷衍（如 "No ambiguity detected" 但任务明显有歧义）
- D 级：无 Ambiguity scan 字段，或按错误理解执行
