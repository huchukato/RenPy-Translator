"""
CustomTkinter Component Library
================================
Reusable widget classes that mirror the Figma Make UI-element library
(CustomTkinter dark-theme, v5.x).

Each class wraps standard CTk widgets and applies the design tokens from
the Figma library so you get a consistent look without copy-pasting
inline styles everywhere.

Design tokens (C dict) match the default CTk dark-theme colours used
in the Figma source.  Override them *once* in this file and every widget
picks up the change.

Usage
-----
    from ctk_components import (
        CtkStyledButton, CtkStyledEntry, CtkStyledComboBox,
        CtkStyledCheckBox, CtkStyledSwitch, CtkStyledRadioGroup,
        CtkStyledSegmented, CtkStyledSlider, CtkStyledProgressBar,
        CtkStyledTabview, CtkStyledLabel, CtkStyledBadge,
        CtkStyledTextbox, CtkIconButton, CtkSplitButton,
        CtkStepper, CtkNavItem, CtkStyledFrame, CtkAlertBar,
        C,
    )
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional, Sequence

import customtkinter as ctk

# ── Design tokens (match Figma Make / CTk dark theme) ─────────────────────────
C = {
    "bg":         "#212121",
    "frame":      "#2b2b2b",
    "widget":     "#343638",
    "border":     "#565B5E",
    "blue":       "#1F6AA5",
    "blue_hover": "#144870",
    "blue_bord":  "#144870",
    "text":       "#DCE4EE",
    "subtext":    "#8B9099",
    "disabled":   "#4a4d50",
    "dis_text":   "#6b7077",
    "red":        "#C0392B",
    "red_hover":  "#962d22",
    "green":      "#2E7D32",
    "green_hover":"#1B5E20",
    "seg":        "#2b2b2b",
    "seg_sel":    "#1F6AA5",
    "switch_on":  "#1F6AA5",
    "switch_off": "#565B5E",
    "slider":     "#1F6AA5",
    "progress":   "#1F6AA5",
}

_FONT_FAMILY = "Roboto"
_FONT_SIZE   = 13
_CORNER_R    = 8
_BORDER_W    = 2

# variant -> (fg_color, hover_color, text_color, border_color)
_BTN_VARIANTS = {
    "blue":        (C["blue"],     C["blue_hover"], "#ffffff", C["blue_bord"]),
    "transparent": ("transparent", "#3a3d40",       C["text"], C["border"]),
    "red":         (C["red"],      C["red_hover"],  "#ffffff", C["red_hover"]),
    "green":       (C["green"],    C["green_hover"],"#ffffff", C["green_hover"]),
    "disabled":    (C["disabled"], C["disabled"],   C["dis_text"], C["disabled"]),
}


# ── CtkStyledFrame ────────────────────────────────────────────────────────────

class CtkStyledFrame(ctk.CTkFrame):
    """Frame matching the Figma ``CtkFrame`` component: rounded corners,
    ``C['frame']`` background, ``C['border']`` border."""

    def __init__(self, master, **kw):
        kw.setdefault("fg_color", C["frame"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", 10)
        super().__init__(master, **kw)


# ── CtkStyledButton ──────────────────────────────────────────────────────────

class CtkStyledButton(ctk.CTkButton):
    """Button with Figma variant support: ``blue`` (default), ``transparent``,
    ``red``, ``green``, ``disabled``."""

    def __init__(
        self,
        master,
        text: str = "",
        variant: str = "blue",
        width: int = 0,
        **kw,
    ):
        fg, hov, txt, brd = _BTN_VARIANTS.get(variant, _BTN_VARIANTS["blue"])
        kw.setdefault("fg_color", fg)
        kw.setdefault("hover_color", hov)
        kw.setdefault("text_color", txt)
        kw.setdefault("border_color", brd)
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", _CORNER_R)
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE, weight="bold"))
        if width:
            kw["width"] = width
        if variant == "disabled":
            kw["state"] = "disabled"
        super().__init__(master, text=text, **kw)


# ── CtkStyledEntry ───────────────────────────────────────────────────────────

class CtkStyledEntry(ctk.CTkEntry):
    """Entry field with Figma styling: widget background, border highlight on
    focus (handled natively by CTk)."""

    def __init__(self, master, placeholder: str = "", width: int = 200, **kw):
        kw.setdefault("fg_color", C["widget"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", _CORNER_R)
        kw.setdefault("text_color", C["text"])
        kw.setdefault("placeholder_text_color", C["subtext"])
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE))
        super().__init__(master, placeholder_text=placeholder, width=width, **kw)


# ── CtkStyledComboBox ────────────────────────────────────────────────────────

class CtkStyledComboBox(ctk.CTkComboBox):
    """ComboBox with Figma styling."""

    def __init__(
        self,
        master,
        values: list[str] | None = None,
        width: int = 140,
        **kw,
    ):
        kw.setdefault("fg_color", C["widget"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", _CORNER_R)
        kw.setdefault("button_color", C["widget"])
        kw.setdefault("button_hover_color", C["blue_hover"])
        kw.setdefault("dropdown_fg_color", C["frame"])
        kw.setdefault("dropdown_hover_color", C["blue"])
        kw.setdefault("text_color", C["text"])
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE))
        super().__init__(master, values=values or [], width=width, **kw)


# ── CtkStyledCheckBox ───────────────────────────────────────────────────────

class CtkStyledCheckBox(ctk.CTkCheckBox):
    """CheckBox matching the Figma style: blue when checked, border when not."""

    def __init__(self, master, text: str = "", **kw):
        kw.setdefault("fg_color", C["blue"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("hover_color", C["blue_hover"])
        kw.setdefault("text_color", C["text"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", 6)
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE))
        super().__init__(master, text=text, **kw)


# ── CtkStyledSwitch ─────────────────────────────────────────────────────────

class CtkStyledSwitch(ctk.CTkSwitch):
    """Switch matching the Figma toggle style."""

    def __init__(self, master, text: str = "", **kw):
        kw.setdefault("fg_color", C["switch_off"])
        kw.setdefault("progress_color", C["switch_on"])
        kw.setdefault("button_color", "#ffffff")
        kw.setdefault("button_hover_color", "#e0e0e0")
        kw.setdefault("text_color", C["text"])
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE))
        super().__init__(master, text=text, **kw)


# ── CtkStyledRadioGroup ─────────────────────────────────────────────────────

class CtkStyledRadioGroup(ctk.CTkFrame):
    """A group of radio buttons laid out vertically (like the Figma
    ``CtkRadioGroup``).  Read the current value via ``.get()``."""

    def __init__(
        self,
        master,
        options: Sequence[str],
        default: str | None = None,
        command: Optional[Callable[[str], None]] = None,
        orientation: str = "vertical",
        **kw,
    ):
        kw.setdefault("fg_color", "transparent")
        super().__init__(master, **kw)

        self._var = tk.StringVar(value=default or (options[0] if options else ""))
        self._command = command
        self._buttons: list[ctk.CTkRadioButton] = []

        for i, opt in enumerate(options):
            rb = ctk.CTkRadioButton(
                self,
                text=opt,
                variable=self._var,
                value=opt,
                command=self._on_change,
                fg_color=C["blue"],
                border_color=C["border"],
                hover_color=C["blue_hover"],
                text_color=C["text"],
                font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE),
            )
            if orientation == "vertical":
                rb.pack(anchor="w", pady=2)
            else:
                rb.pack(side="left", padx=(0, 12))
            self._buttons.append(rb)

    def _on_change(self):
        if self._command:
            self._command(self._var.get())

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str):
        self._var.set(value)


# ── CtkStyledSegmented ──────────────────────────────────────────────────────

class CtkStyledSegmented(ctk.CTkSegmentedButton):
    """Segmented button matching the Figma ``CtkSegmented`` style."""

    def __init__(
        self,
        master,
        values: Sequence[str],
        default: str | None = None,
        command: Optional[Callable[[str], None]] = None,
        **kw,
    ):
        kw.setdefault("fg_color", C["seg"])
        kw.setdefault("selected_color", C["seg_sel"])
        kw.setdefault("selected_hover_color", C["blue_hover"])
        kw.setdefault("unselected_color", C["seg"])
        kw.setdefault("unselected_hover_color", "#3a3d40")
        kw.setdefault("text_color", C["text"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", _CORNER_R)
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE))
        super().__init__(master, values=list(values), command=command, **kw)
        if default:
            self.set(default)
        elif values:
            self.set(values[0])


# ── CtkStyledSlider ─────────────────────────────────────────────────────────

class CtkStyledSlider(ctk.CTkSlider):
    """Slider matching Figma colours."""

    def __init__(self, master, width: int = 200, **kw):
        kw.setdefault("fg_color", C["widget"])
        kw.setdefault("progress_color", C["slider"])
        kw.setdefault("button_color", C["slider"])
        kw.setdefault("button_hover_color", C["blue_hover"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", 1)
        super().__init__(master, width=width, **kw)


# ── CtkStyledProgressBar ────────────────────────────────────────────────────

class CtkStyledProgressBar(ctk.CTkProgressBar):
    """Progress bar matching the Figma component."""

    def __init__(self, master, width: int = 280, **kw):
        kw.setdefault("fg_color", C["widget"])
        kw.setdefault("progress_color", C["progress"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", 1)
        kw.setdefault("corner_radius", 6)
        kw.setdefault("height", 12)
        super().__init__(master, width=width, **kw)


# ── CtkStyledTabview ─────────────────────────────────────────────────────────

class CtkStyledTabview(ctk.CTkTabview):
    """Tabview with Figma dark-theme styling."""

    def __init__(self, master, tabs: Sequence[str] | None = None, **kw):
        kw.setdefault("fg_color", C["frame"])
        kw.setdefault("segmented_button_fg_color", C["frame"])
        kw.setdefault("segmented_button_selected_color", C["blue"])
        kw.setdefault("segmented_button_selected_hover_color", C["blue_hover"])
        kw.setdefault("segmented_button_unselected_color", C["frame"])
        kw.setdefault("segmented_button_unselected_hover_color", "#3a3d40")
        kw.setdefault("text_color", C["text"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", 10)
        super().__init__(master, **kw)
        if tabs:
            for t in tabs:
                self.add(t)


# ── CtkStyledLabel ───────────────────────────────────────────────────────────

class CtkStyledLabel(ctk.CTkLabel):
    """Label with optional ``sub`` mode for subdued text."""

    def __init__(self, master, text: str = "", sub: bool = False, **kw):
        if sub:
            kw.setdefault("text_color", C["subtext"])
            kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=12))
        else:
            kw.setdefault("text_color", C["text"])
            kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE, weight="bold"))
        super().__init__(master, text=text, **kw)


# ── CtkStyledBadge ───────────────────────────────────────────────────────────

class CtkStyledBadge(ctk.CTkLabel):
    """Small coloured badge/tag (like the Figma ``CtkBadge``)."""

    _COLORS = {
        "blue":  ("#1a3550", "#5ba3d9", "#2a5070"),
        "red":   ("#3a1a1a", "#e07070", "#7a3030"),
        "green": ("#1a3020", "#50c878", "#2a5530"),
        "gray":  ("#343638", "#8B9099", "#565B5E"),
    }

    def __init__(self, master, text: str = "", color: str = "blue", **kw):
        bg, fg, brd = self._COLORS.get(color, self._COLORS["blue"])
        kw.setdefault("fg_color", bg)
        kw.setdefault("text_color", fg)
        kw.setdefault("corner_radius", 12)
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=11, weight="bold"))
        kw.setdefault("padx", 8)
        kw.setdefault("pady", 1)
        super().__init__(master, text=text, **kw)
        self.configure(
            fg_color=bg,
            text_color=fg,
        )


# ── CtkStyledTextbox ────────────────────────────────────────────────────────

class CtkStyledTextbox(ctk.CTkTextbox):
    """Textbox matching the Figma component."""

    def __init__(self, master, width: int = 300, height: int = 120, **kw):
        kw.setdefault("fg_color", C["widget"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("corner_radius", _CORNER_R)
        kw.setdefault("text_color", C["text"])
        kw.setdefault("font", ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE))
        super().__init__(master, width=width, height=height, **kw)


# ── CtkIconButton ────────────────────────────────────────────────────────────

class CtkIconButton(ctk.CTkButton):
    """32 x 32 icon-only button matching the Figma ``IconBtn``.

    Variants: ``primary``, ``secondary``, ``ghost``, ``danger``.
    """

    _VARIANTS = {
        "primary":   (C["blue"],     C["blue_hover"], C["blue_bord"],    "#ffffff"),
        "secondary": (C["widget"],   "#3e4144",       C["border"],       C["text"]),
        "ghost":     ("transparent", "#343638",       C["frame"],        C["text"]),
        "danger":    (C["red"],      C["red_hover"],  C["red_hover"],    "#ffffff"),
    }

    def __init__(self, master, variant: str = "secondary", **kw):
        fg, hov, brd, txt = self._VARIANTS.get(variant, self._VARIANTS["secondary"])
        kw.setdefault("fg_color", fg)
        kw.setdefault("hover_color", hov)
        kw.setdefault("border_color", brd)
        kw.setdefault("border_width", _BORDER_W)
        kw.setdefault("text_color", txt)
        kw.setdefault("corner_radius", _CORNER_R)
        kw.setdefault("width", 32)
        kw.setdefault("height", 32)
        kw.setdefault("text", "")
        super().__init__(master, **kw)


# ── CtkSplitButton ──────────────────────────────────────────────────────────

class CtkSplitButton(ctk.CTkFrame):
    """Split button: main action on the left, dropdown arrow on the right.

    Parameters
    ----------
    text : str
        Label for the main part.
    options : list[str]
        Items shown in the dropdown menu.
    command : callable, optional
        Called with the selected option string when a dropdown item is chosen.
    main_command : callable, optional
        Called when the main button area is clicked.
    """

    def __init__(
        self,
        master,
        text: str = "",
        options: Sequence[str] = (),
        command: Optional[Callable[[str], None]] = None,
        main_command: Optional[Callable[[], None]] = None,
        **kw,
    ):
        kw.setdefault("fg_color", "transparent")
        # Only pass CTkFrame-safe kwargs to super
        frame_kw = {k: v for k, v in kw.items() if k in (
            "fg_color", "border_color", "border_width", "corner_radius",
            "width", "height", "bg_color",
        )}
        super().__init__(master, **frame_kw)

        self._menu_options = list(options)
        self._on_select = command

        self.main_btn = ctk.CTkButton(
            self,
            text=text,
            fg_color=C["blue"],
            hover_color=C["blue_hover"],
            border_color=C["blue_bord"],
            border_width=_BORDER_W,
            corner_radius=0,
            text_color="#ffffff",
            font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE, weight="bold"),
            command=main_command,
        )
        self.main_btn.pack(side="left")
        # round left corners only (CTk doesn't support per-corner, so we
        # approximate with a wrapping frame)

        self.arrow_btn = ctk.CTkButton(
            self,
            text="\u25bc",
            width=28,
            fg_color=C["blue_hover"],
            hover_color=C["blue"],
            border_color=C["blue_bord"],
            border_width=_BORDER_W,
            corner_radius=0,
            text_color="#ffffff",
            font=ctk.CTkFont(family=_FONT_FAMILY, size=10),
            command=self._show_menu,
        )
        self.arrow_btn.pack(side="left")

        self._menu = tk.Menu(
            self,
            tearoff=0,
            bg=C["frame"],
            fg=C["text"],
            activebackground=C["blue"],
            activeforeground="#ffffff",
            font=(_FONT_FAMILY, _FONT_SIZE),
            borderwidth=0,
            relief="flat",
        )
        for opt in self._menu_options:
            self._menu.add_command(label=opt, command=lambda o=opt: self._select(o))

    def _show_menu(self):
        x = self.arrow_btn.winfo_rootx()
        y = self.arrow_btn.winfo_rooty() + self.arrow_btn.winfo_height()
        self._menu.post(x, y)

    def _select(self, option: str):
        if self._on_select:
            self._on_select(option)


# ── CtkStepper ───────────────────────────────────────────────────────────────

class CtkStepper(ctk.CTkFrame):
    """Numeric stepper (−  value  +) matching the Figma ``Stepper``."""

    def __init__(
        self,
        master,
        value: int = 0,
        minimum: int = 0,
        maximum: int = 999,
        command: Optional[Callable[[int], None]] = None,
        **kw,
    ):
        kw.setdefault("fg_color", "transparent")
        super().__init__(master, **kw)

        self._value = value
        self._min = minimum
        self._max = maximum
        self._command = command

        self.minus_btn = ctk.CTkButton(
            self, text="\u2212", width=32, height=32,
            fg_color=C["widget"], hover_color="#3e4144",
            border_color=C["border"], border_width=_BORDER_W,
            corner_radius=0, text_color=C["text"],
            font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE),
            command=self._dec,
        )
        self.minus_btn.pack(side="left")

        self.label = ctk.CTkLabel(
            self, text=str(self._value), width=44, height=32,
            fg_color=C["bg"], text_color=C["text"],
            font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE),
        )
        self.label.pack(side="left")

        self.plus_btn = ctk.CTkButton(
            self, text="+", width=32, height=32,
            fg_color=C["widget"], hover_color="#3e4144",
            border_color=C["border"], border_width=_BORDER_W,
            corner_radius=0, text_color=C["text"],
            font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE),
            command=self._inc,
        )
        self.plus_btn.pack(side="left")

    def _dec(self):
        if self._value > self._min:
            self._value -= 1
            self.label.configure(text=str(self._value))
            if self._command:
                self._command(self._value)

    def _inc(self):
        if self._value < self._max:
            self._value += 1
            self.label.configure(text=str(self._value))
            if self._command:
                self._command(self._value)

    def get(self) -> int:
        return self._value

    def set(self, value: int):
        self._value = max(self._min, min(self._max, value))
        self.label.configure(text=str(self._value))


# ── CtkNavItem ───────────────────────────────────────────────────────────────

class CtkNavItem(ctk.CTkButton):
    """Sidebar navigation item matching the Figma ``NavItem``.

    Call ``set_active(True/False)`` to toggle the highlight."""

    def __init__(self, master, text: str = "", active: bool = False, **kw):
        self._active = active
        kw.setdefault("corner_radius", 6)
        kw.setdefault("anchor", "w")
        kw.setdefault("font", ctk.CTkFont(
            family=_FONT_FAMILY, size=_FONT_SIZE,
            weight="bold" if active else "normal",
        ))
        kw.setdefault("border_width", 0)
        kw.setdefault("height", 28)
        super().__init__(master, text=text, **kw)
        self._apply_active()

    def _apply_active(self):
        if self._active:
            self.configure(
                fg_color=C["blue"],
                hover_color=C["blue_hover"],
                text_color="#ffffff",
                font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE, weight="bold"),
            )
        else:
            self.configure(
                fg_color="transparent",
                hover_color=C["widget"],
                text_color=C["text"],
                font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE),
            )

    def set_active(self, active: bool):
        self._active = active
        self._apply_active()


# ── CtkAlertBar ──────────────────────────────────────────────────────────────

class CtkAlertBar(ctk.CTkFrame):
    """Inline alert bar matching the Figma alert pattern.

    Types: ``info``, ``success``, ``warning``, ``error``.
    """

    _TYPES = {
        "info":    ("#1a2f45", "#5ba3d9", "#2a5070"),
        "success": ("#1a3020", "#50c878", "#2a5530"),
        "warning": ("#3a2f10", "#d4a830", "#5a4a20"),
        "error":   ("#3a1a1a", "#e07070", "#6a2a2a"),
    }

    def __init__(self, master, text: str = "", alert_type: str = "info", **kw):
        bg, fg, brd = self._TYPES.get(alert_type, self._TYPES["info"])
        kw.setdefault("fg_color", bg)
        kw.setdefault("border_color", brd)
        kw.setdefault("border_width", 1)
        kw.setdefault("corner_radius", _CORNER_R)
        super().__init__(master, **kw)

        self.label = ctk.CTkLabel(
            self, text=text, text_color=fg,
            font=ctk.CTkFont(family=_FONT_FAMILY, size=_FONT_SIZE),
        )
        self.label.pack(padx=12, pady=7)


# ── Convenience: apply_figma_theme ───────────────────────────────────────────

def apply_figma_theme():
    """Apply the Figma dark-theme defaults globally.

    Call once before creating any windows::

        import ctk_components
        ctk_components.apply_figma_theme()
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
