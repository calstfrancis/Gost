"""
preview_compiler.py — Compile .typ or .tex source to page PNG bytes or PDF for preview.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

# The flatpak bundles typst at /app/bin/typst and its fonts in /app/share/fonts,
# so Typst compilation runs entirely inside the sandbox. A full LaTeX toolchain
# is far too large to bundle, so LaTeX preview is source-install only; the
# flatpak still generates and exports .tex, it just cannot render it.
_IN_FLATPAK = bool(os.environ.get("FLATPAK_ID"))

LATEX_UNAVAILABLE_IN_FLATPAK = (
    "LaTeX preview is not available in the Flatpak build — a full TeX "
    "installation cannot be bundled.\n"
    "Export the .tex source and compile it locally, or switch to Typst, "
    "which is bundled and needs no setup."
)


def _host_which(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _run(cmd: list, **kwargs):
    return subprocess.run(cmd, **kwargs)


def _preview_pdf_path() -> str:
    d = Path.home() / ".cache" / "gost"
    d.mkdir(parents=True, exist_ok=True)
    return str(d / "preview.pdf")


def typst_available() -> bool:
    return _host_which("typst")


def latex_available() -> bool:
    if _IN_FLATPAK:
        return False
    return _host_which("latexmk")


def image_tools_available() -> bool:
    return _host_which("pdftoppm") or _host_which("convert")


def compile_typst(source: str) -> Tuple[List[bytes], str]:
    """Return (page_png_list, error_str). On success error is empty."""
    if not _host_which("typst"):
        return [], "typst not found in PATH.\nInstall from https://typst.app or via your package manager."

    # Guarantee white page background for preview regardless of GTK theme.
    # Inject before the document so the template's own #set page() overrides
    # only the properties it specifies; fill stays white if not redefined.
    if "fill:" not in source:
        source = "#set page(fill: white)\n" + source

    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "doc.typ")
        out = os.path.join(d, "doc.png")
        with open(src, "w", encoding="utf-8") as f:
            f.write(source)
        try:
            r = _run(
                [_cmd("typst"), "compile", "--format", "png", src, out],
                capture_output=True, text=True, timeout=20,
            )
        except subprocess.TimeoutExpired:
            return [], "Compilation timed out (20 s)."
        except Exception as e:
            return [], str(e)

        if r.returncode != 0:
            return [], (r.stderr or r.stdout).strip()

        pages: List[bytes] = []
        # Typst writes doc_1.png, doc_2.png, … for multi-page
        i = 1
        while True:
            p = os.path.join(d, f"doc_{i}.png")
            if os.path.exists(p):
                with open(p, "rb") as f:
                    pages.append(f.read())
                i += 1
            else:
                break
        # Single-page fallback
        if not pages and os.path.exists(out):
            with open(out, "rb") as f:
                pages.append(f.read())

        return (pages, "") if pages else ([], "Compilation succeeded but no PNG output found.")


def _cmd(name: str) -> str:
    """Resolve a compiler to its full path (/app/bin under flatpak)."""
    return shutil.which(name) or name


def compile_latex(source: str, engine: str = "xelatex") -> Tuple[List[bytes], str]:
    """Return (page_png_list, error_str)."""
    if _IN_FLATPAK:
        return [], LATEX_UNAVAILABLE_IN_FLATPAK
    if not _host_which("latexmk"):
        return [], "latexmk not found.\nInstall TeX Live or MiKTeX."

    has_pdftoppm = _host_which("pdftoppm")
    has_convert  = _host_which("convert")
    if not has_pdftoppm and not has_convert:
        return [], (
            "Image converter not found.\n"
            "Install poppler-tools (pdftoppm) or ImageMagick (convert)."
        )

    flag = {
        "pdflatex": "-pdf",
        "xelatex":  "-xelatex",
        "lualatex": "-lualatex",
    }.get(engine, "-xelatex")

    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "doc.tex")
        pdf = os.path.join(d, "doc.pdf")
        with open(src, "w", encoding="utf-8") as f:
            f.write(source)
        try:
            r = _run(
                [_cmd("latexmk"), flag, "-interaction=nonstopmode",
                 "-output-directory", d, src],
                capture_output=True, text=True, timeout=60, cwd=d,
            )
        except subprocess.TimeoutExpired:
            return [], "LaTeX compilation timed out (60 s)."
        except Exception as e:
            return [], str(e)

        if not os.path.exists(pdf):
            tail = (r.stderr or r.stdout)[-3000:]
            return [], f"Compilation failed:\n{tail}"

        pages: List[bytes] = []

        if has_pdftoppm:
            pfx = os.path.join(d, "pg")
            try:
                _run(
                    [_cmd("pdftoppm"), "-r", "150", "-png", pdf, pfx],
                    check=True, capture_output=True, timeout=30,
                )
                i = 1
                while True:
                    found = None
                    for pat in (f"pg-{i:02d}.png", f"pg-{i:03d}.png", f"pg-{i}.png"):
                        p = os.path.join(d, pat)
                        if os.path.exists(p):
                            found = p
                            break
                    if found:
                        with open(found, "rb") as f:
                            pages.append(f.read())
                        i += 1
                    else:
                        break
            except Exception:
                pass

        if not pages and has_convert:
            pat = os.path.join(d, "pg-%d.png")
            try:
                _run(
                    [_cmd("convert"), "-density", "150", pdf, pat],
                    check=True, capture_output=True, timeout=30,
                )
                i = 0
                while True:
                    p = os.path.join(d, f"pg-{i}.png")
                    if os.path.exists(p):
                        with open(p, "rb") as f:
                            pages.append(f.read())
                        i += 1
                    else:
                        break
            except Exception:
                pass

        return (pages, "") if pages else ([], "PDF compiled but image conversion failed.")


# ---------------------------------------------------------------------------
# PDF export (for "Open in viewer")
# ---------------------------------------------------------------------------

def compile_typst_to_pdf(source: str) -> Tuple[str, str]:
    """Compile Typst source to PDF. Returns (pdf_path, error_str)."""
    if not _host_which("typst"):
        return "", "typst not found in PATH.\nInstall from https://typst.app."

    if "fill:" not in source:
        source = "#set page(fill: white)\n" + source

    pdf_path = _preview_pdf_path()
    tmp = tempfile.NamedTemporaryFile(suffix=".typ", mode="w", encoding="utf-8", delete=False)
    try:
        tmp.write(source)
        tmp.close()
        r = _run(
            [_cmd("typst"), "compile", tmp.name, pdf_path],
            capture_output=True, text=True, timeout=20,
        )
        if r.returncode != 0:
            return "", (r.stderr or r.stdout).strip()
        return pdf_path, ""
    except subprocess.TimeoutExpired:
        return "", "Compilation timed out (20 s)."
    except Exception as e:
        return "", str(e)
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def compile_latex_to_pdf(source: str, engine: str = "xelatex") -> Tuple[str, str]:
    """Compile LaTeX source to PDF via latexmk. Returns (pdf_path, error_str)."""
    if _IN_FLATPAK:
        return "", LATEX_UNAVAILABLE_IN_FLATPAK
    if not _host_which("latexmk"):
        return "", "latexmk not found.\nInstall TeX Live or MiKTeX."

    flag = {
        "pdflatex": "-pdf",
        "xelatex":  "-xelatex",
        "lualatex": "-lualatex",
    }.get(engine, "-xelatex")

    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "doc.tex")
        pdf = os.path.join(d, "doc.pdf")
        with open(src, "w", encoding="utf-8") as f:
            f.write(source)
        try:
            r = _run(
                [_cmd("latexmk"), flag, "-interaction=nonstopmode",
                 "-output-directory", d, src],
                capture_output=True, text=True, timeout=60, cwd=d,
            )
        except subprocess.TimeoutExpired:
            return "", "LaTeX compilation timed out (60 s)."
        except Exception as e:
            return "", str(e)

        if not os.path.exists(pdf):
            tail = (r.stderr or r.stdout)[-2000:]
            return "", f"Compilation failed:\n{tail}"

        dest = _preview_pdf_path()
        shutil.copy2(pdf, dest)
        return dest, ""
