#!/usr/bin/env bash
# uninstall.sh — remove Gost
set -euo pipefail
GREEN='\033[0;32m'; NC='\033[0m'
info() { echo -e "${GREEN}[✓]${NC} $*"; }

sudo rm -rf  /usr/local/lib/gost
sudo rm -f   /usr/local/bin/gost
sudo rm -f   /usr/local/share/applications/gost.desktop
sudo rm -f   /usr/local/share/icons/hicolor/scalable/apps/gost.svg
sudo rm -f   /usr/local/share/icons/hicolor/symbolic/apps/gost-symbolic.svg
for SIZE in 16 32 48 64 128 256; do
    sudo rm -f "/usr/local/share/icons/hicolor/${SIZE}x${SIZE}/apps/gost.png"
done

command -v gtk4-update-icon-cache &>/dev/null && \
    sudo gtk4-update-icon-cache -f -t /usr/local/share/icons/hicolor 2>/dev/null || true
command -v update-desktop-database &>/dev/null && \
    sudo update-desktop-database /usr/local/share/applications 2>/dev/null || true

info "Gost uninstalled."
