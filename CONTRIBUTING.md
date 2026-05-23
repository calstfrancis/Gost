# Contributing to Gost

## Code structure

```
essay_builder/
  app.py             — GApplication entry point, font-install helper
  window.py          — GostWindow (Adw.ApplicationWindow) — the entire UI
  texgen.py          — LaTeX template generator (no GTK dependency)
  typstgen.py        — Typst template generator (no GTK dependency)
  wordgen.py         — Word/ODT template generator (optional python-docx dependency)
  config.py          — Persistent JSON config (~/.config/gost/config.json)
  preview_compiler.py — Compile .typ/.tex to PNG pages for in-app preview
  journal_importer.py — Parse .tex/.cls/.sty files and extract settings
  validators.py      — Input validation helpers (bib path, output path, engine)
  logger.py          — Shared logger ("gost")
  version.py         — VERSION string
tests/
  test_texgen.py     — Unit tests for texgen.generate()
  test_typstgen.py   — Unit tests for typstgen.generate()
```

**Key design principle:** `texgen.py` and `typstgen.py` have zero GTK imports. All template logic lives there and is covered by tests. The GTK layer in `window.py` only calls `generate()` and displays the result.

## GTK4 / Adwaita widget hierarchy

`GostWindow` is an `Adw.ApplicationWindow`. Its content tree:

```
Adw.ToastOverlay
  └── Gtk.Box (vertical)
        ├── Adw.HeaderBar  (format toggle, Preview, Export, Copy, Profiles, Import buttons)
        └── Gtk.Box (horizontal, hexpand+vexpand)
              ├── Gtk.ListBox  ← navigation sidebar (one row per panel)
              └── Gtk.Stack    ← content area
                    ├── "metadata"  → _build_metadata_panel()
                    ├── "style"     → _build_style_panel()
                    ├── "layout"    → _build_layout_panel()
                    ├── "features"  → _build_features_panel()
                    ├── "languages" → _build_languages_panel()
                    ├── "headers"   → _build_headers_panel()
                    ├── "bib"       → _build_bib_panel()
                    └── "preview"   → _build_preview_panel()
```

Each panel returns a widget that is a child of the `Gtk.Stack`. Navigation rows in the `Gtk.ListBox` use `_nav_select(key)` to switch the visible child.

The preview panel has its own inner `Gtk.Stack` with two children: `"source"` (a `Gtk.TextView`) and `"compiled"` (a `Gtk.ScrolledWindow` containing a `Gtk.FlowBox` of page image cards).

## State flow

1. UI widgets emit signals → handler calls `_dirty_preview()` and updates `self._cit_style` / `self._engine` / `self._paper` / `self._font_size` as needed.
2. `_collect_state()` snapshots all widget values into a plain `dict`.
3. `texgen.generate(state)` or `typstgen.generate(state)` converts the dict to a string.
4. `_apply_state(state)` is the reverse: takes a dict and pushes values back into widgets (used by profile load and journal import).

## Adding a new citation style

1. **`texgen.py`** — add an entry to `STYLE_DEFAULTS` and `HEADING_STYLES`.
2. **`typstgen.py`** — add entries to `TYPST_CIT_STYLES` and `TYPST_HEADING_STYLES`.
3. **`window.py`** — add the style key and display label to the `CITATION_STYLES` list near the top of `_build_style_panel()`. The radio-button group is built dynamically from that list.
4. Add test cases for the new style in `tests/test_texgen.py` and `tests/test_typstgen.py`.

## Adding a new extra package

### LaTeX

1. Add a `(key, display_label, description)` tuple to `LATEX_FEATURES` in `window.py`.
2. Add `"key": r"\usepackage{…}"` to `FEATURE_PACKAGES` in `texgen.py`.
3. Add a test in `TestGenerateExtras` in `tests/test_texgen.py`.

### Typst

1. Add a `(key, display_label, description)` tuple to `TYPST_FEATURES` in `window.py`.
2. Add `"key": '#import "@preview/…"'` to `TYPST_FEATURE_IMPORTS` in `typstgen.py`.
3. Add a test in `TestTypstGenerateExtras` in `tests/test_typstgen.py`.

## Running tests

No GTK display required — `texgen` and `typstgen` have no UI dependency.

```bash
python3 -m unittest discover tests/ -v
# or, if pytest is available:
python3 -m pytest tests/ -v
```

## Running the app

```bash
python3 -m essay_builder.app
```

Requires Python 3.10+, PyGObject, GTK4 ≥ 4.10, and libadwaita ≥ 1.4. See `HELP.md` for distribution-specific install commands.

## Building an AppImage

```bash
bash build-appimage.sh
```

The script bundles the Python source, a compatible CPython, and all typelibs into a self-contained `gost-<version>-x86_64.AppImage`. Run on the oldest distribution you want to support for widest compatibility.

## Code style

- Python 3.10+ syntax; type hints on all public functions.
- No GTK imports in `texgen.py`, `typstgen.py`, `validators.py`, or `journal_importer.py`.
- Keep `generate()` in both generator modules as a pure function: `dict → str`, no side effects.
- Comments only where the *why* is non-obvious (a subtle LaTeX invariant, a workaround for a GTK behaviour, etc.).
