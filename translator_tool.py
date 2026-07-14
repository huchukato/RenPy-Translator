#!/usr/bin/env python3
"""
Ren'Py Translator - Main GUI
"""

import threading
import json
import os
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

from tr_extractor import TRExtractor
from tr_parser import parse_rpy_file, ExtractedString
from tr_translator import Translator, TranslatorConfig, TranslationError, OPENROUTER_FREE_MODELS, LANG_NAMES
from tr_writer import write_tl_files, write_activator

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ─── Costanti ────────────────────────────────────────────────────────────────

APP_TITLE = "Ren'Py Translator"
VERSION   = "2.0.0"
SCRIPT_DIR = Path(__file__).parent
SETTINGS_FILE = SCRIPT_DIR / "translator_settings.json"

LANGUAGES = {
    "English": "en", "Italian": "it", "French": "fr", "Spanish": "es",
    "German": "de", "Portuguese": "pt", "Japanese": "ja", "Chinese": "zh",
    "Russian": "ru", "Korean": "ko", "Arabic": "ar",
}
BACKENDS = ["google", "bing", "bing_turbo", "bing_ultra", "openrouter", "llama"]

UI_TEXTS = {
    "en": {
        "game_selection": "Game Selection",
        "game_selected": "Game selected",
        "no_game": "No game selected",
        "btn_app": ".app",
        "btn_folder": "Folder",
        "strings_tab": "Strings",
        "log_tab": "Log",
        "filter_all": "All",
        "filter_translated": "Translated",
        "filter_untranslated": "Untranslated",
        "target_lang": "Target language:",
        "backend": "Backend:",
        "analyze": "Analyze Game",
        "translate_all": "Translate All",
        "translate_sel": "Translate Selected",
        "save_tl": "Save TL Files",
        "settings": "Settings",
        "cancel": "Cancel",
        "analysis_complete": "Analysis complete: {} strings in {} files",
        "translation_complete": "Translation complete: {}/{} strings",
        "saved": "Saved {} files in {}",
        "error": "Error",
        "col_num": "#",
        "col_kind": "Kind",
        "col_speaker": "Speaker",
        "col_original": "Original",
        "col_translation": "Translation",
        "col_file": "File",
    },
    "it": {
        "game_selection": "Selezione Gioco",
        "game_selected": "Gioco selezionato",
        "no_game": "Nessun gioco selezionato",
        "btn_app": ".app",
        "btn_folder": "Cartella",
        "strings_tab": "Stringhe",
        "log_tab": "Log",
        "filter_all": "Tutte",
        "filter_translated": "Tradotte",
        "filter_untranslated": "Non tradotte",
        "target_lang": "Lingua target:",
        "backend": "Backend:",
        "analyze": "Analizza Gioco",
        "translate_all": "Traduci Tutto",
        "translate_sel": "Traduci Selezionate",
        "save_tl": "Salva File TL",
        "settings": "Impostazioni",
        "cancel": "Annulla",
        "analysis_complete": "Analisi completata: {} stringhe in {} file",
        "translation_complete": "Traduzione completata: {}/{} stringhe",
        "saved": "Salvati {} file in {}",
        "error": "Errore",
        "col_num": "#",
        "col_kind": "Tipo",
        "col_speaker": "Personaggio",
        "col_original": "Originale",
        "col_translation": "Traduzione",
        "col_file": "File",
    },
}

# ─── Tema ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG       = "#1a1025"
COLOR_PANEL    = "#231535"
COLOR_ACCENT   = "#3d2060"
COLOR_BTN_MAIN = "#7c3aed"
COLOR_BTN_ALT  = "#06b6d4"
COLOR_BTN_WARN = "#e11d48"
COLOR_TEXT     = "#f0e6ff"
COLOR_SUBTEXT  = "#a78bfa"


# ─── Settings Dialog ─────────────────────────────────────────────────────────
class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("500x460")
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self._load()

    def _build(self):
        pad = {"padx": 16, "pady": 6}
        ctk.CTkLabel(self, text="OpenRouter API Key:").pack(anchor="w", **pad)
        self.or_key = ctk.CTkEntry(self, width=460, show="*")
        self.or_key.pack(**pad)

        ctk.CTkLabel(self, text="OpenRouter Model:").pack(anchor="w", **pad)
        self.or_model = ctk.CTkComboBox(self, values=OPENROUTER_FREE_MODELS, width=460)
        self.or_model.pack(**pad)

        ctk.CTkLabel(self, text="llama model repo (HuggingFace):").pack(anchor="w", **pad)
        self.llama_repo = ctk.CTkEntry(self, width=460)
        self.llama_repo.pack(**pad)

        ctk.CTkLabel(self, text="llama model file (.gguf):").pack(anchor="w", **pad)
        self.llama_file = ctk.CTkEntry(self, width=460)
        self.llama_file.pack(**pad)

        ctk.CTkButton(self, text="Save", command=self._save,
                      fg_color=COLOR_BTN_MAIN).pack(pady=12)

    def _load(self):
        s = self.parent.settings
        self.or_key.insert(0, s.get("openrouter_api_key", ""))
        self.or_model.set(s.get("openrouter_model", OPENROUTER_FREE_MODELS[0]))
        self.llama_repo.insert(0, s.get("llama_model_repo", "llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic-GGUF"))
        self.llama_file.insert(0, s.get("llama_model_file", ""))

    def _save(self):
        self.parent.settings.update({
            "openrouter_api_key": self.or_key.get().strip(),
            "openrouter_model": self.or_model.get(),
            "llama_model_repo": self.llama_repo.get().strip(),
            "llama_model_file": self.llama_file.get().strip(),
        })
        self.parent._save_settings()
        self.destroy()


# ─── Main Window ─────────────────────────────────────────────────────────────
class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=COLOR_BG)

        self.lang = "en"
        self.game_path: Path | None = None
        self.extractor: TRExtractor | None = None
        self.items: list[ExtractedString] = []
        self._filtered: list[ExtractedString] = []
        self._page = 0
        self._page_size = 100
        self.translator: Translator | None = None
        self.settings: dict = {}
        self._load_settings()
        self._build_ui()
        self._set_icon()

    # ─── UI Build ──────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=80)
        top.pack(fill="x", padx=0, pady=0)
        top.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(top, text="")
        self.logo_label.pack(side="left", padx=12, pady=8)
        self._set_logo(top)

        game_frame = ctk.CTkFrame(top, fg_color="transparent")
        game_frame.pack(side="left", fill="both", expand=True, padx=8)

        self.game_section_label = ctk.CTkLabel(game_frame, text=self.t("game_selection"),
                                               font=ctk.CTkFont(size=12, weight="bold"),
                                               text_color=COLOR_SUBTEXT)
        self.game_section_label.pack(anchor="w")

        path_row = ctk.CTkFrame(game_frame, fg_color="transparent")
        path_row.pack(fill="x")
        self.path_entry = ctk.CTkEntry(path_row, width=500, placeholder_text="...")
        self.path_entry.pack(side="left", padx=(0, 6))
        ctk.CTkButton(path_row, text=self.t("btn_app"), width=60,
                      fg_color=COLOR_ACCENT, command=self._pick_app).pack(side="left", padx=2)
        ctk.CTkButton(path_row, text=self.t("btn_folder"), width=80,
                      fg_color=COLOR_ACCENT, command=self._pick_folder).pack(side="left", padx=2)

        self.game_status = ctk.CTkLabel(game_frame, text=self.t("no_game"),
                                        text_color=COLOR_SUBTEXT, font=ctk.CTkFont(size=11))
        self.game_status.pack(anchor="w")

        # Progress
        prog_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=36)
        prog_frame.pack(fill="x", padx=0, pady=(2, 0))
        prog_frame.pack_propagate(False)
        self.progress = ctk.CTkProgressBar(prog_frame, height=14)
        self.progress.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(prog_frame, text="", text_color=COLOR_SUBTEXT,
                                           font=ctk.CTkFont(size=11))
        self.progress_label.pack(side="right", padx=12)

        # Filter + lang row
        ctrl = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=44)
        ctrl.pack(fill="x", pady=(2, 0))
        ctrl.pack_propagate(False)

        ctk.CTkLabel(ctrl, text="Filter:", text_color=COLOR_SUBTEXT).pack(side="left", padx=(12, 4))
        self.filter_var = ctk.StringVar(value="all")
        for val, key in [("all", "filter_all"), ("translated", "filter_translated"),
                         ("untranslated", "filter_untranslated")]:
            rb = ctk.CTkRadioButton(ctrl, text=self.t(key), variable=self.filter_var,
                                    value=val, command=self._apply_filter)
            rb.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl, text=self.t("target_lang"), text_color=COLOR_SUBTEXT).pack(side="left", padx=(20, 4))
        self.lang_var = ctk.StringVar(value="Italian")
        self.lang_combo = ctk.CTkComboBox(ctrl, values=list(LANGUAGES.keys()), width=130,
                                          variable=self.lang_var)
        self.lang_combo.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl, text=self.t("backend"), text_color=COLOR_SUBTEXT).pack(side="left", padx=(16, 4))
        self.backend_var = ctk.StringVar(value=self.settings.get("backend", "bing_ultra"))
        self.backend_combo = ctk.CTkComboBox(ctrl, values=BACKENDS, width=120,
                                             variable=self.backend_var)
        self.backend_combo.pack(side="left", padx=4)

        self.preserve_names_var = ctk.BooleanVar(value=self.settings.get("preserve_names", False))
        ctk.CTkCheckBox(ctrl, text="Preserve names", variable=self.preserve_names_var,
                        command=self._on_checkbox).pack(side="left", padx=(16, 4))

        self.translate_ui_var = ctk.BooleanVar(value=self.settings.get("translate_menu", False))
        ctk.CTkCheckBox(ctrl, text="Translate UI", variable=self.translate_ui_var,
                        command=self._on_checkbox).pack(side="left", padx=4)

        # Tabs
        self.tabs = ctk.CTkTabview(self, fg_color=COLOR_PANEL)
        self.tabs.pack(fill="both", expand=True, padx=0, pady=(2, 0))
        self.tab_strings = self.tabs.add(self.t("strings_tab"))
        self.tab_log = self.tabs.add(self.t("log_tab"))
        self._build_strings_tab()
        self._build_log_tab()

        # Bottom buttons
        bottom = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=56)
        bottom.pack(fill="x", pady=(2, 0))
        bottom.pack_propagate(False)

        self.btn_analyze = ctk.CTkButton(bottom, text=self.t("analyze"),
                                         fg_color=COLOR_BTN_MAIN, width=140, command=self._analyze)
        self.btn_analyze.pack(side="left", padx=10, pady=10)

        self.btn_translate = ctk.CTkButton(bottom, text=self.t("translate_all"),
                                           fg_color=COLOR_BTN_ALT, width=140, command=self._translate_all,
                                           state="disabled")
        self.btn_translate.pack(side="left", padx=6, pady=10)

        self.btn_translate_sel = ctk.CTkButton(bottom, text=self.t("translate_sel"),
                                               fg_color=COLOR_BTN_ALT, width=150, command=self._translate_selected,
                                               state="disabled")
        self.btn_translate_sel.pack(side="left", padx=6, pady=10)

        self.btn_save = ctk.CTkButton(bottom, text=self.t("save_tl"),
                                      fg_color="#4f1d96", width=140, command=self._save_tl,
                                      state="disabled")
        self.btn_save.pack(side="left", padx=6, pady=10)

        self.btn_cancel = ctk.CTkButton(bottom, text=self.t("cancel"),
                                        fg_color=COLOR_BTN_WARN, width=100, command=self._cancel,
                                        state="disabled")
        self.btn_cancel.pack(side="left", padx=6, pady=10)

        ctk.CTkButton(bottom, text=self.t("settings"), fg_color=COLOR_ACCENT,
                      width=100, command=self._open_settings).pack(side="right", padx=10, pady=10)

        next_lang = "IT" if self.lang == "en" else "EN"
        ctk.CTkButton(bottom, text=next_lang, fg_color=COLOR_ACCENT,
                      width=50, command=self._toggle_lang).pack(side="right", padx=6, pady=10)

    def _build_strings_tab(self):
        self.table_frame = ctk.CTkScrollableFrame(self.tab_strings, fg_color=COLOR_BG)
        self.table_frame.pack(fill="both", expand=True)
        self._build_table_header()

    def _build_table_header(self):
        cols = [("#", 40), ("Kind", 80), ("Speaker", 100), ("Original", 340), ("Translation", 340), ("File", 160)]
        header = ctk.CTkFrame(self.table_frame, fg_color=COLOR_ACCENT)
        header.pack(fill="x", pady=(0, 2))
        for text, width in cols:
            ctk.CTkLabel(header, text=text, width=width,
                         font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=4, pady=4)
        self.table_rows_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.table_rows_frame.pack(fill="both", expand=True)

    def _build_log_tab(self):
        log_top = ctk.CTkFrame(self.tab_log, fg_color="transparent", height=36)
        log_top.pack(fill="x")
        log_top.pack_propagate(False)
        self.verbose_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(log_top, text="Verbose (log every string)", variable=self.verbose_var,
                        text_color=COLOR_SUBTEXT).pack(side="left", padx=12, pady=6)
        self.log_text = ctk.CTkTextbox(self.tab_log, fg_color=COLOR_BG,
                                       font=ctk.CTkFont(family="Courier", size=11))
        self.log_text.pack(fill="both", expand=True)

    # ─── Table rendering ───────────────────────────────────────────────────

    def _render_table(self, items: list[ExtractedString]):
        self._filtered = items
        self._page = 0
        self._render_page()

    def _render_page(self):
        for w in self.table_rows_frame.winfo_children():
            w.destroy()
        items = self._filtered
        start = self._page * self._page_size
        end = start + self._page_size
        page_items = items[start:end]
        cols_w = [40, 80, 100, 340, 340, 160]
        for i, item in enumerate(page_items):
            abs_i = start + i
            bg = COLOR_BG if abs_i % 2 == 0 else COLOR_PANEL
            row = ctk.CTkFrame(self.table_rows_frame, fg_color=bg, height=28)
            row.pack(fill="x")
            row.pack_propagate(False)
            for val, w in [
                (str(abs_i + 1), cols_w[0]),
                (item.kind, cols_w[1]),
                (item.speaker or "", cols_w[2]),
                (item.text[:60], cols_w[3]),
                (item.translated[:60] if item.translated else "", cols_w[4]),
                (Path(item.file).name, cols_w[5]),
            ]:
                ctk.CTkLabel(row, text=val, width=w, anchor="w",
                             text_color=COLOR_TEXT if item.translated else COLOR_SUBTEXT,
                             font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
        # Pagination controls
        total_pages = max(1, (len(items) + self._page_size - 1) // self._page_size)
        pag = ctk.CTkFrame(self.table_rows_frame, fg_color=COLOR_PANEL, height=32)
        pag.pack(fill="x", pady=(4, 0))
        pag.pack_propagate(False)
        ctk.CTkButton(pag, text="◀", width=36, fg_color=COLOR_ACCENT,
                      command=self._prev_page).pack(side="left", padx=6, pady=4)
        ctk.CTkLabel(pag, text=f"Page {self._page + 1} / {total_pages}  ({len(items)} strings)",
                     text_color=COLOR_SUBTEXT, font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        ctk.CTkButton(pag, text="▶", width=36, fg_color=COLOR_ACCENT,
                      command=self._next_page).pack(side="left", padx=2, pady=4)

    def _prev_page(self):
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def _next_page(self):
        total_pages = max(1, (len(self._filtered) + self._page_size - 1) // self._page_size)
        if self._page < total_pages - 1:
            self._page += 1
            self._render_page()

    def _apply_filter(self):
        f = self.filter_var.get()
        if f == "translated":
            visible = [i for i in self.items if i.translated]
        elif f == "untranslated":
            visible = [i for i in self.items if not i.translated]
        else:
            visible = self.items
        self._render_table(visible)

    # ─── Game Selection ────────────────────────────────────────────────────

    def _pick_app(self):
        path = filedialog.askopenfilename(title="Select .app")
        if path:
            self._set_game(Path(path))

    def _pick_folder(self):
        path = filedialog.askdirectory()
        if path:
            self._set_game(Path(path))

    def _set_game(self, path: Path):
        self.game_path = path
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, str(path))
        self.game_status.configure(text=f"{self.t('game_selected')}: {path.name}",
                                   text_color=COLOR_BTN_MAIN)

    # ─── Analysis ──────────────────────────────────────────────────────────

    def _analyze(self):
        if not self.game_path:
            messagebox.showerror(self.t("error"), "Seleziona un gioco prima.")
            return
        self.btn_analyze.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress.set(0)
        self.items = []
        threading.Thread(target=self._analyze_thread, daemon=True).start()

    def _analyze_thread(self):
        try:
            self.extractor = TRExtractor(self.game_path)
            self.log("Phase 1: Extracting .rpa files...")
            self.root_after(lambda: self.progress.set(0.1))
            self.extractor.extract_rpa_files()

            self.log("Phase 2: Decompiling .rpyc files...")
            self.root_after(lambda: self.progress.set(0.3))
            self.extractor.decompile_rpyc_files()

            self.log("Phase 3: Parsing .rpy files...")
            self.root_after(lambda: self.progress.set(0.6))

            rpy_files = self.extractor.get_rpy_files()
            translate_menu = self.settings.get("translate_menu", False)
            items = []
            for f in rpy_files:
                items.extend(parse_rpy_file(f, self.extractor.game_dir, translate_menu))

            self.items = items
            msg = self.t("analysis_complete").format(len(items), len(rpy_files))
            self.log(msg)
            self.root_after(lambda: self._on_analysis_done(msg))
        except Exception as e:
            err = str(e)
            self.log(f"Error: {err}")
            self.root_after(lambda: messagebox.showerror(self.t("error"), err))
            self.root_after(lambda: self.btn_analyze.configure(state="normal"))

    def _on_analysis_done(self, msg):
        self.progress.set(1.0)
        self.progress_label.configure(text=msg)
        self.btn_analyze.configure(state="normal")
        self.btn_translate.configure(state="normal")
        self.btn_translate_sel.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self._apply_filter()

    # ─── Translation ───────────────────────────────────────────────────────

    def _on_checkbox(self):
        self.settings["preserve_names"] = bool(self.preserve_names_var.get())
        self.settings["translate_menu"] = bool(self.translate_ui_var.get())
        self._save_settings()

    def _make_config(self) -> TranslatorConfig:
        lang_name = self.lang_var.get()
        target = LANGUAGES.get(lang_name, "it")
        s = self.settings
        return TranslatorConfig(
            backend=self.backend_var.get(),
            source_lang="en",
            target_lang=target,
            libre_endpoint=s.get("libre_endpoint", "http://localhost:5000"),
            openrouter_api_key=s.get("openrouter_api_key", ""),
            openrouter_model=s.get("openrouter_model", OPENROUTER_FREE_MODELS[0]),
            llama_model_repo=s.get("llama_model_repo", ""),
            llama_model_file=s.get("llama_model_file", ""),
            preserve_names=bool(self.preserve_names_var.get()),
            translate_menu=bool(self.translate_ui_var.get()),
        )

    def _translate_all(self):
        self._do_translate(self.items)

    def _translate_selected(self):
        untranslated = [i for i in self.items if not i.translated]
        self._do_translate(untranslated)

    def _do_translate(self, targets: list[ExtractedString]):
        if not targets:
            return
        cfg = self._make_config()
        self.translator = Translator(cfg)
        self.btn_translate.configure(state="disabled")
        self.btn_translate_sel.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress.set(0)

        def thread():
            try:
                texts = [i.text for i in targets]
                verbose = self.verbose_var.get()
                def _progress(d, t):
                    pct = int(d / t * 100)
                    self.root_after(lambda d=d, t=t, pct=pct: (
                        self.progress.set(d / t),
                        self.progress_label.configure(text=f"{pct}%  ({d}/{t})")
                    ))
                result = self.translator.translate_many(
                    texts,
                    progress_cb=_progress,
                    log_cb=(lambda orig, tr: self.log(f"  {orig[:40]} → {tr[:40]}")) if verbose else None,
                )
                # DEBUG: log prime 3 entry del result
                sample = list(result.items())[:3]
                for k, v in sample:
                    self.log(f"[DBG] {repr(k[:30])} => {repr(v[:30])}")
                for item in targets:
                    item.translated = result.get(item.text, "")
                done = sum(1 for i in self.items if i.translated)
                msg = self.t("translation_complete").format(done, len(self.items))
                self.log(msg)
                self.root_after(lambda: self._on_translation_done(msg))
            except TranslationError as e:
                err = str(e)
                self.log(f"Translation error: {err}")
                self.root_after(lambda: messagebox.showerror(self.t("error"), err))
                self.root_after(lambda: self._reset_buttons())
            except Exception as e:
                err = str(e)
                self.log(f"Error: {err}")
                self.root_after(lambda: messagebox.showerror(self.t("error"), err))
                self.root_after(lambda: self._reset_buttons())

        threading.Thread(target=thread, daemon=True).start()

    def _on_translation_done(self, msg):
        self.progress.set(1.0)
        self.progress_label.configure(text=msg)
        self._reset_buttons()
        self.btn_save.configure(state="normal")
        self._apply_filter()
        messagebox.showinfo(self.t("translation_complete").split(":")[0], msg)

    def _reset_buttons(self):
        self.btn_translate.configure(state="normal")
        self.btn_translate_sel.configure(state="normal")
        self.btn_cancel.configure(state="disabled")

    def _cancel(self):
        if self.translator:
            self.translator.cancel()

    # ─── Save TL ───────────────────────────────────────────────────────────

    def _save_tl(self):
        if not self.extractor or not self.items:
            return
        lang_name = self.lang_var.get()
        lang_folder = lang_name.lower()  # es. "italian", "french", ...
        translations = {i.text: i.translated for i in self.items if i.translated}
        if not translations:
            messagebox.showinfo("", "Nessuna traduzione da salvare.")
            return
        written = write_tl_files(self.extractor.game_dir, lang_folder, self.items, translations)
        activator = write_activator(self.extractor.game_dir, lang_folder)
        msg = self.t("saved").format(len(written), self.extractor.game_dir / "tl" / lang_folder)
        self.log(msg)
        self.log(f"Activator: {activator}")
        messagebox.showinfo("", msg)

    # ─── Settings ──────────────────────────────────────────────────────────

    def _open_settings(self):
        SettingsDialog(self)

    def _load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                self.settings = json.loads(SETTINGS_FILE.read_text())
            except Exception:
                self.settings = {}
        else:
            self.settings = {}

    def _save_settings(self):
        SETTINGS_FILE.write_text(json.dumps(self.settings, indent=2))

    # ─── Helpers ───────────────────────────────────────────────────────────

    def t(self, key: str) -> str:
        return UI_TEXTS.get(self.lang, UI_TEXTS["en"]).get(key, key)

    def log(self, msg: str):
        def _log():
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
        self.root_after(_log)

    def root_after(self, fn):
        self.after(0, fn)

    def _toggle_lang(self):
        self.lang = "it" if self.lang == "en" else "en"
        self.destroy()
        app = TranslatorApp()
        app.lang = self.lang
        app.mainloop()

    def _set_icon(self):
        if not PIL_OK:
            return
        icon_path = SCRIPT_DIR / "logo_48.png"
        if icon_path.exists():
            try:
                img = Image.open(icon_path)
                self.iconphoto(True, ImageTk.PhotoImage(img))
            except Exception:
                pass

    def _set_logo(self, parent):
        if not PIL_OK:
            return
        logo_path = SCRIPT_DIR / "logo_48.png"
        if logo_path.exists():
            try:
                img = ctk.CTkImage(Image.open(logo_path), size=(48, 48))
                self.logo_label.configure(image=img)
            except Exception:
                pass


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
