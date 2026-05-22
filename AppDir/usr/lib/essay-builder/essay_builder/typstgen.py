"""
typstgen.py — Build a complete Typst (.typ) document from a state dict.
No GTK dependency; import and test freely.
"""

from typing import Dict, Any, List

# Closest Typst bibliography styles for each citation tradition
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

# Typst leading values corresponding to 1×, 1.5×, 2× line spacing
TYPST_LEADING: Dict[str, str] = {
    "1":   "0.65em",
    "1.5": "0.9em",
    "2":   "1.3em",
}

STRUCT_SECTION_TYPES = {"section", "subsection", "subsubsection"}


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


def _struct_typ(item_type: str, label: str, num_cols: int) -> str:
    lbl = label or ""
    if item_type == "part":
        return "#heading(level: 1, numbering: none)[{}]".format(lbl or "Part Title")
    if item_type == "section":
        return "= {}".format(lbl or "Section Title")
    if item_type == "subsection":
        return "== {}".format(lbl or "Subsection Title")
    if item_type == "subsubsection":
        return "=== {}".format(lbl or "Sub-subsection")
    if item_type == "appendix":
        return "= Appendix"
    if item_type == "multicol":
        n = str(num_cols)
        return (
            "#columns(" + n + ")[\n"
            "  // Multi-column content here\n"
            "]"
        )
    if item_type == "quote":
        return (
            "#block(inset: (x: 2em))[\n"
            "  // Extended quotation.\n"
            "]"
        )
    if item_type == "figure":
        cap = lbl or "Caption text."
        return (
            '#figure(\n'
            '  image("filename.png"),\n'
            '  caption: [' + cap + '],\n'
            ')'
        )
    if item_type == "table":
        cap = lbl or "Caption."
        return (
            '#figure(\n'
            '  table(\n'
            '    columns: 2,\n'
            '    [Col A], [Col B],\n'
            '    [], [],\n'
            '  ),\n'
            '  caption: [' + cap + '],\n'
            ')'
        )
    if item_type == "epigraph":
        text = lbl or "Epigraph text."
        return (
            "#block(inset: (x: 3em))[\n"
            "  _" + text + "_ #h(1fr) ---Source\n"
            "]\n"
            "#v(1em)"
        )
    return ""


def generate(s: Dict[str, Any]) -> str:
    """
    s: dict produced by EssayBuilderWindow._collect_state()
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

    margin      = s.get("margin",    "1.00")
    linespace   = s.get("linespace", "1.5")
    font_pkg    = s.get("font_pkg",  "ebgaramond")
    parindent   = s.get("parindent", "1.5")

    numbered    = s.get("numbered_heads", False)
    has_abs     = s.get("has_abstract",   False)
    has_kw      = s.get("has_keywords",   False)

    struct      = s.get("struct_items",   [])
    num_cols    = s.get("num_cols",       2)

    bib_style   = TYPST_CIT_STYLES.get(cit, "chicago-notes")
    font_name   = TYPST_FONTS.get(font_pkg)
    paper_name  = TYPST_PAPER.get(paper, "us-letter")
    leading     = TYPST_LEADING.get(linespace, "0.9em")

    L.append("// Academic Essay Template")
    L.append("// Citation style: {}  |  Format: Typst".format(cit))
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

    # Page geometry
    L.append("#set page(")
    L.append('  paper: "{}",'.format(paper_name))
    L.append("  margin: {}in,".format(margin))
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

    # Body
    if struct:
        for item in struct:
            t   = item.get("type",  "section")
            lbl = item.get("label", "")
            typ = _struct_typ(t, lbl, num_cols)
            if not typ:
                continue
            L.append("")
            L.append(typ)
            if t in STRUCT_SECTION_TYPES:
                L.append("")
                L.append("// Body text. @key")
                L.append("")
    else:
        L.append("// --- Body ---")
        L.append("")
        L.append("= Introduction")
        L.append("")
        L.append("// Begin writing here. Use @citationkey to cite.")
        L.append("")
        L.append("= Conclusion")
        L.append("")

    if print_bib:
        L.append("")
        L.append("// --- Bibliography ---")
        bib_path = bib_file or "references.bib"
        L.append('#bibliography("{}", title: "{}", style: "{}")'.format(
            bib_path, bib_head, bib_style
        ))
        L.append("")

    return "\n".join(L)
