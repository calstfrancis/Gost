#!/usr/bin/env bash
# build-rpm.sh — Build gost-<version>-1.noarch.rpm
# Requires: rpmbuild (rpm-build package)
#
# Usage:
#   bash build-rpm.sh
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
die()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }
step()  { echo -e "\n${BOLD}── $* ──${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(python3 -c "from essay_builder import __version__; print(__version__)" 2>/dev/null || echo "0.1.9")"
SPEC="${SCRIPT_DIR}/packaging/gost.spec"
RPMBUILD_DIR="${SCRIPT_DIR}/.rpmbuild"
OUTPUT="${SCRIPT_DIR}/gost-${VERSION}-1.noarch.rpm"

step "Pre-flight checks"
command -v rpmbuild &>/dev/null || die "rpmbuild not found. Install rpm-build: zypper in rpm-build  |  dnf in rpm-build"
[[ -f "$SPEC" ]] || die "Spec file not found: $SPEC"
info "rpmbuild OK, spec found"

step "Creating source tarball"
TARBALL="${RPMBUILD_DIR}/SOURCES/gost-${VERSION}.tar.gz"
mkdir -p "${RPMBUILD_DIR}/"{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Pack source from the repo root, excluding build artifacts
tar -czf "$TARBALL" \
    --transform "s|^\./|gost-${VERSION}/|" \
    --exclude='./.git' \
    --exclude='./.rpmbuild' \
    --exclude='./AppDir' \
    --exclude='./.appimage-tools' \
    --exclude='./__pycache__' \
    --exclude='./*.AppImage' \
    --exclude='./*.egg-info' \
    --exclude='./dist' \
    --exclude='./gost.egg-info' \
    --exclude='./gost_academic.egg-info' \
    -C "$SCRIPT_DIR" .
info "Source tarball: $TARBALL"

step "Building RPM"
cp "$SPEC" "${RPMBUILD_DIR}/SPECS/gost.spec"
rpmbuild \
    --define "_topdir ${RPMBUILD_DIR}" \
    --define "_version ${VERSION}" \
    -bb "${RPMBUILD_DIR}/SPECS/gost.spec"

BUILT_RPM="$(find "${RPMBUILD_DIR}/RPMS" -name "gost-${VERSION}*.rpm" | head -1)"
[[ -n "$BUILT_RPM" ]] || die "RPM not found after build"

cp "$BUILT_RPM" "$OUTPUT"

echo ""
info "${BOLD}Built: $(basename "$OUTPUT")${NC}  ($(du -sh "$OUTPUT" | cut -f1))"
echo ""
echo "  Install (openSUSE / Fedora):  sudo zypper in ./${OUTPUT##*/}"
echo "                                sudo rpm -i ${OUTPUT##*/}"
echo ""
echo "  GitHub Release:"
echo "  1. Tag: git tag v${VERSION} && git push origin v${VERSION}"
echo "  2. Attach ${OUTPUT##*/} to the GitHub Release"
echo ""
