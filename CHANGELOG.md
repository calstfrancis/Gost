# Changelog

## [1.2.0] – 2026-05-22

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

## [1.1.0] – 2026-05-06

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

## [1.0.0] – initial release

- Original monolithic `essay_builder.py`.
- LaTeX-only output with SBL, Chicago, MLA, APA styles.
