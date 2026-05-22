#!/usr/bin/env python3
"""debug_launch.py — run this to find exactly where essay_builder dies."""
import sys, os

print("step 1: python running", flush=True)

import gi
print("step 2: gi imported", flush=True)

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
print("step 3: versions required", flush=True)

from gi.repository import Gtk, Adw, Gdk, GLib, Gio
print("step 4: all gi imports ok", flush=True)

sys.path.insert(0, "/usr/local/lib/gost")
from texgen import generate, STYLE_DEFAULTS
print("step 5: texgen imported", flush=True)

APP_ID = "ca.astheology.Gost"

class TestApp(Adw.Application):
    def __init__(self):
        print("step 6: TestApp.__init__", flush=True)
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.connect("activate", self._activate)
        print("step 7: activate connected", flush=True)

    def _activate(self, app):
        print("step 8: activate fired", flush=True)
        win = Adw.ApplicationWindow(application=app)
        print("step 9: window created", flush=True)
        win.set_default_size(400, 300)
        win.set_title("Debug Test")
        win.present()
        print("step 10: window presented — if you see this, the crash is in the full UI build", flush=True)

print("step 6a: creating app", flush=True)
app = TestApp()
print("step 6b: running app", flush=True)
ret = app.run(sys.argv)
print(f"step 11: app exited with {ret}", flush=True)
sys.exit(ret)
