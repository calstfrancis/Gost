# Changelog

## [0.1.7] – 2026-05-23

### Added
- **Simple mode in header bar** — the Simple toggle is now always visible in the top panel, labelled "Simple", instead of being buried in the hamburger menu.
- **About dialog developer link** — author name in Credits links to <https://calstfrancis.github.io>.

### Fixed
- About dialog version now reflects the actual package version (`__version__`) rather than a hardcoded string.

---

## [0.1.6.1] – 2026-05-23

### Fixed
- pipx desktop integration now runs automatically on first launch — no manual `gost-setup-desktop` step required.
- `ModuleNotFoundError: No module named 'gi'` with pipx now documented; fix is `pipx install gost-academic --system-site-packages`.

---

## [0.1.5] – 2026-05-23

### Added
- **Word / ODT export** — new Word format button in the header bar generates a fully styled `.docx` template with correct margins, font, line spacing, heading styles, and a bibliography section for all seven citation styles. ODT export is available via LibreOffice headless conversion. Requires `python-docx` (bundled in the AppImage; `pip install gost-academic[word]` for source installs).
- **PyPI package** (`gost-academic`) — Gost is now published on PyPI. Install with `pip install gost-academic` or `pip install gost-academic[word]` for Word export support.
- **GitHub Actions publish workflow** — releases tagged on GitHub automatically publish to PyPI via OIDC trusted publishing (no API token required).

### Changed
- `setup.py` replaced by `pyproject.toml` (modern packaging standard).
- `_ensure_desktop_integration()` now updates installed icon and desktop entry when the source file is newer, preventing a stale launcher icon after source-tree updates.

---

## [0.1.4] – 2026-05-23

### Added
- **ASA citation style** — American Sociological Association author-date; centered-bold headings; `asa` BibLaTeX backend; `american-sociological-association` CSL for Typst.
- **Turabian citation style** — student edition of Chicago Notes-Bibliography; uses `chicago-notes` / `chicago-fullnote-bibliography`.
- **Harvard citation style** — author-date widely used in UK/European/Australian academia; `authoryear` BibLaTeX backend; `harvard-cite-them-right` CSL for Typst.
- **Hamburger menu** — Profiles, Style Packs, Import Journal, and About moved out of the header bar into a ⋮ menu, decluttering the toolbar.
- **Simple Mode toggle** (on by default) — hides Chapters, Custom Code, and Grammar panels for everyday use; accessible from the hamburger menu.
- **Hover tooltips** — every control in every panel now has an accessibility tooltip describing its purpose.

### Changed
- **Default line spacing** is now **Double** — standard requirement for most academic journal and course submissions.
- **Sidebar title bar removed** — the "Sections" header strip above the navigation list is gone; the list now starts at the top of the sidebar.
- Citation style selector is now displayed in two rows (SBL / Chicago / MLA / APA on top; ASA / Turabian / Harvard below) to accommodate the expanded set without crowding.
- Copy button in header bar is now icon-only; tooltip updates to reflect current format (Typst or LaTeX).
- Preview button in header bar is now icon-only.

### Fixed
- `_on_format_toggled` no longer calls `set_label()` on the icon-only copy button.

---

## [0.1.2] – 2026-05-22

### Added
- **Compiled preview** — click the header-bar Preview button to compile the template via `typst` or `latexmk` and render the actual PDF pages as images inside the app. Falls back gracefully when the compiler is not installed.
- **Headers & Footers panel** — choose from Auto, None, Page numbers only, Title·Page, Section·Page, Author·Page, or Double-sided running headers. Includes a header rule toggle and first-page suppression. Both LaTeX (fancyhdr) and Typst (`#set page(header:…)`) are supported.
- **Journal template importer** — open any `.tex`, `.cls`, or `.sty` file; the app extracts font, paper size, margin, line spacing, paragraph indent, and BibLaTeX style and merges them into the current settings.
- **Typst endnotes** — `#endnote[…]` / `#print-endnotes()` inline implementation (no external package required).
- **About dialog** — application name, version, credits, license, and release notes.
- **GOST Type B font toggle** — switch in the sidebar to use the GOST Type B engineering lettering as the application UI font.
- `preview_compiler.py` — standalone module for compiling Typst/LaTeX to PNG.
- `journal_importer.py` — standalone parser for journal template files.

### Changed
- **Renamed to Gost** (previously "Academic Essay Builder" / "LaTemplater").
- Default output format is now **Typst** (was LaTeX).
- Format toggle order changed to Typst | LaTeX in the header bar.
- Notes mode row is now split: LaTeX Notes and Typst Notes are shown only for their respective format.
- Header-bar Preview button now triggers compiled view instead of source view.
- Config directory changed to `~/.config/gost`, cache to `~/.cache/gost`.

### Fixed
- Format toggle now correctly shows/hides all LaTeX-only widgets after all panels are built.
- `_compile_done` no longer repeats via GLib idle add (returns `GLib.SOURCE_REMOVE`).

---

## [0.1.1] – 2026-05-06

### Added
- Typst template generation (`.typ` output).
- AppImage build script (`build-appimage.sh`).
- Extra packages / features panel.
- Per-style heading show rules (titlesec for LaTeX, `#show heading` for Typst).
- Template profiles — save/load/delete named configurations.
- Table of contents toggle.
- Language support — Russian, Hebrew, Japanese, Tibetan, Sanskrit, Ancient Greek, Chinese.
- Drop caps and marginalia for both LaTeX and Typst.
- Author name and bib file path persisted across sessions.

### Fixed
- LaTeX engine selector hidden when Typst format is active.
- Dead space in lower half of window.
- Document Structure panel removed.
- Preview button now works from any panel.
- Format toggle updates preview live.

---

## [0.1.0] – initial release

- Original monolithic `essay_builder.py`.
- LaTeX-only output with SBL, Chicago, MLA, APA styles.
