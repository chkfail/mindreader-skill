---
name: mindreader
description: 构建数字影子，分析过去对话，预演未来对话
user-invocable: true
triggers:
  - /mindreader
  - /seance
  - /rehearse
---

# mindreader-skill — 数字影子构建器

Stop guessing what they really meant. Stop rehearsing in your head. Talk to their shadow first.

---

## 工作模式

收到 `/mindreader` 后，按以下流程运行：

```
/mindreader build     → 构建新影子
/mindreader list      → 列出所有影子
/mindreader forget    → 删除影子
/seance               → 进入 Séance Mode
/rehearse             → 进入 Rehearsal Mode
```

---

## `/mindreader build` — 构建新影子

### Step 1：基础信息录入

开场白：
```
我来帮你构建 {name} 的数字影子。

只需要回答几个问题，每个都可以跳过。
信息越详细，影子越准。
```

按顺序问：
1. **称呼/代号** — TA 叫什么？
2. **关系基本信息** — 性别、年龄、你们的关系阶段
3. **性格标签**（可选）— MBTI、星座、依恋风格
4. **关系特质标签** — 话痨/沉默系/冷战派/嘴硬心软 等
5. **主观印象** — 你对 TA 的整体感受

### Step 2：数据导入

```
现在需要导入 TA 的聊天记录或描述。有三种方式：

方式 A：直接粘贴聊天记录（任意格式，我会自动解析）
方式 B：从 ex-skill 导入（如果你有现成的 persona 文件）
方式 C：只描述（没有聊天记录也可以，但质量会低一些）

跳过也行，后续随时可以追加。
```

### Step 3：生成影子

根据 prompts/shadow_builder.md 的模板生成 shadow.md。

**分析时的注意事项：**
- 手动标签优先于聊天记录分析结论
- 消息少于 100 条时，在输出开头标注 `⚠️ 样本偏少，可信度较低`
- 有原文依据的结论引用原话，没有依据的标注"（基于标签推断）"

### Step 4：预览并确认

向用户展示：

```
━━━ {name} 影子预览 ━━━

核心模式（3条最典型）：
  1. ...
  2. ...
  3. ...

表达风格：
  口头禅：...
  招牌 emoji：...
  情绪好时：...
  情绪差时：...

━━━ 示例对话 ━━━

场景 A — 你主动找 TA：
  你：嗨
  TA：{按影子回复}

场景 B — 你们有点小矛盾：
  你：你好像有点不高兴？
  TA：{按影子回复}

---
确认生成？（确认 / 修改某部分）
```

### Step 5：写入文件

用户确认后：
```bash
python tools/shadow_manager.py --action create \
  --slug {slug} \
  --name "{name}" \
  --meta meta.json \
  --shadow shadow_content.md \
  --base-dir ./shadows
```

创建目录结构：
```
shadows/{slug}/
  ├── shadow.md      # 影子人格
  ├── meta.json      # 元数据
  ├── versions/      # 历史版本
  └── knowledge/
      └── chats/     # 聊天记录归档
```

完成后告知用户：
```
✅ 影子已构建完成：{name}

后续操作：
  /seance                   # 分析过去的对话
  /rehearse                # 预演未来的对话
  追加记录                  # 粘贴新的聊天记录
  纠正                      # 说"这不对，TA 不会这样"
  /mindreader list          # 查看所有影子
  /mindreader forget {slug} # 删除影子
```

---

## `/mindreader list` — 列出所有影子

```bash
python tools/shadow_manager.py --action list --base-dir ./shadows
```

输出所有影子的列表（名字、关系阶段、版本、消息数、最后更新）。

---

## `/mindreader forget <slug>` — 删除影子

```bash
python tools/shadow_manager.py --action delete --slug {slug} --base-dir ./shadows
```

---

## `/seance` — Séance Mode

**目的**：分析过去的对话，理解"他们到底在想什么"

### 工作流程

1. 加载对应影子
2. 收集要分析的对话
3. 按 prompts/seance.md 生成多个矛盾解读

### 输出要求

必须输出 **3 个矛盾解读**，每个包含：
- 置信度
- 证据（引用具体消息）
- 如果这个解读是对的（推测动机）
- 这个解读成立的条件

最后必须有自警告：
```
⚠️ 我可以让这三种解读听起来都像真的。
这是 LLM 最擅长的事，也是最危险的事。
把我当作"你没考虑到的情况"，而不是"答案"。
```

---

## `/rehearse` — Rehearsal Mode

**目的**：在和真人说之前，先在影子身上预演

### 工作流程

1. 确认用户想说的话
2. 确认用户的目标
3. 加载影子
4. 运行最多 5 轮模拟
5. 输出：影子反应 + 失败模式 + 建议修改

### 输出要求

每轮必须包含影子的**内心独白**，不只是表面回复。

结果必须包含：
- 目标达成率（X/10）
- 失败模式分析
- 建议修改（带估计达成率）

最后必须有 fidelity warning：
```
⚠️ 这个影子是从 {N} 条消息构建的。
这是排练，不是剧本。真实对话中，stay present。
```

---

## 持续进化

### 追加记录

用户说"追加记录"或粘贴新聊天记录：
→ 按 `prompts/merger.md` 执行增量 merge
→ 调用 `shadow_manager.py --action update`

### 对话纠正

用户说"这不对"或"TA 不会这样"：
→ 按 `prompts/correction_handler.md` 识别并写入 Correction 层
→ 调用 `shadow_manager.py --action update`

### 版本管理

用户说"查看版本历史"：
→ 调用 `python tools/version_manager.py --action list --slug {slug}`

用户说"回滚到 v2"：
→ 调用 `python tools/version_manager.py --action rollback --slug {slug} --version v2`

---

## 文件引用索引

| 文件 | 用途 |
|------|------|
| `prompts/shadow_builder.md` | 构建影子人格 |
| `prompts/seance.md` | Séance Mode 分析 |
| `prompts/rehearsal.md` | Rehearsal Mode 模拟 |
| `prompts/merger.md` | 追加记录 merge |
| `prompts/correction_handler.md` | 对话纠正处理 |
| `tools/shadow_manager.py` | 影子文件管理 |
| `tools/version_manager.py` | 版本存档与回滚 |
