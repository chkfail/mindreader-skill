# mindreader-skill — 产品需求文档 v1.0

---

## 一、产品概述

**mindreader-skill** 是一个用于构建"数字影子"(Shadow) 的 Skill，源自 ex-skill 的 6 层人格模型。

用户通过导入聊天记录 + 主观描述，构建一个人的数字影子。然后用影子来：
- **Séance Mode** (`/seance`) — 回顾过去的对话，问"他们到底在想什么"
- **Rehearsal Mode** (`/rehearse`) — 在和真人说之前，先在影子身上预演

**核心哲学**：这是"假设生成器"，不是"读心术"。它给你3个矛盾的解读，不是1个答案。

---

## 二、用户流程

```
用户触发 /mindreader build
        ↓
[Step 1] 基础信息录入
  - 称呼/代号
  - 关系基本信息（性别、年龄、关系阶段）
  - MBTI / 星盘 / 依恋风格（可选）
  - 关系特质标签
  - 对这个人的主观印象
        ↓
[Step 2] 数据导入
  - 粘贴聊天记录（任何格式）
  - 或导入 ex-skill persona 文件
  - 或只提供文字描述
        ↓
[Step 3] 自动分析
  - 提取沟通风格、情绪模式、冲突行为
  - 重用 ex-skill 的 6 层人格模型
        ↓
[Step 4] 生成预览
  - 展示影子摘要（3-5条典型行为）
  - 展示 2 个例子对话
        ↓
[Step 5] 写入文件
  - 生成 shadows/{slug}/
  - 包含 shadow.md（影子人格）
  - 包含 meta.json（元数据）
        ↓
[持续] 进化模式
  - 追加记录 → merge 进影子
  - 对话纠正 → patch 对应层
```

---

## 三、影子分层结构（基于 ex-skill 6 层模型）

```
Layer 0 — 核心模式（手动标签直接翻译，最高优先级）
  示例："当你追问 TA 在想什么，TA会说'没什么'然后沉默"
  示例："TA 发小动物表情包的时候通常是想缓和气氛"

Layer 1 — 身份
  "你是 {name}。"
  "你的 MBTI 是 {X}，星座是 {X}。"
  "{依恋风格} 影响你很深，具体体现在..."

Layer 2 — 表达风格
  - 用词习惯、口头禅、标志性表达
  - emoji 使用习惯
  - 回复速度模拟
  - 语气在不同情绪下的变化

Layer 3 — 情感行为模式
  - 如何表达喜欢/在乎
  - 如何表达不满
  - 吵架时的典型行为链
  - 和好时通常用什么方式开口

Layer 4 — 冲突与边界
  - 触发点
  - 冲突链
  - 冷战模式
  - 边界话题

Layer 5 — 雷区与 Tripwires
  - 什么会让 TA 消失
  - 什么会让 TA 重新出现
  - 深度敏感话题
```

---

## 四、运行模式

### 4.1 Séance Mode (`/seance`)

**目的**：分析过去的对话，理解"他们到底在想什么"

**输出格式**：
```
我看到这 {N} 条消息里有 {M} 个矛盾点。
我没有办法告诉你哪个是"真相"，但我可以给你3个不同的解读：

━━━ 解读 A：{标签}（置信度 ~XX%）
证据：{引用消息}
如果这个解读是对的：{推测 TA 的动机}

━━━ 解读 B：{标签}（置信度 ~XX%）
...

━━━ 解读 C：{标签}（置信度 ~XX%）
...

⚠️ 我可以让这三种解读听起来都像真的。这是 LLM 最擅长的事，也是最危险的事。
把这些当作"我没考虑到的情况"，而不是"答案"。
```

**关键设计**：
- 强制输出多个矛盾解读（不能只给一个）
- 每个解读都要有证据
- 必须有置信度和自警告

### 4.2 Rehearsal Mode (`/rehearse`)

**目的**：在和真人说之前，预演这句话会不会炸

**流程**：
```
Step 1: 用户说"我要跟 TA 说 X"
Step 2: 影子问"你的目标是什么？"
Step 3: 用户描述目标
Step 4: 运行 5 轮模拟
Step 5: 输出：影子反应 + 失败模式 + 建议修改
```

**输出格式**：
```
目标达成率：X/10

━━━ 影子的反应
影子：（内心）{内心独白}
影子：（回复）{回复内容}

━━━ 失败模式
{分析哪里会出问题}

━━━ 建议修改（估计达成率 Y/10）
"建议的说法"

⚠️ 这个影子是从 {N} 条消息构建的。
  如果消息覆盖的场景有限，模拟可能不准确。
  这不是剧本，是排练。真实对话中stay present。
```

**关键设计**：
- 最多 5 轮，防止过度拟合
- 必须输出内心独白
- 必须有 fidelity warning

---

## 五、项目结构

```
mindreader-skill/
│
├── docs/
│   └── PRD.md
│
├── prompts/
│   ├── shadow_builder.md        # Step 3：构建影子
│   ├── seance.md                # Séance Mode 分析
│   ├── rehearsal.md             # Rehearsal Mode 模拟
│   ├── merger.md                # 追加数据 merge
│   └── correction_handler.md    # 对话纠正处理
│
├── tools/
│   ├── shadow_manager.py        # 影子文件管理
│   └── version_manager.py       # 版本管理
│
└── shadows/                     # 影子存储
    └── {slug}/
        ├── shadow.md            # 影子人格
        ├── meta.json            # 元数据
        ├── versions/            # 历史版本
        └── knowledge/
            └── chats/           # 聊天记录归档
```

---

## 六、元数据格式 (meta.json)

```json
{
  "name": "小美",
  "slug": "xiaomei",
  "created_at": "2026-04-13T10:00:00Z",
  "updated_at": "2026-04-13T10:00:00Z",
  "version": "v1",
  "profile": {
    "gender": "女",
    "age_range": "23-27",
    "rel_stage": "暧昧",
    "duration": "3个月",
    "zodiac": "天蝎座",
    "mbti": "INFP"
  },
  "tags": {
    "attachment": ["焦虑型"],
    "rel_traits": ["话痨", "冷战派", "嘴硬心软"]
  },
  "impression": "忽冷忽热，搞不清楚她到底想要什么",
  "knowledge_sources": [
    "knowledge/chats/wechat_messages.txt"
  ],
  "corrections_count": 0,
  "message_count": 0
}
```

---

## 七、命令列表

| 命令 | 功能 |
|------|------|
| `/mindreader build` | 构建新影子 |
| `/mindreader list` | 列出所有影子 |
| `/mindreader forget <n>` | 删除影子 |
| `/seance` | 进入 Séance Mode |
| `/rehearse` | 进入 Rehearsal Mode |

---

## 八、约束与边界

- 影子文件 100% 本地存储，无服务器，无遥测
- 数据来源：聊天记录文本 / ex-skill persona 文件 / 纯文字描述
- Correction 层最多 50 条
- 版本存档最多保留 10 个版本
- 如果消息数少于 100 条，生成时标注"样本偏少，可信度低"
