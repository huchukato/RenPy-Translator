# 🌐 Ren'Py Translator

<p align="center">
  <img src="logo_512.png" alt="Ren'Py Translator Logo" width="160">
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/🇬🇧-Read%20in%20English-blue?style=flat-square" alt="Read in English"></a>
</p>

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![GUI](https://img.shields.io/badge/GUI-customtkinter-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> Uno strumento GUI universale per tradurre automaticamente i giochi Ren'Py — estrae gli script, rileva dialoghi e narrazione, e scrive i file di traduzione compatibili con Ren'Py (`tl/<lingua>/`).

<p align="center">
  <img src="translator-gui.png" alt="Ren'Py Translator GUI" width="800">
</p>

---

## ✨ Funzionalità

| Funzione | Descrizione |
|---|---|
| 📦 **Estrazione automatica** | Estrae archivi `.rpa` e decompila file `.rpyc` automaticamente |
| 🧠 **Parsing intelligente** | Rileva dialoghi, narrazione, scelte di menu e testi UI |
| 🌍 **Più backend** | Google, Bing, Bing Turbo, Bing Ultra, LibreTranslate, OpenRouter, llama_cpp |
| ⚡ **Bing Turbo / Ultra** | Pool di sessioni parallele (3–6 worker) per traduzioni fino a 6× più veloci |
| 🔒 **Protezione token** | Preserva i tag Ren'Py `{color=...}`, `[variabile]`, ecc. durante la traduzione |
| 📄 **Tabella paginata** | Gestisce 10.000+ stringhe senza bloccarsi — 100 righe per pagina |
| 💾 **Output file TL** | Scrive file `game/tl/<lingua>/` standard compatibili con Ren'Py |
| 🌐 **Interfaccia IT / EN** | Passa dall'italiano all'inglese con un click |

---

## 🚀 Avvio rapido

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```bat
start.bat
```

Le dipendenze vengono installate automaticamente tramite `uv` al primo avvio.

---

## 🔧 Flusso di lavoro

1. **Seleziona il gioco** — `.app` (macOS) o cartella del gioco (Windows/Linux)
2. **Scegli lingua target e backend**
3. **Clicca Start Translation** — estrae, decompila, analizza, traduce e salva `game/tl/<lingua>/` automaticamente con avanzamento in tempo reale
4. **Export** — crea una cartella distribuibile chiamata `<NomeGioco>-<lingua>/`

---

## 🌍 Backend di traduzione

| Backend | Velocità | Requisiti |
|---|---|---|
| **Google Turbo** | Veloce (12 mirror, parallelo, resistente ai rate limit) | nessuno (gratuito) |
| **Bing Turbo** | Veloce (sessioni parallele) | nessuno (gratuito) |
| **OpenRouter** | Medio | API key su openrouter.ai |
| **Llama Local** | Lento | modello `.gguf` locale via llama_cpp |

---

## 🛡️ Profili di traduzione

Scegli un profilo nelle **Impostazioni** per Google Turbo e Bing Turbo:

| Profilo | Worker | Ritmo richieste | Uso consigliato |
|---|---:|---|---|
| **Safe** | 2 | Ritardo casuale di 350ms | Traduzioni lunghe; minor rischio di rate limit |
| **Balanced** | 4 | Ritardo casuale di 120ms | Predefinito; equilibrio tra velocità e affidabilità |
| **Fast** | 6 | Nessun ritardo aggiuntivo | Lavori brevi; rischio maggiore di rate limit |

Google Turbo usa sempre controllo salute dei mirror, sessioni HTTP riutilizzabili, ritmo adattivo e backoff esponenziale dopo risposte rate-limited.

## 💾 Cache delle traduzioni

Le traduzioni completate vengono memorizzate per coppia di lingue in `~/.cache/renpy-translator/`. Rieseguire una traduzione salta i testi già in cache, riducendo tempi e richieste ai servizi di traduzione.

---

## ⚙️ Opzioni

| Opzione | Descrizione |
|---|---|
| **Preserve names** | Salta le parole singole in maiuscolo (nomi dei personaggi) |
| **Translate Menu** | Traduce anche le scelte di menu e i testi UI |
| **Verbose log** | Logga ogni stringa tradotta (disabilitato di default per le performance) |

---

## 📦 Installazione manuale

```bash
pip install customtkinter pillow deep-translator requests
```

---

## 🎮 Uso con WTForge

Se usi anche **[Ren'Py WTForge](https://github.com/huchukato/RenPy-WTForge)** per generare una mod walkthrough, **traduci sempre prima**, poi genera la mod — così WTForge include automaticamente i testi tradotti.

---

## 🙏 Crediti

- Tool di **[huchukato](https://f95zone.to/members/huchukato.11155677/)** (F95Zone)
- UnRen Tools di **huchukato, goobdoob, jimmy5 & Sam**
- rpatool di **[Shiz](https://codeberg.org/shiz/rpatool)**
- unrpyc di **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
