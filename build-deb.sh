#!/usr/bin/env bash
# build-deb.sh — Build gost_<version>_all.deb
# Requires: dpkg-deb (dpkg-dev package on Debian/Ubuntu)
#
# Usage (run on a Debian/Ubuntu/Mint system):
#   bash build-deb.sh
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }
step()  { echo -e "\n${BOLD}── $* ──${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(python3 -c "from essay_builder import __version__; print(__version__)" 2>/dev/null || echo "0.1.9")"
DEBROOT="${SCRIPT_DIR}/.debuild/gost_${VERSION}"
OUTPUT="${SCRIPT_DIR}/gost_${VERSION}_all.deb"

step "Pre-flight checks"
command -v dpkg-deb &>/dev/null || die "dpkg-deb not found. Install dpkg-dev: apt install dpkg-dev"
info "dpkg-deb OK"

step "Staging package tree"
rm -rf "$DEBROOT"
mkdir -p "${DEBROOT}/DEBIAN"
mkdir -p "${DEBROOT}/usr/share/gost"
mkdir -p "${DEBROOT}/usr/bin"
mkdir -p "${DEBROOT}/usr/share/applications"
mkdir -p "${DEBROOT}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${DEBROOT}/usr/share/icons/hicolor/symbolic/apps"
mkdir -p "${DEBROOT}/usr/share/fonts/gost"
mkdir -p "${DEBROOT}/usr/share/doc/gost"

# Python package
cp -r "${SCRIPT_DIR}/essay_builder" "${DEBROOT}/usr/share/gost/"
find "${DEBROOT}/usr/share/gost" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Fonts
for f in "${SCRIPT_DIR}/essay_builder/fonts"/*.ttf "${SCRIPT_DIR}/essay_builder/fonts"/*.otf; do
    [[ -f "$f" ]] && cp "$f" "${DEBROOT}/usr/share/fonts/gost/"
done

# Launcher
cat > "${DEBROOT}/usr/bin/gost" << 'LAUNCHER'
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/gost${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m essay_builder.app "$@"
LAUNCHER
chmod 755 "${DEBROOT}/usr/bin/gost"

# Desktop entry
cp "${SCRIPT_DIR}/gost.desktop" \
    "${DEBROOT}/usr/share/applications/ca.calstfrancis.Gost.desktop"

# Icons
cp "${SCRIPT_DIR}/icons/gost.svg" \
    "${DEBROOT}/usr/share/icons/hicolor/scalable/apps/ca.calstfrancis.Gost.svg"
[[ -f "${SCRIPT_DIR}/icons/gost-symbolic.svg" ]] && \
    cp "${SCRIPT_DIR}/icons/gost-symbolic.svg" \
       "${DEBROOT}/usr/share/icons/hicolor/symbolic/apps/ca.calstfrancis.Gost-symbolic.svg"

# Docs
cp "${SCRIPT_DIR}/README.md" "${DEBROOT}/usr/share/doc/gost/"
cp "${SCRIPT_DIR}/CHANGELOG.md" "${DEBROOT}/usr/share/doc/gost/"
cp "${SCRIPT_DIR}/HELP.md" "${DEBROOT}/usr/share/doc/gost/" 2>/dev/null || true
gzip -9 "${DEBROOT}/usr/share/doc/gost/CHANGELOG.md"

info "Package tree staged"

step "Writing DEBIAN/control"
cat > "${DEBROOT}/DEBIAN/control" << CONTROL
Package: gost
Version: ${VERSION}
Architecture: all
Maintainer: Cal St Francis <calstfrancis@gmail.com>
Installed-Size: $(du -sk "${DEBROOT}" | cut -f1)
Depends: python3 (>= 3.10), python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1
Recommends: typst, texlive-latexmk, poppler-utils, python3-docx
Section: text
Priority: optional
Homepage: https://github.com/calstfrancis/gost
Description: Academic essay templater for LaTeX and Typst
 Gost is a native GTK4 / libadwaita desktop application for generating
 fully-configured LaTeX and Typst essay templates for academic writing.
 .
 Supported citation styles: SBL, Chicago, MLA, APA 7th ed., ASA,
 Turabian, Harvard — each applies correct heading formatting, page
 numbering, and running headers automatically.
CONTROL

step "Writing DEBIAN/postinst"
cat > "${DEBROOT}/DEBIAN/postinst" << 'POSTINST'
#!/bin/sh
set -e
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
fc-cache -f /usr/share/fonts/gost 2>/dev/null || true
POSTINST
chmod 755 "${DEBROOT}/DEBIAN/postinst"

cat > "${DEBROOT}/DEBIAN/postrm" << 'POSTRM'
#!/bin/sh
set -e
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
POSTRM
chmod 755 "${DEBROOT}/DEBIAN/postrm"

step "Building DEB"
dpkg-deb --build --root-owner-group "$DEBROOT" "$OUTPUT"

echo ""
info "${BOLD}Built: $(basename "$OUTPUT")${NC}  ($(du -sh "$OUTPUT" | cut -f1))"
echo ""
echo "  Install:  sudo apt install ./${OUTPUT##*/}"
echo "            # or: sudo dpkg -i ${OUTPUT##*/} && sudo apt-get install -f"
echo ""
