"""
Unit tests for texgen.py
"""

import unittest
from essay_builder.texgen import generate, STYLE_DEFAULTS, _struct_tex


class TestTexgen(unittest.TestCase):
    """Test cases for LaTeX generation functions."""
    
    def test_style_defaults_structure(self):
        """Test that STYLE_DEFAULTS has correct structure."""
        self.assertIn("SBL", STYLE_DEFAULTS)
        self.assertIn("Chicago", STYLE_DEFAULTS)
        self.assertIn("MLA", STYLE_DEFAULTS)
        self.assertIn("APA", STYLE_DEFAULTS)
        
        for style, config in STYLE_DEFAULTS.items():
            self.assertIn("biblatex_style", config)
            self.assertIn("notes", config)
    
    def test_struct_tex_section(self):
        """Test section generation."""
        result = _struct_tex("section", "Test Section", 2)
        self.assertIn(r"\section{Test Section}", result)
    
    def test_struct_tex_section_default_label(self):
        """Test section generation with default label."""
        result = _struct_tex("section", "", 2)
        self.assertIn(r"\section{Section Title}", result)
    
    def test_struct_tex_subsection(self):
        """Test subsection generation."""
        result = _struct_tex("subsection", "Test Subsection", 2)
        self.assertIn(r"\subsection{Test Subsection}", result)
    
    def test_struct_tex_part(self):
        """Test part generation."""
        result = _struct_tex("part", "Part One", 2)
        self.assertIn(r"\part{Part One}", result)
    
    def test_struct_tex_multicol(self):
        """Test multicol generation."""
        result = _struct_tex("multicol", "", 3)
        self.assertIn(r"\begin{multicols}{3}", result)
        self.assertIn(r"\end{multicols}", result)
    
    def test_struct_tex_quote(self):
        """Test quote generation."""
        result = _struct_tex("quote", "", 2)
        self.assertIn(r"\begin{quote}", result)
        self.assertIn(r"\end{quote}", result)
    
    def test_struct_tex_figure(self):
        """Test figure generation."""
        result = _struct_tex("figure", "Test Caption", 2)
        self.assertIn(r"\begin{figure}", result)
        self.assertIn(r"\caption{Test Caption}", result)
        self.assertIn(r"\end{figure}", result)
    
    def test_struct_tex_table(self):
        """Test table generation."""
        result = _struct_tex("table", "Table Caption", 2)
        self.assertIn(r"\begin{table}", result)
        self.assertIn(r"\begin{tabular}", result)
        self.assertIn(r"\end{table}", result)
    
    def test_struct_tex_epigraph(self):
        """Test epigraph generation."""
        result = _struct_tex("epigraph", "Test epigraph text", 2)
        self.assertIn(r"\textit{Test epigraph text}", result)
    
    def test_struct_tex_appendix(self):
        """Test appendix generation."""
        result = _struct_tex("appendix", "", 2)
        self.assertIn(r"\appendix", result)
        self.assertIn(r"\section{Appendix}", result)
    
    def test_struct_tex_unknown_type(self):
        """Test unknown type returns empty string."""
        result = _struct_tex("unknown_type", "", 2)
        self.assertEqual(result, "")
    
    def test_generate_minimal_state(self):
        """Test generate with minimal state."""
        state = {
            "cit_style": "SBL",
            "engine": "xelatex",
            "font_size": "11pt",
            "paper": "letterpaper",
            "title": "Test Title",
            "authors": "Test Author",
        }
        result = generate(state)
        self.assertIsInstance(result, str)
        self.assertIn(r"\documentclass{extarticle}", result)
        self.assertIn("Test Title", result)
        self.assertIn("Test Author", result)
    
    def test_generate_with_bibliography(self):
        """Test generate with bibliography."""
        state = {
            "cit_style": "SBL",
            "engine": "xelatex",
            "font_size": "11pt",
            "paper": "letterpaper",
            "title": "Test",
            "authors": "Author",
            "bib_file": "/path/to/test.bib",
        }
        result = generate(state)
        self.assertIn(r"\addbibresource{/path/to/test.bib}", result)
    
    def test_generate_default_values(self):
        """Test that generate uses sensible defaults."""
        state = {}
        result = generate(state)
        self.assertIn(r"\documentclass{extarticle}", result)
        # Should default to SBL style
        self.assertIn("verbose-note", result)


if __name__ == '__main__':
    unittest.main()
