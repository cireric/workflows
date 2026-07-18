# Agent Evaluation Framework

Deepworker agent 的集成测试框架。通过向 agent 委派真实任务、收集完整输出、按评分标准分析，评估 agent 对其协议的遵从度。

## 目录结构

```
docs/agent-deepworker-eval/
  README.md           # 本文件——框架总览
  rubric.md           # 评分标准——9个维度的评分细则
  runbook.md          # 运行手册——如何执行测试、收集日志、生成报告
  ablation-ambiguity-scan.md  # 消融实验——模式表有效性验证（待基线数据后激活）
  prompts/            # 测试提示词——每个文件是一个独立的测试任务
    01-simple-task.md
    02-tdd-task.md
    03-explore-task.md
    03-fixtures/       # Test 03 预置代码
      e3_scorer.py
    04-ambiguous-task.md
    04-fixtures/       # Test 04 预置代码
      e3_scorer.py
    05-qa-failure-task.md
    06-long-chain-task.md
    07-complex-incomplete-task.md
    08-qa-recovery-task.md
    08-fixtures/
      inventory_tracker.py
      test_inventory_tracker.py
    09-implicit-ambiguity-task.md
```

## 评估维度

| #   | 维度         | 测试文件                        | 核心问题                                                                                               |
| --- | ------------ | ------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1   | 基础执行     | `01-simple-task.md`             | TODO 铁律是否生效？步骤追踪、单步聚焦、完成标记是否遵守？                                              |
| 2   | TDD 纪律     | `02-tdd-task.md`                | Red→Green→Refactor 循环是否完整？Red 是否有效（断言失败而非基础设施错误）？                            |
| 3   | 全链路执行   | `03-explore-task.md`            | DISCOVER→PLAN→EXECUTE→VERIFY→QA GATE 是否完整走通？阶段转换输出是否规范？                              |
| 4   | 歧义处理     | `04-ambiguous-task.md`          | 两层歧义是否被逐层识别？工作量差异 2x+ 的歧义是否回问用户？假设是否声明？                              |
| 5   | 交互约束识别 | `05-qa-failure-task.md`         | PLAN Goal 端到端场景是否声明？函数间交互约束是否在 PLAN 阶段识别？                                     |
| 6   | 约束衰减     | `06-long-chain-task.md`         | 多步骤后约束是否仍然遵守？约束重注入是否在阶段转换时触发？                                             |
| 7   | 信息不完备   | `07-complex-incomplete-task.md` | 信息不足时是否主动探索？是否合理声明假设 vs 阻塞？是否使用 explore/librarian？                         |
| 8   | 失败恢复兜底 | `08-qa-recovery-task.md`        | 预置交互约束缺失的 QA GATE 验证：端到端场景是否覆盖函数组合？三层诊断是否正确？恢复路径是否回到 DISCOVER？ |
| 9   | 隐式歧义发现 | `09-implicit-ambiguity-task.md` | 表面清晰的任务中隐式歧义是否被发现？模式表是否覆盖隐式歧义类型？超越模式表的歧义发现能力？             |

## 使用方法

1. **准备**：确认 deepworker agent 已配置为 subagent 类型
2. **执行**：按 `runbook.md` 中的流程，逐个或批量委派测试任务
3. **收集**：将每个任务的完整 session 输出写入日志文件
4. **评分**：按 `rubric.md` 中的标准对每个维度打分
5. **报告**：生成综合分析报告

## 跨模型复用

本框架与具体模型无关。更换模型时：

- 提示词文件无需修改
- 评分标准无需修改
- 只需在日志文件名中标注模型名称，便于横向对比

日志命名约定：`{test-id}_{model-slug}_{timestamp}.md`

示例：`01-simple_astron-code-latest_20260713.md`

## 设计原则

- **真实任务**：每个测试都是可执行的真实编程任务，不是假设性问答
- **可观测**：评估基于 agent 的实际输出，不依赖内部状态
- **可复现**：同一提示词 + 同一模型应产生可比较的结果
- **可对比**：评分标准量化，支持跨模型横向对比

## 已知局限

- **模式表语言覆盖**：deepworker 协议的 Ambiguity Scan 模式表当前仅含英文示例（"optimize"、"improve" 等），测试 prompt 使用中文。跨语言测试依赖模型的双语映射能力——模型需将中文模糊词（如"改进"）映射到英文模式类别（如 Vague verb）。更换模型时需评估其跨语言模式识别能力。

## 附录（新会话运行的提示词）

```text
按 docs/agent-deepworker-eval/runbook.md 执行 deepworker agent 评估测试套件。

要求：
1. 从 01-simple-task 开始，按顺序执行到 09-implicit-ambiguity-task
2. 每个测试只传 Task Prompt 部分，不传评估要点
3. 每个测试完成后收集完整 session 输出，写入 .scratch/agent-deepworker-eval-logs/
4. 每个测试后清理工作区（git checkout + git clean）
5. 全部完成后按 rubric.md 评分，生成综合报告
6. 模型标识：astron-code-latest
```
