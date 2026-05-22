"""
app.py — Adw.Application subclass for the Academic Essay Builder.
"""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from essay_builder.window import EssayBuilderWindow
from essay_builder.logger import setup_logging

APP_ID = "ca.calstfrancis.EssayBuilder"
logger = setup_logging()


class EssayBuilderApp(Adw.Application):

    def __init__(self):
        logger.info("Starting Academic Essay Builder")
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        logger.debug("Activating application window")
        win = EssayBuilderWindow(application=app)
        win.present()
        app.add_window(win)


def main():
    logger.info("Launching application")
    app = EssayBuilderApp()
    ret = app.run(sys.argv)
    logger.info(f"Application exited with code {ret}")
    sys.exit(ret)


if __name__ == "__main__":
    main()