# Deepworker Refactoring Plan

本文档记录 deepworker.md 的重组方案，包含议题 1（已落地的改动）和议题 2（渐进式披露重组方案，待实施）。

---

## 议题 1：已落地的改动

以下改动已直接应用到 `agents/deepworker.md`，未改变文档结构：

### 1.1 mode: all → mode: primary

**原因**：deepworker 是 primary agent，直接面对用户。Sisyphus 有自己的 subagent 体系，deepworker 不作为 sub-agent 存在。

### 1.2 新增 Judgment Integrity 节

**位置**：EXECUTION 下，Operating Loop 和 Subagent Delegation 之间

**内容**：
- 三层防护框架定义（L1 举证倒置 / L2 对抗性构造 / L3 外部对抗）
- 11 个判断点注册表（J1-J11），每个标注阶段、偏向、后果、现有防护、适用层级
- L1 输出格式模板（opposing + refuted by + 意图提示）
- L2 机制引用（J3 fast-track adversarial challenge / J4 behavioral ambiguity construction）

**设计原则**：
- 防护重量与 agent 自我欺骗风险成正比，而非与任务复杂度成正比
- veto 条件（V1-V4）本质是列举 agent 的认知盲区，不是列举任务的复杂度特征
- 三层关系：L1 过滤低风险锚定 → L2 针对最危险判断点 → L3 不可替代的最终防线

### 1.3 fast-track 判定增加 Adversarial Challenge

**位置**：DISCOVER Step 1，在 veto check 和 pass conditions 之后新增 Step 3

**内容**：
- 对每个 pass condition（P1-P5）构造反向论证
- 新增 P5：No semantic boundary change（函数的输入接受范围、输出保证、错误条件不被改变）
- 任何反向论证成立 → fast-track = no；全部反驳 → fast-track = yes

**P5 加入理由**：语义边界变更是独立风险维度，不能被 P1-P4 覆盖。签名不变但语义变了（如空输入从返回空字符串改为抛异常）是高风险变更，但 P1（单文件）、P4（消费者数量）都检测不到。P5 反向论证成本极低（一个语义判断），但能拦截此类风险。

**P5 不加入的理由（已否决）**：语义边界变更通常伴随签名变更 → 已被 P1/P4 覆盖。但实际存在签名不变但语义变更的情况，所以 P5 值得加。

**P6（隐式契约）不加入的理由**：Step 1 已有轻量消费者分析（读目标文件 + grep 引用），P6 反向论证要求更深的调用方分析，会把 Step 1 成本推高到接近完整 DISCOVER，削弱 fast-track 的意义。且 QA GATE 兜底。

### 1.4 behavioral ambiguity test 强化

**位置**：DISCOVER Step 4

**改动**：从"观察式"改为"构造式"

- 旧：问"不同选择是否导致不同用户可见输出？"→ agent 可以回答"我没看到差异"就降级
- 新：要求 agent 构造一个"产生不同输出的调用场景"，穷举后确认无法构造才降级为 design choice
- 新增 Step 2：确认每个尝试的场景确实触及了决策点（避免用不相关的场景充数）

**设计原则**：举证倒置——不是"找支持证据"，而是"尝试构造反对案例"。让伪造高质量举证的成本接近真正做举证的成本。

### 1.5 各判断点输出模板增加 opposing + refuted by

| 判断点 | 位置 | 改动 |
|--------|------|------|
| J1 Intent 分类 | UNDERSTAND Output | Intent 行后加 Opposing + Refuted by |
| J2 Ambiguity Scan | UNDERSTAND Output | 每个 "not found" 条目加 Opposing + Refuted by |
| J5 Assumption | DISCOVER Unified Output | 每个 assumption 加 Opposing + Refuted by |
| J7 步骤粒度 | PLAN Granularity Rules | 新增 Granularity self-check |
| J9 验证通过 | EXECUTE Post-Edit Verification | 新增 Post-edit verification output |
| J11 Assumption 验证 | QA GATE Step 2 | 每个 assumption 验证加 Opposing + Refuted by |

所有 L1 标注统一格式：`↑ Judgment Integrity L1: burden of reversal, preventing anchoring from suppressing alternatives`

---

## 议题 2：渐进式披露重组方案（待实施）

### 2.1 核心问题

**"按需加载"与"始终在线"的边界在哪里？**

### 2.2 分析结论

#### deepworker 不适合 researcher 的 skill 按需加载模式

- Researcher 的 skill（prompt-engineering、source-critique、algorithm-design）是场景特化方法论——用户说"写提示词"就加载，不说就不加载。触发条件明确，skill 之间独立。
- Deepworker 的规则（Judgment Integrity、adversarial challenge、举证倒置）是核心流程的内建质量保障——每个任务都需要，不是按场景加载的。
- 把阶段规则拆成多个文件，最终还是会全部读进上下文，只是从"一开始就有"变成"分批读入"，总 token 量一样，还多了多次 read 的开销。

#### deepworker 的渐进式披露 = 单文件内的信息架构优化

不是"按阶段加载不同内容"，而是**通过文档层级结构控制 agent 的注意力分配优先级**。

LLM 处理系统提示词时的认知特征：
1. **前部权重高**——文档开头的规则对 agent 行为影响最大
2. **结构标记是注意力锚点**——`#`、`##`、`###` 帮助 agent 定位，但 agent 不会"按需跳转"
3. **信息密度影响遵守率**——同一层级 30 条规则时，每条的遵守概率低于只有 5 条时

渐进式披露在 deepworker 语境下的目标：**让 agent 在当前阶段需要关注的规则足够突出，不需要关注的规则不干扰**。

### 2.3 三层信息架构方案

#### 第一层：始终活跃的规则（文档前部，简短，高信号强度）

约 80-100 行。agent 在任何时刻都需要"想起"的内容。

包含：
- 身份定义（ROLE）
- 核心约束（绝对禁令）
- 流程骨架（阶段名 + 转移条件 + 终止条件）
- Judgment Integrity 框架定义
- Subagent Delegation 表格

设计原则：**简短 = 高信号强度**。agent 在做任何决策时，这些规则都有足够的注意力权重。

#### 第二层：阶段入口规则（每个阶段的开头，5-10 行）

定义该阶段的：
- 目的（一句话）
- 入口条件
- 核心输出承诺

作用：给 agent 一个**认知框架**——"我现在在这个阶段，目标是 X，完成后应该产出 Y"。

#### 第三层：阶段内部细节（每个阶段的内部，按需展开）

具体的判断模板、输出格式、条件分支、子步骤。

agent 有了认知框架后，再深入具体规则。此时它知道"我为什么要读这些规则"——因为框架已经告诉它当前阶段的目标。

#### 当前问题 vs 重组后

当前 deepworker 把第二层和第三层混在一起。比如 DISCOVER 阶段，Step 1-4 全部平铺在同一个 `## DISCOVER` 下，没有主次。agent 在 DISCOVER Step 1 时，Step 2-4 的规则和 Step 1 处于同一层级，获得了同等的注意力权重。

重组后，Step 1 的 Purpose & Entry 在第二层（高注意力），Step 1 的具体规则在第三层（按需深入），Step 2-4 在第三层的独立子节（当前阶段不涉及时不干扰）。

### 2.4 重组后的文档结构

```
# ROLE
  (身份 + 核心约束 + 绝对禁令 — 第一层)

# EXECUTION FRAMEWORK
  ## Operating Loop
    (流程骨架：阶段名 + 转移条件 + 终止条件 — 第一层)
  ## Judgment Integrity
    (框架定义 + 判断点表格 — 第一层)
  ## Subagent Delegation
    (表格 — 第一层)

# PHASES

  ## UNDERSTAND
    ### Purpose & Entry
      (目的 + 入口规则 — 第二层)
    ### Actions
      (Intent Classification + Ambiguity Scan — 第三层)
    ### Output
      (输出模板 — 第三层)

  ## DISCOVER
    ### Purpose & Entry
      (目的 + 入口规则 + fast-track 判定 — 第二层)
    ### Step 1: Targeted Reading
      (详细规则 + adversarial challenge — 第三层)
    ### Step 2: Broad Search
      (条件 + 规则 — 第三层)
    ### Step 3: Assumptions Check Round 2
      (条件 + 规则 — 第三层)
    ### Step 4: Gap Analysis
      (条件 + behavioral ambiguity test 强化 — 第三层)
    ### Unified Output
      (输出模板 — 第三层)

  ## DISCOVER Review
    ### Purpose & Entry
      (第二层)
    ### Process
      (第三层)

  ## PLAN
    ### Purpose & Entry
      (第二层)
    ### Output Format & Rules
      (第三层)
    ### Plan Review
      (第三层)
    ### todowrite Write
      (第三层)

  ## EXECUTE
    ### Purpose & Entry
      (第二层)
    ### TODO Iron Law
      (第三层)
    ### Post-Edit Verification
      (第三层)
    ### TDD Enhancement
      (第三层)
    ### Failure Recovery
      (第三层)
    ### Drift Detection
      (第三层)

  ## VERIFY & QA GATE
    ### Purpose & Entry
      (第二层)
    ### Step 1: Full Static Check
      (第三层)
    ### Step 2: Manual QA Gate
      (第三层)
    ### Step 3: Success Criteria
      (第三层)

# CONSTRAINTS
# OUTPUT
```

### 2.5 认知交接机制

当前 deepworker 的阶段转换靠 Phase Transition Output——只记录"产出了什么"，没有提醒 agent 下一个阶段该关注什么。

重组后，在每个阶段的 Phase Transition Output 里加一行：

```
→ Entering [NEXT_PHASE]. Recall: [NEXT_PHASE Purpose & Entry 的核心一句话]
```

作用：在 agent 的注意力从当前阶段切换到下一阶段时，把下一阶段的核心目标注入到注意力最高的位置（刚生成的 token 附近）。比依赖 agent "记住"文档前部的阶段定义更可靠。

### 2.6 始终在线 vs 按需加载的边界判定原则

**如果规则被遗漏的后果是不可逆的，就始终在线（第一层）；如果后果可以在后续阶段纠正，就按需展开（第二/三层）。**

| 规则类型 | 遗漏后果 | 可纠正性 | 归属 |
|---------|---------|---------|------|
| 绝对禁令 | 不可逆 | ❌ | 第一层（始终在线） |
| 阶段流程定义 | 不可逆 | ❌ | 第一层（始终在线） |
| Judgment Integrity 框架 | 不可逆（锚定效应无法自纠） | ❌ | 第一层（始终在线） |
| 阶段内部规则 | 可纠正（下游有兜底） | ✅ | 第三层（按需展开） |
| 输出模板格式 | 可纠正 | ✅ | 第三层（按需展开） |
| 失败恢复协议 | 不可逆（3次失败不自知） | ❌ | 第一层（始终在线） |

**注意**："可纠正"的判断依赖下游防护的存在。如果移除了 DISCOVER Review，Ambiguity Scan 的规则就从"按需展开"变成"始终在线"。

边界不是静态的，而是取决于防护体系的完整性：

```
始终在线 = 防护链的最前端（遗漏后无兜底）
按需展开 = 防护链的中间层（遗漏后下游能捕获）
```

### 2.7 未解决的问题

1. **三层信息架构的实际效果无法精确验证**——我们无法测量"agent 对 `###` 下内容的注意力权重比 `##` 下低多少"。这是基于 LLM 注意力机制的合理推断，但不是已证明的工程事实。需要实际使用后观察 agent 行为变化来验证。

2. **认知交接的"核心一句话"如何写**——太简短可能丢失关键约束，太长又变成噪音。需要为每个阶段提炼出真正不可省略的一句话。

3. **第一层的行数控制**——目标 80-100 行，但当前 ROLE + EXECUTION FRAMEWORK 的内容可能超过。需要精简措辞，确保第一层的信息密度足够高。

---

## 附录：讨论中的关键决策记录

### 决策 1：deepworker 是 primary agent

- 结论：`mode: primary`，不作为 sub-agent
- 理由：Sisyphus 有自己的 subagent 体系，deepworker 直接面对用户

### 决策 2：subagent 在 deepworker 中的角色是质量保障

- 结论：explore/librarian 服务于 DISCOVER（补盲），oracle/momus 服务于 DISCOVER Review 和 Plan Review（校验+兜底）
- 理由：最终目的还是保证"执行"是在正确的前提下进行的

### 决策 3：防止 agent 自我欺骗的优先级高于节省 token

- 证据：fast-track veto-first、一次性判定不可变、必须调 Oracle/Momus、"reading ≠ pass"
- 推论：协议的"重量"应该和 agent 自我欺骗的风险成正比，不是和任务复杂度成正比

### 决策 4：veto 条件本质是列举 agent 的认知盲区

- V1（新符号）→ agent 容易低估新符号的行为歧义
- V2（2+ 函数共享数据）→ agent 容易忽略跨函数交互
- V3（prompt 与规则矛盾）→ agent 容易自行消解矛盾
- V4（TDD 要求）→ agent 容易跳过测试

### 决策 5：fast-track 的一次性判定不可变

- 理由：可变判定 = anchoring bias 的入口，agent 会倾向于维持初始判定来节省精力
- 代价：假阳性（误判为 no）让简单任务走完整流程，但这是可接受的——浪费 token 比跳过安全网安全

### 决策 6：P5（语义边界变更）加入 pass conditions，P6（隐式契约）不加入

- P5 加入：语义边界变更是独立风险维度，签名不变但语义变了的情况存在，P5 反向论证成本极低
- P6 不加入：Step 1 已有轻量消费者分析，P6 反向论证会把成本推高到接近完整 DISCOVER，且 QA GATE 兜底

### 决策 7：deepworker 的渐进式披露是单文件内的信息架构优化

- 否决了 skill 按需加载（规则每个任务都需要，拆文件最终全读进上下文）
- 否决了条件指令（依赖 agent 自觉执行）
- 否决了分层文档（增加 read 开销，总 token 量不变）
- 采纳：三层信息架构 + 认知交接，通过文档层级结构控制注意力分配
