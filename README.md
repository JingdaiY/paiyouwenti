# 牌有问题 (PaiYouWenTi) 🐾

> **人生牌烂，策略为王**
> *The deck is flawed, but the strategy is king.*

一个由 AI 驱动的游戏化学习 OS。通过**小狗狗助理**陪伴你把学习成本转化为多巴胺奖励——由 Markdown 技能文件驱动、实时 XP 反馈、任务系统全自动管理。

📖 **[完整项目路线图 →](ROADMAP.md)**

---

## 功能一览

| 功能 | 状态 |
|------|------|
| Markdown 技能文件动态注入 LLM | ✅ |
| 小狗狗助理人格（温暖、鼓励、狗狗比喻） | ✅ |
| XP / 等级 / 升级系统 | ✅ |
| AI 自动创建并推进任务（含步骤列表） | ✅ |
| 流式打字机效果（实时输出） | ✅ |
| 游戏化 UI（治愈风浅色主题） | ✅ |
| Gemini API Key 前端输入（无需环境变量） | ✅ |
| MCP 工具集成（日历、本地文件） | 📋 规划中 |

---

## 快速开始

**1. 安装依赖**
```bash
pip install -r requirements.txt
```

**2. 启动**
```bash
streamlit run app.py
```

**3. 在左侧边栏粘贴你的 Gemini API Key 即可开始。**

> 获取 Key：[Google AI Studio](https://aistudio.google.com/app/apikey)（免费）

---

## 项目结构

```
paiyouwenti/
├── app.py                  # Streamlit UI（聊天 + 侧边栏 HQ）
├── core/
│   ├── engine.py           # LLM 编排（Gemini）、流式输出、标签解析
│   ├── skill_manager.py    # .md 技能文件加载与 Prompt 注入
│   └── state.py            # XP / 等级 / 任务持久化
├── skills/                 # 放入新 .md 文件即自动加载
│   ├── puppy_mentor.md     # 人格层（适用于所有对话）
│   └── python_learning.md  # 示例领域技能
├── mcp_tools/              # MCP 工具桥接（Milestone 2）
└── state/
    └── deck_state.json     # 运行时状态（已 git ignore）
```

---

## 添加新技能

在 `/skills` 目录新建 `.md` 文件，重启或点击"重新加载技能"即自动生效，无需改代码：

```markdown
# 技能名称

## Syllabus
## Rules
## Reward Logic
## Examples
```

---

## AI 系统标签说明

小狗狗助理在回复中会静默输出以下标签，由系统自动处理，用户不可见：

| 标签 | 作用 |
|------|------|
| `<xp_award>{"xp": N, "reason": "..."}` | 奖励 XP，自动累计到等级系统 |
| `<quest_create>{"name": "...", "steps": [...]}` | 创建带步骤的任务 |
| `<quest_advance>{"name": "..."}` | 推进任务进度一步 |

---

## Tech Stack

- **LLM**: Google Gemini（`gemini-3-flash-preview`）via `google-genai`
- **UI**: Streamlit
- **State**: JSON 文件持久化
- **Skills**: 纯 Markdown，零代码扩展
