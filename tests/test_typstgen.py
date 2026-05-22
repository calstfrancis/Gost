"""
Unit tests for typstgen.py — Typst template generation.
No GTK dependency; run with: python3 -m pytest tests/
"""

import unittest
from essay_builder.typstgen import generate, TYPST_CIT_STYLES, TYPST_HEADING_STYLES


def _base(**overrides):
    state = {
        "cit_style": "SBL",
        "font_size": "11pt",
        "paper": "letterpaper",
        "title": "Test Title",
        "authors": "Test Author",
    }
    state.update(overrides)
    return state


class TestTypstCitStyles(unittest.TestCase):
    def test_all_four_styles_mapped(self):
        for style in ("SBL", "Chicago", "MLA", "APA"):
            self.assertIn(style, TYPST_CIT_STYLES)


class TestTypstGenerateStructure(unittest.TestCase):
    def test_returns_string(self):
        self.assertIsInstance(generate(_base()), str)

    def test_empty_state_uses_defaults(self):
        out = generate({})
        self.assertIn("#set document(", out)

    def test_page_settings_present(self):
        self.assertIn("#set page(", generate(_base()))

    def test_text_settings_present(self):
        self.assertIn("#set text(", generate(_base()))

    def test_par_settings_present(self):
        self.assertIn("#set par(", generate(_base()))


class TestTypstGenerateMetadata(unittest.TestCase):
    def test_title_in_output(self):
        self.assertIn("Test Title", generate(_base()))

    def test_author_in_output(self):
        self.assertIn("Test Author", generate(_base()))

    def test_subtitle_included(self):
        self.assertIn("A Subtitle", generate(_base(subtitle="A Subtitle")))

    def test_affiliation_included(self):
        self.assertIn("University of Testing",
                      generate(_base(affiliation="University of Testing")))

    def test_multiple_authors(self):
        out = generate(_base(authors="Alice Smith, Bob Jones"))
        self.assertIn("Alice Smith", out)
        self.assertIn("Bob Jones", out)

    def test_date_formatted(self):
        self.assertIn("June 1, 2025", generate(_base(date="2025-06-01")))

    def test_date_today_when_empty(self):
        self.assertIn("#datetime.today().display()", generate(_base(date="")))


class TestTypstGeneratePaper(unittest.TestCase):
    def test_letterpaper_maps_to_us_letter(self):
        self.assertIn('"us-letter"', generate(_base(paper="letterpaper")))

    def test_a4paper_maps_to_a4(self):
        self.assertIn('"a4"', generate(_base(paper="a4paper")))


class TestTypstGenerateCitationStyles(unittest.TestCase):
    def test_sbl_uses_chicago_notes(self):
        self.assertIn("chicago-notes", generate(_base(cit_style="SBL")))

    def test_chicago_uses_chicago_notes(self):
        self.assertIn("chicago-notes", generate(_base(cit_style="Chicago")))

    def test_mla_style(self):
        self.assertIn('style: "mla"', generate(_base(cit_style="MLA")))

    def test_apa_style(self):
        self.assertIn('style: "apa"', generate(_base(cit_style="APA")))


class TestTypstGenerateLayout(unittest.TestCase):
    def test_doublespacing_leading(self):
        self.assertIn("1.3em", generate(_base(linespace="2")))

    def test_onehalfspacing_leading(self):
        self.assertIn("0.9em", generate(_base(linespace="1.5")))

    def test_numbered_headings(self):
        self.assertIn('#set heading(numbering: "1.")', generate(_base(numbered_heads=True)))

    def test_unnumbered_headings_no_numbering_set(self):
        self.assertNotIn('#set heading(numbering', generate(_base(numbered_heads=False)))


class TestTypstGenerateHeaders(unittest.TestCase):
    def test_header_none(self):
        self.assertIn("header: none", generate(_base(header_style="none")))

    def test_mla_auto_header_uses_author_last_name(self):
        out = generate(_base(cit_style="MLA", header_style="auto", authors="Alice Smith"))
        self.assertIn("Smith", out)

    def test_apa_auto_header_uses_title(self):
        out = generate(_base(cit_style="APA", header_style="auto", title="My Paper"))
        self.assertIn("My Paper", out)


class TestTypstGenerateBibliography(unittest.TestCase):
    def test_bib_path_included(self):
        self.assertIn("/path/to/refs.bib",
                      generate(_base(bib_file="/path/to/refs.bib", print_bib=True)))

    def test_no_bib_path_uses_placeholder(self):
        self.assertIn("references.bib", generate(_base(bib_file="", print_bib=True)))

    def test_no_bibliography_when_disabled(self):
        self.assertNotIn("#bibliography", generate(_base(print_bib=False)))


class TestTypstGenerateExtras(unittest.TestCase):
    def test_abstract_block(self):
        self.assertIn("*Abstract*", generate(_base(has_abstract=True)))

    def test_no_abstract_by_default(self):
        self.assertNotIn("*Abstract*", generate(_base()))

    def test_keywords_block(self):
        self.assertIn("*Keywords:*", generate(_base(has_keywords=True)))

    def test_toc(self):
        self.assertIn("#outline()", generate(_base(use_toc=True)))

    def test_no_toc_by_default(self):
        self.assertNotIn("#outline()", generate(_base()))

    def test_endnotes_implementation(self):
        out = generate(_base(typst_notes="endnote"))
        self.assertIn("_endnote-store", out)
        self.assertIn("#print-endnotes()", out)

    def test_no_endnotes_by_default(self):
        self.assertNotIn("_endnote-store", generate(_base()))

    def test_dropcaps_feature_import(self):
        self.assertIn("droplet", generate(_base(typst_features=["dropcaps"])))

    def test_codly_feature_import(self):
        self.assertIn("codly", generate(_base(typst_features=["codly"])))

    def test_language_hint_russian(self):
        self.assertIn("Russian", generate(_base(languages=["russian"])))


class TestTypstHeadingStyles(unittest.TestCase):
    def test_all_four_styles_have_rules(self):
        for style in ("SBL", "Chicago", "MLA", "APA"):
            self.assertIn(style, TYPST_HEADING_STYLES)
            self.assertTrue(len(TYPST_HEADING_STYLES[style]) > 0)

    def test_sbl_uses_smallcaps(self):
        self.assertIn("smallcaps", generate(_base(cit_style="SBL", use_style_headings=True)))

    def test_chicago_uses_strong(self):
        self.assertIn("strong", generate(_base(cit_style="Chicago", use_style_headings=True)))


if __name__ == "__main__":
    unittest.main()
