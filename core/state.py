"""
StateManager — persists and mutates deck_state.json.
Tracks XP, Level, and Quest progress.
"""

from __future__ import annotations

import json
from pathlib import Path

# XP required to reach each level (cumulative thresholds)
LEVEL_THRESHOLDS = [0, 100, 250, 500, 900, 1500, 2500, 4000, 6000, 9000]

DEFAULT_STATE: dict = {
    "xp": 0,
    "level": 1,
    "quests": {},          # {quest_name: {"progress": int, "goal": int, "done": bool}}
    "history_summary": "", # periodically summarised by LLM for long-term memory
}


def _xp_to_level(xp: int) -> int:
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    return min(level, len(LEVEL_THRESHOLDS))


def _xp_for_next_level(level: int) -> int:
    """Return the XP needed to reach the next level (or 0 if max)."""
    idx = level  # LEVEL_THRESHOLDS[level] is the threshold for level+1
    if idx >= len(LEVEL_THRESHOLDS):
        return 0
    return LEVEL_THRESHOLDS[idx]


class StateManager:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(DEFAULT_STATE.copy())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> dict:
        with self.path.open(encoding="utf-8") as f:
            return json.load(f)

    def add_xp(self, amount: int) -> dict:
        """Add XP, recalculate level, persist, and return updated state."""
        state = self.load()
        state["xp"] = max(0, state["xp"] + amount)
        state["level"] = _xp_to_level(state["xp"])
        self._write(state)
        return state

    def advance_quest(self, quest_name: str, increment: int = 1) -> dict:
        state = self.load()
        quest = state["quests"].get(quest_name)
        if quest and not quest.get("done"):
            # Mark the next incomplete step as done
            steps = quest.get("steps", [])
            for step in steps:
                if not step["done"]:
                    step["done"] = True
                    break
            quest["progress"] = min(quest["progress"] + increment, quest["goal"])
            quest["done"] = quest["progress"] >= quest["goal"]
        self._write(state)
        return state

    def add_quest(self, name: str, goal: int, steps: list[str] | None = None) -> dict:
        state = self.load()
        if name not in state["quests"]:
            step_list = (
                [{"title": t, "done": False} for t in steps]
                if steps
                else [{"title": f"步骤 {i+1}", "done": False} for i in range(goal)]
            )
            state["quests"][name] = {
                "progress": 0,
                "goal": len(step_list),
                "done": False,
                "steps": step_list,
            }
            self._write(state)
        return state

    def xp_progress(self) -> tuple[int, int, int]:
        """Return (current_xp_in_level, xp_needed_for_next, level)."""
        state = self.load()
        xp = state["xp"]
        level = state["level"]
        current_floor = LEVEL_THRESHOLDS[level - 1]
        next_threshold = _xp_for_next_level(level)
        if next_threshold == 0:
            return xp - current_floor, 1, level  # max level
        return xp - current_floor, next_threshold - current_floor, level

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _write(self, state: dict) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
