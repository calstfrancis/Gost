"""
validators.py — Input validation for Gost.
"""

import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger("gost")


def validate_bibliography_file(bib_path: str) -> Tuple[bool, str]:
    """
    Validate that a bibliography file exists and has valid content.
    
    Args:
        bib_path: Path to the .bib file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not bib_path or not bib_path.strip():
        return True, ""  # Empty path is allowed (optional bibliography)
    
    path = Path(bib_path)
    
    # Check if file exists
    if not path.exists():
        return False, f"Bibliography file does not exist: {bib_path}"
    
    # Check if it's a file (not a directory)
    if not path.is_file():
        return False, f"Path is not a file: {bib_path}"
    
    # Check file extension
    if path.suffix.lower() not in ['.bib', '.bibtex']:
        logger.warning(f"Bibliography file has unusual extension: {path.suffix}")
    
    # Check if file is readable
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # Read first 1000 chars
            if not content.strip():
                return False, "Bibliography file is empty"
            
            # Basic BibTeX validation - check for @article, @book, etc.
            if not any(keyword in content for keyword in ['@article', '@book', '@inproceedings', 
                                                          '@misc', '@phdthesis', '@mastersthesis']):
                logger.warning(f"Bibliography file may not be valid BibTeX: {bib_path}")
    except UnicodeDecodeError:
        return False, "Bibliography file is not valid UTF-8"
    except Exception as e:
        return False, f"Error reading bibliography file: {e}"
    
    return True, ""


def validate_latex_command(engine: str) -> Tuple[bool, str]:
    """
    Validate that the LaTeX engine is available.
    
    Args:
        engine: The LaTeX engine (pdflatex, xelatex, lualatex)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import shutil
    
    valid_engines = ['pdflatex', 'xelatex', 'lualatex']
    if engine not in valid_engines:
        return False, f"Invalid engine: {engine}. Must be one of {valid_engines}"
    
    # Check if the command exists
    if not shutil.which(engine):
        return False, f"LaTeX engine '{engine}' is not installed or not in PATH"
    
    return True, ""


def validate_output_path(output_path: str) -> Tuple[bool, str]:
    """
    Validate that the output path is writable.
    
    Args:
        output_path: Path where the .tex file will be saved
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not output_path or not output_path.strip():
        return False, "Output path cannot be empty"
    
    path = Path(output_path)
    
    # Check if parent directory exists
    if not path.parent.exists():
        return False, f"Parent directory does not exist: {path.parent}"
    
    # Check if parent directory is writable
    if not path.parent.is_dir():
        return False, f"Parent path is not a directory: {path.parent}"
    
    try:
        # Try to create a test file
        test_file = path.parent / ".essay_builder_test"
        test_file.touch()
        test_file.unlink()
    except PermissionError:
        return False, f"Parent directory is not writable: {path.parent}"
    except Exception as e:
        return False, f"Error checking write permissions: {e}"
    
    # Check file extension
    if path.suffix.lower() != '.tex':
        logger.warning(f"Output file has non-standard extension: {path.suffix}")
    
    return True, ""
