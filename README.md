# Gost

**Academic Essay Templater** — a native GTK4 / libadwaita desktop app for generating academic essay templates in **LaTeX** and **Typst**. Built for openSUSE / GNOME. Designed for theology, humanities, and social-science writing.

## Features

- **Citation styles** — SBL, Chicago (Notes), MLA, APA 7th edition — each applies the correct heading formatting, page numbering, and running headers automatically
- **Two output formats** — Typst (default) and LaTeX, chosen by file extension at save time
- **Compiled preview** — click **Preview** in the header bar to compile the template and display rendered pages (requires `typst` or `latexmk`)
- **Template profiles** — save, load, and delete named configurations
- **Headers & Footers** — running section title, document title, author, double-sided, page numbers, or auto per citation style
- **Extra packages** — toggle LaTeX packages (`lettrine`, `marginnote`, `csquotes`, `xcolor`, `listings`, `booktabs`, `siunitx`, `epigraph`, `lineno`, `todonotes`) or Typst packages (`droplet`, `codly`, `showybox`, `gentle-clues`, `tablex`, `drafting`)
- **Language support** — Russian, Hebrew, Japanese, Tibetan, Sanskrit, Ancient Greek, Chinese (polyglossia / xeCJK / luatexja)
- **Journal template importer** — open a `.tex` / `.cls` / `.sty` to extract font, paper, margin, spacing, and bibliography settings
- **Zotero** — paste a BetterBibTeX auto-export path; remembered across sessions
- **Endnotes** — footnotes or endnotes for both LaTeX and Typst
- **Table of contents** toggle
- **GOST Type B font** — toggle to use the GOST Type B engineering lettering as the application UI font

## System Requirements

### Runtime
| Dependency | Notes |
|---|---|
| Python 3.10+ | |
| PyGObject | `python3-gobject` on openSUSE |
| GTK4 typelib | `typelib-1_0-Gtk-4_0` |
| libadwaita ≥ 1.4 | `typelib-1_0-Adw-1` |

### Compiled preview (optional)
| Typst | Install from <https://typst.app> or your package manager |
|---|---|
| LaTeX | `texlive-latexmk` + `poppler-tools` (`pdftoppm`) or ImageMagick (`convert`) |

## Installation

### AppImage
```bash
chmod +x gost-1.2.0-x86_64.AppImage
./gost-1.2.0-x86_64.AppImage
# Or install via Gear Lever for desktop integration
```

### From source
```bash
git clone https://github.com/calstfrancis/gost
cd gost
python3 -m essay_builder.app
```

### Build your own AppImage
```bash
bash build-appimage.sh
# Produces gost-1.2.0-x86_64.AppImage in the current directory
# Install via Gear Lever or run directly
```

## Usage

1. Fill in **Title & Authors**, pick a **Citation Style**, adjust **Layout & Spacing**
2. Toggle extra packages in **Extra Packages** and script support in **Languages**
3. Configure running headers in **Headers & Footers**
4. Set your bibliography path in **Bibliography** (press Enter to persist it)
5. Click **Preview** to compile and view, or **Export** to save the file
6. Use **Profiles** to save and reload full configurations

## Development

```bash
python3 -m essay_builder.app          # run directly
python3 -m pytest tests/              # run tests (no GTK needed)
bash build-appimage.sh                # build AppImage
```

## License

GNU General Public License v3.0 — see `LICENSE`.
