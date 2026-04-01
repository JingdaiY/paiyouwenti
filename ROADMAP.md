# 🐾 PaiYouWenTi (PYWT) — 项目路线图

> **人生牌烂，策略为王**
> *The deck is flawed, but the strategy is king.*

PYWT 是一个游戏化的 AI 原生学习 OS。通过小狗狗助理（小狗狗助理）、Markdown 驱动的技能系统和 MCP 工具集成，将学习的心理成本转化为多巴胺奖励。

---

## 图例

| 符号 | 含义 |
|------|------|
| ✅ | 已实现 |
| 🔨 | 进行中 |
| 📋 | 已规划 |
| 💡 | 探索中 |

---

## Phase 0 — The Skeleton（MVP）`[已完成]`

> 目标：建立核心小狗循环与技能加载机制。

| 功能 | 状态 | 备注 |
|------|------|------|
| `SkillManager` — 加载并解析 `.md` 技能文件 | ✅ | `core/skill_manager.py` |
| 技能文件动态注入系统 Prompt | ✅ | 支持 Persona、Rules、Reward Logic、Syllabus 等 section |
| 小狗狗助理人格（`puppy_mentor.md`） | ✅ | `skills/puppy_mentor.md` |
| `StateManager` — XP、等级、任务持久化 | ✅ | `state/deck_state.json` |
| Gemini LLM 集成（`PYWTEngine`） | ✅ | `core/engine.py`，使用 `google-genai` 新包 |
| Streamlit 聊天 UI + 侧边栏 HQ 面板 | ✅ | `app.py` |
| XP 自动解析（`<xp_award>` 标签） | ✅ | engine 静默处理，UI 显示金色徽章 |
| AI 自动创建任务（`<quest_create>` 含步骤列表） | ✅ | 5–10 条具体可执行步骤 |
| AI 自动推进任务（`<quest_advance>` 标签） | ✅ | 每次实质进展自动勾掉一步 |
| 流式打字机输出（实时渲染） | ✅ | chunk 到达即显示，含 `▌` 光标 |
| 前端 API Key 输入框（无需环境变量） | ✅ | 仅存 session，不写磁盘 |
| 治愈风浅色 UI（燕麦白 + 哑光陶土配色） | ✅ | DM Sans + DM Serif Display 字体 |
| 全局错误捕获（503/429/401 友好提示） | ✅ | 不崩溃，显示中文提示 |

---

## Milestone 1 — The Active Mentor `[学习逻辑]`

> 目标：从简单对话升级为主动教学与结构化评估。

| 功能 | 状态 | 备注 |
|------|------|------|
| **目标分解技能** — 将模糊目标自动拆解为 JSON 技能树 | 📋 | 新 `.md` 技能文件 + 结构化 LLM 输出 |
| **动态课程规划** — 根据用户时间生成限时学习计划 | 📋 | 例："我只有 15 分钟" |
| **多模态 XP 评估** — 评估提交的音频、代码、图片 | 📋 | 文件上传 UI + Gemini 多模态 |
| **多巴胺条动画** — XP 增加时触发小狗动画 | 📋 | Streamlit 自定义组件或 Lottie |
| **连续打卡追踪** — 检测并奖励连续学习天数 | 📋 | `StateManager` 增加日期逻辑 |

---

## Milestone 2 — The Connected World `[MCP 集成]`

> 目标：赋予小狗狗"感知"用户数字环境的能力。

| 功能 | 状态 | 备注 |
|------|------|------|
| **MCP 桥接基础** — 集成 MCP Python SDK | 📋 | `mcp_tools/` 目录已准备 |
| **Google Calendar MCP** — 识别可用学习时段 | 📋 | OAuth + 日历读取权限 |
| **本地文件系统 MCP** — 索引笔记（Obsidian/Notion 导出）和代码库 | 📋 | 路径限定读取 |
| **IntelliJ MCP** — 按需检查项目错误 | 💡 | JetBrains MCP 插件或 LSP 桥接 |
| **守护逻辑** — 学习窗口被忽略时主动推送提醒 | 📋 | 后台调度器 + 系统通知 |
| **技能工具调用** — 技能文件可声明可调用的 MCP 动作 | 📋 | 技能 schema 扩展：`## Tools` section |

---

## Milestone 3 — The Gamified Metaverse `[多巴胺黑客]`

> 目标：最大化心理奖励与长期留存，通过视觉身份和社会认同强化动机。

| 功能 | 状态 | 备注 |
|------|------|------|
| **收藏徽章卡** — 重要里程碑触发专属视觉奖励 | 📋 | 图片生成 API 或 SVG 模板 |
| **角色进化** — 随技能掌握获得"传奇装备"的视觉角色 | 📋 | 分层精灵图系统或生成式美术 |
| **技能星系图** — 交互式 React 知识宇宙地图 | 💡 | D3.js 或 React Flow |
| **现实联动** — 关联真实证书或考试成绩到顶级称号 | 💡 | 手动上传 + LLM 核验流程 |
| **传奇装备系统** — 达到技能精通阈值解锁外观奖励 | 📋 | 绑定 XP 等级 + 任务完成状态 |

---

## 架构概览

```
paiyouwenti/
├── app.py                  # Streamlit UI — 聊天 + 侧边栏 HQ
├── core/
│   ├── engine.py           # LLM 编排（Gemini）、流式输出、标签解析
│   ├── skill_manager.py    # .md 技能文件加载与 Prompt 注入
│   └── state.py            # XP / 等级 / 任务持久化（deck_state.json）
├── skills/                 # 新建 .md 即自动加载，无需改代码
│   ├── puppy_mentor.md     # 人格层（适用于所有对话）
│   └── python_learning.md  # 示例领域技能
├── mcp_tools/              # MCP 服务器桥接（Milestone 2）
└── state/
    └── deck_state.json     # 运行时状态（已 git ignore）
```

---

## 贡献指南

**添加新技能领域** — 在 `skills/<domain>.md` 中按标准 section 创建文件，重启后自动发现：
```
## Syllabus  ## Rules  ## Reward Logic  ## Examples
```

**添加 MCP 工具** — 在 `mcp_tools/` 中按 MCP Python SDK 模式实现，在技能文件的 `## Tools` section 中声明（Milestone 2 schema，即将推出）。

**切换 LLM** — 修改 `core/engine.py` 中的 `GEMINI_MODEL`，其余管道与模型无关。

---

*Project by [@jyang](https://github.com/jyang) · 🐾 loyal · 🦴 persistent · 🐕 always learning*
