# Gost — Help

## Quick start

1. **Title & Authors** — Enter the document title, subtitle, author(s), affiliation, and course. The author name is saved between sessions.
2. **Citation Style** — Pick SBL, Chicago, MLA, or APA. Heading styles, page numbering, and running headers are set automatically. You can override the BibLaTeX style string manually.
3. **Layout & Spacing** — Set paper size, margins (in inches), font size, and line spacing.
4. **Extra Packages** — Toggle optional packages. Only the packages for the active format (LaTeX or Typst) are shown.
5. **Languages** — Enable script support for Russian, Hebrew, Japanese, Tibetan, Sanskrit, Ancient Greek, and Chinese.
6. **Headers & Footers** — Choose a running header preset or leave on Auto to follow citation-style conventions.
7. **Bibliography** — Paste the absolute path to your `.bib` file and press Enter. This path is saved automatically.
8. **Preview** — Click in the sidebar to see the generated source code. Click **Preview** in the top bar to compile and see the actual rendered pages.
9. **Export** — Save as `.typ` (Typst), `.tex` (LaTeX + `.latexmkrc`), or `.docx` / `.odt` (Word).

---

## Format: Typst, LaTeX, or Word

Toggle between Typst, LaTeX, and Word using the buttons in the header bar. The active format is used for all previews and exports. Switching format hides settings that don't apply (e.g., LaTeX engines are hidden in Typst and Word modes).

- **Typst** — outputs a `.typ` file. Requires `typst` for compiled preview.
- **LaTeX** — outputs a `.tex` file plus a `.latexmkrc`. Requires `latexmk` for compiled preview.
- **Word** — outputs a `.docx` (or `.odt` via LibreOffice conversion). Compiled preview is not available; use Export directly. Requires `python-docx` (`pip install gost-academic[word]`).

To export multiple formats from one set of settings, switch formats between exports — the generator reads the same settings for all three.

---

## Citation styles

| Style | Heading format | Page numbers | Notes |
|---|---|---|---|
| **SBL** | Centred small-caps, rule below | Centre bottom | Footnotes; `verbose-note` biblatex |
| **Chicago** | Centred bold | Centre bottom | Footnotes; `chicago-notes` biblatex |
| **MLA** | Left bold | Top right: `LastName Page` | No notes; `mla` biblatex |
| **APA** | Centred bold (5-level hierarchy) | Top right: page; Left: short title | No notes; `apa` biblatex |
| **ASA** | Centred bold | Top right: page | No notes; `asa` biblatex |
| **Turabian** | Centred bold | Centre bottom | Footnotes; `chicago-notes` biblatex |
| **Harvard** | Left bold | Top right: page | No notes; `authoryear` biblatex |

"Style-appropriate headings" must be enabled (it is by default) for the heading rules to be applied.

---

## Headers & Footers

| Preset | Header content |
|---|---|
| Auto | Follows citation style (see table above) |
| None | No header or footer |
| Page numbers only | Page number centred at the bottom |
| Title · Page | Document title on the left, page number on the right |
| Section · Page | Current section title on the left, page number on the right |
| Author · Page | Last name of first author on the left, page number on the right |
| Double-sided | Section left on odd pages, page number right; swapped on even pages |

The **Header rule** switch adds a horizontal line below the running header (LaTeX only).

**Suppress on first page** removes the header from the title page.

---

## Compiled preview

The header-bar **Preview** button compiles your template and displays the rendered pages.

**Requirements:**
- **Typst:** `typst` must be in your PATH. Install from <https://typst.app>.
- **LaTeX:** `latexmk` must be in PATH (part of TeX Live). Plus `pdftoppm` (poppler-tools) or `convert` (ImageMagick) to convert PDF to images.

If the compiler is not found, an error message is shown in the compiled view. The **Source** tab always works without any compiler.

---

## Language support

Enable language packages in the **Languages** panel. For Typst, the app adds a `#set text(lang: "…")` comment and font recommendations — uncomment as needed. For LaTeX, it adds polyglossia / babel / xeCJK / luatexja calls.

**Font requirements:**
- Russian: any Unicode font (EB Garamond or Junicode works)
- Hebrew: SBL Hebrew or Ezra SIL
- Japanese/Chinese: Noto Serif CJK JP/SC (install the Noto CJK package)
- Tibetan: Tibetan Machine Uni
- Sanskrit: Noto Serif Devanagari
- Ancient Greek: GFS Didot or New Athena Unicode

---

## Journal template importer

Click **Import .tex** in the header bar and pick a `.tex`, `.cls`, or `.sty` file. The importer reads:
- Document class options (font size, paper)
- `\geometry{…}` margin
- `\setmainfont{…}` or fontfamily packages
- `\onehalfspacing` / `\doublespacing`
- `\setlength{\parindent}{…}`
- `\usepackage[style=…]{biblatex}`
- `\addbibresource{…}`

Detected settings are merged into the current configuration. A toast notification lists what was imported.

---

## Profiles

Click **Profiles** in the header bar to save the entire current configuration under a name, then reload it later. Profiles are stored in `~/.config/gost/profiles.json`.

---

## Bibliography

- The **Path to .bib file** field accepts any absolute path. Press Enter (or the apply button) to save it permanently.
- **Sorting** controls `biblatex`'s `sorting=` option.
- **Default cite command** inserts the correct `\autocite{}` / `#cite` comment in the template body.
- The Zotero banner reminds you to use BetterBibTeX's "Keep Updated" export for a live-synced `.bib` file.

---

## Endnotes

**LaTeX:** The Notes mode combo in Citation Style → Notes mode selects between footnotes, endnotes (`endnotes` package + `\let\footnote=\endnote`), and none.

**Typst:** The Notes mode (Typst) combo generates a self-contained `#endnote[…]` / `#print-endnotes()` implementation. Use `#endnote[Note text]` in your body and `#print-endnotes()` appears automatically before the bibliography.

---

## GOST Type B font

The **GOST Type B font** toggle at the bottom of the sidebar switches the application UI to the GOST Type B engineering lettering standard font. The font must be installed on your system (search for "GOST type B" in your font manager). The preference is saved between sessions.

---

## Keyboard tips

- The **Today** button next to the date field fills in today's date in `YYYY-MM-DD` format.
- The **Source / Compiled** toggle in the preview panel lets you switch views without leaving the preview.
- The **Refresh** button in the source preview regenerates the template from the current settings.

---

## Extra packages — what each one does

### LaTeX packages

| Toggle | Package | What it adds |
|---|---|---|
| Drop caps | `lettrine` | `\lettrine{L}{etter}` — decorative oversized first letter at the start of a paragraph |
| Marginalia | `marginnote` | `\marginnote{text}` — float notes into the margin independent of footnotes |
| Smart quotes | `csquotes` | Context-sensitive quotation marks; integrates with biblatex so `\autocite` uses the right quote style |
| Color support | `xcolor` | `\textcolor{red}{text}`, `\colorbox{}{}`, and 68 named dvipsnames colours |
| Code listings | `listings` | `\begin{lstlisting}` — syntax-highlighted source code blocks |
| Enhanced lists | `enumitem` | Fine-grained control over `enumerate`, `itemize`, `description` spacing and labels |
| Better tables | `booktabs` | `\toprule`, `\midrule`, `\bottomrule` — publication-quality horizontal rules |
| SI units | `siunitx` | `\qty{9.81}{\metre\per\second\squared}` — correctly typeset physical quantities |
| Epigraph | `epigraph` | `\epigraph{quote}{— Source}` — formatted block quotation with attribution |
| Line numbers | `lineno` | Margin line numbers for draft / peer-review submissions |
| Todo notes | `todonotes` | `\todo{Fix this}` — coloured margin annotations that list in the margin and in a summary |

### Typst packages

| Toggle | Package | What it adds |
|---|---|---|
| Drop caps | `droplet` | `#dropcap[…]` — decorative first-letter drop cap |
| Margin notes | *(built-in)* | `#place(right + top)[…]` snippet — no extra package; just a placement helper comment |
| Code listings | `codly` | `#codly()` show rule — syntax-highlighted code blocks with line numbers |
| Styled boxes | `showybox` | `#showybox(…)[…]` — coloured/framed content boxes with customisable borders |
| Callout boxes | `gentle-clues` | `#info[…]`, `#warning[…]`, `#tip[…]` — admonition blocks |
| Enhanced tables | `tablex` | `#tablex(…)` — column/row spans and merged cells not available in native Typst tables |
| Margin annotations | `drafting` | `#margin-note[…]` — margin annotations for draft review |

---

## Troubleshooting

### Preview button is greyed out / "typst not installed"

The **Preview** button is disabled when the required compiler is not found in your PATH.

- **Typst:** install from <https://typst.app> or via your package manager:
  - openSUSE: `zypper in typst`
  - Arch: `pacman -S typst`
  - Fedora/Ubuntu: download the binary from the releases page and place it in `~/.local/bin/`
- **LaTeX:** install TeX Live including latexmk:
  - openSUSE: `zypper in texlive-latexmk`
  - Debian/Ubuntu: `apt install latexmk`
  - Fedora: `dnf install latexmk`
  - Arch: `pacman -S texlive-binextra`

After installing, restart Gost — the check runs at startup.

---

### Missing `pdftoppm` / PDF preview shows "image converter not found"

LaTeX preview needs either `pdftoppm` (from poppler-tools) or `convert` (from ImageMagick).

- openSUSE: `zypper in poppler-tools`
- Debian/Ubuntu: `apt install poppler-utils`
- Fedora: `dnf install poppler-utils`
- Arch: `pacman -S poppler`

---

### `gi.repository.GLib.Error: gtk-icon-theme-error-quark`

This warning is benign on most systems — the app still works. It means the GTK icon theme cannot find a specific symbolic icon. Fix with:

- openSUSE: `zypper in adwaita-icon-theme`
- Debian/Ubuntu: `apt install adwaita-icon-theme`
- Arch: `pacman -S adwaita-icon-theme`

---

### `ImportError: cannot import name 'Adw' from gi.repository`

libadwaita is not installed or the typelib is missing.

- openSUSE: `zypper in typelib-1_0-Adw-1`
- Debian/Ubuntu (≥ 23.04): `apt install gir1.2-adw-1`
- Fedora: `dnf install libadwaita`
- Arch: `pacman -S libadwaita`

---

### Gost doesn't appear in the application launcher (pipx install)

pipx installs the `gost` binary but does not place a `.desktop` file or icons in your local share directories. Run this once after installing:

```bash
gost-setup-desktop
```

This installs `~/.local/share/applications/ca.calstfrancis.Gost.desktop` and the SVG icons to `~/.local/share/icons/hicolor/`, then refreshes the icon cache and desktop database. No root required. If Gost still doesn't appear, log out and back in.

If you see `command not found: gost-setup-desktop`, make sure `~/.local/bin` is in your PATH and that your pipx install completed successfully:

```bash
export PATH="$HOME/.local/bin:$PATH"   # add to ~/.bashrc or ~/.zshrc to persist
gost-setup-desktop
```

---

### `ModuleNotFoundError: No module named 'gi'`

PyGObject is not installed for your Python, or — if you used pipx — the isolated virtual environment cannot see the system-installed `gi` module.

**pipx install:** reinstall with `--system-site-packages` so the venv inherits system packages:

```bash
pipx reinstall gost-academic --system-site-packages
```

If it's a fresh install:

```bash
pipx install gost-academic --system-site-packages
```

**System package** (required regardless of install method):

- openSUSE: `zypper in python3-gobject`
- Debian/Ubuntu: `apt install python3-gi`
- Fedora: `dnf install python3-gobject`
- Arch: `pacman -S python-gobject`

---

### GTK4 typelib missing (`Gtk-4.0`)

- openSUSE: `zypper in typelib-1_0-Gtk-4_0`
- Debian/Ubuntu (≥ 22.10): `apt install gir1.2-gtk-4.0`
- Fedora: `dnf install gtk4`
- Arch: `pacman -S gtk4`

---

### Word export: "python-docx not installed"

Word and ODT export requires the `python-docx` package:

```bash
# pipx
pipx inject gost-academic python-docx

# pip
pip install 'gost-academic[word]'
```

If Gost was installed from the AppImage, python-docx is already bundled — this message should not appear. If it does, rebuild the AppImage with `bash build-appimage.sh`.

---

### ODT export: "LibreOffice not found"

ODT conversion requires LibreOffice:

- openSUSE: `zypper in libreoffice`
- Debian/Ubuntu: `apt install libreoffice`
- Fedora: `dnf install libreoffice`
- Arch: `pacman -S libreoffice-still`

Alternatively, export as `.docx` and open it in LibreOffice manually.

---

### Bibliography file warning: "may not be valid BibTeX"

Gost checks the first 1 000 bytes of your `.bib` file for standard entry types. If your file uses non-standard or custom entry types this warning appears but the file is still used. Ignore it unless citation output is wrong.

---

### Security warning on journal import

If you see "This file contains potentially dangerous LaTeX commands", the imported `.cls`/`.tex` file contains constructs like `\write18` (shell escape) or `\openout` (arbitrary file writes). These are uncommon in legitimate journal templates. Only click **Import anyway** if you obtained the file from a trusted publisher.
