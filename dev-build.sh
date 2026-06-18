#!/usr/bin/env bash
# dev-build.sh — build and install Gost locally for testing
#
# Run this after Claude has prepped the dev build (bumped to the next rc version,
# updated CHANGELOG, committed, and tagged). No arguments needed — the version
# is read from pyproject.toml.
#
# Generates python3-deps.json if missing, pushes to GitHub first (flatpak-builder
# pulls source from branch: main), then builds and installs locally.
# Does NOT publish to the flatpak repo.

set -euo pipefail

MANIFEST="ca.calstfrancis.Gost.yml"

VERSION=$(python3 -c "exec(open('essay_builder/__init__.py').read()); print(__version__)")
echo "==> Building Gost $VERSION (local dev install)"

if [ ! -f python3-deps.json ]; then
    echo "==> python3-deps.json missing, generating..."
    bash flatpak-gen-sources.sh
fi

echo "==> Pushing to GitHub (flatpak-builder needs this)..."
git push origin main
git push origin "v$VERSION" 2>/dev/null || true

flatpak-builder --force-clean --user --install build-flatpak "$MANIFEST"

echo ""
echo "Done! Gost $VERSION is installed locally."
echo "Run it with: flatpak run ca.calstfrancis.Gost"
