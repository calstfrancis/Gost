"""Post-install helper for pipx / pip users: installs the .desktop file and icons."""

import importlib.resources
import shutil
import subprocess
import sys
from pathlib import Path


DESKTOP_ENTRY = """\
[Desktop Entry]
Name=Gost
GenericName=Academic Essay Templater
Comment=Generate LaTeX and Typst templates for academic essays
Exec=gost
Icon=ca.calstfrancis.Gost
Terminal=false
Type=Application
Categories=Education;Office;
Keywords=latex;tex;typst;essay;academic;bibliography;sbl;chicago;apa;mla;
StartupNotify=true
StartupWMClass=ca.calstfrancis.Gost
"""

ICON_MAP = {
    "gost.svg": Path("hicolor/scalable/apps/ca.calstfrancis.Gost.svg"),
    "gost-symbolic.svg": Path("hicolor/symbolic/apps/ca.calstfrancis.Gost-symbolic.svg"),
}


def _pkg_icon(name: str) -> bytes | None:
    try:
        ref = importlib.resources.files("essay_builder").joinpath(name)
        return ref.read_bytes()
    except (FileNotFoundError, TypeError):
        return None


def main() -> None:
    local_share = Path.home() / ".local" / "share"

    # --- desktop file ---
    apps_dir = local_share / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    desktop_path = apps_dir / "ca.calstfrancis.Gost.desktop"
    desktop_path.write_text(DESKTOP_ENTRY)
    print(f"Installed desktop entry → {desktop_path}")

    # --- icons ---
    icons_base = local_share / "icons"
    installed_any = False
    for src_name, rel_dest in ICON_MAP.items():
        data = _pkg_icon(src_name)
        if data is None:
            print(f"  Warning: {src_name} not found in package, skipping.", file=sys.stderr)
            continue
        dest = icons_base / rel_dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"Installed icon          → {dest}")
        installed_any = True

    # --- refresh caches ---
    if installed_any:
        for cmd in ("gtk4-update-icon-cache", "gtk-update-icon-cache"):
            if shutil.which(cmd):
                subprocess.run(
                    [cmd, "-f", "-t", str(icons_base / "hicolor")],
                    capture_output=True,
                )
                break

    if shutil.which("update-desktop-database"):
        subprocess.run(
            ["update-desktop-database", str(apps_dir)],
            capture_output=True,
        )

    print("\nDone. Gost should now appear in your application launcher.")
    print("If it doesn't appear immediately, try logging out and back in.")
