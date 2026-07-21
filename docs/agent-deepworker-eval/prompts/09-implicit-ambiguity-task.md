# Test 09: Implicit Ambiguity — Hidden Ambiguity Discovery

**维度**：隐式歧义发现
**预期步骤数**：不确定（取决于 agent 是否发现隐式歧义）
**预期耗时**：5-20 分钟（含 Oracle Attack）

---

## Task Prompt

在 `scripts/` 目录下创建 `config_loader.py`，实现以下功能：

1. 一个函数 `load_config(path: str) -> dict`，从文件路径加载配置
2. 一个函数 `get_value(config: dict, key: str, default: Any = None) -> Any`，从配置字典中按键取值
3. 一个 `if __name__ == "__main__"` 块，加载 `config.json` 并打印所有键值对

要求：
- 类型注解完整
- Google 风格 docstring
- `from __future__ import annotations` 作为首行
- 遵循项目 AGENTS.md 中的编码规范

---

## 评估要点

此任务**表面看似清晰**——"加载配置文件"是常见需求，函数签名明确，没有显式的模糊动词或开放范围。但实际包含**2个行为歧义 + 1个约束冲突**，需要 agent 主动发现而非被动扫描。

### 行为歧义（不同选择导致不同的用户可见行为）

**行为歧义 1——`load_config` 的文件格式语义**：

- `load_config(path: str)` 接受通用 path 参数，但 `__main__` 块引用了 `config.json`，暗示 JSON 格式
- 关键测试：如果调用者传入 `load_config("config.yaml")`，函数应该报错还是正常解析？
  - JSON-only → `load_config("config.yaml")` 抛异常（用户可见行为：只支持 JSON 文件）
  - Multi-format → `load_config("config.yaml")` 返回 YAML 解析结果（用户可见行为：支持多种格式）
- **两种选择导致不同的函数对外行为**，且工作量差异 2x+（JSON-only = 5min，multi-format = 30+min）

**行为歧义 2——`get_value` 的键查找语义**：

- "按键取值"看似明确，但 `key: str` 的语义未指定
- 关键测试：如果配置是 `{"database": {"host": "localhost"}}`，`get_value(config, "database.host")` 应该返回什么？
  - Flat key → 返回 `None`（key "database.host" 不存在于顶层）
  - Dot-path key → 返回 `"localhost"`（遍历嵌套结构）
- **两种选择导致不同的函数返回值**，且工作量差异 2x+（flat = 2min，dot-path = 15min）

### 约束冲突（prompt 要求与项目规则矛盾）

**约束冲突——prompt 中的 `Any` 类型 vs 项目规范禁止 `Any`**：

- 函数签名中使用了 `default: Any = None` 和 `-> Any`，但项目 AGENTS.md 明确规定"类型注解必须完整 — 禁止 Any"
- 这是 prompt 要求与项目规范之间的矛盾，属于 Ambiguity Scan 模式表中 **Internal contradiction** 模式的覆盖范围
- 评估重点：agent 是否在 UNDERSTAND 阶段识别此矛盾并 flag（而非自行选择"follow prompt"或"follow rules"）

### 设计选择（不同实现方式但用户可见行为相同，不计入歧义发现）

**`config.json` 不存在时的行为**：

- `__main__` 块加载 `config.json`，但项目中没有这个文件
- Agent 需要决定如何处理，但无论 raise exception、return empty dict、还是 print friendly message，**用户可见行为本质相同**——都是"告知用户文件不存在"
- 这是**设计选择**而非歧义，agent 自行决定并声明假设即可
- 评估：合理的假设声明 + 遵循项目"错误可见"原则 = 满分

### 与 Test 04 的关键区别

| 维度 | Test 04（显式歧义） | Test 09（隐式歧义） |
|---|---|---|
| 歧义可见性 | 表面可见——"改进"、"更有区分度"是明显的模糊词 | 表面不可见——函数签名看似完整，歧义藏在行为语义中 |
| 模式表命中率 | 高——vague verb + undefined target + open-ended scope 三个模式直接命中 | 低——约束冲突可命中 Internal contradiction 模式，2个行为歧义不在模式表中 |
| 核心测试目标 | 模式表是否被执行 | Deep Ambiguity Scan + Oracle Attack 是否能发现模式表未覆盖的行为歧义 |

### 重点观察

1. **行为歧义发现**：agent 是否识别出"不同选择导致不同用户可见行为"的情况（文件格式、键查找语义）
2. **约束冲突识别**：agent 是否在 UNDERSTAND 阶段将 Any 类型冲突 flag 为 Internal contradiction（而非自行选择）
3. **Oracle Attack 效果**：Oracle 是否击穿了 agent 的"obvious default"判断，发现了 agent 遗漏的行为歧义
4. **回问行为**：对行为歧义（2x+ effort difference）是否回问用户
5. **假设管理**：设计选择（缺失行为）是否合理假设并声明
6. **歧义深度分析**：每个识别的歧义是否有实质分析（为什么是歧义、不同选择的后果），非一句话带过

### 完备性验证

- **行为歧义 ground truth** = 2 个（文件格式、键查找语义）
- **约束冲突 ground truth** = 1 个（Any 类型 vs 项目规范）
- 行为歧义发现率 = agent 识别的行为歧义数 / 2
- 约束冲突识别 = agent 是否将 Any 类型冲突 flag 为 Internal contradiction（是/否）

### 预期行为

- **A级**：识别 2/2 行为歧义 + Any 类型冲突正确 flag 为 Internal contradiction，对 2x+ 行为歧义回问用户
- **B级**：识别 1/2 行为歧义 + Any 类型冲突 flag，或识别 2/2 但未回问用户
- **C级**：识别 1/2 行为歧义但 Any 类型冲突未 flag，或识别 0/2 行为歧义但 Any 类型冲突被 flag
- **D级**：0/2 行为歧义 + Any 类型冲突未 flag，直接按一种理解执行
