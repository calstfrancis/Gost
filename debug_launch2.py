#!/usr/bin/env python3
"""debug_launch2.py — builds the full UI with visible error output."""
import sys, traceback

sys.path.insert(0, "/usr/local/lib/gost")

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GLib, Gio

from texgen import generate, STYLE_DEFAULTS

APP_ID = "ca.astheology.Gost.Debug"

class TestApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.connect("activate", self._activate)

    def _activate(self, app):
        print("activate fired — building UI...", flush=True)
        try:
            # Import and instantiate the real window
            from essay_builder.window import GostWindow
            win = GostWindow(application=app)
            win.present()
            print("window presented OK", flush=True)
        except Exception:
            traceback.print_exc()
            app.quit()

app = TestApp()
sys.exit(app.run(sys.argv))
