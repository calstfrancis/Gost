#!/usr/bin/env bash
# Generate offline pip sources for the flatpak build.
# Run this once before building, or whenever requirements-flatpak.txt changes.
# Requires: flatpak-pip-generator (pip install flatpak-pip-generator)
set -euo pipefail

# pipx installs the binary as flatpak_pip_generator (underscores)
FPG=$(command -v flatpak_pip_generator 2>/dev/null || command -v flatpak-pip-generator 2>/dev/null || true)
if [[ -z "$FPG" ]]; then
    echo "flatpak-pip-generator not found. Install with: pipx install flatpak-pip-generator"
    exit 1
fi

echo "Generating python3-deps.json from requirements-flatpak.txt …"
"$FPG" \
    --runtime org.gnome.Sdk//47 \
    --output python3-deps \
    $(cat requirements-flatpak.txt | grep -v '^#' | tr '\n' ' ')
echo "Done: python3-deps.json"
