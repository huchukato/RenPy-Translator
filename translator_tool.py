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
from tr_parser import parse_rpy_file, ExtractedString, extract_character_names
from tr_translator import Translator, TranslatorConfig, TranslationError, OPENROUTER_FREE_MODELS, LANG_NAMES
from tr_writer import write_tl_files, write_activator, backup_tl_dir, restore_tl_backup

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ─── Costanti ────────────────────────────────────────────────────────────────

APP_TITLE = "Ren'Py Translator"
VERSION   = "2.1.0"
SCRIPT_DIR = Path(__file__).parent
SETTINGS_FILE = SCRIPT_DIR / "translator_settings.json"

LANGUAGES = {
    "English": "en", "Italian": "it", "French": "fr", "Spanish": "es",
    "German": "de", "Portuguese": "pt", "Japanese": "ja", "Chinese": "zh",
    "Russian": "ru", "Korean": "ko", "Arabic": "ar",
}
BACKENDS = {
    "Google Turbo": "google_turbo",
    "Bing Turbo": "bing_ultra",
    "OpenRouter": "openrouter",
    "Llama Local": "llama",
}
BACKEND_LABELS = {value: label for label, value in BACKENDS.items()}

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
        "analyze_translate": "Analyze & Translate",
        "save_translation": "Save Translation",
        "export": "Export",
        "save_edit": "Save Edit",
        "edit_selected": "Edit selected translation:",
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
        "filter": "Filter:",
        "search": "Search:",
        "search_placeholder": "Search strings...",
        "search_original": "Original",
        "search_translation": "Translation",
        "search_both": "Both",
        "clear_cache": "Clear cache",
        "clear_cache_title": "Clear cache",
        "clear_cache_confirm": "This will delete the global translation cache. This cannot be undone. Proceed?",
        "clear_cache_done": "Cache cleared: {0} file(s) removed.",
        "restore_backup": "Restore Backup",
        "restore_backup_title": "Restore Backup",
        "restore_backup_confirm": "This will restore the original translation files from the backup. This cannot be undone. Proceed?",
        "restore_backup_done": "Backup restored from {0}.",
        "restore_backup_none": "No original backup found.",
        "select_all": "Select All",
        "delete_row": "Delete Row",
        "replace_all": "Replace All",
        "replace_all_title": "Replace All",
        "replace_all_find": "Find:",
        "replace_all_replace": "Replace with:",
        "replace_all_case": "Case sensitive",
        "replace_all_filtered": "Only in filtered items",
        "replace_all_scope": "Search in:",
        "replace_all_scope_original": "Original",
        "replace_all_scope_translation": "Translation",
        "replace_all_scope_both": "Both",
        "replace_all_replaced": "Replaced in {0} items.",
        "replace_all_no_matches": "No matches found. Checked {0} items in {1}.",
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
        "analyze_translate": "Analizza & Traduci",
        "save_translation": "Salva Traduzione",
        "export": "Esporta",
        "save_edit": "Salva Modifica",
        "edit_selected": "Modifica traduzione selezionata:",
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
        "filter": "Filtro:",
        "search": "Cerca:",
        "search_placeholder": "Cerca stringhe...",
        "search_original": "Originale",
        "search_translation": "Traduzione",
        "search_both": "Entrambi",
        "clear_cache": "Cancella cache",
        "clear_cache_title": "Cancella cache",
        "clear_cache_confirm": "Verrà cancellata la cache globale delle traduzioni. Non è annullabile. Procedere?",
        "clear_cache_done": "Cache cancellata: {0} file rimossi.",
        "restore_backup": "Ripristina Backup",
        "restore_backup_title": "Ripristina Backup",
        "restore_backup_confirm": "Verranno ripristinati i file di traduzione originali dal backup. Non è annullabile. Procedere?",
        "restore_backup_done": "Backup ripristinato da {0}.",
        "restore_backup_none": "Nessun backup originale trovato.",
        "select_all": "Seleziona Tutto",
        "delete_row": "Cancella Riga",
        "replace_all": "Sostituisci Tutto",
        "replace_all_title": "Sostituisci Tutto",
        "replace_all_find": "Trova:",
        "replace_all_replace": "Sostituisci con:",
        "replace_all_case": "Maiuscole/minuscole",
        "replace_all_filtered": "Solo negli item filtrati",
        "replace_all_scope": "Cerca in:",
        "replace_all_scope_original": "Originale",
        "replace_all_scope_translation": "Traduzione",
        "replace_all_scope_both": "Entrambi",
        "replace_all_replaced": "Sostituito in {0} elementi.",
        "replace_all_no_matches": "Nessuna corrispondenza. Controllati {0} elementi in {1}.",
    },
    "es": {
        "game_selection": "Selección de juego",
        "game_selected": "Juego seleccionado",
        "no_game": "Ningún juego seleccionado",
        "btn_app": ".app",
        "btn_folder": "Carpeta",
        "strings_tab": "Cadenas",
        "log_tab": "Registro",
        "filter_all": "Todas",
        "filter_translated": "Traducidas",
        "filter_untranslated": "No traducidas",
        "analyze_translate": "Analizar y Traducir",
        "save_translation": "Guardar Traducción",
        "export": "Exportar",
        "save_edit": "Guardar Edición",
        "edit_selected": "Editar traducción seleccionada:",
        "target_lang": "Idioma de destino:",
        "backend": "Backend:",
        "analyze": "Analizar juego",
        "translate_all": "Traducir todo",
        "translate_sel": "Traducir selección",
        "save_tl": "Guardar archivos TL",
        "settings": "Ajustes",
        "cancel": "Cancelar",
        "analysis_complete": "Análisis completado: {} cadenas en {} archivos",
        "translation_complete": "Traducción completada: {}/{} cadenas",
        "saved": "Guardados {} archivos en {}",
        "error": "Error",
        "col_num": "#",
        "col_kind": "Tipo",
        "col_speaker": "Personaje",
        "col_original": "Original",
        "col_translation": "Traducción",
        "col_file": "Archivo",
        "filter": "Filtro:",
        "search": "Buscar:",
        "search_placeholder": "Buscar cadenas...",
        "search_original": "Original",
        "search_translation": "Traducción",
        "search_both": "Ambos",
        "clear_cache": "Borrar caché",
        "clear_cache_title": "Borrar caché",
        "clear_cache_confirm": "Se borrará la caché global de traducciones. No se puede deshacer. ¿Proceder?",
        "clear_cache_done": "Caché borrada: {0} archivo(s) eliminado(s).",
        "restore_backup": "Restaurar copia de seguridad",
        "restore_backup_title": "Restaurar copia de seguridad",
        "restore_backup_confirm": "Se restaurarán los archivos de traducción originales desde la copia de seguridad. No se puede deshacer. ¿Proceder?",
        "restore_backup_done": "Copia de seguridad restaurada desde {0}.",
        "restore_backup_none": "No se encontró ninguna copia de seguridad original.",
        "select_all": "Seleccionar todo",
        "delete_row": "Eliminar fila",
        "replace_all": "Reemplazar todo",
        "replace_all_title": "Reemplazar todo",
        "replace_all_find": "Buscar:",
        "replace_all_replace": "Reemplazar con:",
        "replace_all_case": "Distinguir mayúsculas/minúsculas",
        "replace_all_filtered": "Solo en elementos filtrados",
        "replace_all_scope": "Buscar en:",
        "replace_all_scope_original": "Original",
        "replace_all_scope_translation": "Traducción",
        "replace_all_scope_both": "Ambos",
        "replace_all_replaced": "Reemplazado en {0} elementos.",
        "replace_all_no_matches": "No se encontraron coincidencias. Revisados {0} elementos en {1}.",
    },
}

# ─── Tema ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG       = "#0c0a12"
COLOR_PANEL    = "#18122b"
COLOR_ACCENT   = "#7c3aed"
COLOR_ACCENT_MAGENTA = "#ec4899"
COLOR_ACCENT_GOLD = "#f59e0b"
COLOR_ACCENT_CYAN = "#06b6d4"
COLOR_BTN_MAIN = "#7c3aed"
COLOR_BTN_ALT  = "#ec4899"
COLOR_BTN_WARN = "#e11d48"
COLOR_BTN_SUCCESS = "#10b981"
COLOR_TEXT     = "#f0e6ff"
COLOR_SUBTEXT  = "#a78bfa"
COLOR_ROW_EVEN = "#0c0a12"
COLOR_ROW_ODD  = "#18122b"
COLOR_SELECTED = "#0e7490"


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
        self.character_names: frozenset = frozenset()
        self._page = 0
        self._page_size = 100
        self._selected_indices: set[int] = set()
        self.translator: Translator | None = None
        self.settings: dict = {}
        self._load_settings()
        self.lang = self.settings.get("ui_lang", "en")
        self._build_ui()
        self._set_icon()
        self._restore_last_game()

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

        # Language selector
        lang_frame = ctk.CTkFrame(top, fg_color="transparent")
        lang_frame.pack(side="right", padx=12, pady=8, anchor="n")
        lang_display = {"en": "English", "it": "Italiano", "es": "Español"}
        self.ui_lang_var = ctk.StringVar(value=lang_display.get(self.lang, "English"))
        self.ui_lang_combo = ctk.CTkComboBox(
            lang_frame,
            values=["English", "Italiano", "Español"],
            width=120,
            variable=self.ui_lang_var,
            command=self._on_lang_change,
        )
        self.ui_lang_combo.pack()

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

        ctk.CTkLabel(ctrl, text=self.t("filter"), text_color=COLOR_SUBTEXT).pack(side="left", padx=(12, 4))
        self.filter_var = ctk.StringVar(value="all")
        for val, key in [("all", "filter_all"), ("translated", "filter_translated"),
                         ("untranslated", "filter_untranslated")]:
            rb = ctk.CTkRadioButton(ctrl, text=self.t(key), variable=self.filter_var,
                                    value=val, command=self._apply_filter)
            rb.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl, text=self.t("target_lang"), text_color=COLOR_SUBTEXT).pack(side="left", padx=(20, 4))
        self.lang_var = ctk.StringVar(value=self.settings.get("target_lang", "Italian"))
        self.lang_combo = ctk.CTkComboBox(ctrl, values=list(LANGUAGES.keys()), width=130,
                                          variable=self.lang_var, command=self._on_target_lang_change)
        self.lang_combo.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl, text=self.t("backend"), text_color=COLOR_SUBTEXT).pack(side="left", padx=(16, 4))
        saved_backend = self.settings.get("backend", "bing_ultra")
        self.backend_var = ctk.StringVar(value=BACKEND_LABELS.get(saved_backend, "Bing Turbo"))
        self.backend_combo = ctk.CTkComboBox(ctrl, values=list(BACKENDS), width=140,
                                             variable=self.backend_var, command=self._on_backend_change)
        self.backend_combo.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl, text="Profile:", text_color=COLOR_SUBTEXT).pack(side="left", padx=(12, 4))
        self.profile_var = ctk.StringVar(value=self.settings.get("translation_profile", "Balanced"))
        self.profile_combo = ctk.CTkComboBox(ctrl, values=["Safe", "Balanced", "Fast"], width=105,
                                             variable=self.profile_var, command=self._on_profile_change)
        self.profile_combo.pack(side="left", padx=4)

        # Tabs
        self.tabs = ctk.CTkTabview(self, fg_color=COLOR_PANEL)
        self.tabs.pack(fill="both", expand=True, padx=0, pady=(2, 0))
        self.tab_strings = self.tabs.add(self.t("strings_tab"))
        self.tab_log = self.tabs.add(self.t("log_tab"))
        self._build_strings_tab()
        self._build_log_tab()

        # Bottom buttons
        # ── Riga comandi ─────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=56)
        bottom.pack(fill="x", pady=(2, 0))
        bottom.pack_propagate(False)

        self.btn_analyze_translate = ctk.CTkButton(bottom, text=f"▶  {self.t('analyze_translate')}",
                                                   fg_color="#16a34a", hover_color="#15803d",
                                                   width=200, command=self._analyze_translate,
                                                   state="disabled")
        self.btn_analyze_translate.pack(side="left", padx=10, pady=10)

        self.btn_save_translation = ctk.CTkButton(bottom, text=self.t("save_translation"),
                                                  fg_color=COLOR_BTN_ALT, width=140, command=self._save_translation,
                                                  state="disabled")
        self.btn_save_translation.pack(side="left", padx=6, pady=10)

        self.btn_export = ctk.CTkButton(bottom, text=self.t("export"),
                                        fg_color="#ec4899", width=110, command=self._export_tl,
                                        state="disabled")
        self.btn_export.pack(side="left", padx=6, pady=10)

        self.btn_cancel = ctk.CTkButton(bottom, text=self.t("cancel"),
                                        fg_color=COLOR_BTN_WARN, width=100, command=self._cancel,
                                        state="disabled")
        self.btn_cancel.pack(side="left", padx=6, pady=10)

        self.btn_clear_cache = ctk.CTkButton(bottom, text=self.t("clear_cache"),
                                              fg_color=COLOR_BTN_WARN, width=100, command=self._clear_cache)
        self.btn_clear_cache.pack(side="right", padx=6, pady=10)

        self.btn_restore_backup = ctk.CTkButton(bottom, text=self.t("restore_backup"),
                                                 fg_color=COLOR_BTN_WARN, width=140, command=self._restore_backup)
        self.btn_restore_backup.pack(side="right", padx=6, pady=10)

        ctk.CTkButton(bottom, text=self.t("settings"), fg_color=COLOR_ACCENT,
                      width=100, command=self._open_settings).pack(side="right", padx=10, pady=10)

        # ── Riga opzioni ─────────────────────────────────────────────────
        opts = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=44)
        opts.pack(fill="x")
        opts.pack_propagate(False)

        ctk.CTkLabel(opts, text="Options:", text_color=COLOR_SUBTEXT,
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=(12, 8), pady=10)

        self.preserve_names_var = ctk.BooleanVar(value=self.settings.get("preserve_names", False))
        ctk.CTkSwitch(opts, text="Preserve names", variable=self.preserve_names_var,
                      command=self._on_option_change,
                      onvalue=True, offvalue=False).pack(side="left", padx=10, pady=8)

        self.translate_ui_var = ctk.BooleanVar(value=self.settings.get("translate_ui", True))
        ctk.CTkSwitch(opts, text="Translate Menu", variable=self.translate_ui_var,
                      command=self._on_option_change,
                      onvalue=True, offvalue=False).pack(side="left", padx=10, pady=8)

    def _build_strings_tab(self):
        # Search bar
        search_frame = ctk.CTkFrame(self.tab_strings, fg_color=COLOR_PANEL, height=36)
        search_frame.pack(fill="x", padx=8, pady=(8, 4))
        search_frame.pack_propagate(False)
        ctk.CTkLabel(search_frame, text=self.t("search"), text_color=COLOR_SUBTEXT).pack(side="left", padx=(8, 4))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        self.search_entry = ctk.CTkEntry(search_frame, width=310, textvariable=self.search_var,
                                         placeholder_text=self.t("search_placeholder"))
        self.search_entry.pack(side="left", padx=(0, 6), pady=4)
        self._search_scopes = {
            self.t("search_original"): "original",
            self.t("search_translation"): "translation",
            self.t("search_both"): "both",
        }
        self.search_scope_var = ctk.StringVar(value=self.t("search_both"))
        self.search_scope_combo = ctk.CTkComboBox(search_frame, values=list(self._search_scopes), width=150,
                                                   variable=self.search_scope_var, command=self._on_search_scope_change)
        self.search_scope_combo.pack(side="left", padx=4, pady=4)

        self.select_all_var = ctk.StringVar(value="off")
        self.select_all_checkbox = ctk.CTkCheckBox(search_frame, text=self.t("select_all"), variable=self.select_all_var,
                                                   onvalue="on", offvalue="off", command=self._on_select_all)
        self.select_all_checkbox.pack(side="left", padx=(8, 4), pady=4)

        self.btn_delete_row = ctk.CTkButton(search_frame, text=self.t("delete_row"),
                                            fg_color="#dc2626", hover_color="#b91c1c",
                                            text_color="white", width=100, command=self._delete_selected_row)
        self.btn_delete_row.pack(side="left", padx=(4, 8), pady=4)
        self.btn_delete_row.configure(state="disabled")

        self.table_frame = ctk.CTkScrollableFrame(self.tab_strings, fg_color=COLOR_BG)
        self.table_frame.pack(fill="both", expand=True)
        self._build_table_header()

        self.editor_frame = ctk.CTkFrame(self.tab_strings, fg_color=COLOR_PANEL, height=160)
        self.editor_frame.pack(side="bottom", fill="x", padx=8, pady=8)
        self.editor_frame.pack_propagate(False)

        ctk.CTkLabel(self.editor_frame, text=self.t("edit_selected"), text_color=COLOR_SUBTEXT,
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(6, 2))
        self.edit_text = ctk.CTkTextbox(self.editor_frame, height=80, font=ctk.CTkFont(size=12))
        self.edit_text.pack(fill="x", padx=10, pady=(0, 6))
        self.edit_text.configure(state="disabled")

        btn_row = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 6))
        self.btn_replace_all = ctk.CTkButton(btn_row, text=self.t("replace_all"), width=100,
                                             fg_color=COLOR_ACCENT, text_color="white", command=self._open_replace_dialog)
        self.btn_replace_all.pack(side="left", padx=4)
        self.btn_replace_all.configure(state="disabled")
        self.btn_edit_save = ctk.CTkButton(btn_row, text=self.t("save_edit"), width=100,
                                           fg_color=COLOR_BTN_MAIN, command=self._save_edit,
                                           state="disabled")
        self.btn_edit_save.pack(side="right")

    def _build_table_header(self):
        cols = [("", 40), ("#", 40), ("Kind", 80), ("Speaker", 100), ("Original", 320), ("Translation", 320), ("File", 140)]
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
        self.verbose_var = ctk.BooleanVar(value=self.settings.get("verbose", False))
        ctk.CTkCheckBox(log_top, text="Verbose (log every string)", variable=self.verbose_var,
                        command=self._on_verbose_change, text_color=COLOR_SUBTEXT).pack(side="left", padx=12, pady=6)
        self.log_text = ctk.CTkTextbox(self.tab_log, fg_color=COLOR_BG,
                                       font=ctk.CTkFont(family="Courier", size=11))
        self.log_text.pack(fill="both", expand=True)

    # ─── Table rendering ───────────────────────────────────────────────────

    def _render_table(self, items: list[ExtractedString]):
        self._filtered = items
        self._page = 0
        self._selected_index = None
        self._clear_editor()
        self._render_page()

    def _render_page(self):
        for w in self.table_rows_frame.winfo_children():
            w.destroy()
        items = self._filtered
        start = self._page * self._page_size
        end = start + self._page_size
        page_items = items[start:end]
        cols_w = [40, 40, 80, 100, 320, 320, 140]
        for i, item in enumerate(page_items):
            abs_i = start + i
            bg = COLOR_ROW_EVEN if abs_i % 2 == 0 else COLOR_ROW_ODD
            if abs_i in self._selected_indices:
                bg = COLOR_SELECTED
            row = ctk.CTkFrame(self.table_rows_frame, fg_color=bg, height=28)
            row.pack(fill="x")
            row.pack_propagate(False)

            # Checkbox
            var = ctk.StringVar(value="on" if abs_i in self._selected_indices else "off")
            chk = ctk.CTkCheckBox(row, text="", width=24, variable=var,
                                  onvalue="on", offvalue="off")
            chk.pack(side="left", padx=4)
            chk.bind("<Button-1>", lambda event: "break")
            chk.configure(command=lambda v=var, idx=abs_i: self._on_checkbox_toggle(idx, v))

            for val, w in [
                (str(abs_i + 1), cols_w[1]),
                (item.kind, cols_w[2]),
                (item.speaker or "", cols_w[3]),
                (item.text[:60], cols_w[4]),
                (item.translated[:60] if item.translated else "", cols_w[5]),
                (Path(item.file).name, cols_w[6]),
            ]:
                lbl = ctk.CTkLabel(row, text=val, width=w, anchor="w",
                                   text_color=COLOR_TEXT if item.translated else COLOR_SUBTEXT,
                                   font=ctk.CTkFont(size=11))
                lbl.pack(side="left", padx=4)

            def _make_click(idx=abs_i, it=item):
                return lambda event: self._on_row_click(idx, it)
            row.bind("<Button-1>", _make_click())
            for child in row.winfo_children():
                if child != chk:
                    child.bind("<Button-1>", _make_click())
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

        query = self.search_var.get().strip().casefold()
        scope = self._search_scopes.get(self.search_scope_var.get(), "both")
        if query:
            def matches(item: ExtractedString) -> bool:
                original = item.text.casefold()
                translation = (item.translated or "").casefold()
                if scope == "original":
                    return query in original
                if scope == "translation":
                    return query in translation
                return query in original or query in translation
            visible = [item for item in visible if matches(item)]
        self._render_table(visible)

    def _on_search_scope_change(self, _value: str):
        self._apply_filter()

    def _clear_editor(self):
        self.edit_text.configure(state="normal")
        self.edit_text.delete("1.0", "end")
        self.edit_text.configure(state="disabled")
        self.btn_edit_save.configure(state="disabled")

    def _on_row_click(self, abs_i: int, item: ExtractedString):
        self._selected_indices.clear()
        self._selected_indices.add(abs_i)
        self._render_page()
        self.edit_text.configure(state="normal")
        self.edit_text.delete("1.0", "end")
        self.edit_text.insert("end", item.translated if item.translated else "")
        self.btn_edit_save.configure(state="normal")
        self.btn_delete_row.configure(state="normal")

    def _on_checkbox_toggle(self, abs_i: int, checkbox_var: ctk.StringVar):
        if checkbox_var.get() == "on":
            self._selected_indices.add(abs_i)
        else:
            self._selected_indices.discard(abs_i)
        self._render_page()
        self.btn_delete_row.configure(state="normal" if self._selected_indices else "disabled")

    def _on_select_all(self):
        if self.select_all_var.get() == "on":
            self._selected_indices = set(range(len(self._filtered)))
        else:
            self._selected_indices.clear()
        self._render_page()
        self.btn_delete_row.configure(state="normal" if self._selected_indices else "disabled")

    def _delete_selected_row(self):
        if not self._selected_indices:
            return
        if not messagebox.askyesno(self.t("delete_row"), f"Delete {len(self._selected_indices)} selected row(s)?"):
            return
        count = 0
        for abs_i in sorted(self._selected_indices, reverse=True):
            if abs_i < len(self._filtered):
                item = self._filtered[abs_i]
                if item in self.items:
                    self.items.remove(item)
                    count += 1
        self._selected_indices.clear()
        self._clear_editor()
        self._apply_filter()
        self.btn_delete_row.configure(state="disabled")
        self.log(f"Deleted {count} row(s)")

    def _save_edit(self):
        if not self._selected_indices:
            return
        selected_index = next(iter(self._selected_indices))
        if selected_index >= len(self._filtered):
            return
        item = self._filtered[selected_index]
        new_text = self.edit_text.get("1.0", "end-1c")
        item.translated = new_text
        self._render_page()
        if not self.translator:
            self.translator = Translator(self._make_config())
        self.translator.update_cache(item.text, new_text)
        self.btn_save_translation.configure(state="normal")
        self.btn_export.configure(state="normal")

    def _open_replace_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.t("replace_all_title"))
        dialog.geometry("420x320")
        dialog.configure(fg_color=COLOR_PANEL)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=self.t("replace_all_find"), text_color=COLOR_SUBTEXT).pack(anchor="w", padx=20, pady=(20, 4))
        find_entry = ctk.CTkEntry(dialog, width=350)
        find_entry.pack(padx=20, pady=(0, 12))

        ctk.CTkLabel(dialog, text=self.t("replace_all_replace"), text_color=COLOR_SUBTEXT).pack(anchor="w", padx=20, pady=(0, 4))
        replace_entry = ctk.CTkEntry(dialog, width=350)
        replace_entry.pack(padx=20, pady=(0, 12))

        case_sensitive_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(dialog, text=self.t("replace_all_case"), variable=case_sensitive_var).pack(anchor="w", padx=20, pady=(0, 8))

        filtered_only_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(dialog, text=self.t("replace_all_filtered"), variable=filtered_only_var).pack(anchor="w", padx=20, pady=(0, 8))

        scope_var = ctk.StringVar(value="translation")
        scope_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        scope_frame.pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkLabel(scope_frame, text=self.t("replace_all_scope"), text_color=COLOR_SUBTEXT).pack(side="left")
        ctk.CTkRadioButton(scope_frame, text=self.t("replace_all_scope_original"), variable=scope_var, value="original").pack(side="left", padx=(8, 4))
        ctk.CTkRadioButton(scope_frame, text=self.t("replace_all_scope_translation"), variable=scope_var, value="translation").pack(side="left", padx=4)
        ctk.CTkRadioButton(scope_frame, text=self.t("replace_all_scope_both"), variable=scope_var, value="both").pack(side="left", padx=4)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        def do_replace():
            import re as _re
            find_text = find_entry.get().strip()
            replace_text = replace_entry.get().strip()
            if not find_text:
                messagebox.showerror(self.t("error"), "Please enter text to find")
                return
            case_sensitive = case_sensitive_var.get()
            only_filtered = filtered_only_var.get()
            scope = scope_var.get()
            target_items = self._filtered if only_filtered else self.items

            count = 0
            for item in target_items:
                if scope == "original":
                    text = item.text
                    if case_sensitive:
                        if find_text in text:
                            item.text = text.replace(find_text, replace_text)
                            count += 1
                    else:
                        if find_text.lower() in text.lower():
                            pattern = _re.compile(_re.escape(find_text), _re.IGNORECASE)
                            item.text = pattern.sub(replace_text, text)
                            count += 1
                elif scope == "translation":
                    text = item.translated or ""
                    if case_sensitive:
                        if find_text in text:
                            item.translated = text.replace(find_text, replace_text)
                            count += 1
                    else:
                        if find_text.lower() in text.lower():
                            pattern = _re.compile(_re.escape(find_text), _re.IGNORECASE)
                            item.translated = pattern.sub(replace_text, text)
                            count += 1
                else:  # both
                    if case_sensitive:
                        if find_text in item.text:
                            item.text = item.text.replace(find_text, replace_text)
                            count += 1
                        if item.translated and find_text in item.translated:
                            item.translated = item.translated.replace(find_text, replace_text)
                            count += 1
                    else:
                        if find_text.lower() in item.text.lower():
                            pattern = _re.compile(_re.escape(find_text), _re.IGNORECASE)
                            item.text = pattern.sub(replace_text, item.text)
                            count += 1
                        if item.translated and find_text.lower() in item.translated.lower():
                            pattern = _re.compile(_re.escape(find_text), _re.IGNORECASE)
                            item.translated = pattern.sub(replace_text, item.translated)
                            count += 1

            if count > 0:
                self._render_page()
                self.btn_save_translation.configure(state="normal")
                self.btn_export.configure(state="normal")
                messagebox.showinfo(self.t("replace_all_title"), self.t("replace_all_replaced").format(count))
                dialog.destroy()
            else:
                messagebox.showinfo(self.t("replace_all_title"), self.t("replace_all_no_matches").format(len(target_items), scope))

        ctk.CTkButton(btn_frame, text=self.t("replace_all"), fg_color=COLOR_BTN_SUCCESS, width=100,
                      command=do_replace).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text=self.t("cancel"), fg_color=COLOR_BTN_WARN, width=100,
                      command=dialog.destroy).pack(side="left", padx=4)

    # ─── Game Selection ────────────────────────────────────────────────────

    def _pick_app(self):
        initialdir = self.settings.get("last_game_dir", str(Path.home() / "Downloads"))
        path = filedialog.askopenfilename(title="Select .app", initialdir=initialdir)
        if path:
            self._set_game(Path(path))

    def _pick_folder(self):
        initialdir = self.settings.get("last_game_dir", str(Path.home() / "Downloads"))
        path = filedialog.askdirectory(initialdir=initialdir)
        if path:
            self._set_game(Path(path))

    def _set_game(self, path: Path):
        self.game_path = path
        self.extractor = None
        self.items = []
        self._filtered = []
        self.translator = None
        self._selected_index = None
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, str(path))
        self.game_status.configure(text=f"{self.t('game_selected')}: {path.name}",
                                   text_color=COLOR_BTN_MAIN)
        self.btn_analyze_translate.configure(state="normal")
        self.btn_save_translation.configure(state="disabled")
        self.btn_export.configure(state="disabled")
        self._apply_filter()
        self._clear_editor()

    # ─── Analysis ──────────────────────────────────────────────────────────

    def _analyze_translate(self):
        if not self.game_path:
            messagebox.showerror(self.t("error"), "Seleziona un gioco prima.")
            return
        self._reset_for_work()
        self.items = []
        threading.Thread(target=self._analyze_translate_thread, daemon=True).start()

    def _analyze_translate_thread(self):
        try:
            self.extractor = TRExtractor(self.game_path)
            self.log("Phase 1: Extracting .rpa files...")
            self.root_after(lambda: self._set_progress(0.05, "Extracting..."))
            self.extractor.extract_rpa_files()

            self.log("Phase 2: Decompiling .rpyc files...")
            self.root_after(lambda: self._set_progress(0.15, "Decompiling..."))
            self.extractor.decompile_rpyc_files()

            self.log("Phase 3: Parsing .rpy files...")
            self.root_after(lambda: self._set_progress(0.25, "Parsing..."))
            rpy_files = self.extractor.get_rpy_files()
            translate_ui = bool(self.translate_ui_var.get())
            self.character_names = frozenset(extract_character_names(self.extractor.game_dir))
            self.log(f"Characters found: {', '.join(sorted(self.character_names)[:10])}{'...' if len(self.character_names) > 10 else ''}")
            items = []
            seen_global: set[str] = set()
            for f in rpy_files:
                for item in parse_rpy_file(f, self.extractor.game_dir, translate_ui):
                    if item.text in seen_global:
                        continue
                    if self.character_names and item.text in self.character_names:
                        continue
                    seen_global.add(item.text)
                    items.append(item)
            self.items = items
            self.log(self.t("analysis_complete").format(len(items), len(rpy_files)))

            self.log("Phase 4: Translating...")
            cfg = self._make_config()
            self.translator = Translator(cfg)
            texts = [i.text for i in self.items]
            verbose = self.verbose_var.get()
            def _progress(d, t):
                frac = 0.25 + (d / t) * 0.65 if t else 0.25
                self.root_after(lambda d=d, t=t, frac=frac: (
                    self._set_progress(frac, f"{int(frac*100)}%  ({d}/{t})")
                ))
            result = self.translator.translate_many(
                texts,
                progress_cb=_progress,
                log_cb=(lambda orig, tr: self.log(f"  {orig[:40]} → {tr[:40]}")) if verbose else None,
            )
            for item in self.items:
                item.translated = result.get(item.text, "")
            done = sum(1 for i in self.items if i.translated)
            msg = self.t("translation_complete").format(done, len(self.items))
            self.log(msg)
            self.root_after(lambda: self._on_analyze_translate_done(msg))
        except Exception as e:
            err = str(e)
            self.log(f"Error: {err}")
            self.root_after(lambda: messagebox.showerror(self.t("error"), err))
            self.root_after(lambda: self._on_work_done())

    def _on_analyze_translate_done(self, msg):
        self.progress.set(1.0)
        self.progress_label.configure(text=msg)
        self._apply_filter()
        self._on_work_done()
        self.update_idletasks()
        self.after(100, lambda: messagebox.showinfo("", msg))

    def _analyze(self):
        if not self.game_path:
            messagebox.showerror(self.t("error"), "Seleziona un gioco prima.")
            return
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
            translate_ui = bool(self.translate_ui_var.get())
            self.character_names = frozenset(extract_character_names(self.extractor.game_dir))
            self.log(f"Characters found: {', '.join(sorted(self.character_names)[:10])}{'...' if len(self.character_names) > 10 else ''}")
            items = []
            seen_global: set[str] = set()
            for f in rpy_files:
                for item in parse_rpy_file(f, self.extractor.game_dir, translate_ui):
                    if item.text in seen_global:
                        continue
                    if self.character_names and item.text in self.character_names:
                        continue
                    seen_global.add(item.text)
                    items.append(item)

            self.items = items
            msg = self.t("analysis_complete").format(len(items), len(rpy_files))
            self.log(msg)
            self.root_after(lambda: self._on_analysis_done(msg))
        except Exception as e:
            err = str(e)
            self.log(f"Error: {err}")
            self.root_after(lambda: messagebox.showerror(self.t("error"), err))
            self.root_after(lambda: self._reset_buttons())

    def _on_analysis_done(self, msg):
        self.progress.set(1.0)
        self.progress_label.configure(text=msg)
        self.btn_cancel.configure(state="disabled")
        self._apply_filter()

    # ─── Translation ───────────────────────────────────────────────────────

    def _on_backend_change(self, label: str):
        self.settings["backend"] = BACKENDS[label]
        self._save_settings()

    def _on_target_lang_change(self, language: str):
        self.settings["target_lang"] = language
        self._save_settings()

    def _on_profile_change(self, profile: str):
        self.settings["translation_profile"] = profile
        self._save_settings()

    def _on_verbose_change(self):
        self.settings["verbose"] = bool(self.verbose_var.get())
        self._save_settings()

    def _on_option_change(self):
        self.settings["preserve_names"] = bool(self.preserve_names_var.get())
        self.settings["translate_ui"] = bool(self.translate_ui_var.get())
        self._save_settings()

    def _make_config(self) -> TranslatorConfig:
        lang_name = self.lang_var.get()
        target = LANGUAGES.get(lang_name, "it")
        s = self.settings
        return TranslatorConfig(
            backend=BACKENDS[self.backend_var.get()],
            source_lang="en",
            target_lang=target,
            libre_endpoint=s.get("libre_endpoint", "http://localhost:5000"),
            openrouter_api_key=s.get("openrouter_api_key", ""),
            openrouter_model=s.get("openrouter_model", OPENROUTER_FREE_MODELS[0]),
            llama_model_repo=s.get("llama_model_repo", ""),
            llama_model_file=s.get("llama_model_file", ""),
            translation_profile=self.profile_var.get(),
            preserve_names=bool(self.preserve_names_var.get()),
            translate_menu=bool(self.translate_ui_var.get()),  # usato da TranslatorConfig
            character_names=self.character_names,
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
                for item in targets:
                    item.translated = result.get(item.text, "")
                done = sum(1 for i in self.items if i.translated)
                msg = self.t("translation_complete").format(done, len(self.items))
                self.log(msg)
                self.root_after(lambda msg=msg: self._on_translation_done(msg))
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
        self.btn_export.configure(state="normal")
        self._apply_filter()
        self.update_idletasks()
        self.after(100, lambda: messagebox.showinfo(self.t("translation_complete").split(":")[0], msg))

    def _reset_buttons(self):
        self._on_work_done()

    def _reset_for_work(self):
        self.btn_analyze_translate.configure(state="disabled")
        self.btn_save_translation.configure(state="disabled")
        self.btn_export.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress.set(0)
        self.progress_label.configure(text="")

    def _on_work_done(self):
        self.btn_cancel.configure(state="disabled")
        self.btn_analyze_translate.configure(state="normal" if self.game_path else "disabled")
        can_save = bool(self.game_path and self.extractor and self.items)
        self.btn_save_translation.configure(state="normal" if can_save else "disabled")
        self.btn_export.configure(state="normal" if can_save else "disabled")
        self.btn_replace_all.configure(state="normal" if can_save else "disabled")
        self.btn_restore_backup.configure(state="normal" if self.game_path else "disabled")

    def _cancel(self):
        if self.translator:
            self.translator.cancel()

    # ─── Save TL / Export ────────────────────────────────────────────────

    def _save_translation(self):
        if not self.game_path or not self.extractor or not self.items:
            return
        translations = {i.text: i.translated for i in self.items if i.translated}
        if not translations:
            messagebox.showinfo("", "Nessuna traduzione da salvare.")
            return
        self._reset_for_work()
        threading.Thread(target=self._save_translation_thread, daemon=True).start()

    def _save_translation_thread(self):
        try:
            self.root_after(lambda: self._set_progress(0.2, "Creating backup..."))
            lang_name = self.lang_var.get()
            lang_folder = lang_name.lower()
            translations = {i.text: i.translated for i in self.items if i.translated}
            if not translations:
                self.root_after(lambda: messagebox.showinfo("", "Nessuna traduzione da salvare."))
                self.root_after(lambda: self._on_work_done())
                return
            backup_tl_dir(self.extractor.game_dir, lang_folder)
            self.log("Original backup created/verified.")
            self.root_after(lambda: self._set_progress(0.5, "Saving translation..."))
            written = write_tl_files(self.extractor.game_dir, lang_folder, self.items, translations)
            splash_src = SCRIPT_DIR / "splash.png"
            activator = write_activator(self.extractor.game_dir, lang_folder, splash_src)
            msg = self.t("saved").format(len(written), self.extractor.game_dir / "tl" / lang_folder)
            self.log(msg)
            self.log(f"Activator: {activator}")
            self.root_after(lambda: self._on_save_done(msg))
        except Exception as e:
            err = str(e)
            self.log(f"Error: {err}")
            self.root_after(lambda: messagebox.showerror(self.t("error"), err))
            self.root_after(lambda: self._on_work_done())

    def _on_save_done(self, msg):
        self._set_progress(1.0, msg)
        self._on_work_done()
        self.update_idletasks()
        self.after(100, lambda: messagebox.showinfo("", msg))

    def _export_tl(self):
        if not self.game_path or not self.extractor or not self.items:
            return
        translations = {i.text: i.translated for i in self.items if i.translated}
        if not translations:
            messagebox.showinfo("", "Nessuna traduzione da esportare.")
            return
        lang_name = self.lang_var.get()
        lang_folder = lang_name.lower()
        game_name = self._game_display_name()
        default_name = f"{game_name}-{lang_folder}"
        dest = filedialog.askdirectory(title=f"Scegli cartella destinazione per '{default_name}'")
        if not dest:
            return
        export_dir = Path(dest) / default_name
        self._reset_for_work()
        threading.Thread(target=self._export_thread, args=(export_dir, lang_folder), daemon=True).start()

    def _export_thread(self, export_dir: Path, lang_folder: str):
        try:
            self.log(f"Exporting patch to {export_dir} ...")
            self.root_after(lambda: self._set_progress(0.3, "Exporting..."))
            translations = {i.text: i.translated for i in self.items if i.translated}
            if not translations:
                self.root_after(lambda: messagebox.showinfo("", "Nessuna traduzione da esportare."))
                self.root_after(lambda: self._on_work_done())
                return
            written = write_tl_files(export_dir / "game", lang_folder, self.items, translations)
            splash_src = SCRIPT_DIR / "splash.png"
            activator = write_activator(export_dir / "game", lang_folder, splash_src)
            self.log(self.t("saved").format(len(written), export_dir / "game" / "tl" / lang_folder))
            self.log(f"Activator: {activator}")
            self.root_after(lambda: self._on_export_done(export_dir))
        except Exception as e:
            err = str(e)
            self.log(f"Error: {err}")
            self.root_after(lambda: messagebox.showerror(self.t("error"), err))
            self.root_after(lambda: self._on_work_done())

    def _on_export_done(self, export_dir: Path):
        self._set_progress(1.0, "Export complete")
        self._on_work_done()
        msg = f"Esportato in:\n{export_dir}"
        self.log(msg)
        messagebox.showinfo("Export", msg)

    def _clear_cache(self):
        if not messagebox.askyesno(self.t("clear_cache_title"), self.t("clear_cache_confirm")):
            return

        removed = 0
        cache_dir = Path.home() / ".cache" / "renpy-translator"
        if cache_dir.exists():
            for cache_file in cache_dir.glob("translation_cache_*.json"):
                try:
                    cache_file.unlink()
                    removed += 1
                except Exception as e:
                    self.log(f"Could not delete {cache_file}: {e}")

        msg = self.t("clear_cache_done").format(removed)
        self.log(msg)
        messagebox.showinfo(self.t("clear_cache_title"), msg)

        if self.translator:
            self.translator.cache = {}

    def _restore_backup(self):
        if not self.game_path:
            messagebox.showerror(self.t("error"), self.t("no_game"))
            return
        if not messagebox.askyesno(self.t("restore_backup_title"), self.t("restore_backup_confirm")):
            return
        try:
            lang_name = self.lang_var.get()
            lang_folder = lang_name.lower()
            restored = restore_tl_backup(self.extractor.game_dir, lang_folder)
            if restored is None:
                messagebox.showinfo(self.t("restore_backup_title"), self.t("restore_backup_none"))
                return
            # Ricarica le traduzioni dalla cartella ripristinata
            self._load_restored_translations(lang_folder)
            msg = self.t("restore_backup_done").format(restored.name)
            self.log(msg)
            messagebox.showinfo(self.t("restore_backup_title"), msg)
        except Exception as e:
            err = str(e)
            self.log(f"Error: {err}")
            messagebox.showerror(self.t("error"), err)

    def _load_restored_translations(self, lang_folder: str):
        """Ricarica le traduzioni ripristinate in memoria dagli items."""
        if not self.extractor:
            return
        tl_dir = self.extractor.game_dir / "tl" / lang_folder
        restored: dict[str, str] = {}
        if tl_dir.exists():
            for f in tl_dir.glob("*.rpy"):
                if f.name == "zz_runtime_filter.rpy":
                    continue
                text = f.read_text(encoding="utf-8")
                # Estrae coppie old "..." / new "..."
                import re as _re
                for old, new in _re.findall(r'    old "(.*?)"\n    new "(.*?)"', text, _re.DOTALL):
                    restored[old] = new
        for item in self.items:
            if item.text in restored:
                item.translated = restored[item.text]
        self._apply_filter()

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

    def _restore_last_game(self):
        pass

    # ─── Helpers ───────────────────────────────────────────────────────────

    def _game_display_name(self) -> str:
        _skip = {"game", "autorun", "Contents", "Resources", "MacOS", "data"}
        p = self.extractor.game_dir
        for part in reversed(p.parts):
            if part.endswith(".app"):
                return part[:-4]
            if part not in _skip:
                return part
        return p.parent.name

    def t(self, key: str) -> str:
        return UI_TEXTS.get(self.lang, UI_TEXTS["en"]).get(key, key)

    def log(self, msg: str):
        def _log():
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
        self.root_after(_log)

    def root_after(self, fn):
        self.after(0, fn)

    def _set_progress(self, value: float, text: str = ""):
        self.progress.set(max(0.0, min(1.0, value)))
        self.progress_label.configure(text=text)

    def _on_lang_change(self, value: str):
        mapping = {"English": "en", "Italiano": "it", "Español": "es"}
        self.lang = mapping.get(value, "en")
        self.settings["ui_lang"] = self.lang
        self._save_settings()
        self.destroy()
        app = TranslatorApp()
        app.lang = self.lang
        app.mainloop()

    def _set_icon(self):
        if not PIL_OK:
            return
        icon_path = SCRIPT_DIR / "img" / "logo_48.png"
        if icon_path.exists():
            try:
                img = Image.open(icon_path)
                self._icon_img = ImageTk.PhotoImage(img)
                self.iconphoto(True, self._icon_img)
            except Exception:
                pass

    def _set_logo(self, parent):
        if not PIL_OK:
            return
        logo_path = SCRIPT_DIR / "img" / "logo_48.png"
        if logo_path.exists():
            try:
                self._logo_img = ctk.CTkImage(Image.open(logo_path), size=(48, 48))
                self.logo_label.configure(image=self._logo_img)
            except Exception:
                pass


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
