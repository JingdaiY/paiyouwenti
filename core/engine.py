"""
PaiyouWenTi Engine — orchestrates the LLM call (Gemini), skill injection,
state management, and XP calculation.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Generator

from google import genai
from google.genai import types

from core.skill_manager import SkillManager
from core.state import StateManager

STATE_PATH = Path(__file__).parent.parent / "state" / "deck_state.json"
SKILLS_DIR = Path(__file__).parent.parent / "skills"

GEMINI_MODEL = "gemini-3-flash-preview"

_BASE_SYSTEM = """\
You are 小狗狗助理 — warm, loyal, encouraging. Keep replies short and punchy.
Use dog metaphors (digging/fetching/bones). Acknowledge feelings before evaluating.

After every reply include these silent system tags (user never sees them):
- XP: <xp_award>{"xp":<int>,"reason":"<one line>"}</xp_award>
- New quest: <quest_create>{"name":"<short name>","steps":["step1","step2",...]}</quest_create>
- Progress: <quest_advance>{"name":"<quest name>"}</quest_advance>

5-10 concrete steps per quest. Never shame or guilt-trip.
"""


class PYWTEngine:
    """
    Wrapper around the Gemini API that handles:
    - System prompt construction (base + skills)
    - Conversation history via stateful Chat
    - XP extraction and state updates
    - Streaming responses
    """

    def __init__(
        self,
        api_key: str | None = None,
        active_skills: list[str] | None = None,
    ):
        api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        # Strip whitespace and non-ASCII characters that break HTTP headers
        api_key = "".join(c for c in api_key.strip() if c.isascii())
        self._client = genai.Client(api_key=api_key)

        self.skill_manager = SkillManager(SKILLS_DIR)
        self.skill_manager.load()

        self.state = StateManager(STATE_PATH)

        self._active_skills = active_skills  # None → all skills
        self._chat = self._new_chat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """Send a message and return the full response string."""
        response = self._chat.send_message(user_message)
        reply = response.text
        self._process_reply(reply)
        return reply

    def stream_chat(self, user_message: str) -> Generator[str, None, None]:
        """Yield response chunks as they arrive (for Streamlit streaming)."""
        full_reply = ""
        for chunk in self._chat.send_message_stream(user_message):
            text = chunk.text or ""
            full_reply += text
            yield text
        self._process_reply(full_reply)

    def reload_skills(self, active_skills: list[str] | None = None) -> None:
        """Hot-reload skills from disk and rebuild the chat session."""
        self._active_skills = active_skills
        self.skill_manager.load()
        self._chat = self._new_chat()

    def get_state(self) -> dict:
        return self.state.load()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _new_chat(self) -> genai.chats.Chat:
        system_prompt = self._build_system_prompt()
        return self._client.chats.create(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )

    def _build_system_prompt(self) -> str:
        skills_block = self.skill_manager.build_system_prompt_block(
            include=self._active_skills
        )
        return _BASE_SYSTEM + ("\n\n" + skills_block if skills_block else "")

    def _process_reply(self, reply: str) -> None:
        """Parse all action tags from a model reply and apply them to state."""
        self._extract_and_apply_xp(reply)
        self._extract_and_apply_quests(reply)

    def _extract_and_apply_xp(self, reply: str) -> None:
        match = re.search(r"<xp_award>(.*?)</xp_award>", reply, re.DOTALL)
        if not match:
            return
        try:
            award = json.loads(match.group(1))
            xp_gained = int(award.get("xp", 0))
            if xp_gained > 0:
                self.state.add_xp(xp_gained)
        except (json.JSONDecodeError, ValueError):
            pass

    def _extract_and_apply_quests(self, reply: str) -> None:
        # Create new quests
        for raw in re.findall(r"<quest_create>(.*?)</quest_create>", reply, re.DOTALL):
            try:
                data = json.loads(raw)
                self.state.add_quest(
                    data["name"],
                    int(data.get("goal", len(data.get("steps", [])))),
                    steps=data.get("steps"),
                )
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # Advance existing quests
        for raw in re.findall(r"<quest_advance>(.*?)</quest_advance>", reply, re.DOTALL):
            try:
                data = json.loads(raw)
                self.state.advance_quest(data["name"])
            except (json.JSONDecodeError, KeyError):
                pass
