# Gost v0.1.5

**Released:** 2026-05-23

## Download

| File | Platform |
|------|----------|
| `gost-0.1.5-x86_64.AppImage` | Linux x86_64 (GTK4 + libadwaita required) |

```bash
chmod +x gost-0.1.5-x86_64.AppImage
./gost-0.1.5-x86_64.AppImage
```

Or install via [Gear Lever](https://flathub.org/apps/it.mijorus.gearlever) for automatic desktop integration.

### pip

```bash
pip install gost-academic          # LaTeX + Typst output
pip install gost-academic[word]    # + Word / ODT export
gost
```

> GTK4 and PyGObject must be installed as system packages. See [HELP.md](HELP.md#troubleshooting) for distribution-specific commands.

---

## What's New

### Word and ODT export

A new **Word** button sits alongside Typst and LaTeX in the header bar. Clicking Export with Word selected saves a fully styled `.docx` template:

- Correct margins, font, double spacing, and heading styles for all seven citation styles
- Centered or left-aligned title block following MLA, APA, Chicago, SBL, ASA, Turabian, or Harvard conventions
- Abstract placeholder (APA and ASA get a separate abstract page)
- Bibliography / Works Cited / References section with hanging-indent sample entry and a Zotero Word plug-in tip
- **ODT** — if LibreOffice is installed, choose `.odt` in the save dialog and it is converted automatically

Word export requires `python-docx`. It is bundled in the AppImage. For source installs: `pip install gost-academic[word]`.

### PyPI

Gost is now available on PyPI as `gost-academic`:

```bash
pip install gost-academic
pip install gost-academic[word]   # includes python-docx for Word export
```

---

## Dependencies

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| PyGObject | `python3-gobject` on openSUSE |
| GTK4 typelib | `typelib-1_0-Gtk-4_0` |
| libadwaita ≥ 1.4 | `typelib-1_0-Adw-1` |

**Compiled preview (optional):** `typst` for Typst output; `latexmk` + `poppler-tools` for LaTeX.

**Word export (optional):** `python-docx` (`pip install gost-academic[word]`). Bundled in the AppImage.

**ODT export (optional):** LibreOffice (`libreoffice` or `soffice` in PATH).

**ASA style (optional):** requires the `biblatex-asa` LaTeX package (`tlmgr install biblatex-asa`).

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
