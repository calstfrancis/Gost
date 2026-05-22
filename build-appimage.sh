#!/usr/bin/env bash
# build-appimage.sh — Build an AppImage for Gost
#
# Requirements on the build machine:
#   - appimagetool (or it will be downloaded to /tmp)
#   - python3 (to verify the app module is importable)
#   - rsvg-convert (optional, for PNG icon generation)
#
# The resulting AppImage uses the *system* GTK4 and libadwaita on the target
# machine. It bundles only the Python application code.
# Target system requirements: python3-gobject, typelib-Gtk-4.0, typelib-Adw-1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="gost"
APP_VERSION="1.2.0"
APP_ID="ca.calstfrancis.Gost"
ARCH="${ARCH:-x86_64}"
APPIMAGE_NAME="${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
APPDIR="${SCRIPT_DIR}/AppDir"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }

echo ""
echo "  Gost — AppImage Builder"
echo "  ========================"
echo ""

# ----------------------------------------------------------------
# Locate or download appimagetool
# ----------------------------------------------------------------
if command -v appimagetool &>/dev/null; then
    APPIMAGETOOL="appimagetool"
    info "Found appimagetool: $(command -v appimagetool)"
else
    APPIMAGETOOL_BIN="/tmp/appimagetool-${ARCH}.AppImage"
    if [[ ! -x "$APPIMAGETOOL_BIN" ]]; then
        warn "appimagetool not found in PATH. Downloading to /tmp ..."
        APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
        curl -fsSL -o "$APPIMAGETOOL_BIN" "$APPIMAGETOOL_URL"
        chmod +x "$APPIMAGETOOL_BIN"
        info "Downloaded appimagetool."
    else
        info "Using cached appimagetool at ${APPIMAGETOOL_BIN}."
    fi
    APPIMAGETOOL="$APPIMAGETOOL_BIN"
fi

# ----------------------------------------------------------------
# Sanity check: make sure the app module exists
# ----------------------------------------------------------------
if [[ ! -d "${SCRIPT_DIR}/essay_builder" ]]; then
    die "essay_builder/ not found in ${SCRIPT_DIR}. Run this from the repo root."
fi

# ----------------------------------------------------------------
# Clean previous build
# ----------------------------------------------------------------
info "Cleaning previous AppDir build..."
rm -rf "$APPDIR"

# ----------------------------------------------------------------
# Create AppDir directory structure
# ----------------------------------------------------------------
info "Creating AppDir structure..."
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib/gost"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${APPDIR}/usr/share/metainfo"
mkdir -p "${APPDIR}/fonts"
mkdir -p "${APPDIR}/etc/fonts"

# ----------------------------------------------------------------
# Copy application source
# ----------------------------------------------------------------
info "Copying application files..."
cp -r "${SCRIPT_DIR}/essay_builder" "${APPDIR}/usr/lib/gost/"
# Strip bytecode cache — AppImage will regenerate on first run
find "${APPDIR}/usr/lib/gost" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ----------------------------------------------------------------
# Bundle fonts
# ----------------------------------------------------------------
info "Bundling fonts..."
FONT_SRC="${SCRIPT_DIR}/essay_builder/fonts"
FONT_COUNT=0
if [[ -d "$FONT_SRC" ]]; then
    for f in "${FONT_SRC}"/*.ttf "${FONT_SRC}"/*.otf; do
        [[ -f "$f" ]] && cp "$f" "${APPDIR}/fonts/" && FONT_COUNT=$((FONT_COUNT+1))
    done
fi
if [[ $FONT_COUNT -gt 0 ]]; then
    # Write a fontconfig that includes the bundled fonts dir + the system config
    cat > "${APPDIR}/etc/fonts/fonts.conf" << 'FONTCONF_EOF'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <!-- Bundled fonts (path resolved by AppRun at launch time) -->
  <dir>__APPDIR_FONTS__</dir>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
</fontconfig>
FONTCONF_EOF
    info "Bundled ${FONT_COUNT} font file(s)."
else
    warn "No .ttf/.otf files found in ${FONT_SRC} — font will not be bundled."
    warn "Place font files in essay_builder/fonts/ before building."
fi

# ----------------------------------------------------------------
# AppRun entry point
# ----------------------------------------------------------------
info "Creating AppRun..."
cat > "${APPDIR}/AppRun" << 'APPRUN_EOF'
#!/usr/bin/env bash
SELF="$(readlink -f "$0")"
HERE="$(dirname "$SELF")"

# Prepend the bundled Python modules
export PYTHONPATH="${HERE}/usr/lib/gost${PYTHONPATH:+:$PYTHONPATH}"

# ---- Bundled fonts via fontconfig ----
# If the AppImage ships fonts, point fontconfig at them before Pango starts.
BUNDLED_FONTCONF="${HERE}/etc/fonts/fonts.conf"
if [[ -f "$BUNDLED_FONTCONF" ]]; then
    # Resolve the __APPDIR_FONTS__ placeholder to the real path
    RUNTIME_FONTCONF="${XDG_RUNTIME_DIR:-/tmp}/gost-fonts-$$.conf"
    sed "s|__APPDIR_FONTS__|${HERE}/fonts|g" "$BUNDLED_FONTCONF" > "$RUNTIME_FONTCONF"
    export FONTCONFIG_FILE="$RUNTIME_FONTCONF"
    trap "rm -f '$RUNTIME_FONTCONF'" EXIT
fi

# Verify GTK4 and libadwaita are available on this system
if ! python3 -c "
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
" 2>/dev/null; then
    MSG="GTK4 and libadwaita (libadwaita >= 1.4) are required.\n\nInstall: python3-gobject typelib-1_0-Gtk-4_0 typelib-1_0-Adw-1"
    if command -v zenity &>/dev/null; then
        zenity --error --title="Missing dependency" --text="$MSG" 2>/dev/null
    else
        echo -e "ERROR: $MSG" >&2
    fi
    exit 1
fi

exec python3 -m essay_builder.app "$@"
APPRUN_EOF
chmod +x "${APPDIR}/AppRun"

# ----------------------------------------------------------------
# Desktop entry (must be at AppDir root and in usr/share/applications)
# ----------------------------------------------------------------
info "Writing desktop entry..."
cat > "${APPDIR}/${APP_ID}.desktop" << DESKTOP_EOF
[Desktop Entry]
Name=Gost
GenericName=Academic Essay Templater
Comment=Generate LaTeX and Typst templates for academic essays
Exec=AppRun
Icon=gost
Terminal=false
Type=Application
Categories=Education;Office;
Keywords=latex;tex;typst;essay;academic;bibliography;
StartupNotify=true
StartupWMClass=${APP_ID}
DESKTOP_EOF
cp "${APPDIR}/${APP_ID}.desktop" "${APPDIR}/usr/share/applications/"

# ----------------------------------------------------------------
# Icon
# ----------------------------------------------------------------
info "Installing icon..."
SVG_SRC="${SCRIPT_DIR}/icons/gost.svg"

if [[ -f "$SVG_SRC" ]]; then
    cp "$SVG_SRC" "${APPDIR}/usr/share/icons/hicolor/scalable/apps/gost.svg"

    if command -v rsvg-convert &>/dev/null; then
        rsvg-convert -w 256 -h 256 "$SVG_SRC" \
            > "${APPDIR}/usr/share/icons/hicolor/256x256/apps/gost.png"
        cp "${APPDIR}/usr/share/icons/hicolor/256x256/apps/gost.png" \
           "${APPDIR}/gost.png"
        info "PNG icon generated (256×256)."
    else
        warn "rsvg-convert not found; appimagetool will use the SVG directly."
        cp "$SVG_SRC" "${APPDIR}/gost.svg"
    fi
else
    warn "Icon not found at ${SVG_SRC} — AppImage will have no icon."
fi

# ----------------------------------------------------------------
# AppStream metainfo (optional but good practice)
# ----------------------------------------------------------------
cat > "${APPDIR}/usr/share/metainfo/${APP_ID}.metainfo.xml" << META_EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_ID}</id>
  <name>Gost</name>
  <summary>Academic Essay Templater — LaTeX and Typst</summary>
  <description>
    <p>
      A native GTK4 / libadwaita desktop app for generating academic essay
      templates in LaTeX (extarticle) or Typst. Supports SBL, Chicago, MLA,
      and APA citation styles, configurable layout, and Zotero integration.
    </p>
  </description>
  <url type="homepage">https://github.com/calstfrancis/gost</url>
  <releases>
    <release version="${APP_VERSION}" date="$(date +%Y-%m-%d)"/>
  </releases>
</component>
META_EOF

# ----------------------------------------------------------------
# Build the AppImage
# ----------------------------------------------------------------
info "Running appimagetool..."
cd "${SCRIPT_DIR}"
# APPIMAGE_EXTRACT_AND_RUN=1 lets appimagetool (itself an AppImage) run without FUSE
ARCH="${ARCH}" APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" "${APPDIR}" "${APPIMAGE_NAME}"

echo ""
info "AppImage created: ${SCRIPT_DIR}/${APPIMAGE_NAME}"
echo ""
echo "  System requirements on the target machine:"
echo "    python3-gobject   (PyGObject bindings)"
echo "    typelib-1_0-Gtk-4_0"
echo "    typelib-1_0-Adw-1  (libadwaita >= 1.4)"
echo ""
echo "  Run directly:"
echo "    chmod +x ${APPIMAGE_NAME}"
echo "    ./${APPIMAGE_NAME}"
echo ""
echo "  Or install via Gear Lever for desktop integration."
echo ""
