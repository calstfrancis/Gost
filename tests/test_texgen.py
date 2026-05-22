"""
Unit tests for texgen.py — LaTeX template generation.
No GTK dependency; run with: python3 -m pytest tests/
"""

import unittest
from essay_builder.texgen import generate, STYLE_DEFAULTS, HEADING_STYLES, FEATURE_PACKAGES


def _base(**overrides):
    state = {
        "cit_style": "SBL",
        "engine": "xelatex",
        "font_size": "11pt",
        "paper": "letterpaper",
        "title": "Test Title",
        "authors": "Test Author",
    }
    state.update(overrides)
    return state


class TestStyleDefaults(unittest.TestCase):
    def test_all_four_styles_present(self):
        for style in ("SBL", "Chicago", "MLA", "APA"):
            self.assertIn(style, STYLE_DEFAULTS)

    def test_each_style_has_required_keys(self):
        for style, cfg in STYLE_DEFAULTS.items():
            self.assertIn("biblatex_style", cfg, style)
            self.assertIn("notes", cfg, style)


class TestGenerateDocumentClass(unittest.TestCase):
    def test_returns_string(self):
        self.assertIsInstance(generate(_base()), str)

    def test_documentclass_includes_font_and_paper(self):
        out = generate(_base())
        self.assertIn(r"\documentclass[11pt,letterpaper]{extarticle}", out)

    def test_empty_state_uses_defaults(self):
        out = generate({})
        self.assertIn(r"\documentclass", out)
        self.assertIn("verbose-note", out)   # SBL is default

    def test_document_begin_end(self):
        out = generate(_base())
        self.assertIn(r"\begin{document}", out)
        self.assertIn(r"\end{document}", out)


class TestGenerateMetadata(unittest.TestCase):
    def test_title_in_output(self):
        self.assertIn("Test Title", generate(_base()))

    def test_author_in_output(self):
        self.assertIn("Test Author", generate(_base()))

    def test_subtitle_included(self):
        self.assertIn("A Subtitle", generate(_base(subtitle="A Subtitle")))

    def test_multiple_authors_use_and(self):
        out = generate(_base(authors="Alice Smith, Bob Jones"))
        self.assertIn(r"\and", out)

    def test_single_author_with_affiliation(self):
        out = generate(_base(authors="Alice Smith", affiliation="Some University"))
        self.assertIn("Some University", out)

    def test_date_today_when_empty(self):
        self.assertIn(r"\today", generate(_base(date="")))

    def test_date_formatted(self):
        self.assertIn("January 15, 2025", generate(_base(date="2025-01-15")))


class TestGenerateCitationStyles(unittest.TestCase):
    def test_sbl_uses_verbose_note(self):
        self.assertIn("verbose-note", generate(_base(cit_style="SBL")))

    def test_chicago_uses_chicago_notes(self):
        self.assertIn("chicago-notes", generate(_base(cit_style="Chicago")))

    def test_mla_style(self):
        self.assertIn("  style=mla,", generate(_base(cit_style="MLA")))

    def test_apa_style(self):
        self.assertIn("  style=apa,", generate(_base(cit_style="APA")))


class TestGenerateEngines(unittest.TestCase):
    def test_pdflatex_uses_inputenc(self):
        self.assertIn(r"\usepackage[utf8]{inputenc}", generate(_base(engine="pdflatex")))

    def test_xelatex_uses_fontspec(self):
        self.assertIn(r"\usepackage{fontspec}", generate(_base(engine="xelatex")))

    def test_lualatex_uses_fontspec(self):
        self.assertIn(r"\usepackage{fontspec}", generate(_base(engine="lualatex")))


class TestGenerateLayout(unittest.TestCase):
    def test_doublespacing(self):
        self.assertIn(r"\doublespacing", generate(_base(linespace="2")))

    def test_onehalfspacing(self):
        self.assertIn(r"\onehalfspacing", generate(_base(linespace="1.5")))

    def test_single_spacing_no_command(self):
        out = generate(_base(linespace="1"))
        self.assertNotIn(r"\onehalfspacing", out)
        self.assertNotIn(r"\doublespacing", out)

    def test_unnumbered_headings(self):
        self.assertIn(r"\setcounter{secnumdepth}{0}", generate(_base(numbered_heads=False)))

    def test_numbered_headings(self):
        self.assertNotIn(r"\setcounter{secnumdepth}{0}", generate(_base(numbered_heads=True)))

    def test_multicol(self):
        self.assertIn(r"\usepackage{multicol}", generate(_base(use_multicol=True, num_cols=2)))


class TestGenerateHeaders(unittest.TestCase):
    def test_header_none(self):
        self.assertIn(r"\pagestyle{empty}", generate(_base(header_style="none")))

    def test_header_pagenum_bottom(self):
        self.assertIn(r"\pagestyle{plain}", generate(_base(header_style="pagenum_bottom")))

    def test_mla_auto_header_uses_last_name(self):
        out = generate(_base(cit_style="MLA", header_style="auto", authors="Alice Smith"))
        self.assertIn("Smith", out)
        self.assertIn(r"\thepage", out)

    def test_apa_auto_header_uses_short_title(self):
        self.assertIn("MY PAPER", generate(_base(cit_style="APA", header_style="auto", title="My Paper")))


class TestGenerateBibliography(unittest.TestCase):
    def test_bib_path_included(self):
        self.assertIn(r"\addbibresource{/path/to/refs.bib}",
                      generate(_base(bib_file="/path/to/refs.bib")))

    def test_no_bib_path_uses_placeholder(self):
        self.assertIn("references.bib", generate(_base(bib_file="")))

    def test_print_bib_present_by_default(self):
        self.assertIn(r"\printbibliography", generate(_base()))

    def test_print_bib_suppressed(self):
        self.assertNotIn(r"\printbibliography", generate(_base(print_bib=False)))

    def test_endnotes_package_for_sbl(self):
        out = generate(_base(cit_style="SBL", notes_mode="endnote"))
        self.assertIn(r"\usepackage{endnotes}", out)
        self.assertIn(r"\let\footnote=\endnote", out)

    def test_endnotes_not_added_for_mla(self):
        out = generate(_base(cit_style="MLA", notes_mode="endnote"))
        self.assertNotIn(r"\usepackage{endnotes}", out)


class TestGenerateExtras(unittest.TestCase):
    def test_abstract_block(self):
        out = generate(_base(has_abstract=True))
        self.assertIn(r"\begin{abstract}", out)
        self.assertIn(r"\end{abstract}", out)

    def test_no_abstract_by_default(self):
        self.assertNotIn(r"\begin{abstract}", generate(_base()))

    def test_toc(self):
        self.assertIn(r"\tableofcontents", generate(_base(use_toc=True)))

    def test_no_toc_by_default(self):
        self.assertNotIn(r"\tableofcontents", generate(_base()))

    def test_csquotes_feature(self):
        self.assertIn(r"\usepackage[american]{csquotes}",
                      generate(_base(latex_features=["csquotes"])))

    def test_booktabs_feature(self):
        self.assertIn(r"\usepackage{booktabs}",
                      generate(_base(latex_features=["booktabs"])))

    def test_language_russian_xelatex(self):
        self.assertIn(r"\usepackage{polyglossia}",
                      generate(_base(engine="xelatex", languages=["russian"])))

    def test_language_hebrew_pdflatex_warns(self):
        out = generate(_base(engine="pdflatex", languages=["hebrew"]))
        self.assertIn("XeLaTeX", out)

    def test_sbl_heading_style_applied(self):
        self.assertIn(r"\scshape\centering",
                      generate(_base(cit_style="SBL", use_style_headings=True)))


class TestHeadingStyles(unittest.TestCase):
    def test_all_four_styles_have_rules(self):
        for style in ("SBL", "Chicago", "MLA", "APA"):
            self.assertIn(style, HEADING_STYLES)
            self.assertTrue(len(HEADING_STYLES[style]) > 0)


class TestFeaturePackages(unittest.TestCase):
    def test_known_features_mapped(self):
        for key in ("dropcaps", "csquotes", "xcolor", "booktabs", "lineno"):
            self.assertIn(key, FEATURE_PACKAGES)


if __name__ == "__main__":
    unittest.main()

