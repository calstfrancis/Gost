"""
journal_importer.py — Extract settings from a journal LaTeX template file.
Returns a partial state dict suitable for merging into _apply_state().
"""

import re
from typing import Any, Dict


def _docclass(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    m = re.search(r'\\documentclass\[([^\]]*)\]\{([^}]+)\}', text)
    if not m:
        return out
    opts = m.group(1)
    out["_doc_class"] = m.group(2).strip()
    fs = re.search(r'\b(10|11|12)pt\b', opts)
    if fs:
        out["font_size"] = fs.group(0)
    if "a4paper" in opts:
        out["paper"] = "a4paper"
    elif "letterpaper" in opts:
        out["paper"] = "letterpaper"
    return out


def _geometry(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # Match \usepackage[...]{geometry} or \geometry{...}
    for pat in (
        r'\\usepackage\[([^\]]*)\]\{geometry\}',
        r'\\geometry\{([^}]+)\}',
    ):
        m = re.search(pat, text)
        if m:
            opts = m.group(1)
            break
    else:
        return out

    for pap in ("a4paper", "letterpaper"):
        if pap in opts:
            out["paper"] = pap

    # Try various margin keys in order of specificity
    for key in ("margin", "hmargin", "left", "inner"):
        mg = re.search(rf'(?:^|[,\s]){key}\s*=\s*([\d.]+)(in|cm|mm|pt)', opts)
        if mg:
            val, unit = float(mg.group(1)), mg.group(2)
            inches = {"in": val, "cm": val / 2.54, "mm": val / 25.4, "pt": val / 72.27}[unit]
            out["margin"] = f"{round(inches, 2)}"
            break

    return out


def _font(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # fontspec \setmainfont
    m = re.search(r'\\setmainfont(?:\[[^\]]*\])?\{([^}]+)\}', text, re.DOTALL)
    if m:
        fn = m.group(1).strip().lower()
        for needle, key in [
            ("garamond", "ebgaramond"), ("eb garamond", "ebgaramond"),
            ("palatino",  "palatino"),  ("pagella",     "palatino"),
            ("times",     "times"),     ("libertine",   "libertine"),
            ("junicode",  "junicode"),
        ]:
            if needle in fn:
                out["font_pkg"] = key
                break

    if "font_pkg" not in out:
        for pkg, key in [
            ("ebgaramond", "ebgaramond"), ("mathpazo",  "palatino"),
            ("mathptmx",   "times"),      ("libertine", "libertine"),
        ]:
            if re.search(r'\\usepackage(?:\[[^\]]*\])?\{' + re.escape(pkg) + r'\}', text):
                out["font_pkg"] = key
                break

    return out


def _spacing(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if re.search(r'\\doublespacing', text):
        out["linespace"] = "2"
    elif re.search(r'\\onehalfspacing', text):
        out["linespace"] = "1.5"
    else:
        m = re.search(r'\\(?:setstretch|linespread)\{([\d.]+)\}', text)
        if m:
            v = float(m.group(1))
            out["linespace"] = "2" if v > 1.7 else ("1.5" if v > 1.1 else "1")
    return out


def _parindent(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    m = re.search(r'\\setlength\{\\parindent\}\{([\d.]+)(em|pt|cm|in)\}', text)
    if m:
        v, u = float(m.group(1)), m.group(2)
        em = {"em": v, "pt": v / 10, "cm": v * 2, "in": v * 5}[u]
        out["parindent"] = str(min(max(round(em, 1), 0.0), 4.0))
    return out


def _biblatex(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    m = re.search(r'\\usepackage\[([^\]]*)\]\{biblatex\}', text)
    if m:
        opts = m.group(1)
        sm = re.search(r'style\s*=\s*([^\s,\]]+)', opts)
        if sm:
            out["biblatex_style"] = sm.group(1)
    return out


def _bib_resource(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    m = re.search(r'\\addbibresource\{([^}]+)\}', text)
    if m:
        out["bib_file"] = m.group(1).strip()
    return out


def parse_template(path: str) -> Dict[str, Any]:
    """
    Parse a .tex / .cls / .sty file and return a partial state dict.
    Keys beginning with '_' are metadata for display only, not applied to state.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return {"_error": str(e)}

    result: Dict[str, Any] = {}
    for fn in (_docclass, _geometry, _font, _spacing, _parindent, _biblatex, _bib_resource):
        result.update(fn(text))
    return result


def describe_result(state: Dict[str, Any]) -> str:
    """Return a human-readable summary of what was imported."""
    if "_error" in state:
        return f"Error reading file: {state['_error']}"

    lines = []
    if "_doc_class" in state:
        lines.append(f"Class: {state['_doc_class']}")
    if "font_size" in state:
        lines.append(f"Font size: {state['font_size']}")
    if "paper" in state:
        lines.append(f"Paper: {state['paper']}")
    if "margin" in state:
        lines.append(f"Margin: {state['margin']} in")
    if "font_pkg" in state:
        lines.append(f"Font: {state['font_pkg']}")
    if "linespace" in state:
        lines.append(f"Line spacing: {state['linespace']}×")
    if "parindent" in state:
        lines.append(f"Paragraph indent: {state['parindent']} em")
    if "biblatex_style" in state:
        lines.append(f"BibLaTeX style: {state['biblatex_style']}")
    if "bib_file" in state:
        lines.append(f"Bib file: {state['bib_file']}")
    if not lines:
        return "No recognisable settings found."
    return "Imported: " + ", ".join(lines)
