"""
texgen.py — Build a complete extarticle .tex document from a state dict.
No GTK dependency; import and test freely.
"""

from typing import Dict, List, Any

STYLE_DEFAULTS: Dict[str, Dict[str, str]] = {
    "SBL":      {"biblatex_style": "verbose-note",  "notes": "footnote"},
    "Chicago":  {"biblatex_style": "chicago-notes", "notes": "footnote"},
    "MLA":      {"biblatex_style": "mla",           "notes": "none"},
    "APA":      {"biblatex_style": "apa",           "notes": "none"},
    "ASA":      {"biblatex_style": "asa",           "notes": "none"},
    "Turabian": {"biblatex_style": "chicago-notes", "notes": "footnote"},
    "Harvard":  {"biblatex_style": "authoryear",    "notes": "none"},
}

PDFLATEX_FONTS: Dict[str, str | None] = {
    "ebgaramond": r"\usepackage{ebgaramond}",
    "palatino":   r"\usepackage{mathpazo}",
    "times":      r"\usepackage{newtxtext,newtxmath}",
    "libertine":  r"\usepackage{libertine}",
    "none":       None,
}

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
    "times": (
        r"\usepackage{fontspec}" + "\n"
        r"\setmainfont{Times New Roman}"
    ),
}

# Fonts that require fontspec and have no pdfLaTeX fallback
FONTSPEC_ONLY = {"junicode"}

FONT_OPTIONS: List[Dict[str, Any]] = [
    {"display": "Junicode (fontspec)", "key": "junicode", "requires_fontspec": True},
    {"display": "EB Garamond",         "key": "ebgaramond", "requires_fontspec": False},
    {"display": "Palatino (mathpazo)", "key": "palatino",   "requires_fontspec": False},
    {"display": "Times (newtxtext)",   "key": "times",      "requires_fontspec": False},
    {"display": "Linux Libertine",     "key": "libertine",  "requires_fontspec": False},
    {"display": "None (default CM)",   "key": "none",       "requires_fontspec": False},
]

STRUCT_SECTION_TYPES = {"part", "section", "subsection", "subsubsection"}

# ---------------------------------------------------------------------------
# titlesec heading presets per citation style
# ---------------------------------------------------------------------------

HEADING_STYLES: Dict[str, List[str]] = {
    "SBL": [
        r"\usepackage{titlesec}",
        r"\titleformat{\section}[block]{\normalfont\large\scshape\centering}"
        r"{}{0em}{}[\vspace{-0.25ex}\rule{\textwidth}{0.4pt}]",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\itshape\centering}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\centering}{}{0em}{}",
        r"\titlespacing*{\section}{0pt}{2.5ex plus 1ex}{1ex}",
        r"\titlespacing*{\subsection}{0pt}{2ex}{0.75ex}",
    ],
    "Chicago": [
        r"\usepackage{titlesec}",
        r"\titleformat{\section}[block]{\normalfont\large\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\itshape\centering}{}{0em}{}",
        r"\titlespacing*{\section}{0pt}{2ex}{1ex}",
    ],
    "MLA": [
        r"\usepackage{titlesec}",
        r"\titleformat{\section}[block]{\normalfont\large\bfseries}{}{0em}{}",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\bfseries}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\itshape}{}{0em}{}",
    ],
    "APA": [
        r"\usepackage{titlesec}",
        r"% APA 7th edition — five heading levels",
        r"\titleformat{\section}[block]{\normalfont\large\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\bfseries}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\bfseries\itshape}{}{0em}{}",
        r"\titlespacing*{\section}{0pt}{2ex}{0.5ex}",
        r"\titlespacing*{\subsection}{0pt}{1.5ex}{0ex}",
        r"\titlespacing*{\subsubsection}{0pt}{1.25ex}{0ex}",
    ],
    "ASA": [
        r"\usepackage{titlesec}",
        r"% ASA Style Guide — centered bold (level 1), flush-left bold (level 2)",
        r"\titleformat{\section}[block]{\normalfont\large\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\bfseries}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\itshape}{}{0em}{}",
        r"\titlespacing*{\section}{0pt}{2ex}{0.5ex}",
        r"\titlespacing*{\subsection}{0pt}{1.5ex}{0ex}",
    ],
    "Turabian": [
        r"\usepackage{titlesec}",
        r"% Turabian (Chicago student edition) — centered bold",
        r"\titleformat{\section}[block]{\normalfont\large\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\itshape\centering}{}{0em}{}",
        r"\titlespacing*{\section}{0pt}{2ex}{1ex}",
    ],
    "Harvard": [
        r"\usepackage{titlesec}",
        r"% Harvard referencing — centered bold (level 1), flush-left bold (level 2)",
        r"\titleformat{\section}[block]{\normalfont\large\bfseries\centering}{}{0em}{}",
        r"\titleformat{\subsection}[block]{\normalfont\normalsize\bfseries}{}{0em}{}",
        r"\titleformat{\subsubsection}[block]{\normalfont\normalsize\bfseries\itshape}{}{0em}{}",
        r"\titlespacing*{\section}{0pt}{2ex}{0.5ex}",
        r"\titlespacing*{\subsection}{0pt}{1.5ex}{0ex}",
    ],
}

# ---------------------------------------------------------------------------
# Language support (polyglossia / babel / CJK)
# ---------------------------------------------------------------------------

def _language_block(lang: str, eng: str) -> str:
    """Return the package lines for a given language and engine."""
    is_xe_or_lua = eng in ("xelatex", "lualatex")
    is_xe = eng == "xelatex"
    is_lua = eng == "lualatex"

    if lang == "russian":
        if is_xe_or_lua:
            return (
                r"\usepackage{polyglossia}" + "\n"
                r"\setmainlanguage{english}" + "\n"
                r"\setotherlanguage{russian}" + "\n"
                r"% Usage: \textrussian{текст}  or  \begin{russian}…\end{russian}"
            )
        return (
            r"\usepackage[russian,english]{babel}" + "\n"
            r"\usepackage[T2A,T1]{fontenc}" + "\n"
            r"% Usage: \foreignlanguage{russian}{текст}"
        )

    if lang == "hebrew":
        if is_xe_or_lua:
            return (
                r"\usepackage{polyglossia}" + "\n"
                r"\setmainlanguage{english}" + "\n"
                r"\setotherlanguage{hebrew}" + "\n"
                r"\usepackage{bidi}" + "\n"
                r"% Usage: \texthebrew{טקסט}  or  \begin{hebrew}…\end{hebrew}"
            )
        return (
            r"% Hebrew requires XeLaTeX or LuaLaTeX + polyglossia + bidi." + "\n"
            r"% Switch engine in Citation Style → Engine."
        )

    if lang == "japanese":
        if is_xe:
            return (
                r"\usepackage{xeCJK}" + "\n"
                r"\setCJKmainfont{Noto Serif CJK JP}" + "\n"
                r"\setCJKsansfont{Noto Sans CJK JP}" + "\n"
                r"% Japanese text can be typed directly"
            )
        if is_lua:
            return (
                r"\usepackage{luatexja}" + "\n"
                r"\setmainjfont{Noto Serif CJK JP}" + "\n"
                r"% Japanese text can be typed directly"
            )
        return (
            r"% Japanese requires XeLaTeX (xeCJK) or LuaLaTeX (luatexja)." + "\n"
            r"% Switch engine."
        )

    if lang == "tibetan":
        if is_xe_or_lua:
            return (
                r"\usepackage{polyglossia}" + "\n"
                r"\setotherlanguage{tibetan}" + "\n"
                r"% Requires a Tibetan font — e.g.:" + "\n"
                r"% \newfontfamily\tibetanfont{Tibetan Machine Uni}" + "\n"
                r"% Usage: \texttibetan{…}"
            )
        return r"% Tibetan requires XeLaTeX or LuaLaTeX + polyglossia."

    if lang == "sanskrit":
        if is_xe_or_lua:
            return (
                r"\usepackage{polyglossia}" + "\n"
                r"\setotherlanguage{sanskrit}" + "\n"
                r"% Requires a Devanagari font — e.g.:" + "\n"
                r"% \newfontfamily\sanskritfont{Noto Serif Devanagari}" + "\n"
                r"% Usage: \textsanskrit{…}  (Devanagari script)"
            )
        return (
            r"\usepackage{devanagari}  % basic transliteration only" + "\n"
            r"% For full Unicode Devanagari switch to XeLaTeX + polyglossia."
        )

    if lang == "greek":
        if is_xe_or_lua:
            return (
                r"\usepackage{polyglossia}" + "\n"
                r"\setotherlanguage[variant=ancient]{greek}" + "\n"
                r"% Requires a polytonic Greek font — e.g. GFS Didot or New Athena Unicode" + "\n"
                r"% \newfontfamily\greekfont{GFS Didot}" + "\n"
                r"% Usage: \textgreek{Ἐν ἀρχῇ ἦν ὁ Λόγος}"
            )
        return (
            r"\usepackage[greek,english]{babel}" + "\n"
            r"\usepackage[LGR,T1]{fontenc}" + "\n"
            r"% Usage: \textgreek{…}  (LGR-encoded polytonic Greek)"
        )

    if lang == "chinese":
        if is_xe:
            return (
                r"\usepackage{xeCJK}" + "\n"
                r"\setCJKmainfont{Noto Serif CJK SC}  % Simplified" + "\n"
                r"% Traditional Chinese: use Noto Serif CJK TC" + "\n"
                r"% Chinese text can be typed directly"
            )
        if is_lua:
            return (
                r"\usepackage{ctex}" + "\n"
                r"% Chinese text can be typed directly"
            )
        return (
            r"% Chinese requires XeLaTeX (xeCJK) or LuaLaTeX (ctex)." + "\n"
            r"% Switch engine."
        )

    return ""

# ---------------------------------------------------------------------------
# Optional extra packages
# ---------------------------------------------------------------------------

FEATURE_PACKAGES: Dict[str, str] = {
    "dropcaps":     r"\usepackage{lettrine}",
    "marginalia":   r"\usepackage{marginnote}",
    "csquotes":     r"\usepackage[american]{csquotes}",
    "xcolor":       r"\usepackage[dvipsnames]{xcolor}",
    "listings":     r"\usepackage{listings}",
    "enumitem":     r"\usepackage{enumitem}",
    "booktabs":     r"\usepackage{booktabs}",
    "siunitx":      r"\usepackage{siunitx}",
    "epigraph_pkg": r"\usepackage{epigraph}",
    "lineno":       "\\usepackage{lineno}\n\\linenumbers",
    "todonotes":    r"\usepackage[colorinlistoftodos]{todonotes}",
}


def _chapter_slug(title: str, index: int) -> str:
    slug = "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")
    return f"chapter{index:02d}_{slug}" if slug else f"chapter{index:02d}"


def generate_chapter_file(title: str, cite_cmd: str = "autocite") -> str:
    """Return a minimal standalone chapter body file (no preamble)."""
    lines = [
        f"% Chapter: {title}",
        "",
        r"\section{" + (title or "Chapter") + "}",
        "",
        f"% Write chapter content here. Use \\{cite_cmd}{{key}} to cite.",
        "",
    ]
    return "\n".join(lines)


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


def generate(s: Dict[str, Any]) -> str:
    """
    s: dict produced by GostWindow._collect_state()
    Returns a complete .tex string.
    """
    L: List[str] = []

    cit      = s.get("cit_style",      "SBL")
    eng      = s.get("engine",         "xelatex")
    fs       = s.get("font_size",      "11pt")
    paper    = s.get("paper",          "letterpaper")

    _cit_def = STYLE_DEFAULTS.get(cit, STYLE_DEFAULTS["APA"])
    bib_sty  = s.get("biblatex_style") or _cit_def["biblatex_style"]
    notes    = s.get("notes_mode")     or _cit_def["notes"]

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
    font_pkg    = s.get("font_pkg",    "times")
    parindent   = s.get("parindent",   "1.5")
    parskip     = s.get("parskip",     "0")
    microtype   = s.get("microtype",   True)
    encoding    = s.get("encoding",    "utf8")

    use_mc      = s.get("use_multicol", False)
    num_cols    = s.get("num_cols",    2)
    col_rule    = s.get("col_rule",    False)
    col_sep     = s.get("col_sep",     "14")

    numbered          = s.get("numbered_heads",    False)
    has_abs           = s.get("has_abstract",      False)
    has_kw            = s.get("has_keywords",      False)
    use_toc           = s.get("use_toc",           False)
    use_style_hdgs    = s.get("use_style_headings", True)

    features    = s.get("latex_features", [])
    languages   = s.get("languages",      [])

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
            L.append("% Note: {} requires XeLaTeX or LuaLaTeX; no font package loaded".format(font_pkg))
        else:
            fp = PDFLATEX_FONTS.get(font_pkg)
            if fp:
                L.append(fp)
    else:
        if font_pkg in FONTSPEC_FONTS:
            L.append(FONTSPEC_FONTS[font_pkg])
        elif font_pkg in PDFLATEX_FONTS and PDFLATEX_FONTS[font_pkg]:
            L.append(r"\usepackage{fontspec}")
            L.append("% Note: {} is a pdflatex package; set \\setmainfont manually".format(font_pkg))
        else:
            L.append(r"\usepackage{fontspec}")
            L.append(r"% \setmainfont{Your Font Here}")

    if microtype:
        if eng == "pdflatex":
            L.append(r"\usepackage[protrusion=true,expansion=true]{microtype}")
        else:
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

    # Style-specific heading formatting (titlesec)
    if use_style_hdgs and cit in HEADING_STYLES:
        L.append("")
        L.append("% --- Section heading style ({}) ---".format(cit))
        for line in HEADING_STYLES[cit]:
            L.append(line)

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

    # Header / footer via fancyhdr
    header_style   = s.get("header_style",          "auto")
    header_rule    = s.get("header_rule",            False)
    suppress_first = s.get("suppress_first_header",  True)

    L.append("")
    rule_w = "0.4pt" if header_rule else "0pt"

    if header_style == "none":
        L.append("% --- No header/footer ---")
        L.append(r"\pagestyle{empty}")

    elif header_style == "pagenum_bottom":
        L.append("% --- Page numbers only (bottom centre) ---")
        L.append(r"\pagestyle{plain}")

    elif header_style in ("title_left", "section_left", "author_left", "doublesided"):
        L.append("% --- Custom running header ---")
        L.append(r"\usepackage{fancyhdr}")
        L.append(r"\pagestyle{fancy}")
        L.append(r"\fancyhf{}")
        if header_style == "title_left":
            esc = (title or "Untitled").replace("{", r"\{").replace("}", r"\}")
            L.append(rf'\fancyhead[L]{{\itshape {esc}}}')
            L.append(r'\fancyhead[R]{\thepage}')
        elif header_style == "section_left":
            L.append(r'\fancyhead[L]{\itshape\nouppercase{\leftmark}}')
            L.append(r'\fancyhead[R]{\thepage}')
        elif header_style == "author_left":
            al = ""
            if authors.strip():
                parts = authors.split(",")[0].strip().split()
                al = parts[-1] if parts else ""
            L.append(rf'\fancyhead[L]{{\itshape {al}}}')
            L.append(r'\fancyhead[R]{\thepage}')
        elif header_style == "doublesided":
            L.append(r'\fancyhead[LE,RO]{\thepage}')
            L.append(r'\fancyhead[RE]{\itshape\nouppercase{\leftmark}}')
            L.append(r'\fancyhead[LO]{\itshape\nouppercase{\rightmark}}')
        L.append(rf'\renewcommand{{\headrulewidth}}{{{rule_w}}}')
        L.append(r'\renewcommand{\footrulewidth}{0pt}')

    else:  # "auto" — use citation-style defaults
        if cit == "MLA":
            L.append("% --- MLA running header: last name + page number (top right) ---")
            author_last = ""
            if authors.strip():
                parts = authors.split(",")[0].strip().split()
                author_last = parts[-1] if parts else ""
            L.append(r"\usepackage{fancyhdr}")
            L.append(r"\pagestyle{fancy}")
            L.append(r"\fancyhf{}")
            L.append(r"\fancyhead[R]{" + author_last + r" \thepage}")
            L.append(r"\renewcommand{\headrulewidth}{0pt}")
        elif cit == "APA":
            L.append("% --- APA running head + page number ---")
            short_title = (title[:50].upper() if title else "RUNNING HEAD")
            L.append(r"\usepackage{fancyhdr}")
            L.append(r"\pagestyle{fancy}")
            L.append(r"\fancyhf{}")
            L.append(r"\fancyhead[L]{" + short_title + "}")
            L.append(r"\fancyhead[R]{\thepage}")
            L.append(r"\renewcommand{\headrulewidth}{0pt}")
        else:
            L.append("% --- Page number (bottom centre) ---")
            L.append(r"\usepackage{fancyhdr}")
            L.append(r"\pagestyle{fancy}")
            L.append(r"\fancyhf{}")
            L.append(r"\fancyfoot[C]{\thepage}")
            L.append(r"\renewcommand{\headrulewidth}{0pt}")

    # Language packages
    if languages:
        L.append("")
        L.append("% --- Language support ---")
        for lang in languages:
            block = _language_block(lang, eng)
            if block:
                L.append("% -- {} --".format(lang.capitalize()))
                L.append(block)

    # Optional extra packages
    if features:
        L.append("")
        L.append("% --- Extra packages ---")
        for feat in features:
            pkg = FEATURE_PACKAGES.get(feat)
            if pkg:
                L.append(pkg)

    if notes == "endnote" and cit in ("SBL", "Chicago"):
        L.append("")
        L.append("% --- Endnotes ---")
        L.append(r"\usepackage{endnotes}")
        L.append(r"\let\footnote=\endnote")

    custom_preamble = s.get("custom_latex_preamble", "").strip()
    if custom_preamble:
        L.append("")
        L.append("% --- Custom preamble ---")
        for line in custom_preamble.splitlines():
            L.append(line)

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
    if suppress_first and header_style not in ("auto", "none", "pagenum_bottom"):
        L.append(r"\thispagestyle{plain}")

    if has_abs:
        L.append("")
        L.append(r"\begin{abstract}")
        L.append("  % Your abstract here.")
        L.append(r"\end{abstract}")

    if has_kw:
        L.append("")
        L.append(r"\noindent\textbf{Keywords:} keyword one, keyword two, keyword three")

    if use_toc:
        L.append("")
        L.append(r"\tableofcontents")
        L.append(r"\newpage")

    raw_chapters = s.get("chapters", [])
    chapters = [c["title"] if isinstance(c, dict) else c for c in raw_chapters]
    multifile = s.get("multifile", False)

    L.append("")
    L.append("% --- Body ---")
    L.append("")
    if chapters:
        if multifile:
            for i, ch in enumerate(chapters, 1):
                slug = _chapter_slug(ch, i)
                L.append(r"\input{" + slug + "}")
                L.append("")
        else:
            for ch in chapters:
                L.append(r"\section{" + (ch or "Untitled Chapter") + "}")
                L.append("")
                L.append("% Begin writing here. Use " + chr(92) + cite_cmd + "{citationkey} to cite.")
                L.append("")
    else:
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
