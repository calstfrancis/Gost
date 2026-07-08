#!/usr/bin/env bash
# capture-screenshots.sh — capture a fresh screenshot of Gost against demo data
#
# Launches the app from source under a throwaway $HOME (so it never touches
# Cal's real config/data), inside an isolated Xvfb display forced via
# GDK_BACKEND=x11 (GTK4 otherwise prefers the real Wayland session and would
# render on the actual desktop). Waits for the window to render, screenshots
# just the window, and overwrites screenshots/gost-main.png.
#
# Requires: Xvfb, ImageMagick (magick), python3-gi/gtk4/libadwaita (same deps
# as running Gost normally).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DEMO_HOME=$(mktemp -d /tmp/gost-demo-home.XXXXXX)
OUT="screenshots/gost-main.png"
WINDOW_W=960
WINDOW_H=720

cleanup() {
  [[ -n "${APP_PID:-}" ]] && kill "$APP_PID" 2>/dev/null || true
  [[ -n "${XVFB_PID:-}" ]] && kill "$XVFB_PID" 2>/dev/null || true
  rm -rf "$DEMO_HOME"
}
trap cleanup EXIT

echo "==> Seeding demo config in $DEMO_HOME"
mkdir -p "$DEMO_HOME/.config/gost"
cat > "$DEMO_HOME/.config/gost/config.json" <<JSON
{
  "citation_style": "SBL",
  "engine": "xelatex",
  "font_size": "11pt",
  "paper": "letterpaper",
  "window_width": $WINDOW_W,
  "window_height": $WINDOW_H
}
JSON

# Isolated Xvfb display, well clear of any real display number in use.
DISPLAY_NUM=222
while [[ -e "/tmp/.X${DISPLAY_NUM}-lock" ]]; do
  DISPLAY_NUM=$((DISPLAY_NUM + 1))
done

echo "==> Starting isolated Xvfb on :$DISPLAY_NUM"
Xvfb ":$DISPLAY_NUM" -screen 0 1280x800x24 &
XVFB_PID=$!
sleep 2

echo "==> Launching Gost against demo config inside the isolated display"
# GDK_BACKEND=x11 + unsetting WAYLAND_DISPLAY is required: GTK4 prefers Wayland
# by default, which would otherwise connect to the real desktop session and
# render there instead of into the isolated Xvfb display.
env -u WAYLAND_DISPLAY GDK_BACKEND=x11 HOME="$DEMO_HOME" DISPLAY=":$DISPLAY_NUM" python3 -m essay_builder.app &
APP_PID=$!

echo "==> Waiting for window to render"
sleep 10

echo "==> Capturing and cropping to the app window"
DISPLAY=":$DISPLAY_NUM" magick x:root -crop "${WINDOW_W}x${WINDOW_H}+0+0" +repage "$OUT"

echo "Done. Wrote $OUT"
