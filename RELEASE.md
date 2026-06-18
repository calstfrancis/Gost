# Gost v0.1.12

**Released:** 2026-06-18

## What's new

- Book mode and GOST Type B font toggles consolidated into the status bar.

## Download

| File | Platform |
|------|----------|
| Flatpak | All Linux (via personal flatpak repo) |
| `gost-0.1.12-1.noarch.rpm` | Fedora, openSUSE, RHEL, and RPM-based distros |
| `gost_0.1.12_all.deb` | Debian, Ubuntu, Linux Mint, and DEB-based distros |

## Installation

### Flatpak (recommended)

```bash
flatpak remote-add --user calstfrancis \
  https://calstfrancis.github.io/flatpak/calstfrancis.flatpakrepo
flatpak install calstfrancis ca.calstfrancis.Gost
```

### RPM (Fedora / openSUSE / RHEL)

```bash
sudo zypper in ./gost-0.1.12-1.noarch.rpm   # openSUSE
sudo dnf install ./gost-0.1.12-1.noarch.rpm  # Fedora / RHEL
```

### DEB (Debian / Ubuntu / Mint)

```bash
sudo apt install ./gost_0.1.12_all.deb
```

---

## Dependencies

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| PyGObject | `python3-gobject` / `python3-gi` |
| GTK4 typelib | `typelib-1_0-Gtk-4_0` / `gir1.2-gtk-4.0` |
| libadwaita ≥ 1.4 | `typelib-1_0-Adw-1` / `gir1.2-adw-1` |

**Compiled preview (optional):** `typst` for Typst output; `latexmk` + `poppler-tools` for LaTeX.

**Word export (optional):** `python-docx` (`pip install python-docx`).

**ODT export (optional):** LibreOffice.

---

## Building from source

```bash
git clone https://github.com/calstfrancis/gost
cd gost
python3 -m essay_builder.app   # run directly
bash build-rpm.sh              # build RPM (requires rpmbuild)
bash build-deb.sh              # build DEB (requires dpkg-deb; run on Debian/Ubuntu)
```

---

## Full changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete history.
