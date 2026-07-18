# Agent Evaluation Runbook

Sisyphus 执行 deepworker 评估测试的操作手册。

## 前置条件

1. deepworker agent 已配置为 subagent 类型（在 opencode 配置中）
2. 项目工作区干净（`git status` 无未提交更改，或已声明 pre-existing changes）
3. 了解当前测试的模型名称（用于日志命名）

## 执行流程

### Step 1: 选择测试

从 `docs/agent-deepworker-eval/prompts/` 中选择要执行的测试。可以逐个执行，也可以批量执行。

**建议顺序**：01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09（从简单到复杂）

### Step 2: 委派任务

使用 `task()` 工具将测试提示词委派给 deepworker：

```
task(
  subagent_type="deepworker",
  run_in_background=false,
  description="Eval test 01: simple task",
  prompt="<从对应 .md 文件中读取的 Task Prompt 部分>"
)
```

**关键**：
- `run_in_background=false`：同步等待，确保完整收集输出
- prompt 中只包含 "Task Prompt" 部分的内容，不包含 "评估要点" 部分
- 每个测试独立执行，不要在一个 session 中连续执行多个测试

**Session ID 收集**：`task()` 返回结果中包含 deepworker 的 session ID（格式 `ses_...`）。记录此 ID，用于后续日志收集。如果 `task()` 返回值中未直接暴露 session ID，可通过 `session_list()` 按时间排序获取最近创建的 session。

### Step 3: 收集日志

任务完成后，使用 `session_read` 读取完整 session 输出：

```
session_read(session_id="<deepworker 的 session ID>", include_transcript=true)
```

将完整输出写入日志文件：

```
.scratch/agent-deepworker-eval-logs/{test-id}_{model-slug}_{timestamp}.md
```

**日志文件格式**：

```markdown
# Eval Log: {test-id} — {test-name}

- **Model**: {model-slug}
- **Date**: {timestamp}
- **Session ID**: {ses_...}

---

## Raw Output

{完整 session 输出}

---

## Evaluator Notes

{执行者观察到的关键行为，实时记录}
```

### Step 4: 清理工作区

每个测试完成后，清理 agent 创建的文件：

```bash
git checkout -- .  # 恢复所有被修改的文件
git clean -fd scripts/ tests/  # 删除新创建的文件（谨慎使用）
```

**注意**：只清理 agent 在测试中创建/修改的文件，不要清理日志文件。

**清理验证**：清理后运行 `git status` 确认工作区干净。如果仍有残留文件，手动删除后再开始下一个测试。避免测试间污染。

### Step 5: 评分

按 `docs/agent-deepworker-eval/rubric.md` 中的标准，对每个检查项打分。

将评分写入日志文件的 `Evaluator Notes` 部分：

```markdown
## Scoring

| 检查项 | 等级 | 证据 |
|--------|------|------|
| 步骤追踪 | A | todo list 完整，与 PLAN 一致 |
| 单步聚焦 | B | 步骤 3 出现短暂 2 个 in_progress |
| ... | ... | ... |

**维度总分**: {A/B/C/D}
```

### Step 6: 生成综合报告

所有测试完成后，生成综合分析报告：

```
.scratch/agent-deepworker-eval-logs/report_{model-slug}_{timestamp}.md
```

**报告格式**：

```markdown
# Deepworker Agent Evaluation Report

- **Model**: {model-slug}
- **Date**: {timestamp}
- **Tests Run**: {N}/9

---

## Summary Scores

| 维度 | 测试 | 等级 | 得分 | 关键发现 |
|------|------|------|------|---------|
| 基础执行 | 01-simple | A | 4 | ... |
| TDD 纪律 | 02-tdd | B | 3 | ... |
| ... | ... | ... | ... | ... |

**综合分**: {total}/48（加权）
**综合等级**: {A+/A/B/C/D}

---

## Dimension Analysis

### 1. 基础执行 (A)
{详细分析}

### 2. TDD 纪律 (B)
{详细分析}

...

---

## Cross-Dimension Patterns

{跨维度的共性发现}

---

## Protocol Defects

### 🔴 阻断性问题
{导致任务失败的协议缺陷}

### 🟡 质量问题
{降低产出质量的协议弱点}

### 🟢 亮点
{协议设计中特别有效的部分}

---

## Recommendations

{基于评估结果的协议修订建议}
```

## 批量执行脚本

如果需要一次性运行所有 9 个测试，按以下顺序逐个执行（不要并行，因为每个测试都会修改工作区）：

1. 读取 `01-simple-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
2. 读取 `02-tdd-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
3. 复制 `03-fixtures/e3_scorer.py` → 读取 `03-explore-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
4. 复制 `04-fixtures/e3_scorer.py` → 读取 `04-ambiguous-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
5. 读取 `05-qa-failure-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
6. 读取 `06-long-chain-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
7. 读取 `07-complex-incomplete-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
8. 复制 `08-fixtures/` → 读取 `08-qa-recovery-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
9. 读取 `09-implicit-ambiguity-task.md` 的 Task Prompt → 委派 → 收集日志 → 清理
10. 全部完成后 → 生成综合报告

**Test 03 特殊说明**：此测试使用预置代码。委派前，执行者需先运行素材准备步骤（见 `03-explore-task.md` 的"执行者准备步骤"），将 fixtures 中的代码复制到 `scripts/`。**准备步骤不得出现在传给 agent 的 prompt 中**——agent 只应看到"代码已存在"的事实。清理时 `git clean -fd scripts/ tests/` 会删除这些文件，无需额外操作。

**Test 04 特殊说明**：此测试需要 `scripts/e3_scorer.py` 存在，以测试"评分脚本"指代不明的歧义。委派前，执行者需先运行素材准备步骤（见 `04-ambiguous-task.md` 的"执行者准备步骤"），将 fixtures 中的代码复制到 `scripts/`。**准备步骤不得出现在传给 agent 的 prompt 中**——agent 只应看到"代码已存在"的事实。清理时 `git clean -fd scripts/ tests/` 会删除这些文件，无需额外操作。

**Test 08 特殊说明**：此测试使用预置交互约束缺失代码。委派前，执行者需先运行素材准备步骤（见 `08-qa-recovery-task.md` 的"执行者准备步骤"），将 fixtures 中的代码复制到 `scripts/` 和 `tests/`。**准备步骤不得出现在传给 agent 的 prompt 中**——agent 只应看到"代码已存在"的事实。清理时 `git clean -fd scripts/ tests/` 会删除这些文件，无需额外操作。

**不要并行执行**：每个测试都会创建/修改文件，并行执行会导致文件冲突。

## 跨模型对比

更换模型后，重复执行流程。日志文件名中的 model-slug 会区分不同模型的结果。

对比时，将多个模型的报告并排分析：

```markdown
# Cross-Model Comparison

| 维度 | Model A | Model B | Model C |
|------|---------|---------|---------|
| 基础执行 | A | B | A |
| TDD 纪律 | B | C | A |
| ... | ... | ... | ... |
| **综合** | A (40/48) | C (24/48) | A+ (46/48) |
```

## 注意事项

1. **环境一致性**：每次测试前确保工作区状态一致（干净或声明 pre-existing changes）
2. **不干预**：测试执行中不要干预 agent 的行为，即使它走偏了——走偏本身就是测试数据
3. **完整记录**：即使 agent 输出很长，也要完整记录，不要截断
4. **时间记录**：记录每个测试的实际耗时，作为效率参考
5. **清理彻底**：每个测试后必须彻底清理，避免测试间污染
6. **清理验证**：清理后运行 `git status` 确认工作区干净，残留文件需手动删除后再开始下一个测试
