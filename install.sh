#!/usr/bin/env bash
# install.sh — install Gost
set -euo pipefail

INSTALL_DIR="/usr/local/lib/gost"
BIN_LINK="/usr/local/bin/gost"
DESKTOP_DIR="/usr/local/share/applications"
ICON_DIR_BASE="/usr/local/share/icons/hicolor"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }

echo ""
echo "  Gost — Academic Essay Templater — installer"
echo "  ============================================"
echo ""

if [[ "$EUID" -eq 0 ]]; then
    die "Do not run this script as root. It will sudo only when needed."
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ------------------------------------------------------------
# Check dependencies
# ------------------------------------------------------------
info "Checking Python & GTK dependencies..."

MISSING=()
python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" \
    2>/dev/null || MISSING+=("python3-gobject / typelib-1_0-Gtk-4_0")

python3 -c "import gi; gi.require_version('Adw','1'); from gi.repository import Adw" \
    2>/dev/null || MISSING+=("typelib-1_0-Adw-1 / libadwaita")

if [[ ${#MISSING[@]} -gt 0 ]]; then
    warn "Missing dependencies:"
    for m in "${MISSING[@]}"; do
        echo "       $m"
    done
    echo ""
    read -rp "  Install them now with zypper? [Y/n] " answer
    answer="${answer:-Y}"
    if [[ "$answer" =~ ^[Yy] ]]; then
        sudo zypper install --no-confirm \
            python3-gobject \
            python3-gobject-Gdk \
            typelib-1_0-Gtk-4_0 \
            typelib-1_0-Adw-1 \
            libadwaita \
            librsvg \
            gtk4-tools
    else
        die "Cannot install without required dependencies."
    fi
fi

# ------------------------------------------------------------
# Install Python package
# ------------------------------------------------------------
info "Installing application to ${INSTALL_DIR}..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r "$SCRIPT_DIR/essay_builder" "$INSTALL_DIR/"
sudo chmod -R 644 "$INSTALL_DIR/essay_builder/"*
sudo find "$INSTALL_DIR/essay_builder" -type d -exec chmod 755 {} \;

# ------------------------------------------------------------
# Create launcher
# ------------------------------------------------------------
info "Creating launcher at ${BIN_LINK}..."
sudo tee "$BIN_LINK" > /dev/null << 'LAUNCHER'
#!/usr/bin/env bash
export PYTHONPATH="/usr/local/lib/gost${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m essay_builder.app "$@"
LAUNCHER
sudo chmod 755 "$BIN_LINK"

# ------------------------------------------------------------
# Install icons
# ------------------------------------------------------------
info "Installing icons..."
sudo mkdir -p "${ICON_DIR_BASE}/scalable/apps"
sudo mkdir -p "${ICON_DIR_BASE}/symbolic/apps"

if [[ -f "$SCRIPT_DIR/icons/gost.svg" ]]; then
    sudo cp "$SCRIPT_DIR/icons/gost.svg" \
        "${ICON_DIR_BASE}/scalable/apps/gost.svg"
else
    warn "gost.svg not found – will show generic icon"
fi

if [[ -f "$SCRIPT_DIR/icons/gost-symbolic.svg" ]]; then
    sudo cp "$SCRIPT_DIR/icons/gost-symbolic.svg" \
        "${ICON_DIR_BASE}/symbolic/apps/gost-symbolic.svg"
fi

if command -v rsvg-convert &>/dev/null && [[ -f "$SCRIPT_DIR/icons/gost.svg" ]]; then
    for SIZE in 16 32 48 64 128 256; do
        sudo mkdir -p "${ICON_DIR_BASE}/${SIZE}x${SIZE}/apps"
        rsvg-convert -w "$SIZE" -h "$SIZE" \
            "$SCRIPT_DIR/icons/gost.svg" \
            | sudo tee "${ICON_DIR_BASE}/${SIZE}x${SIZE}/apps/gost.png" \
            > /dev/null
    done
    info "PNG icons generated."
else
    warn "rsvg-convert not found or SVG missing; only scalable icon installed."
fi

if command -v gtk4-update-icon-cache &>/dev/null; then
    sudo gtk4-update-icon-cache -f -t "${ICON_DIR_BASE}" 2>/dev/null || true
elif command -v gtk-update-icon-cache &>/dev/null; then
    sudo gtk-update-icon-cache -f -t "${ICON_DIR_BASE}" 2>/dev/null || true
fi

# ------------------------------------------------------------
# Install .desktop file
# ------------------------------------------------------------
info "Installing desktop entry..."
sudo mkdir -p "$DESKTOP_DIR"
if [[ -f "$SCRIPT_DIR/gost.desktop" ]]; then
    sudo cp "$SCRIPT_DIR/gost.desktop" "${DESKTOP_DIR}/gost.desktop"
else
    sudo tee "${DESKTOP_DIR}/gost.desktop" > /dev/null << 'DESKTOP'
[Desktop Entry]
Name=Gost
GenericName=Academic Essay Templater
Comment=Generate LaTeX and Typst templates for academic essays
Exec=/usr/local/bin/gost
Icon=gost
Terminal=false
Type=Application
Categories=Education;Office;
Keywords=latex;tex;typst;essay;academic;bibliography;
StartupNotify=true
StartupWMClass=ca.astheology.Gost
DESKTOP
fi
sudo chmod 644 "${DESKTOP_DIR}/gost.desktop"

if command -v update-desktop-database &>/dev/null; then
    sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------
echo ""
info "Installation complete."
echo ""
echo "  Run from terminal:    gost"
echo "  Or find it in your GNOME application launcher."
echo ""

read -rp "  Launch now? [Y/n] " launch
launch="${launch:-Y}"
if [[ "$launch" =~ ^[Yy] ]]; then
    nohup gost &>/dev/null &
fi
