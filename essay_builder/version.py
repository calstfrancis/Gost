"""
version.py — Version management for Gost.
"""

from essay_builder import __version__

def get_version() -> str:
    return __version__

def get_version_info() -> dict:
    return {
        "version": __version__,
        "name": "Gost",
        "description": "Academic Essay Templater"
    }
