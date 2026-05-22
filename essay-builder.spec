Name:           gost
Version:        1.2.0
Release:        1%{?dist}
Summary:        Academic Essay Templater — LaTeX and Typst (GTK4 / libadwaita)
License:        GPL-3.0-or-later
URL:            https://github.com/calstfrancis/gost

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-setuptools
BuildRequires:  python3-build
BuildRequires:  python3-wheel

Requires:       python3 >= 3.11
Requires:       python3-gobject >= 3.44
Requires:       typelib(Gtk) = 4.0
Requires:       typelib(Adw) = 1
Requires:       libadwaita >= 1.4

%description
Gost is a native GTK4/libadwaita desktop application for generating
academic essay templates in LaTeX (extarticle) or Typst.

Supports SBL, Chicago, MLA, and APA citation styles via BibLaTeX, with
configurable layout, language support, journal template importer, compiled
preview, and Zotero/BetterBibTeX integration.

%prep
%setup -q

%build
%{python3} -m build --wheel --no-isolation

%install
%{python3} -m pip install \
    --no-deps \
    --no-build-isolation \
    --root=%{buildroot} \
    --prefix=%{_prefix} \
    dist/*.whl

install -Dm644 gost.desktop \
    %{buildroot}%{_datadir}/applications/ca.calstfrancis.Gost.desktop

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/essay_builder/
%{python3_sitelib}/essay_builder*.dist-info/
%{_bindir}/gost
%{_datadir}/applications/ca.calstfrancis.Gost.desktop

%changelog
* %(date "+%a %b %d %Y") Build User <build@localhost> - 1.2.0-1
- Renamed to Gost
