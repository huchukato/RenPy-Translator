# Release Notes — Ren'Py Translator v2.1.0

🎉 **Ren'Py Translator v2.1.0** is a major UI update that adds a more flexible, reviewable translation workflow and improves the overall speed and reliability of the translation backends.

---

## ✨ What's New

- **Multi-step translation workflow** — the single "Start Translation" pipeline is replaced by:
  - **Analyze & Translate** — extracts, decompiles, parses and translates the game in one click.
  - **Editable translation table** — click any row to review and edit the machine translation before saving.
  - **Save Translation** — writes the reviewed translations to `game/tl/<lang>/` and installs the activator.
  - **Export** — creates a standalone `GameName/game/tl/<lang>/` folder plus activator, without requiring the game to have been patched first.
- **Simplified backend menu** — only the recommended backends are exposed:
  - **Google Turbo**
  - **Bing Turbo**
  - **OpenRouter**
  - **Llama Local**
- **Translation profiles** — choose a profile next to the backend selector:
  - **Safe** — 2 workers, conservative request pacing.
  - **Balanced** — 4 workers, recommended default.
  - **Fast** — 6 workers, no added delay.
- **Google Turbo enhancements** — 12 mirror endpoints, reusable HTTP sessions, mirror health tracking, adaptive pacing, and exponential backoff on rate limits.
- **Persistent translation cache** — completed translations are saved per language pair in `~/.cache/renpy-translator/`, skipping already translated strings on later runs.
- **Options bar** — `Preserve names` and `Translate Menu` are now toggle switches in a dedicated row.
- **`renpy.input()` prompts** and Ren'Py native `_("...")` UI strings are now extracted and translated.
- **Export folders** now use the actual game name, e.g. `LustLine-italian/`.
- **Remembered preferences** — selected backend, profile, target language, verbose logging and last selected game path are persisted.

## 🐛 Fixed

- Dialogues with Ren'Py tags (`{i}`, `{b}`, `{color=...}`) were silently skipped.
- Menu choices like `Exit`, `Continue`, `Save` and `Load` were filtered out as Python identifiers.
- Multiline translations caused `Could not parse string` runtime errors.
- `screens.rpyc` was excluded from decompilation, so main-menu labels (Start/Load/Quit) were never parsed.
- The splash screen could reappear every time the player returned to the main menu.
- Export folders were named `autorun-italian` instead of the actual game name.
- Google Turbo now correctly falls back to individual translations when the chunk separator is altered.

## 🗑️ Removed

- Single "Start Translation" pipeline (replaced by the Analyze & Translate / Save / Export workflow).
- Non-Turbo Google and Bing backends from the GUI selector.

## 🚀 Quick Workflow

1. Select the game folder (or `.app` on macOS).
2. Choose a **target language** and **backend**.
3. Pick a **translation profile** (`Safe`, `Balanced` or `Fast`).
4. Click **Analyze & Translate**.
5. Review and edit translations in the table.
6. Click **Save Translation** to install the translation in the game.
7. Optionally click **Export** to create a distributable `GameName-<lang>/` folder.

## 📦 Download

**Ren'Py Translator v2.1.0**

## 🙏 Credits

- UnRen Tools by **huchukato, goobdoob, jimmy5 & Sam**
- rpatool by **[Shiz](https://codeberg.org/shiz/rpatool)**
- unrpyc by **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
