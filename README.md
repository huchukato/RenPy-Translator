# 🌐 Ren'Py Translator

<p align="center">
  <img src="logo_512.png" alt="Ren'Py Translator Logo" width="160">
</p>

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![GUI](https://img.shields.io/badge/GUI-customtkinter-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> A universal GUI tool to automatically translate Ren'Py games — extracts scripts, detects dialogue and narration, and writes Ren'Py-compatible translation files (`tl/<lang>/`).

---

## ✨ Features

| Feature | Description |
|---|---|
| 📦 **Auto Extraction** | Extracts `.rpa` archives and decompiles `.rpyc` files automatically |
| 🧠 **Smart Parsing** | Detects dialogue, narration, menu choices, and UI strings |
| 🌍 **Multiple Backends** | Google Translate, LibreTranslate, OpenRouter (free models), local llama_cpp |
| 🔒 **Token Protection** | Preserves Ren'Py tags `{color=...}`, `[variable]`, etc. during translation |
| ✏️ **Manual Edit** | Edit any translation directly in the table |
| 💾 **TL File Output** | Writes standard `game/tl/<lang>/` files compatible with Ren'Py |
| 🌐 **EN / IT** | Switch between English and Italian interface |

---

## 🚀 Quick Start

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```bat
start.bat
```

---

## 🔧 Workflow

1. **Select Game** — `.app` (macOS) or folder (Windows/Linux)
2. **Analyze Game** — extracts `.rpa`, decompiles `.rpyc`, scans scripts
3. **Choose target language and backend**
4. **Translate All** — translates all strings in background
5. **Save TL Files** — writes `game/tl/<lang>/` in the game directory

---

## 📦 Installation

Dependencies are installed automatically via `uv` when you run the startup scripts.

Manual:
```bash
pip install customtkinter pillow deep-translator requests
```

---

## 🙏 Credits

- GUI by **[huchukato](https://f95zone.to/members/huchukato.11155677/)** (F95Zone)
- UnRen Tools by **huchukato, goobdoob, jimmy5 & Sam**
- rpatool by **[Shiz](https://codeberg.org/shiz/rpatool)**
- unrpyc by **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
