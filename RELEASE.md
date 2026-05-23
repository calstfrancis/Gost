# Gost v0.1.6

**Released:** 2026-05-23

## Download

| File | Platform |
|------|----------|
| `gost-0.1.6-x86_64.AppImage` | Linux x86_64 (GTK4 + libadwaita required) |

```bash
chmod +x gost-0.1.6-x86_64.AppImage
./gost-0.1.6-x86_64.AppImage
```

Or install via [Gear Lever](https://flathub.org/apps/it.mijorus.gearlever) for automatic desktop integration.

### pipx (recommended)

```bash
# 1. Install system dependencies (once)
sudo zypper install python3-gobject typelib-1_0-Gtk-4_0 typelib-1_0-Adw-1  # openSUSE
# sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1                  # Debian/Ubuntu
# sudo dnf install python3-gobject gtk4 libadwaita                          # Fedora

# 2. Install Gost
pipx install gost-academic --system-site-packages
pipx install 'gost-academic[word]' --system-site-packages  # + Word / ODT export

# 3. Add to application launcher
gost-setup-desktop

# 4. Run
gost
```

> `--system-site-packages` is required so pipx can access the system-installed PyGObject and GTK4 typelibs, which cannot be installed via pip. Run `gost-setup-desktop` once after install to add Gost to your GNOME application launcher.

### pip

```bash
pip install gost-academic
pip install 'gost-academic[word]'  # + Word / ODT export
gost
```

---

## What's New in v0.1.6

### pipx desktop integration

Running `gost` via pipx previously required finding the binary manually, and Gost did not appear in the GNOME application launcher. This release adds a `gost-setup-desktop` command that installs the `.desktop` file and application icons into your local user directories:

```bash
gost-setup-desktop
```

This places `~/.local/share/applications/ca.calstfrancis.Gost.desktop` and the SVG icons under `~/.local/share/icons/hicolor/`, then refreshes the icon cache and desktop database automatically. Run it once after `pipx install`; no root required.

### pipx `--system-site-packages` now documented

The `ModuleNotFoundError: No module named 'gi'` error that pipx users encountered is caused by pipx's isolated virtual environment not having access to the system-installed PyGObject. The fix — `pipx install gost-academic --system-site-packages` — is now prominently documented in the install steps above and in HELP.md.

---

## Previous release — v0.1.5

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
