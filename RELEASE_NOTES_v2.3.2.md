# Release Notes — Ren'Py Translator v2.3.2

Ren'Py Translator v2.3.2 improves compatibility with games that store dialogue and interface text in Python data structures.

## Fixed

- Translatable `_("...")` calls are now extracted even when they appear inside `init python` and other Python blocks.
- Added support for gettext calls using single-quoted strings.
- Escaped quotes and other Python string escapes are decoded before translation and safely escaped again when writing Ren'Py TL files.

This fixes games such as Risky Business, where most dynamic dialogue is registered through a `translation_hints.rpy` catalog instead of conventional Ren'Py dialogue statements.

## Download

**Ren'Py Translator v2.3.2**
