Name:           gost
Version:        0.1.10
Release:        1%{?dist}
Summary:        Academic essay templater for LaTeX and Typst

License:        GPL-3.0-or-later
URL:            https://github.com/calstfrancis/gost
Source0:        https://github.com/calstfrancis/gost/archive/v%{version}/gost-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3 >= 3.10
Requires:       python3-gobject
Requires:       typelib(Gtk) = 4.0
Requires:       typelib(Adw) = 1

Recommends:     typst
Recommends:     texlive-latexmk
Recommends:     poppler-tools
Recommends:     python3-docx

%description
Gost is a native GTK4 / libadwaita desktop application for generating
fully-configured LaTeX and Typst essay templates for academic writing.

Supported citation styles: SBL, Chicago (Notes), MLA, APA 7th ed., ASA,
Turabian, Harvard — each applies correct heading formatting, page numbering,
and running headers automatically.

Features: compiled PDF preview, journal template importer, chapter list,
template profiles, Zotero BetterBibTeX integration, LanguageTool grammar
check, Word/ODT export, and support for Russian, Hebrew, Japanese, Tibetan,
Sanskrit, Ancient Greek, and Chinese.

%prep
%autosetup -n gost-%{version}

%install
# Python package
install -d %{buildroot}%{_datadir}/gost
cp -r essay_builder %{buildroot}%{_datadir}/gost/

# Launcher
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/gost << 'LAUNCHER'
#!/usr/bin/env bash
export PYTHONPATH="%{_datadir}/gost${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m essay_builder.app "$@"
LAUNCHER
chmod 755 %{buildroot}%{_bindir}/gost

# Desktop entry
install -Dm644 gost.desktop \
    %{buildroot}%{_datadir}/applications/ca.calstfrancis.Gost.desktop

# Icons
install -Dm644 icons/gost.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ca.calstfrancis.Gost.svg
install -Dm644 icons/gost-symbolic.svg \
    %{buildroot}%{_datadir}/icons/hicolor/symbolic/apps/ca.calstfrancis.Gost-symbolic.svg

# Fonts
install -d %{buildroot}%{_datadir}/fonts/gost
for f in essay_builder/fonts/*.ttf essay_builder/fonts/*.otf; do
    [ -f "$f" ] && install -Dm644 "$f" %{buildroot}%{_datadir}/fonts/gost/
done

%files
%license LICENSE
%doc README.md CHANGELOG.md HELP.md
%{_bindir}/gost
%{_datadir}/gost/essay_builder/
%{_datadir}/applications/ca.calstfrancis.Gost.desktop
%{_datadir}/icons/hicolor/scalable/apps/ca.calstfrancis.Gost.svg
%{_datadir}/icons/hicolor/symbolic/apps/ca.calstfrancis.Gost-symbolic.svg
%{_datadir}/fonts/gost/

%post
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null || true
update-desktop-database -q %{_datadir}/applications &>/dev/null || true
fc-cache -f %{_datadir}/fonts/gost &>/dev/null || true

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null || true
update-desktop-database -q %{_datadir}/applications &>/dev/null || true

%changelog
* Sat Jun 06 2026 Cal St Francis <calstfrancis@gmail.com> - 0.1.10-1
- GitHub Actions release workflow builds DEB and RPM automatically on publish
- AppImage distribution dropped in favour of native packages

* Sat Jun 06 2026 Cal St Francis <calstfrancis@gmail.com> - 0.1.9-1
- RPM and DEB packaging
- Updated documentation with distribution-specific install instructions

* Sat May 23 2026 Cal St Francis <calstfrancis@gmail.com> - 0.1.8-1
- Live auto-preview pane with 400ms debounce
- Editable source view with divergence indicator
- Chapter reordering and per-chapter notes
