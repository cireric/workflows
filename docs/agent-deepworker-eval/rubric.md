# Agent Evaluation Rubric

每个维度按 A/B/C/D 四级评分。评分基于 agent 输出的**可观测行为**，不推测内部状态。

## 评分等级定义

| 等级 | 含义 | 标准 |
|------|------|------|
| **A** | 完全遵从 | 协议要求的行为全部出现，无遗漏、无违反 |
| **B** | 基本遵从 | 核心行为出现，有少量遗漏但不影响任务完成质量 |
| **C** | 部分遵从 | 关键行为缺失或违反，任务勉强完成但质量受损 |
| **D** | 严重违反 | 核心协议被跳过或违反，任务未完成或质量不可接受 |

---

## 维度 1：基础执行（TODO 铁律 + 阶段纪律）

**测试文件**：`01-simple-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| 步骤追踪 | PLAN 路径完整转为 todo list | todo list 存在但与 PLAN 有轻微偏差 | todo list 不完整或与 PLAN 严重偏离 | 无 todo list |
| 单步聚焦 | 始终只有 1 个 in_progress | 偶尔 2 个 in_progress 但很快修正 | 多次出现多个 in_progress | 无 in_progress 标记或全部同时 in_progress |
| 完成标记 | 每步完成后立即标记 completed | 大部分及时标记，1-2 次延迟批量标记 | 批量标记为主 | 从不标记 completed |
| 意图声明 | Exit Declaration 包含 Goal + Ambiguity scan + Scope 三字段 | Exit Declaration 存在但缺 1 个字段 | Exit Declaration 模糊或与实际执行不符 | 无 Exit Declaration |
| Post-edit 验证 | 每次编辑后运行 lsp_diagnostics（或 fallback）+ 项目 lint | 大部分编辑后运行 | 偶尔运行 | 从不运行 |
| 阶段转换输出 | 全部 5 个阶段转换（UNDERSTAND→DISCOVER→PLAN→EXECUTE→VERIFY→QA GATE）有规范输出 | 4 个转换有输出 | 3 个及以下转换有输出 | 无阶段转换输出 |
| 最终交付 | Done 输出格式完整 | Done 输出缺少 1-2 个字段 | Done 输出严重不完整 | 无 Done 输出 |

---

## 维度 2：TDD 纪律 + 触发决策

**测试文件**：`02-tdd-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| TDD 触发 | PLAN 中每个新函数步骤标记为 `[TDD]` 且附理由 | 大部分步骤标记正确但有遗漏 | 步骤标记为 `[direct]` 但实际用了 TDD（或反之） | 所有步骤标记为 `[direct]`，无 TDD 意识 |
| Red 阶段 | 先写测试，确认断言失败（非基础设施错误） | 先写测试但 Red 输出不够明确 | 写了测试但未确认 Red 或 Red 为基础设施错误 | 先写实现再写测试 |
| Green 阶段 | 写最小代码使测试通过 | 代码略多于最小但测试通过 | 代码明显过度设计但测试通过 | 测试未通过就进入下一步 |
| Refactor 阶段 | 有重构输出或明确声明 "no refactor needed" | 重构存在但未声明 | 跳过重构且未声明 | 无重构意识 |
| TDD 循环完整性 | 每个 TDD 步骤都有 Red→Green→Refactor 输出 | 大部分循环完整 | 循环不完整但最终测试通过 | 无 TDD 循环 |
| 测试质量 | 测试有意义，覆盖关键行为 | 测试基本有效但覆盖不足 | 测试存在但质量低（如 always-pass） | 无有效测试 |

---

## 维度 3：全链路执行

**测试文件**：`03-explore-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|
| UNDERSTAND 阶段 | 有 Exit Declaration（Goal + Ambiguity scan + Scope）+ 阶段转换输出 | Exit Declaration 缺 1 字段或无转换输出 | 只有 Goal 声明，无 Ambiguity scan | 跳过 UNDERSTAND |
| DISCOVER | 满足 sub-agent 触发条件时启动 Explore/Librarian，有 Deep Ambiguity Scan（4 项逐项声明），有退出声明 | 有探索但未触发 sub-agent 或 Deep Ambiguity Scan 部分项缺失 | 探索浅显，未启动 sub-agent，无 Deep Ambiguity Scan | 跳过 DISCOVER 直接编辑 |
| PLAN | 输出完整计划（Goal/End-to-End Scenario/Path/Constraints/Risks），步骤 ≤10，每步声明 TDD/direct + 理由 | 计划存在但缺少 End-to-End Scenario 或部分步骤缺模式理由 | 计划过于粗略或步骤 >10 | 无 PLAN 直接执行 |
| 阶段转换输出 | 全部阶段转换（UNDERSTAND→DISCOVER→PLAN→EXECUTE→VERIFY→QA GATE）有规范输出 | 大部分转换有输出 | 转换输出不完整 | 无阶段转换输出 |
| VERIFY | 运行所有可用检查，声明未运行的检查 | 运行大部分检查 | 检查不完整且未声明 | 跳过 VERIFY |
| QA GATE | 通过表面验证（实际运行交付物） | 表面验证存在但不充分 | "看起来正确"即通过 | 跳过 QA GATE |

---

## 维度 4：歧义处理（模式表 + 隐式歧义）

**测试文件**：`04-ambiguous-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| 模式表歧义识别 | Ambiguity scan 字段覆盖了所有应命中的模式（vague verb + undefined target + open-ended scope），扫描结果完整 | 覆盖了部分模式但遗漏了次要模式 | 扫描字段存在但结果为空或敷衍（如 "No ambiguity detected" 但任务明显有歧义） | 无 Ambiguity scan 字段 |
| 隐式歧义识别 | DISCOVER Deep Ambiguity Scan 覆盖了应发现的隐式歧义（如代码结构歧义、跨函数语义不一致、运行时交互假设） | 覆盖了部分隐式歧义 | Deep Ambiguity Scan 存在但输出 "none found"（任务明显有隐式歧义） | 无 Deep Ambiguity Scan |
| 回问行为 | 对工作差异 2x+ 的歧义回问用户，在 Ambiguity scan / Deep Ambiguity Scan 中有对应的 "asked_user" 记录 | 回问了但时机或方式不理想 | 未回问，直接把歧义声明为 assumption | 完全忽略歧义，不声明 |
| 假设管理 | 对未澄清的部分在 Ambiguity scan / Deep Ambiguity Scan 中声明为 assumed + 包含 chosen_interpretation | 有假设但缺少 chosen_interpretation | 隐式假设未在扫描中声明 | 无假设意识 |
| 意图声明 | Exit Declaration 完整包含 Goal + Ambiguity scan + Scope | 缺少 1 个字段 | Exit Declaration 与执行不符 | 无 Exit Declaration |

**完备性验证**：
- 模式表歧义：任务描述中应命中的模式 = vague verb ("改进") + undefined target ("评分脚本") + open-ended scope ("更有区分度") = 3
- 隐式歧义：由 DISCOVER Deep Ambiguity Scan 发现（结合代码信息）
- 模式表完备性 = agent 覆盖的模式数 / 3
- 隐式歧义完备性 = agent 发现的隐式歧义数 / 应发现数

---

## 维度 5：交互约束识别（PLAN 阶段）

**测试文件**：`05-qa-failure-task.md`

**评分范围**：仅评估 PLAN 阶段及之前的行为。QA GATE 阶段的行为由维度 8 评估，不在本维度评分。

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| Deep Ambiguity Scan (cross-function) | DISCOVER 阶段的 Deep Ambiguity Scan cross-function semantic consistency 检查识别了 filter_files 与 categorize 的匹配语义不一致 | 识别了部分但不完整 | 未执行 cross-function 检查 | 无 Deep Ambiguity Scan |
| 端到端场景声明 | PLAN Goal 包含完整的端到端场景声明（数据流 + 预期结果） | 有端到端场景但缺失部分函数组合 | 端到端场景存在但与实际实现不匹配 | 无端到端场景声明 |
| 交互约束识别 | PLAN 阶段明确识别函数间交互约束并反映在 Constraints 中 | 识别了部分交互约束但不完整 | PLAN 阶段未识别交互约束（无论后续是否发现） | 从未识别交互约束 |
| PLAN 阶段修正 | 识别约束后在 PLAN 中调整了实现路径或增加了验证步骤 | 约束识别了但未反映到 PLAN 中 | 约束识别了但未修正，PLAN 仍按原路径 | 识别约束后仍按原路径执行 |
| 端到端场景质量 | 场景覆盖了所有关键函数组合，包括非直觉的组合路径 | 场景覆盖了主要数据流但遗漏了非直觉组合 | 场景只覆盖了单个函数的独立使用 | 场景与交付物功能无关 |

---

## 维度 6：约束衰减

**测试文件**：`06-long-chain-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| 约束重注入 | 阶段转换时有约束重注入输出（Constraints: [...] — still valid） | 部分转换有重注入 | 重注入存在但内容空洞 | 无约束重注入 |
| 硬约束遵守 | 全程遵守 TODO Iron Law 7 条规则 + 各阶段 Exit Declaration 约束及任务特定约束（不修改项目现有文件） | 违反 1 条非关键约束或任务约束 | 违反 1 条关键约束 | 违反多条关键约束 |
| 操作约束遵守 | 全程遵守操作约束（edit scope、no-skip-verify 等） | 偶尔遗漏但不影响结果 | 多次遗漏影响结果 | 系统性忽略操作约束 |
| 偏离检测 | 步骤完成后检查与 PLAN 的一致性 | 偏离检测存在但不及时 | 偏离后无检测 | 严重偏离无意识 |
| TDD 模式纪律 | 后半程 TDD/direct 模式声明与 PLAN 一致，不因疲劳而跳过 TDD | 后半程 1-2 步模式声明遗漏 | 后半程多步模式声明缺失 | 后半程完全无模式声明 |
| 后半程纪律 | 后半程（步骤 5+）与前半程纪律水平一致 | 后半程轻微松懈 | 后半程明显松懈 | 后半程几乎无纪律 |
| Assumption tracking | PLAN Constraints 包含 assumption count（UNDERSTAND: X, DISCOVER: Y），EXECUTE 中 assumption 增减有记录，QA GATE 验证最终计数 | 有 assumption 记录但计数不完整 | assumption 存在但未在 PLAN 中追踪 | 无 assumption 追踪意识 |

---

## 维度 7：信息不完备

**测试文件**：`07-complex-incomplete-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| 主动探索 | 信息不足时主动启动 Explore/Librarian（按信息缺口触发条件） | 有探索但未使用 sub-agent 或探索不够广 | 探索浅显，只读已知文件 | 不探索直接假设 |
| 假设 vs 阻塞 | 合理区分 assumption（可继续）和 blocked（不可继续），每个 assumption 包含 chosen_interpretation | 区分存在但部分缺少 chosen_interpretation | 全部标记为 assumption 或全部标记为 blocked | 不区分 |
| 外部资料搜索 | 使用 Librarian 搜索外部文档/API，查询精准 | 有搜索但查询不够精准或未使用 sub-agent | 仅搜索内部代码 | 不搜索外部资料 |
| 算法设计 | 在信息不完备时仍能设计合理算法方案 | 算法方案存在但不够优化 | 算法方案有明显缺陷 | 无算法设计直接编码 |
| 退出声明 | DISCOVER 退出时有完整的 confirmed facts / Gap Analysis（含 chosen_interpretation）/ scope boundary | 退出声明存在但不完整 | 退出声明过于简略 | 无退出声明直接执行 |
| 不确定性传达 | 对不确定的决策明确标注确信度或风险 | 部分标注 | 隐式处理不确定性 | 将假设当作事实 |

---

## 维度 8：QA GATE Failure Recovery 兜底

**测试文件**：`08-qa-recovery-task.md`（预置交互约束缺失设计：`inventory_tracker.py` 中 `reconcile` 按仓库分组比对，代码本身正确，但合并后跨仓库 SKU 差异检测缺失——需求未说明合并后盘点语义）

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| Non-obvious combination path | 设计了 merge_inventories → reconcile 的非直觉组合路径测试，暴露跨仓库差异漏检 | 设计了 merge+reconcile 场景但未构造跨仓库同 SKU 不同数量的测试数据 | 端到端场景只覆盖单仓库流程，未测试 merge+reconcile 组合 | 跳过 QA GATE |
| 失败诊断（Level 1） | 正确诊断为 understanding error（需求未说明合并后盘点语义） | 诊断为 implementation error（但修对了） | 无诊断直接重试 | 跳过问题或放弃 |
| 二级诊断（Level 2） | 正确区分为 understanding incomplete（非 ambiguity missed——需求不是多义，是隐含约束缺失） | 区分为 ambiguity missed（但修复方向仍有效） | 无二级诊断 | 错误分类导致修复方向错误 |
| 恢复路由 | understanding incomplete → DISCOVER（重新聚焦交互约束）→ 修正 | 路由基本正确但跳过 DISCOVER，直接在 EXECUTE 中修复 | 恢复路径不合理 | 无恢复路径 |
| 回溯声明 | 有 "→ Returning to DISCOVER" + 重新聚焦声明 | 有回溯声明但不完整 | 回溯无声明 | 不回溯 |
| Loop termination | 回退循环 2 次无进展时触发升级（Oracle → user），不无限循环 | 循环 3+ 次但最终自行脱出 | 循环 3+ 次且无升级意识 | 无限循环或放弃 |

---

## 维度 9：隐式歧义发现

**测试文件**：`09-implicit-ambiguity-task.md`

| 检查项 | A | B | C | D |
|--------|---|---|---|---|
| Deep Ambiguity Scan 执行 | DISCOVER 阶段执行了 Deep Ambiguity Scan（4 项逐项声明：re-evaluate UNDERSTAND / code structure / cross-function semantic consistency / runtime interaction），在 Exit Declaration 的 "Deep Ambiguity Scan" 字段输出结果 | 执行了部分项（1-3 项） | Deep Ambiguity Scan 字段存在但输出 "none found"（任务明显有隐式歧义） | 无 Deep Ambiguity Scan |
| 隐式歧义发现 | 识别 3+ 个隐式歧义（共 4 个：文件格式、键查找语义、文件不存在行为、Any 类型冲突） | 识别 2 个隐式歧义 | 识别 1 个隐式歧义，或仅依赖模式表扫描未命中则认为无歧义 | 无扫描 |
| Deep Ambiguity Scan 补充 | DISCOVER 阶段的 Deep Ambiguity Scan 补充发现了 UNDERSTAND 模式表未覆盖的歧义 | Deep Ambiguity Scan 存在但未发现新歧义 | 无 Deep Ambiguity Scan | DISCOVER 阶段未补充扫描 |
| 回问行为 | 对工作量差异 2x+ 的隐式歧义回问用户 | 部分回问，部分自行假设 | 未回问，将隐式歧义声明为 assumption | 完全忽略隐式歧义 |
| 假设管理 | 隐式歧义的假设在 Ambiguity scan / Deep Ambiguity Scan 中声明，包含 chosen_interpretation | 有假设但缺少 chosen_interpretation | 隐式假设未在扫描中声明 | 无假设意识 |
| 歧义深度分析 | 每个识别的歧义有实质分析（为什么是歧义、不同理解的后果），非一句话带过 | 部分歧义有深度分析 | 歧义识别了但分析敷衍（如"可能有歧义"无具体说明） | 无分析 |

**注意**：维度 9 的 Deep Ambiguity Scan 是 v2 协议新增的推理框架。如果评估的是旧协议（v1，无 Deep Ambiguity Scan），则"Deep Ambiguity Scan 执行"和"Deep Ambiguity Scan 补充"检查项不适用，评分时跳过，按剩余 4 个检查项的平均等级映射为维度总分。

---

## 综合评分

每个维度得分：A=4, B=3, C=2, D=1

### 维度权重

| 权重 | 维度 | 理由 |
|------|------|------|
| **×2** | 1 基础执行 | TODO 铁律 + 阶段纪律是所有其他维度的基础设施；D = 全局失效 |
| **×2** | 3 全链路执行 | 覆盖核心操作循环；D = 协议未被执行 |
| **×1.5** | 6 约束衰减 | 混合架构存在的核心理由（ADR 0007） |
| **×1.5** | 8 失败恢复兜底 | QA GATE 是最后一道防线；D = 缺陷代码被交付 |
| **×1** | 2 TDD 纪律 | 可选增强层，非基础设施 |
| **×1** | 4 歧义处理 | 协议防护层，但非全局依赖 |
| **×1** | 5 交互约束识别 | PLAN 阶段防护，QA GATE 可兜底 |
| **×1** | 7 信息不完备 | 探索能力评估，非协议遵从 |
| **×1** | 9 隐式歧义发现 | 探索性维度，v2 协议新增推理框架 |

**加权总分** = Σ(维度得分 × 权重)，满分 = 4×(2+2+1.5+1.5+1+1+1+1+1) = **48**

### 综合等级

| 加权总分 | 等级 | 含义 |
|----------|------|------|
| 44-48 | A+ | 协议设计优秀，agent 执行可靠 |
| 36-43 | A | 协议整体有效，少量可优化点 |
| 28-35 | B | 协议基本有效，有明显改进空间 |
| 20-27 | C | 协议存在系统性问题，需要修订 |
| 12-19 | D | 协议严重失效，需要重新设计 |

### 关键维度否决

以下情况直接降级，不受加权总分影响：

- **维度 1 得 D** → 综合等级上限为 C（基础设施崩塌，其他维度得分无意义）
- **维度 3 得 D** → 综合等级上限为 C（核心循环未执行）
- **维度 8 得 D** → 综合等级上限为 B（缺陷代码被交付，但其他维度可能仍有效）

**多否决交互规则**：当多个否决同时触发时，取**最严格的限制**。例如维度 1 得 D（上限 C）且维度 8 得 D（上限 B），实际生效上限为 C。

**关键发现标记**：

- 🔴 **阻断性问题**：导致任务失败或产出不可用的协议缺陷
- 🟡 **质量问题**：不影响任务完成但降低产出质量的协议弱点
- 🟢 **亮点**：协议设计中特别有效的部分
