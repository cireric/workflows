# ADR 0008: Deepworker 提示词优化——护栏投放原则与建议修订

## Status

Accepted

## Context

Deepworker agent 在 5 个开发会话中暴露 16 个问题，经 5-Why 分析收敛为 4 个系统性模式：

| 模式               | 问题数 | 根因                                            |
| ------------------ | ------ | ----------------------------------------------- |
| A: DISCOVER 不充分 | 5/16   | DISCOVER 是"读什么"驱动，非"确认什么"驱动       |
| B: 验证走过场      | 5/16   | VERIFY 检查退出码级别，QA GATE 缺乏语义验证标准 |
| C: 知道≠做到       | 4/16   | 规则以原则声明形式存在，缺少可执行检查点        |
| D: Lint 治标不治本 | 2/16   | Lint 被视为通过/不通过的二元门，非诊断工具      |

核心诊断：4 个模式的共同根因是"原则声明 vs 可执行检查点"的落差——规则被声明了，但缺少结构化执行模板使规则可操作化。

参考了 Hephaestus GPT-5.5 提示词（code-yeongyu/oh-my-openagent, commit 9edaa6e9）的设计，但 Deepworker 的目标模型（K2.6/GLM-5.1/V4-Pro）与 GPT-5.5 存在约束衰减差异，不能直接照搬。

## Decision

### 设计原则：不可逆操作的入口加护栏，可逆操作信任模型

- **不可逆操作**：错误理解（DISCOVER）、文件删除、git 破坏性操作、交付缺陷代码（QA GATE）、伪造验证结果、修改规则抑制自己引入的错误
- **可逆操作**：代码编写、PLAN 规划、lint 修复、TDD 流程

不可逆操作偏指令跟随（加结构化护栏），可逆操作偏 Hephaestus（现称偏自主判断，信任模型自主判断）。

### 信任光谱分布

| 阶段/操作 | 可逆性 | 光谱位置 | 理由 | 修正 |
|---|---|---|---|---|
| DISCOVER | 不可逆 | 偏指令跟随 | 错误理解传播到所有下游，修复成本是重做整个任务 | |
| PLAN | 可逆 | 偏 Hephaestus（现称偏自主判断） | 模型规划能力是强项，漂移检测已提供安全网 | **ADR 0009**：重新分类为"不可逆，偏指令跟随"——跳过 PLAN 导致下游全部失去锚点，修复成本 = 重做任务 |
| EXECUTE 常规 | 可逆 | 偏 Hephaestus（现称偏自主判断） | TODO 铁律已提供基础纪律 | |
| EXECUTE 破坏性操作 | 不可逆 | 偏指令跟随 | 删除/git 误操作不可逆 | |
| VERIFY | 可逆 | 中间 | 退出码检查是必要的，但不需要过度结构化 | |
| QA GATE | 不可逆 | 偏指令跟随 | 交付缺陷代码不可逆 | |
| Lint 修复 | 可逆（但隐蔽） | 中间 | 后果可能不被后续测试捕获 | |
| TDD 流程 | 可逆 | 中间 | 后续 QA GATE 可发现 | |

### 修订后建议（7 条）

#### R1: DISCOVER 重构

融合 Hephaestus 追加触发条件 + 缺口探测提示 + 缺口声明退出要求。

关键设计选择：

- 采用 Hephaestus 的"追加搜索触发条件"（4 条）和"停止搜索条件"（3 条）替代原有的"3 consecutive searches"停止条件
- 增加"缺口探测提示"（5 维度自问）——不是逐项勾选的清单，而是引导模型识别盲区的自问提示
- 退出要求从"covered/uncovered areas"改为"Confirmed facts + Open gaps + Scope boundary"——从"读了什么"转向"确认了什么"
- R6（DISCOVER 输出格式重构）已被 R1 吸收，不再独立存在

#### R2: Surface-based QA Gate

借鉴 Hephaestus Manual QA Gate，按交付物类型映射验证方法。

关键设计选择：

- "Reading the source and concluding 'this should work' does NOT pass this gate"——直接对治 ISS-015
- 2 次 QA GATE 失败限制（Hephaestus 用 3 次，弱模型更早衰减故减为 2 次）
- "No matching surface"兜底确保无遗漏

#### R3: Hard Invariants + 最小检查点

4 条绝对禁止 + Deletion Declaration + Staged Area Check。

关键设计选择：

- 从原 5 条精简为 4 条：移除与 R4 重叠的全局抑制禁止，合并测试删除与验证伪造为一条
- 后因实测发现 K2.6 会修改 pyproject.toml 抑制 lint 错误（ISS-001 复现），恢复第 4 条但措辞更精确："Never modify lint/type rules to suppress errors your changes introduced"
- Deletion Declaration 和 Staged Area Check 是操作级检查点，对应不可逆操作

#### R4: Lint Fix Guide

3 步决策树，降级为"apply judgment"。

关键设计选择：

- 从"mandatory before any lint fix"降级为"mandatory for behavioral/suppression fixes, optional for formatting-only"
- 理由：lint 修复是可逆操作，按原则应偏 Hephaestus（现称偏自主判断）；但行为/抑制类修复有隐蔽后果，需强制走决策树
- Step 1 责任区分（自己引入 vs 预存在）借鉴 Hephaestus "Fix only issues your changes caused"

#### R5a: TDD 红阶段验收标准

定义"正确的红"= assertion failure，非 infrastructure error。

关键设计选择：

- 这是定义性问题（消除歧义），不涉及信任光谱位置
- 通用化：用"assertion error"替代 Python 特定的"AssertionError"

#### R5b: TDD 证据要求

Red/Green/Refactor 输出要求，简化版。

关键设计选择：

- 移除与 Hard Invariants 重复的硬性声明
- TDD 证据要求本身是轻量级重注入——模型必须回顾 TDD 纪律

#### 新增: Failure Recovery 诊断步骤

QA GATE 失败后强制 re-read original request + 区分实现错误/理解错误 → 不同回退路径。

关键设计选择：

- 不信任模型自主区分失败性质——用结构化诊断步骤强制区分
- 理解错误 → 回到 DISCOVER（不可逆，必须重新理解）
- 实现错误 → 回到 EXECUTE（可逆，换方法即可）

### 移除的建议

| 原建议                   | 移除理由                                                           |
| ------------------------ | ------------------------------------------------------------------ |
| R6 DISCOVER 输出格式重构 | 已被 R1 吸收                                                       |
| R7 约束重注入精简        | 已被 R3（Hard Invariants 始终生效）+ R5b（TDD 证据隐式重注入）覆盖 |

### 通用化修改

- FIRST PRINCIPLES 中"your model (K2.6)"改为"Your model"——不绑定特定模型
- frontmatter model 参数通用化——模型适配在配置层，不在提示词核心

## Alternatives Considered

### 纯确认清单（原 R1）

5 类别逐项勾选✅/❌/N/A。

**优点**：最保守，强制逐项确认。
**缺点**：不完备（只覆盖已知失败模式）、仪式化程度高、容易被形式化勾选。
**结论**：过度保守。缺口探测提示 + 缺口声明的组合更难被形式化勾选。

### 纯缺口声明（无探测提示）

开放式声明"还缺什么"。

**优点**：最轻量，不增加仪式化。
**缺点**：依赖模型主动识别缺口——K2.6/GLM-5.1 的"不知道自己不知道"问题未解决。
**结论**：不够保守。DISCOVER 是最不可逆阶段，需要结构化提示帮助识别盲区。

### 强制 Lint Decision Tree（原 R4）

所有 lint 修复必须走决策树。

**优点**：最安全，最小化模型自主判断。
**缺点**：对格式类 lint 修复过度仪式化。
**结论**：过度约束。lint 修复是可逆操作，按原则应偏 Hephaestus（现称偏自主判断）。

### 固定回退路径（原 Failure Recovery）

QA GATE 失败 → 固定回到 EXECUTE。

**优点**：最简单，无需模型判断。
**缺点**：理解错误时回到 EXECUTE 只会重复错误实现。
**结论**：不够保守。理解错误是不可逆的，必须回到 DISCOVER。

## Consequences

- deepworker.md 从 ~428 行增长到 ~480 行（净增 ~50 行），在可接受范围内
- DISCOVER 阶段输出量增加（缺口声明退出要求），但这是最关键阶段的必要成本
- QA GATE 的 surface-based verification 增加实际运行交付物的步骤，但这是核心质量门
- 提示词核心模型无关，切换模型只需修改 frontmatter 配置
- 所有建议缺乏前瞻性验证，需在后续会话中观察 4 个系统性模式是否改善
- 如果 ISS-008/009（删除/git 范围）在提示词补强后仍频繁出现，需推进运行时机制（R8/R9）
