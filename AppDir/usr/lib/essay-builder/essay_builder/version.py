"""
version.py — Version management for Academic Essay Builder.
"""

from essay_builder import __version__

def get_version() -> str:
    """Get the current version string."""
    return __version__

def get_version_info() -> dict:
    """Get version information as a dictionary."""
    return {
        "version": __version__,
        "name": "Academic Essay Builder",
        "description": "LaTeX essay template generator"
    }
