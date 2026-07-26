# ADR 0010: Deepworker 前置/后置防护边界——R6/R7 盲区修复

## Status

Proposed

## Context

### 问题起源

Deepworker v2（`deepworker-refactoring.md`）为降低 token 成本，从 v1 中删除了多项前置防护机制：

| 删除的机制 | v1 中的定位 | 覆盖风险 |
|---|---|---|
| ORACLE ATTACK 独立阶段 | 对 UNDERSTAND + DISCOVER 结论的对抗性审查 | R6/R7 |
| Gap Analysis | 逐 deliverable 分解：prompt 指定了什么、未指定什么 | R6 |
| End-to-End Scenario | ≥2 函数必须声明消费者视角的端到端调用链 | R7 |
| Backward transitions 到 UNDERSTAND/DISCOVER | QA GATE 发现理解错误后系统性回退 | R6/R7 |
| 模式表逐项声明 | 5 个模式独立声明结果 | R5 |

v2 的设计理由（L56）："Full-phase redo has extreme token cost."

### Test 09 实测结果

使用 v2 协议执行 Test 09（隐式歧义发现），结果：

| 检查项 | 得分 | 原因 |
|---|---|---|
| 行为歧义发现 | D（0/2） | 协议无发现路径 |
| 约束冲突识别 | D | 未在 UNDERSTAND flag |
| Oracle Attack | N/A | v2 无此阶段 |
| 回问行为 | D | 上游依赖——0/2 歧义未识别 |
| 假设管理 | C | 行为歧义被降级为假设 |
| 歧义深度分析 | D | 0 识别 = 0 分析 |

A 级在 v2 下结构性不可达。

### 根因分析

v2 的核心设计选择是**后置防护优先**（轻流程重 QA）——前端轻量快速，靠 QA 阶段兜底。但对以下两类风险，后置防护无效：

| 风险 | 定义 | 后置防护为何无效 | Test 覆盖 |
|---|---|---|---|
| R6 隐式歧义 | 参数/返回值语义空间 > prompt 使用上下文 | 实现不失败，QA 测试基于错误理解，测试通过但行为错误 | Test 09 |
| R7 交互约束缺失 | 跨函数组合语义不一致，单函数测试通过 | agent 不会设计测试验证自己没意识到的组合 | Test 05/08 |

此外，v2 的 fast-track 机制与 R6/R7 的存在条件重合——隐式歧义恰恰出现在"表面简单"的任务中，而 fast-track 跳过了深度检查。

### 风险分类（完整）

| 风险 | 后置防护 | 根因 | v2 覆盖 |
|---|---|---|---|
| R1 实现错误 | ✅ | 能力不足 | ✅ |
| R2 约束衰减 | ✅ | 记忆衰减 | ✅ |
| R3 显式歧义 | ✅ | 信息不足 | ✅ |
| R4 协议不作为 | ⚠️ | 省力倾向 | ⚠️ |
| R5 约束冲突 | ⚠️ | 信息矛盾 | ❌（逐项声明被简化） |
| R6 隐式歧义 | ❌ | 理解不完整 | ❌（Gap Analysis 被删除） |
| R7 交互约束缺失 | ❌ | 理解不完整 | ❌（Oracle Attack 被删除） |

R4（不作为）是 R6/R7 的放大器——agent 跳过 Gap Analysis / Deep Ambiguity Scan / Oracle Attack，等于前置防护形同虚设。

## Decision

### 设计原则：混合防护，风险分级触发

核心思路：**前置防护覆盖后置防护的盲区（R6/R7），后置防护覆盖前置防护的遗漏（R1/R2），两者通过 fast-track 条件分级触发**。

- 前置防护的触发条件 = 非 fast-track 任务（由 D1 的 7 个条件判定）
- 后置防护的深度 = 与前置防护对齐（fast-track 轻量，非 fast-track 完整）

### D1: fast-track 条件修正

在 v2 现有 5 个条件基础上增加第 7 项：

```
7. No new function/class creation (all steps modify existing code)
```

**理由**：R6 只出现在新创建的函数中——现有函数的行为已由代码隐含指定。此条件语言无关（所有语言都有"创建新可调用单元"的概念），零推理成本（读 PLAN step 列表即可判定），且不作为风险低（二元事实，可审计）。

现有条件 4（"No cross-function shared concepts"）已覆盖 R7。条件 7 补充覆盖 R6。

### D2: 前置防护恢复与强化

#### D2.1: DISCOVER Review（新增，替代 v1 ORACLE ATTACK）

- **触发条件**：非 fast-track 任务（从 D1 继承，零额外判定成本）
- **提交内容**：UNDERSTAND Exit Declaration + DISCOVER Unified Output
- **Oracle prompt**：v1 的 5 项挑战模板（understanding errors / missed ambiguities / invalid assumptions / unverified constraints / cross-stage inconsistencies）
- **最大轮数**：3 轮
- **发现问题**：incrementally supplement（不 full-phase redo）
- **命名**：DISCOVER Review（非 "Oracle Attack"——核心作用是审查，不是攻击）

**与 v1 ORACLE ATTACK 的区别**：
- v1 对所有任务强制执行；本方案仅对非 fast-track 任务触发
- v1 允许回退到 UNDERSTAND/DISCOVER；本方案改为增量补充（降低 token 成本）

#### D2.2: Gap Analysis 精简版（恢复）

```
For each deliverable (function/class to implement):
  1. What does the prompt explicitly specify? (list concrete specifications)
  2. What decisions must be made that the prompt does NOT specify?
     → One obvious default → assumption with chosen_interpretation
     → Multiple plausible options → flag as ambiguity (follows Evaluation rule)
```

对比 v1 完整版删除了：
- Step 0（Deliverable decomposition + shared concept marking）——与 DISCOVER Step 3 cross-function 检查重叠
- Step 3（Include Deep Ambiguity Scan findings）——合并了
- "upgrade to ambiguity" 详细流程——直接引用 Evaluation rule

**触发条件**：非 fast-track 任务

#### D2.3: End-to-End Scenario（不恢复）

R7 已被 Gap Analysis + Deep Ambiguity Scan cross-function + DISCOVER Review 覆盖。End-to-End Scenario 的增量价值有限，不增加机制 = 不增加 R4 攻击面。

#### D2.4: 模式表逐项声明（恢复）

UNDERSTAND Exit Declaration 从 v2 的 `Ambiguity: [none | list]` 改为：

```
Ambiguity scan:
- Vague verb: [found: [term] → action | not found]
- Undefined target: [found: [term] → action | not found]
- Open-ended scope: [found: [term] → action | not found]
- Missing constraint: [found: [what] → assumption | not found]
- Internal contradiction: [found: [what] → flag | not found]
```

**理由**：逐项声明使不作为可审计，且 R5（约束冲突）直接被 Internal contradiction 模式覆盖。成本极低（~60-130 tokens）。

### D3: 后置防护对齐

| 任务类型 | QA GATE 设计 |
|---|---|
| 非 fast-track | Step 1 静态检查 + Step 2 完整 QA Gate（surface + assumption 逐项验证 + combination path）+ Step 3 Success Criteria |
| fast-track | Step 1 静态检查 + happy path 验证 |

#### 非 fast-track QA GATE Failure Recovery

| 问题类型 | 路由 |
|---|---|
| 具体理解错误（单点问题） | Oracle consult + 就地修复 + Post-fix reflection |
| 系统性理解错误 | → DISCOVER Review（增量补充，非 full-phase redo） |
| 实现错误 | → EXECUTE |
| 测试错误 | → 修复验证 → re-run |
| 环境问题 | → 修复环境 → re-run |

Post-fix reflection：修复行为是 prompt 未指定的 → 声明新 assumption + verify（不回退 DISCOVER，前置防护已提供发现机会）。

### D4: 不作为抑制

核心思路：**增加不作为成本，使省力倾向消失**。

#### Gap Analysis 参数级问题序列

```
For each deliverable:
  1. Prompt specifies: [list]
  2. For each parameter: what input space does the type/semantics allow?
     What subset does the prompt's usage context use?
     Is there a gap? → If yes, what should happen for inputs in the gap?
  3. Unspecified decisions: [list from step 2 + any others]
  4. For each decision: one obvious default → assumption | multiple options → flag
```

步骤 2 的"对于每个参数"是结构化的——agent 不能跳过任何参数。这使得"跳过 Gap Analysis"的成本从"写 none"（零成本）变为"对每个参数编造 reasoning"（高成本）。

#### QA GATE assumption 验证 evidence 要求

每个 assumption 验证必须附带 evidence（命令输出或测试名），使"声明 verified 但没运行"变成谎报——可审计。

### D5: Backward Transitions

在 v2 的 3 条基础上增加 2 条：

| # | Trigger | Path | 理由 |
|---|---|---|---|
| 1 | Single-step verification fails | Fix in-place | = v2 |
| 2 | 3 methods all fail | Oracle consult | = v2 |
| 3 | Still fails after Oracle | Ask user | = v2 |
| **4** | **PLAN discovers information gap** | **→ DISCOVER** | **信息缺口不应降级为 assumption** |
| **5** | **No PLAN before first edit** | **→ PLAN** | **安全网，防止无计划执行** |

不恢复的 v1 路径：
- DISCOVER → UNDERSTAND：增量补充已覆盖
- DISCOVER Review → UNDERSTAND/DISCOVER：增量补充覆盖 90%；极端情况 record as unresolved risk
- EXECUTE(stall) → DISCOVER：Three-Attempt Protocol + 就地阅读已覆盖
- QA GATE → VERIFY：合并设计已覆盖
- QA GATE → UNDERSTAND/DISCOVER：D3 已决定用 DISCOVER Review / Oracle consult 替代

## Alternatives Considered

### 纯前置防护（v1 方案）

所有任务走完整流程，包括 ORACLE ATTACK、完整 Gap Analysis、End-to-End Scenario、6 条 backward transitions。

**优点**：R6/R7 覆盖率最高。
**缺点**：token 成本高；ORACLE ATTACK 对简单任务浪费；full-phase backward transitions 成本极高；R4（不作为）风险仍存在——agent 可以形式化勾选。
**结论**：过度防护。简单任务不应承担复杂任务的成本。

### 纯后置防护（v2 方案）

轻量前置 + 完整 QA 兜底。

**优点**：token 成本最低。
**缺点**：R6/R7 盲区——后置防护无法发现"理解正确但不完整"的问题；fast-track 与隐式歧义条件重合。
**结论**：不够安全。R6/R7 是不可逆风险——缺陷代码可能通过 QA 被交付。

### 无分级混合防护（方案 C，被否决）

所有任务都跑 DISCOVER Review，但 Review 深度分级（full / light）。

**优点**：100% 覆盖率。
**缺点**："深度分级"的判定引入新的 R4 攻击面——agent 倾向于判定 light。且 light Review 的触发条件（低风险任务）恰好等于 fast-track 条件，实际等价于方案 B。
**结论**：假性分级。触发条件与 fast-track 重叠，light Review 的中间态不存在。

### 条件 7 基于"宽语义类型"（str/dict/Any）

用参数类型特征判定 R6 风险。

**优点**：粒度细，误判率低。
**缺点**：语言特化——`str`/`dict`/`Any` 是 Python 类型系统的特征，不适用于 Go/Rust/TypeScript/C 等。协议应语言无关。
**结论**：不可接受。协议不能绑定特定语言。

### 恢复 End-to-End Scenario

PLAN 中 ≥2 函数必须声明端到端调用链和消费者期望。

**优点**：增加消费者视角，可能发现交互约束缺失。
**缺点**：R7 已被 Gap Analysis + Deep Ambiguity Scan cross-function + DISCOVER Review 覆盖；增量价值有限；每增加一个必须执行的机制，增加一个 R4 攻击面。
**结论**：不恢复。ROI 不足。

### 恢复 full-phase backward transitions

DISCOVER Review 发现问题 → 回退 UNDERSTAND/DISCOVER 全阶段重做。

**优点**：系统性重扫描可能发现其他遗漏。
**缺点**：token 成本极高（full-phase redo）；90% 的场景只需要增量补充。
**结论**：不恢复。增量补充 + DISCOVER Review 重跑已足够。

## Consequences

### Token 成本变化

| 任务类型 | v1 | v2 | 新方案 | 对比 |
|---|---|---|---|---|
| fast-track | ~2650 | ~420 | ~550 | 比 v2 多 ~130（逐项声明），比 v1 省 ~2100 |
| 非 fast-track | ~2950 | ~720 | ~2950 | 与 v1 持平，但 backward transitions 成本更低（增量补充替代 full-phase redo） |

### 对现有 ADR 的影响

| ADR | 影响 |
|---|---|
| ADR 0007 | 混合架构的边界被重新定义——前置防护覆盖后置防护的盲区，而非"全面前置"或"全面后置" |
| ADR 0008 | 信任光谱中 DISCOVER Review 属于"不可逆，偏指令跟随"（与 DISCOVER 一致） |
| ADR 0009 | PLAN → DISCOVER 回退路径恢复，与"PLAN 不可逆"的定位一致——信息缺口不应降级为 assumption |

### 后续观察点

1. **D1 条件 7 的过度覆盖**：Test 01/02 类简单创建任务也被纳入非 fast-track，多跑 Gap Analysis + DISCOVER Review。观察这些任务的实际 Review 输出——如果 Review 一致说 "no challenges"，考虑对"单函数 + ≤3 步 + 无宽语义参数"的创建任务进一步分级。
2. **Gap Analysis 参数级问题序列的有效性**：观察 agent 是否真正推理"输入空间 vs 使用上下文"的差集，还是形式化回答。如果形式化回答比例高，考虑增加最低推理深度要求。
3. **DISCOVER Review 的 Oracle 模型依赖**：Review 的效果依赖 Oracle 模型的推理深度。跨模型测试时需评估 Oracle 的挑战质量。
4. **R4 抑制措施的长期效果**：逐项声明 + 参数级问题序列 + evidence 要求是否真正提高了不作为成本，还是 agent 找到了新的形式化路径。
5. **fast-track 任务的 R5 覆盖**：fast-track 任务只有逐项声明覆盖 R5（无 DISCOVER Review）。观察 fast-track 任务中约束冲突的发现率——如果发现率低，考虑 fast-track 也保留 Gap Analysis 精简版。
