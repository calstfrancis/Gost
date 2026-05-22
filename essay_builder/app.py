"""
app.py — Adw.Application subclass for Gost.
"""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from essay_builder.window import GostWindow
from essay_builder.logger import setup_logging

APP_ID = "ca.astheology.Gost"
logger = setup_logging()


class GostApp(Adw.Application):

    def __init__(self):
        logger.info("Starting Gost")
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        logger.debug("Activating application window")
        win = GostWindow(application=app)
        win.present()
        app.add_window(win)


def main():
    logger.info("Launching application")
    app = GostApp()
    ret = app.run(sys.argv)
    logger.info(f"Application exited with code {ret}")
    sys.exit(ret)


if __name__ == "__main__":
    main()