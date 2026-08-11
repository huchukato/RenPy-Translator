# Release Notes — Ren'Py Translator v2.2.0

🎉 **Ren'Py Translator v2.2.0** adds full compatibility with third-party walkthrough mods and expands the build system to all platforms.

---

## ✨ What's New

- **Walkthrough mod compatibility** — when a game includes a third-party walkthrough mod (e.g. Ronnu's WT) that uses a `MENUS` dictionary for choice hints, the translator now auto-generates a compatibility patch. The patch scans `tl/` for translated captions and builds a lookup table so that hints display correctly even when choices are translated.
- **Build scripts for all platforms:**
  - `build/build_mac_app.sh` — now automatically creates a `.dmg` installer with an Applications symlink for drag-and-drop install.
  - `build/build_linux.sh` — creates a `.tar.gz` archive with an embedded Python venv (self-contained).
  - `build/build_win.sh` — creates a `.zip` that auto-creates a venv on first launch via `start.bat`.
- **DMG naming** — macOS DMG is named `RenPy-Translator[vX.Y.Z]-<arch>.dmg` (e.g. `RenPy-Translator[v2.2.0]-arm64.dmg`).

## 🐛 Fixed

- Walkthrough mod hints (e.g. "(recommended)", variable effects) were not displayed after translation because the mod's `get_override` function could not match translated captions to the English-only `MENUS` dictionary keys.
- Parser no longer extracts `MENUS` dictionary values for translation (Ren'Py does not translate strings inside `init python` blocks, so these translations were dead and caused lookup mismatches).

## 🔧 Technical Details

The walkthrough mod patch (`renpy_translator_wt_patch.rpy`) is generated in `game/` (not in `tl/`, where Ren'Py ignores `init python` blocks). At init time it:
1. Scans all `tl/<lang>/*.rpy` files to build a `{translated_caption: original_caption}` map.
2. For each `MENUS` key, registers both the original and translated caption pointing to the same hint.
3. Wraps `get_override` with a fallback that matches translated captions via this lookup table.

---

## 📦 Download

**Ren'Py Translator v2.2.0**

## 🙏 Credits

- UnRen Tools by **huchukato, goobdoob, jimmy5 & Sam**
- rpatool by **[Shiz](https://codeberg.org/shiz/rpatool)**
- unrpyc by **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
