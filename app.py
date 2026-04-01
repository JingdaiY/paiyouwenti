"""
PaiyouWenTi — Streamlit UI
Warm, cozy, light-mode dashboard with the Puppy Assistant.
"""

import os
import re

import streamlit as st

from core.engine import PYWTEngine

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="牌有问题 🐾",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    /* ─────────────────────────────────────────
       PALETTE
       --bg:        #f8f6f2   oat-milk white
       --sidebar:   #f3f0eb   parchment beige
       --surface:   #ffffff
       --border:    rgba(185,155,130,0.18)
       --accent:    #b8785a   muted terracotta
       --accent-lt: rgba(184,120,90,0.10)
       --text-1:    #3a322b   warm charcoal
       --text-2:    #8a7a6e   muted brown-grey
       --text-3:    #b5a99e   light muted
    ───────────────────────────────────────── */

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ── Base ── */
    .stApp {
        background-color: #f8f6f2;
        color: #3a322b;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #f3f0eb;
        border-right: 1px solid rgba(185,155,130,0.22);
    }
    section[data-testid="stSidebar"] * { color: #4a3e36 !important; }

    /* ── XP progress bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #c9896e, #b8785a);
        border-radius: 99px;
    }
    .stProgress > div {
        background: rgba(184,120,90,0.12);
        border-radius: 99px;
        height: 8px !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid rgba(185,155,130,0.2);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 2px 12px rgba(90,60,40,0.06);
    }
    [data-testid="stMetricValue"] {
        color: #b8785a !important;
        font-weight: 600;
        font-size: 1.4rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8a7a6e !important;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* ── Chat: user bubble ── */
    .user-bubble {
        display: flex;
        justify-content: flex-end;
        margin: 14px 0;
    }
    .user-bubble-inner {
        background: #b8785a;
        border-radius: 18px 18px 4px 18px;
        padding: 13px 20px;
        max-width: 68%;
        color: #fdf9f6;
        font-size: 0.94rem;
        line-height: 1.65;
        font-weight: 400;
        box-shadow: 0 4px 18px rgba(184,120,90,0.22);
        letter-spacing: 0.01em;
    }

    /* ── Chat: puppy bubble ── */
    .ai-bubble {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin: 14px 0;
    }
    .ai-avatar {
        font-size: 1.75rem;
        line-height: 1;
        flex-shrink: 0;
        margin-top: 4px;
    }
    .ai-bubble-inner {
        background: #ffffff;
        border: 1px solid rgba(185,155,130,0.2);
        border-radius: 4px 18px 18px 18px;
        padding: 16px 22px;
        max-width: 76%;
        color: #3a322b;
        font-size: 0.94rem;
        line-height: 1.75;
        box-shadow: 0 4px 20px rgba(90,60,40,0.07);
        letter-spacing: 0.01em;
    }

    /* ── XP badge ── */
    .xp-toast {
        display: inline-block;
        background: rgba(184,120,90,0.10);
        border: 1px solid rgba(184,120,90,0.28);
        color: #9a5c3e;
        font-weight: 600;
        font-size: 0.78rem;
        border-radius: 99px;
        padding: 3px 12px;
        margin-top: 10px;
        letter-spacing: 0.02em;
    }

    /* ── Text input ── */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid rgba(185,155,130,0.3) !important;
        border-radius: 14px !important;
        color: #3a322b !important;
        padding: 14px 18px !important;
        font-size: 0.94rem !important;
        font-family: 'DM Sans', sans-serif !important;
        box-shadow: 0 2px 8px rgba(90,60,40,0.04) !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(184,120,90,0.55) !important;
        box-shadow: 0 0 0 3px rgba(184,120,90,0.10) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #b5a99e !important;
    }

    /* ── Buttons ── */
    .stFormSubmitButton > button, .stButton > button {
        background: #b8785a !important;
        color: #fdf9f6 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 3px 10px rgba(184,120,90,0.22) !important;
        letter-spacing: 0.02em !important;
    }
    .stFormSubmitButton > button:hover, .stButton > button:hover {
        background: #a86a4d !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 16px rgba(184,120,90,0.30) !important;
    }

    /* ── Headings ── */
    h1 {
        font-family: 'DM Serif Display', serif !important;
        color: #3a322b !important;
        font-weight: 400 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.3px;
    }
    h2 {
        font-family: 'DM Sans', sans-serif !important;
        color: #4a3e36 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    h3 { color: #5a4a3e !important; font-weight: 500 !important; }

    /* ── Divider ── */
    hr { border-color: rgba(185,155,130,0.2) !important; }

    /* ── Alert ── */
    .stAlert { border-radius: 14px !important; }

    /* ── Captions ── */
    .stCaption, small, caption { color: #8a7a6e !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(185,155,130,0.35); border-radius: 99px; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer { visibility: hidden; }

    /* ── Welcome card ── */
    .welcome-card {
        background: #ffffff;
        border: 1px solid rgba(185,155,130,0.2);
        border-radius: 24px;
        padding: 48px 44px;
        text-align: center;
        box-shadow:
            0 2px 4px rgba(90,60,40,0.04),
            0 8px 24px rgba(90,60,40,0.07),
            0 24px 48px rgba(90,60,40,0.04);
        max-width: 460px;
        margin: 56px auto;
    }
    .welcome-card .paw { font-size: 3.2rem; margin-bottom: 16px; }
    .welcome-card h2 {
        font-family: 'DM Serif Display', serif !important;
        color: #3a322b !important;
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        margin-bottom: 12px;
    }
    .welcome-card p {
        color: #7a6a60;
        line-height: 1.75;
        margin: 0;
        font-size: 0.95rem;
    }
    .welcome-card em { color: #b8785a; font-style: normal; font-weight: 500; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state defaults ─────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "engine" not in st.session_state:
    st.session_state.engine = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐾 小狗狗助理 HQ")
    st.divider()

    # API Key
    st.markdown("**🔑 Gemini API Key**")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="Paste your Gemini API key...",
        label_visibility="collapsed",
    )

    api_key_clean = "".join(c for c in api_key_input.strip() if c.isascii())
    if api_key_clean != st.session_state.api_key:
        st.session_state.api_key = api_key_clean
        st.session_state.engine = None
        st.session_state.messages = []

    if st.session_state.api_key and st.session_state.engine is None:
        with st.spinner("正在唤醒小狗狗... 🐾"):
            st.session_state.engine = PYWTEngine(api_key=st.session_state.api_key)

    st.caption("🔒 Key 仅保存在本次会话，不会被存储。")
    st.divider()

    # Stats
    if st.session_state.engine:
        engine: PYWTEngine = st.session_state.engine
        state = engine.get_state()
        xp_in_level, xp_needed, level = engine.state.xp_progress()

        col1, col2 = st.columns(2)
        col1.metric("等级", f"Lv. {level}")
        col2.metric("经验值", state["xp"])

        st.markdown("**🐾 升级进度**")
        progress_ratio = xp_in_level / xp_needed if xp_needed else 1.0
        st.progress(min(progress_ratio, 1.0))
        st.caption(f"🦴 {xp_in_level} / {xp_needed} XP")

        st.divider()

        st.markdown("**🗺️ 当前任务**")
        quests = state.get("quests", {})
        if quests:
            for qname, q in quests.items():
                icon = "✅" if q["done"] else "🟠"
                pct = int(q["progress"] / q["goal"] * 100) if q["goal"] else 0
                st.markdown(f"{icon} **{qname}**")
                st.progress(pct / 100)
                st.caption(f"🐾 {q['progress']} / {q['goal']} 步完成")
                # Show step list
                for step in q.get("steps", []):
                    step_icon = "✅" if step["done"] else "⬜"
                    st.markdown(
                        f"<span style='font-size:0.82rem;color:#8a7a6e'>"
                        f"{step_icon} {step['title']}</span>",
                        unsafe_allow_html=True,
                    )
        else:
            st.caption("还没有任务 — 让小狗狗帮你创建一个吧！")

        st.divider()

        st.markdown("**📚 已加载技能**")
        for s in engine.skill_manager.names():
            st.markdown(f"🦴 `{s}`")

        if st.button("↺ 重新加载技能", use_container_width=True):
            engine.reload_skills()
            st.success("技能已重新加载！")

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("# 牌有问题 🐾")
st.caption("*人生牌烂，策略为王 — The deck is flawed, but the strategy is king.*")
st.divider()

# Gate: no API key
if not st.session_state.api_key:
    st.markdown(
        """
        <div class="welcome-card">
            <div style="font-size:4rem;margin-bottom:12px">🐾</div>
            <h2>你好，我是小狗狗助理！</h2>
            <p>在左侧边栏粘贴你的 <strong>Gemini API Key</strong>，<br>
            我就可以陪你一起学习啦！<br><br>
            <em>学习很难，但有你陪着我。</em> 🦴</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if st.session_state.engine is None:
    st.info("正在唤醒小狗狗，请稍候...")
    st.stop()

engine: PYWTEngine = st.session_state.engine

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">'
            f'<div class="user-bubble-inner">{msg["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        clean = re.sub(
            r"<(xp_award|quest_create|quest_advance)>.*?</\1>", "", msg["content"], flags=re.DOTALL
        ).strip()
        xp_match = re.search(r'"xp"\s*:\s*(\d+)', msg["content"])
        xp_badge = (
            f'<div><span class="xp-toast">🦴 +{xp_match.group(1)} XP 获得！</span></div>'
            if xp_match and int(xp_match.group(1)) > 0 else ""
        )
        st.markdown(
            f'<div class="ai-bubble">'
            f'  <div class="ai-avatar">🐶</div>'
            f'  <div class="ai-bubble-inner">{clean}{xp_badge}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Input ──────────────────────────────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([9, 1])
    user_input = cols[0].text_input(
        "message",
        placeholder="汇报进度、提问、或让小狗狗给你布置任务... 🦴",
        label_visibility="collapsed",
    )
    submitted = cols[1].form_submit_button("发送 🐾")

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show user bubble immediately
    st.markdown(
        f'<div class="user-bubble">'
        f'<div class="user-bubble-inner">{user_input}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Stream AI response chunk-by-chunk into a live placeholder
    stream_placeholder = st.empty()
    full_reply = ""
    try:
        for chunk in engine.stream_chat(user_input):
            full_reply += chunk
            visible = re.sub(
                r"<(xp_award|quest_create|quest_advance)>.*?</\1>", "", full_reply, flags=re.DOTALL
            ).strip()
            stream_placeholder.markdown(
                f'<div class="ai-bubble">'
                f'  <div class="ai-avatar">🐶</div>'
                f'  <div class="ai-bubble-inner">{visible}▌</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    except Exception as e:
        err = str(e)
        if "503" in err or "UNAVAILABLE" in err:
            msg = "服务器暂时过载，稍等一下再试试吧 🐾"
        elif "429" in err or "RESOURCE_EXHAUSTED" in err:
            msg = "API 请求太频繁啦，休息一下再继续 🦴"
        elif "401" in err or "API_KEY" in err:
            msg = "API Key 好像有问题，检查一下侧边栏的 Key 是否正确 🔑"
        else:
            msg = f"出了点小问题：{err}"
        stream_placeholder.warning(msg)
        st.session_state.messages.pop()  # remove the user message that failed
        st.stop()

    # Final render with XP badge, no cursor
    stream_placeholder.empty()
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.rerun()
