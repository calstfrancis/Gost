#!/usr/bin/env bash
# build-appimage.sh — Build gost-<version>-x86_64.AppImage
# Produces a "thin" AppImage: bundles the Python source and fonts;
# relies on the host's Python 3.10+, PyGObject, GTK4, and libadwaita.
#
# Usage:
#   bash build-appimage.sh           # build
#   bash build-appimage.sh --clean   # remove AppDir and cached appimagetool then build
set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }
step()  { echo -e "\n${BOLD}── $* ──${NC}"; }

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(python3 -c "from essay_builder import __version__; print(__version__)" 2>/dev/null || echo "0.1.5")"
ARCH="$(uname -m)"
APP_ID="ca.calstfrancis.Gost"
APPDIR="${SCRIPT_DIR}/AppDir"
OUTPUT="${SCRIPT_DIR}/gost-${VERSION}-${ARCH}.AppImage"
TOOLS_DIR="${SCRIPT_DIR}/.appimage-tools"
APPIMAGETOOL="${TOOLS_DIR}/appimagetool-${ARCH}.AppImage"
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"

# ── Options ───────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--clean" ]]; then
    warn "Removing AppDir and cached tools..."
    rm -rf "$APPDIR" "$TOOLS_DIR"
fi

# ── Pre-flight checks ─────────────────────────────────────────────────────────
step "Pre-flight checks"

python3 --version >/dev/null 2>&1 || die "python3 not found"

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
    info "Python ${PY_VER}"
else
    die "Python 3.10+ required (found ${PY_VER})"
fi

python3 -c "
import gi
gi.require_version('Gtk','4.0')
gi.require_version('Adw','1')
from gi.repository import Gtk, Adw
" 2>/dev/null || die "GTK4 / libadwaita Python bindings not found. Install python3-gobject + typelib-1_0-Gtk-4_0 + typelib-1_0-Adw-1"
info "GTK4 + libadwaita bindings OK"

# ── Download appimagetool ─────────────────────────────────────────────────────
step "appimagetool"

if [[ ! -x "$APPIMAGETOOL" ]]; then
    info "Downloading appimagetool..."
    mkdir -p "$TOOLS_DIR"
    if command -v wget &>/dev/null; then
        wget -q --show-progress -O "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
    elif command -v curl &>/dev/null; then
        curl -L --progress-bar -o "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
    else
        die "Neither wget nor curl found. Install one and retry."
    fi
    chmod +x "$APPIMAGETOOL"
    info "Downloaded appimagetool"
else
    info "appimagetool already cached"
fi

# ── Build AppDir ──────────────────────────────────────────────────────────────
step "Building AppDir"

rm -rf "$APPDIR"
mkdir -p \
    "${APPDIR}/usr/lib/python" \
    "${APPDIR}/usr/share/applications" \
    "${APPDIR}/usr/share/icons/hicolor/scalable/apps" \
    "${APPDIR}/usr/share/icons/hicolor/symbolic/apps" \
    "${APPDIR}/usr/share/metainfo" \
    "${APPDIR}/usr/share/fonts/gost"

# ── Copy app source ───────────────────────────────────────────────────────────
step "Copying source"

cp -r "${SCRIPT_DIR}/essay_builder" "${APPDIR}/usr/lib/python/"
# Remove __pycache__ to keep the AppImage clean
find "${APPDIR}/usr/lib/python" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
info "Copied essay_builder package"

# ── Bundle python-docx (Word export) ─────────────────────────────────────────
step "Bundling python-docx"
if pip3 install --quiet --break-system-packages --target "${APPDIR}/usr/lib/python" python-docx 2>/dev/null; then
    # Remove tests and dist-info to slim the bundle
    find "${APPDIR}/usr/lib/python" \( -name "*.dist-info" -o -name "*.egg-info" \) \
        -exec rm -rf {} + 2>/dev/null || true
    info "python-docx bundled"
else
    warn "pip3 install python-docx failed — Word export will require python-docx on the host"
fi

# ── Bundled fonts ─────────────────────────────────────────────────────────────
FONT_SRC="${SCRIPT_DIR}/essay_builder/fonts"
shopt -s nullglob
for f in "${FONT_SRC}"/*.ttf "${FONT_SRC}"/*.otf; do
    cp "$f" "${APPDIR}/usr/share/fonts/gost/"
done
shopt -u nullglob
info "Fonts copied"

# ── AppRun ────────────────────────────────────────────────────────────────────
step "AppRun"

cat > "${APPDIR}/AppRun" << 'APPRUN'
#!/usr/bin/env bash
# AppRun — Gost AppImage launcher
set -euo pipefail

HERE="$(dirname "$(readlink -f "$0")")"

# ── Runtime dependency check ──────────────────────────────────────────────────
_check_deps() {
    python3 -c "
import sys, gi
if sys.version_info < (3, 10):
    print('ERROR: Python 3.10+ required (found ' + '.'.join(map(str,sys.version_info[:2])) + ')')
    sys.exit(1)
try:
    gi.require_version('Gtk','4.0')
    gi.require_version('Adw','1')
    from gi.repository import Gtk, Adw
except Exception as e:
    print('ERROR: GTK4/libadwaita not found:', e)
    print()
    print('Install the required packages for your distro:')
    print('  openSUSE:     zypper in python3-gobject typelib-1_0-Gtk-4_0 typelib-1_0-Adw-1')
    print('  Debian/Ubuntu: apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1')
    print('  Fedora:        dnf install python3-gobject gtk4 libadwaita')
    print('  Arch:          pacman -S python-gobject gtk4 libadwaita')
    sys.exit(1)
" || exit 1
}

# ── Environment ───────────────────────────────────────────────────────────────
# Add bundled Python source to PYTHONPATH; system PyGObject stays in system path
export PYTHONPATH="${HERE}/usr/lib/python${PYTHONPATH:+:$PYTHONPATH}"

# Make bundled fonts visible to fontconfig
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"

# ── Launch ────────────────────────────────────────────────────────────────────
_check_deps
exec python3 -m essay_builder.app "$@"
APPRUN

chmod +x "${APPDIR}/AppRun"
info "AppRun created"

# ── Desktop entry ─────────────────────────────────────────────────────────────
step "Desktop entry"

cat > "${APPDIR}/${APP_ID}.desktop" << DESKTOP
[Desktop Entry]
Name=Gost
GenericName=Academic Essay Templater
Comment=Generate LaTeX and Typst templates for academic essays (SBL, Chicago, MLA, APA, ASA, Turabian, Harvard)
Exec=gost
Icon=${APP_ID}
Terminal=false
Type=Application
Categories=Education;Office;
Keywords=latex;tex;typst;essay;academic;bibliography;sbl;chicago;apa;mla;asa;turabian;harvard;sociology;theology;humanities;
StartupNotify=true
StartupWMClass=${APP_ID}
X-AppImage-Name=Gost
X-AppImage-Version=${VERSION}
X-AppImage-Arch=${ARCH}
DESKTOP

cp "${APPDIR}/${APP_ID}.desktop" "${APPDIR}/usr/share/applications/${APP_ID}.desktop"
info "Desktop entry created"

# ── Icons ─────────────────────────────────────────────────────────────────────
step "Icons"

if [[ -f "${SCRIPT_DIR}/icons/gost.svg" ]]; then
    cp "${SCRIPT_DIR}/icons/gost.svg" "${APPDIR}/${APP_ID}.svg"
    cp "${SCRIPT_DIR}/icons/gost.svg" "${APPDIR}/usr/share/icons/hicolor/scalable/apps/${APP_ID}.svg"
    info "SVG icon copied"
else
    die "icons/gost.svg not found — cannot build without an icon"
fi

if [[ -f "${SCRIPT_DIR}/icons/gost-symbolic.svg" ]]; then
    cp "${SCRIPT_DIR}/icons/gost-symbolic.svg" \
        "${APPDIR}/usr/share/icons/hicolor/symbolic/apps/${APP_ID}-symbolic.svg"
fi

# Generate PNG thumbnails for AppImageHub if rsvg-convert is available
if command -v rsvg-convert &>/dev/null; then
    mkdir -p \
        "${APPDIR}/usr/share/icons/hicolor/256x256/apps" \
        "${APPDIR}/usr/share/icons/hicolor/128x128/apps" \
        "${APPDIR}/usr/share/icons/hicolor/64x64/apps"
    for SIZE in 256 128 64; do
        rsvg-convert -w "$SIZE" -h "$SIZE" \
            "${SCRIPT_DIR}/icons/gost.svg" \
            -o "${APPDIR}/usr/share/icons/hicolor/${SIZE}x${SIZE}/apps/${APP_ID}.png"
    done
    # appimagetool needs a .DirIcon at the root
    cp "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png" \
        "${APPDIR}/.DirIcon"
    info "PNG icons generated (256, 128, 64)"
else
    warn "rsvg-convert not found — only SVG icon included (install librsvg2-tools for PNG thumbnails)"
fi

# ── AppStream metainfo ────────────────────────────────────────────────────────
step "AppStream metainfo"

TODAY="$(date +%Y-%m-%d)"

cat > "${APPDIR}/usr/share/metainfo/${APP_ID}.metainfo.xml" << XML
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_ID}</id>
  <name>Gost</name>
  <summary>Academic essay templater for LaTeX and Typst</summary>
  <metadata_license>MIT</metadata_license>
  <project_license>GPL-3.0-or-later</project_license>

  <description>
    <p>
      Gost is a native GTK4 / libadwaita desktop application that generates
      fully-configured LaTeX and Typst essay templates for academic writing.
      It supports SBL, Chicago (Notes), MLA, APA 7th edition, ASA, Turabian,
      and Harvard citation styles, each with correct heading formatting,
      page numbering, and running headers.
    </p>
    <p>Key features:</p>
    <ul>
      <li>Compiled PDF preview via typst or latexmk</li>
      <li>Journal template importer (.cls / .tex / .sty)</li>
      <li>Chapter list with single-file and multi-file project export</li>
      <li>Custom preamble / show-rules editor</li>
      <li>10 journal style packs (JBL, NTS, CBQ, HTR, Turabian, APA, MLA…)</li>
      <li>42-entry CSL style browser for Typst bibliography</li>
      <li>LanguageTool grammar check (public or self-hosted API)</li>
      <li>Language support: Russian, Hebrew, Japanese, Tibetan, Sanskrit, Greek, Chinese</li>
      <li>Template profiles — save and reload named configurations</li>
      <li>Zotero BetterBibTeX integration</li>
    </ul>
  </description>

  <launchable type="desktop-id">${APP_ID}.desktop</launchable>

  <url type="homepage">https://github.com/calstfrancis/gost</url>
  <url type="bugtracker">https://github.com/calstfrancis/gost/issues</url>

  <developer id="ca.calstfrancis">
    <name>Cal St Francis</name>
  </developer>

  <screenshots>
    <screenshot type="default">
      <caption>Main window showing citation style and layout settings</caption>
    </screenshot>
  </screenshots>

  <releases>
    <release version="${VERSION}" date="${TODAY}">
      <description>
        <p>
          Adds ASA, Turabian, and Harvard citation styles; double spacing as default;
          decluttered header bar with hamburger menu; Simple Mode for everyday use;
          hover tooltips throughout; and removal of the sidebar title bar.
        </p>
      </description>
    </release>
  </releases>

  <content_rating type="oars-1.0"/>

  <requires>
    <display_length compare="ge">768</display_length>
  </requires>

  <recommends>
    <control>keyboard</control>
    <control>pointing</control>
  </recommends>

  <supports>
    <control>keyboard</control>
    <control>pointing</control>
  </supports>
</component>
XML

info "AppStream metainfo written"
# appimagetool looks for .appdata.xml; symlink the modern .metainfo.xml name
mkdir -p "${APPDIR}/usr/share/appdata"
ln -sf "../metainfo/${APP_ID}.metainfo.xml" \
    "${APPDIR}/usr/share/appdata/${APP_ID}.appdata.xml"

# ── Pack with appimagetool ────────────────────────────────────────────────────
step "Packing AppImage"

# APPIMAGE_EXTRACT_AND_RUN=1 avoids needing FUSE at build time
# (appimagetool is itself an AppImage)
export APPIMAGE_EXTRACT_AND_RUN=1

if command -v appstream-util &>/dev/null || command -v appstreamcli &>/dev/null; then
    ARCH="$ARCH" "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"
else
    ARCH="$ARCH" "$APPIMAGETOOL" --no-appstream "$APPDIR" "$OUTPUT" 2>/dev/null \
        || ARCH="$ARCH" "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
info "${BOLD}Built: $(basename "$OUTPUT")${NC}  ($(du -sh "$OUTPUT" | cut -f1))"
echo ""
echo "  Test:    ./${OUTPUT##*/}"
echo "  Install: chmod +x ${OUTPUT##*/} && ./${OUTPUT##*/}"
echo ""
echo "  AppImageHub submission:"
echo "  1. Create a GitHub Release tagged v${VERSION}"
echo "  2. Attach ${OUTPUT##*/} to the release assets"
echo "  3. AppImageHub (appimage.github.io) auto-discovers releases"
echo "     — or submit a PR to github.com/AppImage/appimage-catalog"
echo ""
