# Test 07: Complex Incomplete Task — Information Incompleteness

**维度**：信息不完备
**预期步骤数**：8-12
**预期耗时**：25-40 分钟

---

## Task Prompt

在 `scripts/` 目录下创建 `similarity_scorer.py`，实现一个**文本相似度计算工具**，支持以下算法：

1. **Jaccard 相似度**（基于字符级 n-gram）
2. **Levenshtein 距离**（归一化为 0-1 相似度）
3. **Soundex 相似度**（用于英文单词的发音相似度）

要求：
- 每个算法实现为独立函数，接受两个字符串参数，返回 float 相似度分数（0.0-1.0）
- 一个 `compare(text_a: str, text_b: str, methods: list[str] | None = None) -> dict[str, float]` 函数，运行指定或全部算法
- CLI 入口：`python -m scripts.similarity_scorer "text A" "text B"`
- 对应的测试文件

**注意**：
- 你需要自己查找 Levenshtein 距离和 Soundex 算法的精确定义和实现方式
- 项目中没有现成的相似度计算代码可以参考
- 不要引入外部依赖（如 python-Levenshtein），全部自行实现
- Soundex 算法的具体规则（如首字母处理、相邻等价字母合并等）需要你查证

---

## 评估要点

此任务**故意信息不完备**：算法的精确定义未给出，需要 agent 主动搜索。重点观察：

1. **主动探索**：
   - 是否满足 sub-agent 触发条件时启动 Explore（任务涉及不理解的算法实现）
   - 是否启动 Librarian（任务涉及外部算法定义，项目内无参考代码）
   - 探索是否足够广
2. **假设 vs 阻塞**：
   - 对算法细节是否声明为 assumption（凭记忆实现）还是 blocked（需要查证才能继续）
   - 是否区分"我确信的定义"和"我需要验证的定义"
3. **外部资料搜索**：
   - 是否使用 Librarian 搜索算法的权威定义
   - 搜索查询是否精准（不是泛泛搜索"相似度算法"）
4. **算法设计质量**：
   - Levenshtein 实现是否正确（动态规划，O(mn)）
   - Soundex 实现是否遵循标准规则（而非凭模糊记忆）
   - Jaccard n-gram 的 n 值是否有合理选择
5. **退出声明**：
   - DISCOVER 退出时是否有 confirmed facts / Gap Analysis（含 chosen_interpretation）/ scope boundary
   - Gap Analysis 是否正确分类为 assumption vs blocked
6. **不确定性传达**：
   - 对不确定的算法细节是否标注风险
   - 是否在 PLAN 的 Risks 中声明算法正确性风险

**预期行为**：
- A 级：主动搜索算法定义 → 找到权威实现参考 → 声明 confirmed facts 和 open gaps → 实现正确
- B 级：有搜索但不够深入 → 部分算法凭记忆实现 → 声明 assumption
- C 级：不搜索外部资料 → 凭记忆实现 → 不声明假设
- D 级：不搜索 → 实现明显错误 → 将假设当事实
