# Gost v0.1.10

**Released:** 2026-06-06

## Download

| File | Platform |
|------|----------|
| `gost-0.1.9-1.noarch.rpm` | Fedora, openSUSE, RHEL, and RPM-based distros |
| `gost_0.1.9_all.deb` | Debian, Ubuntu, Linux Mint, and DEB-based distros |

---

## Installation

### RPM (Fedora / openSUSE / RHEL)

```bash
# Install system dependencies first (if not already present):
sudo zypper install python3-gobject typelib-1_0-Gtk-4_0 typelib-1_0-Adw-1  # openSUSE
sudo dnf install python3-gobject gtk4 libadwaita                             # Fedora

# Install Gost:
sudo zypper in ./gost-0.1.9-1.noarch.rpm   # openSUSE
sudo dnf install ./gost-0.1.9-1.noarch.rpm  # Fedora / RHEL
```

### DEB (Debian / Ubuntu / Mint)

```bash
# Install system dependencies first:
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Install Gost:
sudo apt install ./gost_0.1.9_all.deb
# or: sudo dpkg -i gost_0.1.9_all.deb && sudo apt-get install -f
```

### pipx (recommended for source installs)

```bash
# 1. Install system dependencies (once)
sudo zypper install python3-gobject typelib-1_0-Gtk-4_0 typelib-1_0-Adw-1  # openSUSE
# sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1                  # Debian/Ubuntu
# sudo dnf install python3-gobject gtk4 libadwaita                          # Fedora

# 2. Install Gost
pipx install gost-academic --system-site-packages
pipx install 'gost-academic[word]' --system-site-packages  # + Word / ODT export

# 3. Run — desktop integration happens automatically on first launch
gost
```

---

## What's New in v0.1.9

### RPM and DEB packages

Gost is now distributed as native Linux packages:

- **RPM** (`gost-0.1.9-1.noarch.rpm`) — for Fedora, openSUSE, RHEL, and any RPM-based distribution. Installs Gost, its launcher, desktop entry, icons, and fonts into the standard system directories. Dependencies are declared in the package so your distro's package manager handles them automatically.
- **DEB** (`gost_0.1.9_all.deb`) — for Debian, Ubuntu, Linux Mint, and any DEB-based distribution. Same set of installed files; `apt install` resolves dependencies automatically.

Both packages:
- Place the launcher at `/usr/bin/gost`
- Register a `.desktop` entry so Gost appears in the GNOME application launcher
- Install the GOST Type B font to `/usr/share/fonts/gost/`
- Run post-install hooks to refresh the icon cache and desktop database

Build your own packages from source:

```bash
bash build-rpm.sh   # requires rpmbuild (rpm-build package)
bash build-deb.sh   # requires dpkg-deb; run on a Debian/Ubuntu host
```

---

## Previous release — v0.1.8

### Live auto-preview pane

A **Live Preview** pane is now always visible on the right side of the app. It compiles automatically as you change settings (400 ms debounce). Toggle with the column-view button in the header bar; preference is remembered between sessions.

### Editable source view

The **Source** tab in the Preview panel is now editable. A **● Edited** badge appears when the buffer has been modified. Click **Regenerate** to reset.

### Enhanced chapter management

- **Reordering** — up/down arrow buttons on each chapter row
- **Per-chapter notes** — collapsible notes field on each row

---

## Dependencies

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| PyGObject | `python3-gobject` / `python3-gi` |
| GTK4 typelib | `typelib-1_0-Gtk-4_0` / `gir1.2-gtk-4.0` |
| libadwaita ≥ 1.4 | `typelib-1_0-Adw-1` / `gir1.2-adw-1` |

**Compiled preview (optional):** `typst` for Typst output; `latexmk` + `poppler-tools` for LaTeX.

**Word export (optional):** `python-docx`. Install via `pip install gost-academic[word]`.

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
