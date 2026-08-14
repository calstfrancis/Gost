# Changelog

## [0.2.0-dev3]

### Added
- **Welcome / What's New window.** Shown on first launch (a quick-start tour) and again after any version bump (jumping straight to a live-rendered What's New tab from `CHANGELOG.md`), matching the rest of the house style. Gost also starts naming its releases now — this cycle's predecessor, 0.1.12, has been retroactively named "Steady Margin" so the About window and this window have something to show; see the `__release_name__` constant in `essay_builder/__init__.py`.
- **Autosave recovery for hand-edited source.** Switching the preview to Source mode and editing it directly was the one kind of work Gost never persisted anywhere at all. Gost now snapshots that manual edit to `~/.local/share/gost/autosave.json` every 3 minutes and offers to restore it on the next launch if it's still there.
- **Typst is now bundled with the Flatpak.** The same `typst` 0.14.2 build Rubric ships is installed to `/app/bin/typst`, so Typst preview and PDF export work immediately after install with no host toolchain. The bundled GOST Type B font moves to `/app/share/fonts` where both the app and Typst find it.

### Changed
- **The Flatpak no longer escapes its sandbox.** Compilation previously ran on the host via `flatpak-spawn --host`, which required `--talk-name=org.freedesktop.Flatpak` (a full host-command escape), plus `--filesystem=home` and `--filesystem=/tmp`. All three are gone; permissions are now `ipc`, `wayland`/`fallback-x11`, `dri`, `network` (LanguageTool), and `xdg-documents`. Exports outside Documents go through the file portal, which needs no static permission.
- Font setup no longer copies into the user's home when running under Flatpak — the build installs fonts system-wide inside the sandbox instead.

### Fixed
- **The Flatpak icon now shows consistently.** The manifest only installed the scalable SVG; launchers that don't invoke an SVG loader showed a blank or generic icon. It now rasterises the same PNG sizes `install.sh` already generates for non-Flatpak installs.

### Removed
- **LaTeX preview is unavailable in the Flatpak build.** A full TeX installation cannot reasonably be bundled, and keeping it would have meant keeping the sandbox escape. LaTeX source generation and `.tex` export are unaffected, and running Gost from source keeps LaTeX preview exactly as before. Typst — the preferred output format — is bundled and needs no setup.

### Removed
- RPM and DEB packaging dropped — `build-rpm.sh`, `build-deb.sh`, and `packaging/gost.spec` removed, along with the CI job that built and attached them to releases. Distribution is flatpak-only via the self-hosted OSTree repo, matching Rubric, Kopilka, and Zerkalo.

---

## [0.1.12] "Steady Margin" – 2026-06-18

### Changed
- Book mode toggle moved exclusively to the status bar; untoggling returns to article mode. The sidebar Document class switch is removed.
- GOST Type B font toggle moved exclusively to the status bar; the sidebar switch is removed.

---

## [0.1.11] – 2026-06-18 — Flatpak, statusbar, book publishing layout, per-page headers

### Added
- **Flatpak packaging** — `ca.calstfrancis.Gost.yml` manifest, `dev-build.sh`, `publish-flatpak.sh`, and `flatpak-gen-sources.sh`. Bundles python-docx offline; LaTeX/Typst compilers are called via `flatpak-spawn --host` so the sandbox stays small.
- **Status bar** — new bottom bar (libadwaita `ToolbarView`) with GOST Type B toggle and Book mode toggle on the left, and a version button (opens About / release notes) on the right. Mirrors Rubric's layout.
- **Book document class** — Layout panel now has an Article / Book toggle (LaTeX only). Book mode uses `extbook` with `\frontmatter` / `\mainmatter` / `\backmatter` structure and promotes top-level headings to `\chapter{}`. Multi-file project export also writes `\chapter{}` stubs in book mode.
- **More paper sizes** — Paper size is now a combo row with Letter, A4, A5, B5, Legal, Executive, and **Custom**. Custom reveals width/height fields (in mm); works in both LaTeX and Typst.
- **More font sizes** — Font size is now a combo row with all `extarticle`/`extbook` sizes: 8 pt, 9 pt, 10 pt, 11 pt, 12 pt, 14 pt, 17 pt, 20 pt.
- **Binding gutter / twoside** — "Binding gutter (twoside)" switch in Layout & Spacing replaces the uniform margin with separate inner and outer margin fields. Adds `twoside` to `\documentclass`, uses `inner=/outer=` in the geometry package, and `margin: (inside:, outside:)` in Typst. Works for both article and book.
- **Metric/imperial margin units** — "in / mm" toggle in the Page Layout group converts all margin spin rows between inches and millimetres in place. Generators always receive inch values internally; the preference is saved between sessions.
- **Recto chapter openings** — "Chapters start on right-hand page" switch adds `openright` to `\documentclass` (book mode); LaTeX inserts a blank verso page before each chapter as needed.
- **Print-ready bleed + crop marks** — "Bleed + crop marks" switch with a bleed mm spin. Expands the PDF paper by the bleed amount on all sides, uses geometry's `layoutwidth/layoutheight/layouthoffset` to keep content centred, and adds `\usepackage{crop}` with `cam` marks at the trim line.
- **Chapter label style** — Combo in Style panel (book mode, LaTeX): default `CHAPTER N / Title`, compact `N. Title`, or `Title only` (no number, via titlesec `\titleformat{\chapter}`).
- **Widow/orphan control** — Combo in Paragraph Style group: Relaxed (default), Standard (`\clubpenalty=\widowpenalty=1000`), or Strict (10000, also sets `\displaywidowpenalty`).
- **Front matter pages** — Three switches in the Metadata panel (LaTeX book mode): **Half-title page** (recto with book title only before title page), **Copyright page** (verso with `©`, year, author, ISBN placeholder), **Dedication page** (centred italic text, with a dedicated text-entry field).
- **Book-standard header** — New header style "Book standard (author verso, chapter recto)": author last name on verso right `[RE]`, `\leftmark` (chapter) on recto left `[LO]`, page numbers on the outer edge.
- **Custom per-position headers** — New header style "Custom (choose per-position content)" reveals a panel with four combos — Verso left `[LE]`, Verso right `[RE]`, Recto left `[LO]`, Recto right `[RO]` — each offering: Empty / Page number / Chapter (`\leftmark`) / Section (`\rightmark`) / Author / Book title.
- **Footer page numbers** — "Footer page numbers" combo in Headers panel (independent of header style): None / Bottom centre / Bottom outer (`[LE,RO]`). Outer is the standard book layout. Works alongside any header style; loads fancyhdr automatically if not already active.
- **Empty blank verses** — Switch in Layout panel: redefines `\cleardoublepage` so auto-inserted blank pages (from `openright`) are completely empty — no header, footer, or page number. Required for professional printing.
- **Heading font pairing** — "Heading font" combo in Font & Encoding: Same as body (default) / Sans-serif (`\sffamily`) / Custom font (fontspec `\newfontfamily`). Overrides titlesec `\titleformat` for all heading levels including chapter.
- **Footnote style** — "Footnote numbering" combo in Style panel: Document default (1, 2, 3…) / Restart per page (`perpage` package) / Symbols (*, †, ‡, §, ¶).
- **Part title page style** — "Part title page style" combo in Style panel (book mode): Plain (default) / Full-page centred / Centred with rule (horizontal rule below title). Uses titlesec `\titleformat{\part}`.
- **Drop cap at chapter opening** — Switch in Style panel: auto-injects `\lettrine[lines=3]{F}{}` stub into each chapter body, ready for the user to fill in. Loads `lettrine` if not already in Extra Packages.
- **Chapter epigraph stubs** — Switch in Style panel: injects `\epigraph{Quote text here.}{--- Attribution}` below each chapter heading. Works with the epigraph package.
- **List of figures / list of tables** — Two switches in the Front Matter section of the Metadata panel: insert `\listoffigures` / `\listoftables` after `\tableofcontents` (both article and book).
- **Index** — Switch in the new Back Matter section: loads `imakeidx` with `\makeindex` in the preamble and inserts `\printindex` in the backmatter.
- **Colophon page** — Switch in Back Matter: inserts a closing page with centred italic text. Defaults to "Typeset in [current font] using LaTeX"; editable via a text entry that appears when the switch is on.

---

## [0.1.10] – 2026-06-06

### Added
- GitHub Actions release workflow — publishing a GitHub Release now automatically builds `gost_*.deb` (Debian/Ubuntu) and `gost-*.noarch.rpm` (Fedora/openSUSE) and attaches them to the release assets.

### Removed
- AppImage distribution dropped in favour of native RPM and DEB packages.
- PyPI (`gost-academic`) publishing dropped; install via RPM, DEB, or from source.

---

## [0.1.9] – 2026-06-06

### Added
- **RPM package** (`gost-0.1.9-1.noarch.rpm`) — install on Fedora, openSUSE, RHEL, and derivatives via `sudo zypper in ./gost-*.rpm` or `sudo rpm -i gost-*.rpm`. Build from source with `bash build-rpm.sh`.
- **DEB package** (`gost_0.1.9_all.deb`) — install on Debian, Ubuntu, Mint, and derivatives via `sudo apt install ./gost_*.deb`. Build from source with `bash build-deb.sh` on a Debian-based host.
- `packaging/gost.spec` — RPM spec file for distribution packaging.
- `build-rpm.sh` / `build-deb.sh` — reproducible build scripts for both package formats.

### Changed
- README updated with RPM and DEB installation instructions and per-distribution package manager commands.

---

## [0.1.8] – 2026-05-23

### Added
- **Live auto-preview pane** — always-visible right panel that recompiles and renders the template automatically on any settings change (400 ms debounce). Toggled by a column-view button in the header bar; preference saved between sessions.
- **Editable source view** — the Source tab in the Preview panel is now editable. Manual edits are used directly for compilation. A "● Edited" badge indicates the buffer has diverged from the auto-generated source; click "Regenerate" to reset.
- **Chapter reordering** — up/down arrow buttons on each chapter row; no drag-and-drop required.
- **Per-chapter notes** — a collapsible notes field on each chapter row, revealed by a notes icon button.

### Changed
- Chapter data structure upgraded from `list[str]` to `list[dict(title, notes)]`; old profiles are migrated automatically on load.
- Preview "Refresh" button renamed to "Regenerate" to clarify it resets manual edits.
- `_compile_done()` now populates both the full preview panel and the live pane from a single compilation result.

---

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
