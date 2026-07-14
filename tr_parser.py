#!/usr/bin/env python3
"""
Ren'Py Translator - Parser Module
Estrae stringhe traducibili dai file .rpy
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class ExtractedString:
    kind: str       # "dialogue" | "narration" | "menu" | "ui"
    text: str
    file: str
    line: int
    speaker: str | None
    translated: str = ""


_TECHNICAL = {"style", "define", "transform", "init", "key", "image", "python", "translate"}
_NON_DIALOGUE = {"scene", "show", "hide", "play", "stop", "queue", "voice",
                 "with", "jump", "call", "return", "label", "pause", "window"}
_RE_MENU = re.compile(r'^\s*menu\b.*:\s*$')
_RE_COMMENT = re.compile(r'^\s*#')
_RE_TRANSLATE = re.compile(r'^(\s*)translate\s+\w+\s+.*:\s*$')
_RE_SCREEN = re.compile(r'^\s*screen\s+\w+\b.*:\s*$')
_RE_SAY = re.compile(r'^(\s*)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(?:\s+[^\s"]+)*\s*"')
_RE_UI = re.compile(r'^\s*(textbutton|text|label|tooltip)\s+"')
_RE_DEFAULT = re.compile(r'^\s*default\s+(\w+)\s*=\s*"')
_RE_HEX = re.compile(r"^#?[0-9a-fA-F]{3,8}$")
_RE_CHARACTER = re.compile(r'^\s*define\s+\w+\s*=\s*Character\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
_RE_ONLY_VARS = re.compile(r'^(\[[^\]]+\]|\{[^}]+\}|[\s$%.,!?])+$')


def extract_character_names(game_dir: Path) -> set[str]:
    """
    Scansiona tutti i .rpy in game_dir e raccoglie i nomi dai define:
        define sac = Character('Sacha', ...)
    Restituisce un set di stringhe come {'Sacha', 'Sarah', 'Mila', ...}.
    """
    names: set[str] = set()
    for rpy in game_dir.rglob("*.rpy"):
        try:
            for line in rpy.read_text(encoding="utf-8", errors="replace").splitlines():
                m = _RE_CHARACTER.match(line)
                if m:
                    name = m.group(1).strip()
                    if name and not name.startswith("{"):
                        names.add(name)
        except Exception:
            pass
    return names


def _indent(s: str) -> int:
    return len(s) - len(s.lstrip())


def _first_quoted(line: str) -> str | None:
    i, n = 0, len(line)
    while i < n:
        if line[i] == '"':
            i += 1
            buf, escaped = [], False
            while i < n:
                ch = line[i]
                if escaped:
                    buf.append(ch); escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    return ''.join(buf)
                else:
                    buf.append(ch)
                i += 1
            return None
        i += 1
    return None


def _ok(text: str) -> bool:
    t = text.strip()
    if not t or _RE_HEX.match(t):
        return False
    if all(ch in ".!?…,-:; " for ch in t):
        return False
    if t.isidentifier():
        return False
    if t.startswith("[") and t.endswith("]"):
        return False
    if _RE_ONLY_VARS.match(t):
        return False
    if any(t.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif")):
        return False
    if "/" in t or "\\" in t:
        return False
    return True


def parse_rpy_file(file_path: Path, rel_from: Path, translate_menu: bool = True) -> list[ExtractedString]:
    rel = str(file_path.relative_to(rel_from)).replace("\\", "/")
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    lines = content.splitlines()
    results: list[ExtractedString] = []
    seen_texts: set[str] = set()

    in_menu = False; menu_ind = 0
    in_tl = False; tl_ind = 0
    in_tech = False; tech_ind = 0
    in_screen = False; screen_ind = 0

    for idx, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or _RE_COMMENT.match(stripped):
            continue

        m = _RE_TRANSLATE.match(raw)
        if m:
            in_tl = True; tl_ind = _indent(m.group(1)); continue
        if in_tl:
            if _indent(raw) <= tl_ind and not raw.lstrip().startswith('#'):
                in_tl = False
            else:
                continue

        if _RE_SCREEN.match(raw):
            in_screen = True; screen_ind = _indent(raw); continue
        if in_screen:
            if _indent(raw) <= screen_ind and not raw.lstrip().startswith('#'):
                in_screen = False
            else:
                if translate_menu and _RE_UI.match(raw):
                    t = _first_quoted(raw)
                    if t and _ok(t) and t not in seen_texts:
                        seen_texts.add(t); results.append(ExtractedString("ui", t, rel, idx, None))
                continue

        fw = stripped.split(" ", 1)[0].rstrip(":")
        if stripped.endswith(":") and fw in _TECHNICAL:
            in_tech = True; tech_ind = _indent(raw); continue
        if in_tech:
            if _indent(raw) <= tech_ind and not raw.lstrip().startswith('#'):
                in_tech = False
            else:
                continue

        if _RE_MENU.match(raw):
            in_menu = True; menu_ind = _indent(raw); continue
        if in_menu:
            if _indent(raw) <= menu_ind and not raw.lstrip().startswith('#'):
                in_menu = False
            else:
                t = _first_quoted(raw)
                if t and _ok(t):
                    after = raw[raw.index(t) + len(t) + 1:]
                    if raw.lstrip().startswith('"') and ':' in after:
                        if translate_menu and t not in seen_texts:
                            seen_texts.add(t); results.append(ExtractedString("menu", t, rel, idx, None))
                    elif raw.lstrip().startswith('"'):
                        if t not in seen_texts:
                            seen_texts.add(t); results.append(ExtractedString("narration", t, rel, idx, None))
                    else:
                        m2 = _RE_SAY.match(raw)
                        if m2:
                            sp = m2.group(2).split(".", 1)[0]
                            if sp not in _NON_DIALOGUE and sp not in _TECHNICAL and t not in seen_texts:
                                seen_texts.add(t); results.append(ExtractedString("dialogue", t, rel, idx, m2.group(2)))
                continue

        if stripped.startswith('$'):
            continue

        m_def = _RE_DEFAULT.match(raw)
        if m_def:
            t = _first_quoted(raw)
            if t and _ok(t) and t not in seen_texts:
                seen_texts.add(t); results.append(ExtractedString("ui", t, rel, idx, None))
            continue

        m_say = _RE_SAY.match(raw)
        if m_say:
            sp = m_say.group(2).split(".", 1)[0]
            if sp in _NON_DIALOGUE or sp in _TECHNICAL or sp in {"old", "new"}:
                continue
            t = _first_quoted(raw)
            if t and _ok(t) and t not in seen_texts:
                seen_texts.add(t); results.append(ExtractedString("dialogue", t, rel, idx, m_say.group(2)))
            continue

        if raw.lstrip().startswith('"'):
            t = _first_quoted(raw)
            if t and _ok(t) and t not in seen_texts:
                seen_texts.add(t); results.append(ExtractedString("narration", t, rel, idx, None))
            continue

        if translate_menu and _RE_UI.match(raw):
            t = _first_quoted(raw)
            if t and _ok(t) and t not in seen_texts:
                seen_texts.add(t); results.append(ExtractedString("ui", t, rel, idx, None))

    return results
