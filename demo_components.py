#!/usr/bin/env python3
"""Demo visuale di tutti i componenti ctk_components."""

import customtkinter as ctk
from ctk_components import (
    CtkStyledFrame, CtkStyledButton, CtkStyledEntry, CtkStyledComboBox,
    CtkStyledCheckBox, CtkStyledSwitch, CtkStyledRadioGroup,
    CtkStyledSegmented, CtkStyledSlider, CtkStyledProgressBar,
    CtkStyledTabview, CtkStyledLabel, CtkStyledBadge, CtkStyledTextbox,
    CtkIconButton, CtkSplitButton, CtkStepper, CtkNavItem, CtkAlertBar,
    C, apply_figma_theme,
)

apply_figma_theme()

app = ctk.CTk()
app.title("CustomTkinter UI Library — Demo")
app.geometry("1100x750")
app.configure(fg_color=C["bg"])

# ── Scrollable container ────────────────────────────────────────────────────
scroll = ctk.CTkScrollableFrame(app, fg_color=C["bg"])
scroll.pack(fill="both", expand=True, padx=16, pady=16)


def section(parent, title):
    lbl = ctk.CTkLabel(
        parent, text=title,
        font=ctk.CTkFont(family="Roboto", size=10, weight="bold"),
        text_color=C["subtext"],
    )
    lbl.pack(anchor="w", pady=(14, 4))
    frame = CtkStyledFrame(parent)
    frame.pack(fill="x", pady=(0, 4))
    return frame


def row(parent):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", pady=4)
    return f


# ── HEADER ──────────────────────────────────────────────────────────────────
hdr = CtkStyledFrame(scroll)
hdr.pack(fill="x", pady=(0, 4))
r = row(hdr)
CtkStyledLabel(r, text="CustomTkinter UI Library").pack(side="left", padx=8)
CtkStyledLabel(r, text="Dark theme · v5.x", sub=True).pack(side="left", padx=8)
CtkStyledBadge(r, text="Stable", color="green").pack(side="right", padx=4)
CtkStyledBadge(r, text="18 widgets", color="blue").pack(side="right", padx=4)

# ── BUTTONS ─────────────────────────────────────────────────────────────────
sec = section(scroll, "CTKBUTTON — VARIANTS")
r = row(sec)
for variant in ("blue", "transparent", "red", "green", "disabled"):
    CtkStyledButton(r, text=variant.capitalize(), variant=variant).pack(side="left", padx=4)

sec = section(scroll, "CTKBUTTON — ICON ONLY / SPLIT / STEPPER")
r = row(sec)
CtkIconButton(r, variant="primary", text="\u25b6").pack(side="left", padx=4)
CtkIconButton(r, variant="secondary", text="\u23f8").pack(side="left", padx=4)
CtkIconButton(r, variant="ghost", text="\u2606").pack(side="left", padx=4)
CtkIconButton(r, variant="danger", text="\u2717").pack(side="left", padx=4)
ctk.CTkFrame(r, width=16, fg_color="transparent").pack(side="left")
CtkSplitButton(r, text="Export Mod", options=["Export .zip", "Export folder", "Copy"]).pack(side="left", padx=4)
ctk.CTkFrame(r, width=16, fg_color="transparent").pack(side="left")
CtkStepper(r, value=3).pack(side="left", padx=4)

# ── INPUTS ──────────────────────────────────────────────────────────────────
sec = section(scroll, "CTKENTRY / CTKTEXTBOX / CTKCOMBOBOX")
r = row(sec)
CtkStyledEntry(r, placeholder="Search strings...", width=220).pack(side="left", padx=4)
CtkStyledEntry(r, placeholder="Path to game...", width=260).pack(side="left", padx=4)
r = row(sec)
CtkStyledComboBox(r, values=["All files", "script.rpy", "day2.rpy"], width=160).pack(side="left", padx=4)
CtkStyledComboBox(r, values=["English", "Italian", "French"], width=130).pack(side="left", padx=4)
CtkStyledComboBox(r, values=["Auto", "Red", "Green", "Blue"], width=110).pack(side="left", padx=4)
r = row(sec)
CtkStyledTextbox(r, width=400, height=70).pack(side="left", padx=4)

# ── SELECTION ───────────────────────────────────────────────────────────────
sec = section(scroll, "CTKCHECKBOX / CTKSWITCH")
r = row(sec)
CtkStyledCheckBox(r, text="Export all with colors").pack(side="left", padx=12)
CtkStyledCheckBox(r, text="Export only best").pack(side="left", padx=12)
CtkStyledCheckBox(r, text="Auto-analyze on open").pack(side="left", padx=12)
r = row(sec)
CtkStyledSwitch(r, text="Dark mode").pack(side="left", padx=12)
CtkStyledSwitch(r, text="Auto-save").pack(side="left", padx=12)
CtkStyledSwitch(r, text="Show hints").pack(side="left", padx=12)

sec = section(scroll, "CTKRADIOGROUP / CTKSEGMENTED")
r = row(sec)
CtkStyledRadioGroup(r, options=["All", "Best only", "Neutral", "Bad"], orientation="horizontal").pack(side="left", padx=12)
r = row(sec)
CtkStyledSegmented(r, values=["Choices", "Log"], default="Choices").pack(side="left", padx=4)
CtkStyledSegmented(r, values=["With colors", "Best only"], default="With colors").pack(side="left", padx=12)

sec = section(scroll, "CTKSLIDER")
r = row(sec)
CtkStyledSlider(r, width=240).pack(side="left", padx=12)
CtkStyledSlider(r, width=240).pack(side="left", padx=12)

# ── DISPLAY ─────────────────────────────────────────────────────────────────
sec = section(scroll, "CTKPROGRESSBAR")
r = row(sec)
p1 = CtkStyledProgressBar(r, width=240)
p1.set(0.65)
p1.pack(side="left", padx=4)
CtkStyledLabel(r, text="65%", sub=True).pack(side="left", padx=4)
p2 = CtkStyledProgressBar(r, width=240)
p2.set(1.0)
p2.pack(side="left", padx=12)
CtkStyledLabel(r, text="100%", sub=True).pack(side="left", padx=4)

sec = section(scroll, "CTKLABEL / CTKBADGE")
r = row(sec)
CtkStyledLabel(r, text="Default label — 13px Roboto medium").pack(side="left", padx=8)
CtkStyledLabel(r, text="Subdued label — 12px Roboto regular", sub=True).pack(side="left", padx=8)
r = row(sec)
CtkStyledBadge(r, text="Processing", color="blue").pack(side="left", padx=4)
CtkStyledBadge(r, text="Complete", color="green").pack(side="left", padx=4)
CtkStyledBadge(r, text="Error", color="red").pack(side="left", padx=4)
CtkStyledBadge(r, text="Skipped", color="gray").pack(side="left", padx=4)

sec = section(scroll, "CTKALERTBAR")
for t in ("info", "success", "warning", "error"):
    msgs = {
        "info": "Analysis complete — 3 choices found.",
        "success": "Mod exported to /output/mod.zip",
        "warning": "Parse error in endings.rpy — skipped.",
        "error": "Failed to load game — path invalid.",
    }
    CtkAlertBar(sec, text=msgs[t], alert_type=t).pack(fill="x", pady=2, padx=4)

sec = section(scroll, "CTKTABVIEW")
tv = CtkStyledTabview(sec, tabs=["Tab 1", "Tab 2", "Tab 3"])
tv.pack(fill="x", padx=4, pady=4)
CtkStyledLabel(tv.tab("Tab 1"), text="Content for Tab 1 — analysis results").pack(padx=8, pady=8)
CtkStyledLabel(tv.tab("Tab 2"), text="Content for Tab 2 — log output").pack(padx=8, pady=8)
CtkStyledLabel(tv.tab("Tab 3"), text="Content for Tab 3 — export settings").pack(padx=8, pady=8)

# ── NAVITEM ─────────────────────────────────────────────────────────────────
sec = section(scroll, "CTKNAVITEM (SIDEBAR)")
r = row(sec)
sidebar = CtkStyledFrame(r)
sidebar.pack(side="left", padx=4)
for i, label in enumerate(["All", "Buttons", "Inputs", "Selection", "Display"]):
    CtkNavItem(sidebar, text=label, active=(i == 0)).pack(fill="x", padx=4, pady=2)

app.mainloop()
