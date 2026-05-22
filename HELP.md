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
9. **Export** — Save as `.typ` (Typst) or `.tex` (LaTeX + `.latexmkrc`).

---

## Format: LaTeX vs Typst

Toggle between LaTeX and Typst using the buttons in the top-right. The active format is used for all previews and exports. Switching format hides settings that don't apply (e.g., LaTeX engines are hidden in Typst mode).

To export both formats from one set of settings, export as `.tex`, then export again as `.typ` — the generator reads the same state dict for both.

---

## Citation styles

| Style | Heading format | Page numbers | Notes |
|---|---|---|---|
| **SBL** | Centred small-caps, rule below | Centre bottom | Footnotes; `verbose-note` biblatex |
| **Chicago** | Centred bold | Centre bottom | Footnotes; `chicago-notes` biblatex |
| **MLA** | Left bold | Top right: `LastName Page` | No notes; `mla` biblatex |
| **APA** | Centred bold (5-level hierarchy) | Top right: page; Left: short title | No notes; `apa` biblatex |

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
