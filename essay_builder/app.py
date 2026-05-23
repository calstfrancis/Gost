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
from gi.repository import Adw, GLib, Gio, Gtk, Gdk

from essay_builder.window import GostWindow
from essay_builder.logger import setup_logging

APP_ID = "ca.calstfrancis.Gost"
logger = setup_logging()

# Project root when running from the source tree
_SRC_ROOT = Path(__file__).parent.parent


def _register_icon_theme(display) -> None:
    """Add the bundled icons/hicolor tree to the icon theme for this process."""
    if display is None:
        return
    icons_root = _SRC_ROOT / "icons"
    if (icons_root / "hicolor").is_dir():
        Gtk.IconTheme.get_for_display(display).add_search_path(str(icons_root))
        logger.debug("Registered bundled icon theme path: %s", icons_root)


def _ensure_desktop_integration() -> None:
    """
    Install the .desktop entry and icons to ~/.local/share/ the first time the
    app is launched from the source tree.  This makes the panel icon and app
    launcher work without requiring a system-wide install.  Silently skips when
    running from an AppImage or a system install (source files not present).
    """
    desktop_src = _SRC_ROOT / "gost.desktop"
    icon_src    = _SRC_ROOT / "icons" / "gost.svg"
    sym_src     = _SRC_ROOT / "icons" / "gost-symbolic.svg"

    if not desktop_src.exists() or not icon_src.exists():
        return  # not running from source tree

    xdg_data  = Path.home() / ".local" / "share"
    apps_dir  = xdg_data / "applications"
    scalable  = xdg_data / "icons" / "hicolor" / "scalable" / "apps"
    symbolic  = xdg_data / "icons" / "hicolor" / "symbolic"  / "apps"

    def _needs_update(src: Path, dst: Path) -> bool:
        return not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime

    changed = False

    dst_icon = scalable / "ca.calstfrancis.Gost.svg"
    if _needs_update(icon_src, dst_icon):
        scalable.mkdir(parents=True, exist_ok=True)
        shutil.copy2(icon_src, dst_icon)
        changed = True
        logger.debug("Installed icon to %s", dst_icon)

    if sym_src.exists():
        dst_sym = symbolic / "ca.calstfrancis.Gost-symbolic.svg"
        if _needs_update(sym_src, dst_sym):
            symbolic.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sym_src, dst_sym)
            changed = True

    dst_desktop = apps_dir / "ca.calstfrancis.Gost.desktop"
    if _needs_update(desktop_src, dst_desktop):
        apps_dir.mkdir(parents=True, exist_ok=True)
        lines = desktop_src.read_text().splitlines()
        patched = []
        for line in lines:
            if line.startswith("Exec="):
                # Point directly at the source tree so launching from the
                # GNOME app menu works even without a system install.
                patched.append(
                    f"Exec=env PYTHONPATH={_SRC_ROOT} python3 -m essay_builder.app"
                )
            else:
                patched.append(line)
        dst_desktop.write_text("\n".join(patched) + "\n")
        changed = True
        logger.debug("Installed desktop entry to %s", dst_desktop)

    if changed:
        icons_hicolor = xdg_data / "icons" / "hicolor"
        for cmd in (
            ["gtk-update-icon-cache", "-f", "-t", str(icons_hicolor)],
            ["update-desktop-database", str(apps_dir)],
        ):
            subprocess.run(cmd, capture_output=True, timeout=5)

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
        _ensure_desktop_integration()
        _register_icon_theme(Gdk.Display.get_default())
        win = GostWindow(application=app)
        win.present()
        app.add_window(win)
        if self._fonts_newly_installed:
            GLib.timeout_add(600, win.notify_fonts_installed)


def _ensure_desktop_integration() -> None:
    desktop = Path.home() / ".local/share/applications/ca.calstfrancis.Gost.desktop"
    if desktop.exists():
        return
    try:
        from essay_builder.setup_desktop import main as _setup
        _setup()
    except Exception:
        pass


def main():
    _ensure_desktop_integration()
    logger.info("Launching application")
    app = GostApp()
    ret = app.run(sys.argv)
    logger.info(f"Application exited with code {ret}")
    sys.exit(ret)


if __name__ == "__main__":
    main()
