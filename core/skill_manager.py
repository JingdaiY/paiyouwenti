"""
SkillManager — scans /skills for .md files and parses them into structured
skill definitions (Syllabus, Rules, Reward Logic) for injection into the LLM
system prompt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Top-level H2 sections we extract from each skill file.
KNOWN_SECTIONS = {"Syllabus", "Rules", "Reward Logic", "Persona", "Examples"}


@dataclass
class Skill:
    name: str          # derived from filename, e.g. "singing"
    title: str         # first H1 heading in the file
    sections: dict[str, str] = field(default_factory=dict)
    raw: str = ""

    def get(self, section: str, default: str = "") -> str:
        return self.sections.get(section, default)

    def to_prompt_block(self) -> str:
        """Render the skill as a formatted block for injection into a system prompt."""
        lines = [f"### Skill: {self.title}"]
        for section, content in self.sections.items():
            lines.append(f"\n**{section}**\n{content.strip()}")
        return "\n".join(lines)


def _parse_sections(text: str) -> tuple[str, dict[str, str]]:
    """
    Split markdown into (title, sections) where sections are keyed by H2 headings.
    The H1 heading becomes the title; everything before the first H2 is ignored.
    """
    title = ""
    h1_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()

    sections: dict[str, str] = {}
    # Split on H2 headings (## Section Name)
    parts = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    # parts = [preamble, heading1, body1, heading2, body2, ...]
    it = iter(parts[1:])  # skip preamble
    for heading, body in zip(it, it):
        sections[heading.strip()] = body.strip()

    return title, sections


class SkillManager:
    """
    Loads all .md skill files from the skills directory.

    Usage:
        sm = SkillManager()
        sm.load()
        prompt_block = sm.build_system_prompt_block()
    """

    def __init__(self, skills_dir: Path = SKILLS_DIR):
        self.skills_dir = skills_dir
        self._skills: dict[str, Skill] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> None:
        """(Re)scan the skills directory and parse all .md files."""
        self._skills.clear()
        for md_file in sorted(self.skills_dir.glob("*.md")):
            skill = self._load_file(md_file)
            self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def all_skills(self) -> list[Skill]:
        return list(self._skills.values())

    def names(self) -> list[str]:
        return list(self._skills.keys())

    def build_system_prompt_block(self, include: list[str] | None = None) -> str:
        """
        Return a concatenated prompt block for all (or a subset of) skills.

        Args:
            include: optional list of skill names to include; if None, include all.
        """
        skills = (
            [s for n, s in self._skills.items() if n in include]
            if include
            else self.all_skills()
        )
        if not skills:
            return ""
        blocks = [s.to_prompt_block() for s in skills]
        header = "---\n## Loaded Skills & Rules\n"
        return header + "\n\n".join(blocks) + "\n---"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_file(self, path: Path) -> Skill:
        raw = path.read_text(encoding="utf-8")
        title, sections = _parse_sections(raw)
        name = path.stem.lower().replace(" ", "_")
        if not title:
            title = name.replace("_", " ").title()
        return Skill(name=name, title=title, sections=sections, raw=raw)
