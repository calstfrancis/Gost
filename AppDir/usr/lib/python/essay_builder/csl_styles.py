"""
csl_styles.py — Curated list of CSL style IDs for Typst bibliography.
Typst accepts these directly in #bibliography(style: "...").
"""

from typing import List, Tuple

# (Display name, Typst CSL style ID)
CSL_STYLES: List[Tuple[str, str]] = [
    # Theology / Humanities
    ("SBL Fullnotes",                         "society-of-biblical-literature-fullnotes"),
    ("Chicago Notes (Fullnotes)",              "chicago-fullnotes"),
    ("Chicago Notes",                          "chicago-notes"),
    ("Chicago Author-Date",                    "chicago-author-date"),
    ("Turabian Fullnotes",                     "turabian-fullnotes"),
    ("Turabian Author-Date",                   "turabian-author-date"),
    ("MHRA (Modern Humanities Research Assoc.)", "modern-humanities-research-association"),
    # Social Science
    ("APA 7th Edition",                        "apa"),
    ("MLA 9th Edition",                        "modern-language-association"),
    ("MLA 8th Edition",                        "modern-language-association-8"),
    ("Harvard (Cite Them Right)",              "harvard-cite-them-right"),
    ("American Political Science Association", "american-political-science-association"),
    # Law
    ("Legal Bluebook",                         "legal-bluebook"),
    # Sciences
    ("IEEE",                                   "ieee"),
    ("Vancouver",                              "vancouver"),
    ("Nature",                                 "nature"),
    ("The Lancet",                             "the-lancet"),
    ("American Medical Association (AMA)",     "american-medical-association"),
    ("American Chemical Society (ACS)",        "american-chemical-society"),
    ("American Geophysical Union (AGU)",       "american-geophysical-union"),
    ("American Meteorological Society (AMS)",  "american-meteorological-society"),
    ("American Physical Society (APS)",        "american-physics-society"),
    ("American Society of Civil Engineers",    "american-society-of-civil-engineers"),
    ("American Society of Mechanical Eng.",    "american-society-of-mechanical-engineers"),
    ("Council of Science Editors (CSE)",       "council-of-science-editors"),
    ("Current Biology",                        "current-biology"),
    ("Institute of Mathematical Statistics",   "institute-of-mathematical-statistics"),
    ("Journal of Audio Engineering Society",   "journal-of-the-audio-engineering-society"),
    ("MDPI",                                   "multidisciplinary-digital-publishing-institute"),
    ("Pensoft",                                "pensoft"),
    ("Royal Society of Chemistry (RSC)",       "royal-society-of-chemistry"),
    ("SAGE Vancouver",                         "sage-vancouver"),
    ("SPIE Proceedings",                       "spie-proceedings"),
    ("Springer (Basic Author-Date)",           "springer-basic-author-date"),
    ("Springer MathPhys",                      "springer-mathphys"),
    ("Springer Socpsych Author-Date",          "springer-socpsych-author-date"),
    ("WHO (World Health Organization)",        "world-health-organization"),
    # Chinese
    ("GB/T 7714-2015 Author-Date",             "gb-7714-2015-author-date"),
    ("GB/T 7714-2015 Note",                    "gb-7714-2015-note"),
    ("GB/T 7714-2015 Numeric",                 "gb-7714-2015-numeric"),
    # Minimal / Fallback
    ("Minimal",                                "minimal"),
    ("Copernicus Publications",                "copernicus-publications"),
]
