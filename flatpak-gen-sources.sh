#!/usr/bin/env bash
# Generate offline pip sources for the flatpak build.
# Run this once before building, or whenever requirements-flatpak.txt changes.
# Requires: flatpak-pip-generator (pip install flatpak-pip-generator)
set -euo pipefail

if ! command -v flatpak-pip-generator &>/dev/null; then
    echo "flatpak-pip-generator not found. Install with: pip install flatpak-pip-generator"
    exit 1
fi

echo "Generating python3-deps.json from requirements-flatpak.txt …"
flatpak-pip-generator \
    --runtime org.gnome.Sdk//47 \
    --output python3-deps \
    $(cat requirements-flatpak.txt | grep -v '^#' | tr '\n' ' ')
echo "Done: python3-deps.json"
