"""
latex_compiler.py — Compile LaTeX documents and handle errors.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger("gost")


class LatexCompiler:
    """Handle LaTeX compilation with error reporting."""
    
    def __init__(self, engine: str = "xelatex"):
        """
        Initialize compiler with specified engine.
        
        Args:
            engine: LaTeX engine to use (pdflatex, xelatex, lualatex)
        """
        self.engine = engine
    
    def compile_tex(
        self, 
        tex_content: str, 
        output_dir: Optional[Path] = None,
        max_runs: int = 2
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Compile LaTeX content to PDF.
        
        Args:
            tex_content: The LaTeX source code as string
            output_dir: Directory for output files (defaults to temp dir)
            max_runs: Maximum number of compilation runs (for references)
            
        Returns:
            Tuple of (success, error_message, pdf_path)
        """
        import shutil
        
        # Check if engine is available
        if not shutil.which(self.engine):
            return False, f"LaTeX engine '{self.engine}' not found in PATH", None
        
        # Create temporary directory if none specified
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="essay_builder_"))
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write tex file
        tex_file = output_dir / "document.tex"
        try:
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(tex_content)
            logger.info(f"Wrote LaTeX file to {tex_file}")
        except Exception as e:
            return False, f"Failed to write .tex file: {e}", None
        
        # Run LaTeX compiler
        pdf_path = output_dir / "document.pdf"
        log_path = output_dir / "document.log"
        
        for run in range(max_runs):
            logger.info(f"Compilation run {run + 1}/{max_runs}")
            
            try:
                result = subprocess.run(
                    [self.engine, '-interaction=nonstopmode', '-file-line-error', 
                     '-output-directory', str(output_dir), str(tex_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    # Extract errors from log
                    error_msg = self._parse_latex_errors(result.stdout + result.stderr)
                    logger.error(f"LaTeX compilation failed: {error_msg}")
                    return False, error_msg, None
                
                if pdf_path.exists():
                    logger.info(f"Successfully compiled PDF to {pdf_path}")
                    return True, "", pdf_path
                    
            except subprocess.TimeoutExpired:
                return False, f"LaTeX compilation timed out after 60 seconds", None
            except Exception as e:
                return False, f"Compilation error: {e}", None
        
        return False, "PDF was not generated after multiple runs", None
    
    def _parse_latex_errors(self, output: str) -> str:
        """
        Parse LaTeX error output to extract meaningful error messages.
        
        Args:
            output: Combined stdout and stderr from LaTeX
            
        Returns:
            Formatted error message
        """
        lines = output.split('\n')
        errors = []
        
        for line in lines:
            line = line.strip()
            # Look for error patterns
            if line.startswith('!'):
                errors.append(line)
            elif 'Error:' in line:
                errors.append(line)
            elif 'Fatal error' in line:
                errors.append(line)
        
        if not errors:
            # If no specific errors found, return last few lines
            errors = lines[-10:] if len(lines) > 10 else lines
        
        return '\n'.join(errors[:5])  # Return first 5 errors
    
    def open_pdf(self, pdf_path: Path) -> Tuple[bool, str]:
        """
        Open PDF with system default viewer.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (success, error_message)
        """
        import subprocess
        import platform
        
        if not pdf_path.exists():
            return False, f"PDF file does not exist: {pdf_path}"
        
        try:
            system = platform.system()
            if system == 'Linux':
                subprocess.run(['xdg-open', str(pdf_path)], check=True)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', str(pdf_path)], check=True)
            elif system == 'Windows':
                subprocess.run(['start', str(pdf_path)], shell=True, check=True)
            else:
                return False, f"Unsupported platform: {system}"
            
            return True, ""
        except Exception as e:
            return False, f"Failed to open PDF: {e}"
