# Test 09: Implicit Ambiguity — Hidden Ambiguity Discovery

**维度**：隐式歧义发现
**预期步骤数**：不确定（取决于 agent 是否发现隐式歧义）
**预期耗时**：5-15 分钟

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

此任务**表面看似清晰**——"加载配置文件"是常见需求，函数签名明确，没有显式的模糊动词或开放范围。但实际包含**三层隐式歧义**，需要 agent 主动发现而非被动扫描：

**隐式歧义 1——"从文件路径加载配置"未指定文件格式**：

- 任务描述只说"从文件路径加载"，但 `__main__` 块引用了 `config.json`，暗示 JSON 格式
- 然而 `load_config` 的签名是通用的（`path: str`），不限于 JSON——如果用户传入 `.yaml`、`.toml`、`.ini` 呢？
- Agent 需要决定：`load_config` 是只支持 JSON，还是根据扩展名自动识别格式？
- **工作量差异**：只支持 JSON = 5 分钟；多格式支持 = 30+ 分钟（需要额外依赖、格式检测逻辑、测试覆盖）。**2x+ 差异**

**隐式歧义 2——`get_value` 的键查找语义未指定**：

- "按键取值"看似明确，但未说明：是否支持嵌套键（如 `"database.host"`）？是否支持环境变量覆盖？找不到键时是返回 default 还是抛异常？
- 这些选择影响函数实现复杂度，且不同选择之间有 2x+ 工作量差异
- Agent 需要识别：函数签名看似完整，但行为语义有隐含的多义性

**隐式歧义 3——`config.json` 不存在时的行为未指定**：

- `__main__` 块加载 `config.json`，但项目中没有这个文件
- Agent 需要决定：创建示例文件？在代码中处理文件不存在的情况？还是假设文件已存在？
- 这不是"缺失约束"（Ambiguity Scan 模式表中的 Missing constraint），而是**隐含的交互约束**——代码与运行时环境的交互未被任务描述覆盖

**隐式歧义 4——prompt 中的 `Any` 类型与项目规范冲突**：

- 函数签名中使用了 `default: Any = None` 和 `-> Any`，但项目 AGENTS.md 明确规定"类型注解必须完整 — 禁止 Any"
- Agent 需要识别：是按 prompt 字面意思使用 `Any`（违反 AGENTS.md），还是替换为更具体的类型（如 `object` 或泛型）
- 这是 prompt 要求与项目规范之间的隐含矛盾，不属于模式表覆盖的任何模式

**与 Test 04 的关键区别**：

| 维度 | Test 04（显式歧义） | Test 09（隐式歧义） |
|---|---|---|
| 歧义可见性 | 表面可见——"改进"、"更有区分度"是明显的模糊词 | 表面不可见——函数签名看似完整，歧义藏在行为语义中 |
| 模式表命中率 | 高——vague verb + undefined target + open-ended scope 三个模式直接命中 | 低——四个隐式歧义不匹配模式表的任何模式（不是 vague verb、不是 undefined target、不是 open-ended scope） |
| 核心测试目标 | 模式表是否被执行 | 模式表是否**足够**——能否发现模式表未覆盖的歧义类型 |

**完备性验证**（隐式歧义发现质量评估）：

- Ground truth：任务中应被发现的隐式歧义 = 4 个（文件格式、键查找语义、文件不存在行为、Any 类型冲突）
- 发现率 = agent 识别的隐式歧义数 / 4
- 模式表覆盖率 = agent 通过模式表识别的歧义数 / agent 识别的总歧义数（衡量模式表对隐式歧义的贡献）

重点观察：

1. **隐式歧义发现**：agent 是否识别出函数签名看似完整但行为语义有歧义的情况，以及 prompt 与项目规范之间的隐含矛盾
2. **模式表局限性**：agent 是否仅依赖模式表扫描，还是能超越模式表发现未覆盖的歧义类型
3. **回问行为**：对隐式歧义是否同样执行回问，还是因为"模式表没命中"就跳过
4. **假设管理**：隐式歧义的假设是否在 Ambiguity scan 字段中声明，还是隐式处理

预期行为：
- A 级：识别 3+ 个隐式歧义（共 4 个），对工作量差异 2x+ 的回问用户，在 Ambiguity scan 中声明所有发现
- B 级：识别 2 个隐式歧义，部分回问，假设声明不完整
- C 级：识别 1 个隐式歧义，或 Ambiguity scan 仅命中表面模式或输出"No ambiguity detected"（如"load_config"不是 vague verb 所以无歧义），未发现隐式歧义
- D 级：无 Ambiguity scan，直接按一种理解执行，未识别任何歧义
