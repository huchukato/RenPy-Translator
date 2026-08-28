# Ren'Py Translator — Updates

Release history for Ren'Py Translator, listed from newest to oldest.

## v2.3.2

Improves compatibility with games that store dialogue and interface text in Python data structures.

### Fixed

- Translatable `_("...")` calls are now extracted even when they appear inside `init python` and other Python blocks.
- Added support for gettext calls using single-quoted strings.
- Escaped quotes and other Python string escapes are decoded before translation and safely escaped again when writing Ren'Py TL files.
- Fixed games such as Risky Business, where most dynamic dialogue is registered through a `translation_hints.rpy` catalog instead of conventional Ren'Py dialogue statements.

## v2.3.1

Patch release focused on packaging reliability and language support.

### Fixed

- Added `ctk_components.py` to the Windows, macOS, Linux and generic release packages, fixing the `ModuleNotFoundError` that prevented packaged builds from starting after the v2.3.0 GUI restyle.

### Added

- Added Turkish (`tr`) as a supported source and target language across the GUI and translation backends.

## v2.3.0

Introduces a Figma-based GUI restyle and fixes walkthrough mod hint duplication.

### What's New

- Introduced `ctk_components.py`, a reusable CustomTkinter component library built from the project's Figma design tokens.
- Updated the main GUI and Settings dialog to use the shared styled components and consistent color palette.
- Added `demo_components.py`, a standalone showcase of the available styled widgets.

### Fixed

- Fixed third-party walkthrough mods showing both the translated caption and original English text before the hint.
- The compatibility patch now measures the hint suffix using the original untranslated caption and appends it only to the translated caption.

### Technical Details

- `tr_writer.py::_wt_override_patch()` reimplements the mod's `MENUS` lookup and supports dynamic captions processed through `renpy.substitute()`.
- Existing GUI functionality and event handlers were retained during the visual restyle.

## v2.2.0

Adds compatibility with third-party walkthrough mods and expands the build system to all platforms.

### What's New

- Added automatic compatibility patches for walkthrough mods that use a `MENUS` dictionary for choice hints.
- Added `build/build_mac_app.sh` with automatic DMG creation and an Applications symlink.
- Added `build/build_linux.sh` for a `.tar.gz` archive with an embedded Python environment.
- Added `build/build_win.sh` for a ZIP that creates its environment on first launch through `start.bat`.
- macOS DMGs use the name `RenPy-Translator[vX.Y.Z]-<arch>.dmg`.

### Fixed

- Fixed walkthrough hints disappearing when translated captions no longer matched English-only `MENUS` keys.
- Stopped extracting dead `MENUS` dictionary values from `init python` blocks.

### Technical Details

- The walkthrough compatibility patch is generated as `game/renpy_translator_wt_patch.rpy`.
- At startup it scans TL files, maps translated captions to their originals and wraps `get_override` with a translated-caption fallback.

## v2.1.0

Major interface and workflow update with faster and more reliable translation backends.

### What's New

- Replaced the single translation action with the Analyze & Translate, review/edit, Save Translation and Export workflow.
- Added an editable, paginated translation table.
- Simplified the backend selector to Google Turbo, Bing Turbo, OpenRouter and Llama Local.
- Added Safe, Balanced and Fast translation profiles.
- Improved Google Turbo with multiple mirror endpoints, reusable sessions, health tracking, adaptive pacing and exponential backoff.
- Added a persistent per-language-pair translation cache in `~/.cache/renpy-translator/`.
- Added source-language selection with automatic detection.
- Added Spanish to the English and Italian interface languages.
- Added extraction for `renpy.input()` prompts and native Ren'Py `_("...")` UI strings.
- Added remembered preferences, fit-to-screen window sizing and CTkMaker export.
- Updated generic build versioning to read from `pyproject.toml`.

### Fixed

- Fixed dialogues with Ren'Py formatting tags being skipped.
- Fixed common menu choices such as Exit, Continue, Save and Load being treated as Python identifiers.
- Fixed multiline translations causing Ren'Py parse errors.
- Fixed missing main-menu strings caused by excluding `screens.rpyc` from decompilation.
- Fixed the splash screen reappearing after returning to the main menu.
- Fixed exported folders using `autorun` instead of the actual game name.
- Improved Google Turbo fallback when a batch separator is altered.
- Corrected the splash image path used by Save and Export.

### Removed

- Removed the old single-step Start Translation pipeline.
- Removed non-Turbo Google and Bing backends from the GUI selector.

## Credits

- UnRen Tools by **huchukato, goobdoob, jimmy5 & Sam**
- rpatool by **[Shiz](https://codeberg.org/shiz/rpatool)**
- unrpyc by **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
