"""
texgen.py — Build a complete extarticle .tex document from a state dict.
No GTK dependency; import and test freely.
Uses raw strings (r"...") throughout to avoid backslash confusion.
"""

from typing import Dict, List, Any

STYLE_DEFAULTS: Dict[str, Dict[str, str]] = {
    "SBL":     {"biblatex_style": "verbose-note",  "notes": "footnote"},
    "Chicago": {"biblatex_style": "chicago-notes", "notes": "footnote"},
    "MLA":     {"biblatex_style": "mla",           "notes": "none"},
    "APA":     {"biblatex_style": "apa",           "notes": "none"},
}

# pdflatex fonts loaded with \usepackage
PDFLATEX_FONTS: Dict[str, str | None] = {
    "ebgaramond": r"\usepackage{ebgaramond}",
    "palatino":   r"\usepackage{mathpazo}",
    "times":      r"\usepackage{newtxtext,newtxmath}",
    "libertine":  r"\usepackage{libertine}",
    "none":       None,
}

# fontspec fonts: require XeLaTeX or LuaLaTeX
FONTSPEC_FONTS: Dict[str, str] = {
    "junicode": (
        r"\usepackage{fontspec}" + "\n"
        r"\setmainfont{Junicode}[" + "\n"
        r"  UprightFont    = *," + "\n"
        r"  BoldFont       = *-Bold," + "\n"
        r"  ItalicFont     = *-Italic," + "\n"
        r"  BoldItalicFont = *-BoldItalic," + "\n"
        r"]"
    ),
}

FONTSPEC_ONLY = set(FONTSPEC_FONTS.keys())

# At the end of the existing imports, add:

FONT_OPTIONS: List[Dict[str, Any]] = [
    {"display": "Junicode (fontspec)", "key": "junicode", "requires_fontspec": True},
    {"display": "EB Garamond", "key": "ebgaramond", "requires_fontspec": False},
    {"display": "Palatino (mathpazo)", "key": "palatino", "requires_fontspec": False},
    {"display": "Times (newtxtext)", "key": "times", "requires_fontspec": False},
    {"display": "Linux Libertine", "key": "libertine", "requires_fontspec": False},
    {"display": "None (default CM)", "key": "none", "requires_fontspec": False},
]
STRUCT_SECTION_TYPES = {"part", "section", "subsection", "subsubsection"}


def _struct_tex(item_type: str, label: str, num_cols: int) -> str:
    lbl = label or ""
    if item_type == "part":
        return r"\part{" + (lbl or "Part Title") + "}"
    if item_type == "section":
        return r"\section{" + (lbl or "Section Title") + "}"
    if item_type == "subsection":
        return r"\subsection{" + (lbl or "Subsection Title") + "}"
    if item_type == "subsubsection":
        return r"\subsubsection{" + (lbl or "Sub-subsection") + "}"
    if item_type == "appendix":
        return r"\appendix" + "\n" + r"\section{Appendix}"
    if item_type == "multicol":
        n = str(num_cols)
        return (r"\begin{multicols}{" + n + "}\n"
                r"  % multicol content" + "\n"
                r"\end{multicols}")
    if item_type == "quote":
        return (r"\begin{quote}" + "\n"
                r"  % Extended quotation." + "\n"
                r"\end{quote}")
    if item_type == "figure":
        cap = lbl or "Caption text."
        return (r"\begin{figure}[htbp]" + "\n"
                r"  \centering" + "\n"
                r"  % \includegraphics[width=0.8\textwidth]{filename}" + "\n"
                r"  \caption{" + cap + "}\n"
                r"  \label{fig:label}" + "\n"
                r"\end{figure}")
    if item_type == "table":
        cap = lbl or "Caption."
        return (r"\begin{table}[htbp]" + "\n"
                r"  \centering" + "\n"
                r"  \begin{tabular}{ll}" + "\n"
                r"    Col A & Col B \\" + "\n"
                r"  \end{tabular}" + "\n"
                r"  \caption{" + cap + "}\n"
                r"  \label{tab:label}" + "\n"
                r"\end{table}")
    if item_type == "epigraph":
        text = lbl or "Epigraph text."
        return (r"\begin{quote}" + "\n"
                r"  \textit{" + text + r"} \hfill ---Source" + "\n"
                r"\end{quote}" + "\n"
                r"\vspace{1em}")
    return ""


def _format_date(raw):
    if not raw:
        return r"\today"
    try:
        y, m, d = raw.split("-")
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        return "{} {}, {}".format(months[int(m) - 1], int(d), y)
    except Exception:
        return raw or r"\today"


def generate(s):
    """
    s : dict s: Dict[ptr, Any]r -> stroduced by EssayBuilderWindow.collect_state()
    Returns a complete .tex string.
    """
    L = []

    cit      = s.get("cit_style",      "SBL")
    eng      = s.get("engine",         "xelatex")
    fs       = s.get("font_size",      "11pt")
    paper    = s.get("paper",          "letterpaper")

    bib_sty  = s.get("biblatex_style") or STYLE_DEFAULTS[cit]["biblatex_style"]
    notes    = s.get("notes_mode")     or STYLE_DEFAULTS[cit]["notes"]

    title    = s.get("title",          "")
    subtitle = s.get("subtitle",       "")
    authors  = s.get("authors",        "")
    affil    = s.get("affiliation",    "")
    date_raw = s.get("date",           "")
    course   = s.get("course",         "")

    bib_file    = s.get("bib_file",    "")
    bib_sort    = s.get("bib_sort",    "nyt")
    bib_head    = s.get("bib_heading", "Bibliography")
    cite_cmd    = s.get("cite_cmd",    "autocite")
    print_bib   = s.get("print_bib",  True)

    margin      = s.get("margin",      "1.00")
    linespace   = s.get("linespace",   "1.5")
    font_pkg    = s.get("font_pkg",    "ebgaramond")
    parindent   = s.get("parindent",   "1.5")
    parskip     = s.get("parskip",     "0")
    microtype   = s.get("microtype",   True)
    encoding    = s.get("encoding",    "utf8")

    use_mc      = s.get("use_multicol", False)
    num_cols    = s.get("num_cols",    2)
    col_rule    = s.get("col_rule",    False)
    col_sep     = s.get("col_sep",     "14")

    numbered    = s.get("numbered_heads", False)
    has_abs     = s.get("has_abstract",   False)
    has_kw      = s.get("has_keywords",   False)

    struct      = s.get("struct_items",   [])

    # ---- document class ----
    L.append("% Academic Essay Template")
    L.append("% Citation style: {}  |  Engine: {}".format(cit, eng))
    L.append("")
    L.append(r"\documentclass[" + fs + "," + paper + r"]{extarticle}")
    L.append("")
    L.append("% --- Encoding & fonts ---")

    if eng == "pdflatex":
        L.append(r"\usepackage[" + encoding + r"]{inputenc}")
        L.append(r"\usepackage[T1]{fontenc}")
        if font_pkg in FONTSPEC_ONLY:
            # fontspec-only font selected but engine is pdflatex — fall back gracefully
            L.append("% Note: {} requires XeLaTeX or LuaLaTeX; no font package loaded".format(font_pkg))
        else:
            fp = PDFLATEX_FONTS.get(font_pkg)
            if fp:
                L.append(fp)
    else:
        # XeLaTeX / LuaLaTeX: use fontspec
        if font_pkg in FONTSPEC_FONTS:
            L.append(FONTSPEC_FONTS[font_pkg])
        elif font_pkg in PDFLATEX_FONTS and PDFLATEX_FONTS[font_pkg]:
            # pdflatex package selected with xelatex/lualatex — warn and use fontspec generic
            L.append(r"\usepackage{fontspec}")
            L.append("% Note: {} is a pdflatex package; switch to a fontspec font or set \\setmainfont manually".format(font_pkg))
        else:
            L.append(r"\usepackage{fontspec}")
            L.append(r"% \setmainfont{Your Font Here}")

    if microtype:
        if eng == "pdflatex":
            # Full microtype support for pdflatex
            L.append(r"\usepackage[protrusion=true,expansion=true]{microtype}")
        else:
            # expansion=true is incompatible with xelatex and lualatex
            L.append(r"\usepackage[protrusion=true]{microtype}")

    L.append("")
    L.append("% --- Page geometry ---")
    L.append(r"\usepackage[" + paper + ",margin=" + margin + r"in]{geometry}")

    L.append("")
    L.append("% --- Line spacing ---")
    L.append(r"\usepackage{setspace}")
    if linespace == "1":
        L.append("% single spacing (default)")
    elif linespace == "1.5":
        L.append(r"\onehalfspacing")
    else:
        L.append(r"\doublespacing")

    L.append("")
    L.append("% --- Paragraph style ---")
    L.append(r"\setlength{\parindent}{" + str(parindent) + "em}")
    if float(parskip) > 0:
        L.append(r"\setlength{\parskip}{" + str(parskip) + "pt}")

    if not numbered:
        L.append("")
        L.append("% --- Suppress section numbering ---")
        L.append(r"\setcounter{secnumdepth}{0}")

    if use_mc:
        L.append("")
        L.append("% --- Multi-column ---")
        L.append(r"\usepackage{multicol}")
        L.append(r"\setlength{\columnsep}{" + str(col_sep) + "pt}")
        if col_rule:
            L.append(r"\setlength{\columnseprule}{0.4pt}")

    L.append("")
    L.append("% --- BibLaTeX ({}) ---".format(cit))
    L.append(r"\usepackage[")
    L.append("  style={},".format(bib_sty))
    L.append("  sorting={},".format(bib_sort))
    L.append("  backend=biber,")
    if notes == "endnote":
        L.append("  notetype=endonly,")
    L.append("  urldate=long,")
    L.append(r"]{biblatex}")
    if bib_file:
        L.append(r"\addbibresource{" + bib_file + "}")
    else:
        L.append(r"\addbibresource{references.bib}  % <- set your .bib path")

    L.append("")
    L.append("% --- Hyperref ---")
    L.append(r"\usepackage[hidelinks]{hyperref}")

    if notes == "endnote" and cit in ("SBL", "Chicago"):
        L.append("")
        L.append("% --- Endnotes ---")
        L.append(r"\usepackage{endnotes}")
        L.append(r"\let\footnote=\endnote")

    # ---- title block ----
    L.append("")
    L.append("% --- Title block ---")

    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    if len(author_list) > 1:
        L.append(r"\author{" + r" \and ".join(author_list) + "}")
    elif author_list:
        author_line = author_list[0]
        if affil:
            author_line += "\\\\\n  " + r"\textit{" + affil + "}"
        L.append(r"\author{" + author_line + "}")
    else:
        L.append(r"\author{}")

    title_line = title or ""
    if subtitle:
        title_line += r"\\[0.4em]\large " + subtitle
    L.append(r"\title{" + title_line + "}")
    L.append(r"\date{" + _format_date(date_raw) + "}")
    if course:
        L.append("% Course/context: " + course)

    # ---- body ----
    L.append("")
    L.append(r"\begin{document}")
    L.append("")
    L.append(r"\maketitle")

    if has_abs:
        L.append("")
        L.append(r"\begin{abstract}")
        L.append("  % Your abstract here.")
        L.append(r"\end{abstract}")

    if has_kw:
        L.append("")
        L.append(r"\noindent\textbf{Keywords:} keyword one, keyword two, keyword three")

    L.append("")

    if struct:
        for item in struct:
            t   = item.get("type",  "section")
            lbl = item.get("label", "")
            tex = _struct_tex(t, lbl, num_cols)
            if not tex:
                continue
            L.append("")
            L.append(tex)
            if t in STRUCT_SECTION_TYPES:
                L.append("")
                L.append("  % Body text. " + chr(92) + cite_cmd + "{key}")
                L.append("")
    else:
        L.append("% --- Body ---")
        L.append("")
        L.append(r"\section{Introduction}")
        L.append("")
        L.append("% Begin writing here. Use " + chr(92) + cite_cmd + "{citationkey} to cite.")
        L.append("")
        L.append(r"\section{Conclusion}")
        L.append("")

    if notes == "endnote" and cit in ("SBL", "Chicago"):
        L.append("")
        L.append(r"\theendnotes")

    if print_bib:
        L.append("")
        L.append(r"\printbibliography[heading=bibintoc,title={" + bib_head + "}]")

    L.append("")
    L.append(r"\end{document}")
    L.append("")

    return "\n".join(L)
