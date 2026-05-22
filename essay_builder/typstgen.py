"""
typstgen.py — Build a complete Typst (.typ) document from a state dict.
No GTK dependency; import and test freely.
"""

from typing import Dict, Any, List

TYPST_CIT_STYLES: Dict[str, str] = {
    "SBL":     "chicago-notes",
    "Chicago": "chicago-notes",
    "MLA":     "mla",
    "APA":     "apa",
}

TYPST_FONTS: Dict[str, str | None] = {
    "junicode":   "Junicode",
    "ebgaramond": "EB Garamond",
    "palatino":   "TeX Gyre Pagella",
    "times":      "Times New Roman",
    "libertine":  "Linux Libertine",
    "none":       None,
}

TYPST_PAPER: Dict[str, str] = {
    "letterpaper": "us-letter",
    "a4paper":     "a4",
}

TYPST_LEADING: Dict[str, str] = {
    "1":   "0.65em",
    "1.5": "0.9em",
    "2":   "1.3em",
}

STRUCT_SECTION_TYPES = {"section", "subsection", "subsubsection"}

TYPST_FEATURE_IMPORTS: Dict[str, str] = {
    "dropcaps":  '#import "@preview/droplet:0.3.1": dropcap',
    "marginalia": (
        "// Margin notes — place with:\n"
        "// #place(right + top, float: false, dx: 1.2em)[#text(size: 0.85em)[Note]]"
    ),
    "codly":    '#import "@preview/codly:1.0.0": *\n#show: codly-init.with()',
    "showybox": '#import "@preview/showybox:2.0.1": showybox',
    "gentle":   '#import "@preview/gentle-clues:0.9.0": *',
    "tablex":   '#import "@preview/tablex:0.0.8": tablex, cellx',
    "drafting": '#import "@preview/drafting:0.2.0": *',
}

# ---------------------------------------------------------------------------
# Per-style heading show rules
# ---------------------------------------------------------------------------

TYPST_HEADING_STYLES: Dict[str, List[str]] = {
    "SBL": [
        "// SBL: centered small-caps (level 1), centered italic (level 2)",
        "#show heading.where(level: 1): it => {",
        "  v(0.8em)",
        "  align(center, smallcaps(it.body))",
        "  v(0.4em)",
        "  line(length: 100%, stroke: 0.4pt)",
        "  v(0.3em)",
        "}",
        "#show heading.where(level: 2): it => {",
        "  v(0.6em)",
        "  align(center, emph(it.body))",
        "  v(0.2em)",
        "}",
        "#show heading.where(level: 3): it => {",
        "  v(0.5em)",
        "  align(center, it.body)",
        "  v(0.1em)",
        "}",
    ],
    "Chicago": [
        "// Chicago: centered bold (level 1), centered bold-italic (level 2)",
        "#show heading.where(level: 1): it => {",
        "  v(0.8em)",
        "  align(center, strong(it.body))",
        "  v(0.4em)",
        "}",
        "#show heading.where(level: 2): it => {",
        "  v(0.6em)",
        "  align(center, strong(emph(it.body)))",
        "  v(0.2em)",
        "}",
    ],
    "MLA": [
        "// MLA: left-aligned bold (level 1), left bold-italic (level 2)",
        "#show heading.where(level: 1): it => {",
        "  v(0.6em)",
        "  strong(it.body)",
        "  v(0.2em)",
        "}",
        "#show heading.where(level: 2): it => {",
        "  v(0.4em)",
        "  strong(emph(it.body))",
        "  v(0.1em)",
        "}",
    ],
    "APA": [
        "// APA 7th edition heading levels",
        "#show heading.where(level: 1): it => {",
        "  v(0.8em)",
        "  align(center, strong(it.body))",
        "  v(0.4em)",
        "}",
        "#show heading.where(level: 2): it => {",
        "  v(0.6em)",
        "  strong(it.body)",
        "  v(0.2em)",
        "}",
        "#show heading.where(level: 3): it => {",
        "  v(0.5em)",
        "  strong(emph(it.body))",
        "  v(0.1em)",
        "}",
        "#show heading.where(level: 4): it => {",
        "  v(0.4em)",
        "  emph(it.body)",
        "  v(0.1em)",
        "}",
    ],
}

# ---------------------------------------------------------------------------
# Language hints for Typst
# ---------------------------------------------------------------------------

TYPST_LANG_HINTS: Dict[str, Dict[str, str]] = {
    "russian":  {"code": "ru",  "font": "Noto Serif (supports Cyrillic)"},
    "hebrew":   {"code": "he",  "font": "SBL Hebrew or Ezra SIL"},
    "japanese": {"code": "ja",  "font": "Noto Serif CJK JP"},
    "tibetan":  {"code": "bo",  "font": "Noto Serif Tibetan or Tibetan Machine Uni"},
    "sanskrit": {"code": "sa",  "font": "Noto Serif Devanagari or Siddhanta"},
    "greek":    {"code": "grc", "font": "GFS Didot or New Athena Unicode"},
    "chinese":  {"code": "zh",  "font": "Noto Serif CJK SC (Simplified) or CJK TC (Traditional)"},
}


def _chapter_slug(title: str, index: int) -> str:
    slug = "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")
    return f"chapter{index:02d}_{slug}" if slug else f"chapter{index:02d}"


def generate_chapter_file(title: str) -> str:
    """Return a minimal standalone chapter body file (no preamble)."""
    lines = [
        f"// Chapter: {title}",
        "",
        f"= {title or 'Chapter'}",
        "",
        "// Write chapter content here. Use @citationkey to cite.",
        "",
    ]
    return "\n".join(lines)


def _format_date(raw: str) -> str:
    if not raw:
        return "#datetime.today().display()"
    try:
        y, m, d = raw.split("-")
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        return "{} {}, {}".format(months[int(m) - 1], int(d), y)
    except Exception:
        return raw


TYPST_ENDNOTES_IMPL = [
    "// --- Endnotes (built-in implementation) ---",
    "#let _endnote-store = state(\"endnotes\", ())",
    "#let endnote(body) = {",
    "  _endnote-store.update(ns => ns + (body,))",
    "  context { super[#_endnote-store.get().len()] }",
    "}",
    "#let print-endnotes(title: \"Notes\") = context {",
    "  let all = _endnote-store.final()",
    "  if all.len() > 0 {",
    "    heading(level: 1)[#title]",
    "    for (i, n) in all.enumerate() {",
    "      [#(i + 1). #n \\ ]",
    "    }",
    "  }",
    "}",
    "// Usage: #endnote[Note text]   instead of #footnote[…]",
    "// At end of document add: #print-endnotes()",
]

TYPST_HEADER_CODE: Dict[str, List[str]] = {
    "none": [
        "#set page(header: none, footer: none)",
    ],
    "pagenum_bottom": [
        "#set page(",
        "  footer: context align(center, counter(page).display()),",
        "  header: none,",
        ")",
    ],
    "title_left": [],  # built dynamically
    "section_left": [
        "#set page(",
        "  header: context {",
        "    let secs = query(heading.where(level: 1))",
        "    let before = secs.filter(h => h.location().page() <= here().page())",
        "    let sec = if before.len() > 0 { before.last().body } else { [] }",
        "    grid(columns: (1fr, 1fr),",
        "      align(left, emph(sec)),",
        "      align(right, counter(page).display()),",
        "    )",
        "  },",
        ")",
    ],
    "author_left": [],  # built dynamically
    "doublesided": [
        "#set page(",
        "  header: context {",
        "    let secs = query(heading.where(level: 1))",
        "    let before = secs.filter(h => h.location().page() <= here().page())",
        "    let sec = if before.len() > 0 { before.last().body } else { [] }",
        "    if calc.odd(here().page()) {",
        "      grid(columns: (1fr, 1fr),",
        "        align(left, emph(sec)),",
        "        align(right, counter(page).display()),",
        "      )",
        "    } else {",
        "      grid(columns: (1fr, 1fr),",
        "        align(left, counter(page).display()),",
        "        align(right, emph(sec)),",
        "      )",
        "    }",
        "  },",
        ")",
    ],
}


def generate(s: Dict[str, Any]) -> str:
    """
    s: dict produced by GostWindow._collect_state()
    Returns a complete .typ string.
    """
    L: List[str] = []

    cit      = s.get("cit_style",    "SBL")
    fs       = s.get("font_size",    "11pt")
    paper    = s.get("paper",        "letterpaper")

    title    = s.get("title",        "")
    subtitle = s.get("subtitle",     "")
    authors  = s.get("authors",      "")
    affil    = s.get("affiliation",  "")
    date_raw = s.get("date",         "")
    course   = s.get("course",       "")

    bib_file    = s.get("bib_file",    "")
    bib_head    = s.get("bib_heading", "Bibliography")
    print_bib   = s.get("print_bib",   True)

    margin    = s.get("margin",    "1.00")
    linespace = s.get("linespace", "1.5")
    font_pkg  = s.get("font_pkg",  "ebgaramond")
    parindent = s.get("parindent", "1.5")

    numbered        = s.get("numbered_heads",    False)
    has_abs         = s.get("has_abstract",      False)
    has_kw          = s.get("has_keywords",      False)
    use_toc         = s.get("use_toc",           False)
    use_style_hdgs  = s.get("use_style_headings", True)

    typst_features  = s.get("typst_features", [])
    languages       = s.get("languages",      [])
    typst_notes     = s.get("typst_notes",    "footnote")
    header_style    = s.get("header_style",   "auto")
    header_rule     = s.get("header_rule",    False)

    bib_style  = s.get("typst_csl_style") or TYPST_CIT_STYLES.get(cit, "chicago-notes")
    font_name  = TYPST_FONTS.get(font_pkg)
    paper_name = TYPST_PAPER.get(paper, "us-letter")
    leading    = TYPST_LEADING.get(linespace, "0.9em")

    L.append("// Academic Essay Template")
    L.append("// Citation style: {}  |  Format: Typst".format(cit))
    L.append("")

    # Extra package imports
    if typst_features:
        L.append("// --- Extra packages ---")
        for feat in typst_features:
            imp = TYPST_FEATURE_IMPORTS.get(feat)
            if imp:
                L.append(imp)
        L.append("")

    # Endnotes implementation
    if typst_notes == "endnote":
        for line in TYPST_ENDNOTES_IMPL:
            L.append(line)
        L.append("")

    # Document metadata
    title_val = title or "Untitled"
    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    L.append("#set document(")
    L.append('  title: "{}",'.format(title_val))
    if len(author_list) == 1:
        L.append('  author: "{}",'.format(author_list[0]))
    elif author_list:
        auth_str = '", "'.join(author_list)
        L.append('  author: ("{}"),'.format(auth_str))
    L.append(")")
    L.append("")

    # Page geometry + style-specific numbering
    L.append("#set page(")
    L.append('  paper: "{}",'.format(paper_name))
    L.append("  margin: {}in,".format(margin))
    if cit in ("MLA", "APA"):
        L.append('  numbering: "1",')
        L.append("  number-align: right + top,")
    else:
        L.append('  numbering: "1",')
        L.append("  number-align: center + bottom,")
    L.append(")")
    L.append("")

    # Text settings
    L.append("#set text(")
    if font_name:
        L.append('  font: "{}",'.format(font_name))
    L.append("  size: {},".format(fs))
    L.append(")")
    L.append("")

    # Paragraph settings
    L.append("#set par(")
    L.append("  justify: true,")
    L.append("  leading: {},".format(leading))
    if float(parindent) > 0:
        L.append("  first-line-indent: {}em,".format(parindent))
    L.append(")")
    L.append("")

    if numbered:
        L.append('#set heading(numbering: "1.")')
        L.append("")

    # Header / footer
    eff_header = header_style
    if header_style == "auto":
        # Citation-style defaults
        if cit == "MLA":
            eff_header = "author_left"
        elif cit == "APA":
            eff_header = "title_left"
        else:
            eff_header = "pagenum_bottom"

    if eff_header != "none" or header_style == "none":
        L.append("// --- Header / footer ---")

    if header_style == "none":
        L.append("#set page(header: none, footer: none)")
        L.append("")
    elif eff_header == "pagenum_bottom":
        L.append("#set page(")
        L.append("  footer: context align(center, counter(page).display()),")
        L.append("  header: none,")
        L.append(")")
        L.append("")
    elif eff_header == "title_left":
        t = title or "Untitled"
        L.append("#set page(")
        L.append("  header: context grid(")
        L.append("    columns: (1fr, 1fr),")
        L.append(f'    align(left, emph("{t}")),')
        L.append("    align(right, counter(page).display()),")
        L.append("  ),")
        L.append(")")
        L.append("")
    elif eff_header == "author_left":
        al = ""
        if authors.strip():
            parts = authors.split(",")[0].strip().split()
            al = parts[-1] if parts else ""
        L.append("#set page(")
        L.append("  header: context grid(")
        L.append("    columns: (1fr, 1fr),")
        L.append(f'    align(left, emph("{al}")),')
        L.append("    align(right, counter(page).display()),")
        L.append("  ),")
        L.append(")")
        L.append("")
    elif eff_header in TYPST_HEADER_CODE:
        L.append("// --- Running header ---")
        for line in TYPST_HEADER_CODE[eff_header]:
            L.append(line)
        L.append("")

    # Style-specific heading show rules
    if use_style_hdgs and cit in TYPST_HEADING_STYLES:
        L.append("// --- Heading style ({}) ---".format(cit))
        for line in TYPST_HEADING_STYLES[cit]:
            L.append(line)
        L.append("")

    custom_preamble = s.get("custom_typst_preamble", "").strip()
    if custom_preamble:
        L.append("// --- Custom show rules / preamble ---")
        for line in custom_preamble.splitlines():
            L.append(line)
        L.append("")

    # Language hints
    if languages:
        L.append("// --- Language support ---")
        primary_lang = languages[0]
        hint = TYPST_LANG_HINTS.get(primary_lang, {})
        if hint:
            L.append('// Primary language: {} — suggested font: {}'.format(
                primary_lang.capitalize(), hint["font"]
            ))
            L.append('// Uncomment to set language for hyphenation:')
            L.append('// #set text(lang: "{}")'.format(hint["code"]))
        for lang in languages[1:]:
            h = TYPST_LANG_HINTS.get(lang, {})
            if h:
                L.append('// {}: #text(lang: "{}")[…]  — font: {}'.format(
                    lang.capitalize(), h["code"], h["font"]
                ))
        L.append("")

    # Title block
    L.append("// --- Title block ---")
    L.append("#align(center)[")
    if title:
        L.append('  #text(size: 1.5em, weight: "bold")[{}]'.format(title))
    if subtitle:
        L.append("  #linebreak()")
        L.append("  #text(size: 1.2em)[_{}_ ]".format(subtitle))
    for a in author_list:
        L.append("  #linebreak()")
        L.append("  {}".format(a))
    if affil:
        L.append("  #linebreak()")
        L.append("  _{}_ ".format(affil))
    date_str = _format_date(date_raw)
    L.append("  #linebreak()")
    L.append("  {}".format(date_str))
    if course:
        L.append("  #linebreak()")
        L.append("  {}".format(course))
    L.append("]")
    L.append("")

    if has_abs:
        L.append("// --- Abstract ---")
        L.append("#block(inset: (x: 2em))[")
        L.append("  *Abstract*")
        L.append("  #linebreak()")
        L.append("  // Your abstract here.")
        L.append("]")
        L.append("")

    if has_kw:
        L.append("*Keywords:* keyword one, keyword two, keyword three")
        L.append("")

    if use_toc:
        L.append("// --- Table of contents ---")
        L.append("#outline()")
        L.append("#pagebreak()")
        L.append("")

    chapters = s.get("chapters", [])
    multifile = s.get("multifile", False)

    L.append("// --- Body ---")
    L.append("")
    if chapters:
        if multifile:
            for i, ch in enumerate(chapters, 1):
                slug = _chapter_slug(ch, i)
                L.append(f'#include "{slug}.typ"')
                L.append("")
        else:
            for ch in chapters:
                L.append(f"= {ch or 'Untitled Chapter'}")
                L.append("")
                L.append("// Begin writing here. Use @citationkey to cite.")
                L.append("")
    else:
        L.append("= Introduction")
        L.append("")
        L.append("// Begin writing here. Use @citationkey to cite.")
        L.append("")
        L.append("= Conclusion")
        L.append("")

    if typst_notes == "endnote":
        L.append("")
        L.append("#print-endnotes()")

    if print_bib:
        L.append("")
        L.append("// --- Bibliography ---")
        bib_path = bib_file or "references.bib"
        L.append('#bibliography("{}", title: "{}", style: "{}")'.format(
            bib_path, bib_head, bib_style
        ))
        L.append("")

    return "\n".join(L)
