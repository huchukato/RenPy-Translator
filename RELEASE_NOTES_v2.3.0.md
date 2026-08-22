# Release Notes — Ren'Py Translator v2.3.0

🎉 **Ren'Py Translator v2.3.0** brings a Figma-based GUI restyle and a definitive fix for walkthrough mod hint duplication.

---

## ✨ What's New

- **Figma-based GUI restyle** — introduced `ctk_components.py`, a reusable CustomTkinter component library (`CtkStyledButton`, `CtkStyledEntry`, `CtkStyledComboBox`, `CtkStyledCheckBox`, `CtkStyledSwitch`, `CtkStyledLabel`, `CtkStyledTextbox`, `CtkStyledProgressBar`, `CtkStyledTabview`, `CtkStyledFrame`, `CtkIconButton`, `CtkSplitButton`, `CtkStepper`, `CtkNavItem`, `CtkAlertBar`) built from the project's Figma design tokens. The main GUI (`translator_tool.py`) and `SettingsDialog` now use these components, with the color palette fully aligned to the Figma design system.
- **`demo_components.py`** — a standalone showcase of every available styled widget, useful as a visual reference when extending the GUI.

## 🐛 Fixed

- **Walkthrough mod hint duplication** — third-party walkthrough mods (e.g. Ronnu's) compute their choice hints via `renpy.substitute()`. This function also auto-translates strings that exactly match a registered translation, not just `[variable]` placeholders. The previous compatibility patch compared a translated string against an untranslated one to isolate the hint suffix, which failed inconsistently and could show both the translated caption **and** the original English text together. The patch now always measures the suffix using the length of the original (untranslated) caption, so translated choices display correctly with only the mod's hint (still in English) appended — no more duplicated text.

## 🔧 Technical Details

- `tr_writer.py::_wt_override_patch()` now reimplements the mod's own `MENUS` lookup (same `(file, line, caption)` key, same `renpy.substitute()`-based fallback for dynamic captions) instead of relying on the mod's own `get_override` return value, and extracts the hint suffix using the raw, untranslated key length before appending it to the explicitly-translated caption.
- The GUI restyle keeps all existing functionality and event handlers unchanged — only widget construction and color tokens were touched, minimizing the risk of regressions.

---

## 📦 Download

**Ren'Py Translator v2.3.0**

## 🙏 Credits

- UnRen Tools by **huchukato, goobdoob, jimmy5 & Sam**
- rpatool by **[Shiz](https://codeberg.org/shiz/rpatool)**
- unrpyc by **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
