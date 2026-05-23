# Gost v0.1.4

**Released:** 2026-05-23

## Download

| File | Platform |
|------|----------|
| `gost-0.1.4-x86_64.AppImage` | Linux x86_64 (GTK4 + libadwaita required) |

```bash
chmod +x gost-0.1.4-x86_64.AppImage
./gost-0.1.4-x86_64.AppImage
```

Or install with [Gear Lever](https://flathub.org/apps/it.mijorus.gearlever) for automatic desktop integration.

---

## What's New

### Three new citation styles

| Style | Used by | BibLaTeX backend | Typst CSL |
|-------|---------|-----------------|-----------|
| **ASA** | American Sociological Association journals | `asa` | `american-sociological-association` |
| **Turabian** | History and humanities students (Chicago student edition) | `chicago-notes` | `chicago-fullnote-bibliography` |
| **Harvard** | UK / European / Australian universities | `authoryear` | `harvard-cite-them-right` |

Each style wires up the correct heading rules, in-text or footnote citation mode, and page-numbering position automatically.

### UI improvements

- **Double spacing by default** — virtually every academic journal and course submission requires it; 1.5× was the previous default.
- **Sidebar title bar removed** — the "Sections" header strip above the navigation list is gone; the nav list starts flush at the top.
- **Hamburger menu** — Profiles, Style Packs, Import Journal, and About are now in a ⋮ menu. The header bar shows only Copy, Format toggle, Preview, and Export.
- **Simple Mode** (on by default) — hides Chapters, Custom Code, and Grammar panels. Toggle in the ⋮ menu when you need them.
- **Hover tooltips** — every control in every panel now has an accessibility tooltip.

---

## Dependencies (unchanged)

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| PyGObject | `python3-gobject` on openSUSE |
| GTK4 typelib | `typelib-1_0-Gtk-4_0` |
| libadwaita ≥ 1.4 | `typelib-1_0-Adw-1` |

**Compiled preview (optional):** `typst` for Typst output; `latexmk` + `poppler-tools` for LaTeX.

**ASA style (optional):** requires the `biblatex-asa` LaTeX package (`tlmgr install biblatex-asa` or install via your TeX distribution).

---

## Building from source

```bash
git clone https://github.com/calstfrancis/gost
cd gost
python3 -m essay_builder.app          # run directly
bash build-appimage.sh                # build AppImage
```

---

## Full changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete history.
