"""
app.py — Adw.Application subclass for Gost.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gio

from essay_builder.window import GostWindow
from essay_builder.logger import setup_logging

APP_ID = "ca.calstfrancis.Gost"
logger = setup_logging()

# Fonts directory bundled alongside this module
_BUNDLED_FONTS_DIR = Path(__file__).parent / "fonts"
_USER_FONTS_DIR = Path.home() / ".local" / "share" / "fonts" / "gost"


def setup_bundled_fonts() -> bool:
    """Copy bundled fonts to the user font dir if newer or missing.

    Returns True if any font was newly installed (restart recommended).
    """
    if not _BUNDLED_FONTS_DIR.exists():
        return False

    font_files = list(_BUNDLED_FONTS_DIR.glob("*.ttf")) + list(_BUNDLED_FONTS_DIR.glob("*.otf"))
    if not font_files:
        return False

    _USER_FONTS_DIR.mkdir(parents=True, exist_ok=True)
    installed_any = False

    for src in font_files:
        dst = _USER_FONTS_DIR / src.name
        if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(src, dst)
            installed_any = True
            logger.info(f"Installed bundled font: {src.name}")

    if installed_any:
        subprocess.run(["fc-cache", "-f", str(_USER_FONTS_DIR)],
                       capture_output=True, timeout=15)

    return installed_any


class GostApp(Adw.Application):

    def __init__(self):
        logger.info("Starting Gost")
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self._fonts_newly_installed = setup_bundled_fonts()
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        logger.debug("Activating application window")
        win = GostWindow(application=app)
        win.present()
        app.add_window(win)
        if self._fonts_newly_installed:
            GLib.timeout_add(600, win.notify_fonts_installed)


def main():
    logger.info("Launching application")
    app = GostApp()
    ret = app.run(sys.argv)
    logger.info(f"Application exited with code {ret}")
    sys.exit(ret)


if __name__ == "__main__":
    main()
