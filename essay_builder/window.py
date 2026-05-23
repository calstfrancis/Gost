"""
window.py — GTK4 / libadwaita UI for Gost.
"""

import datetime
import threading
from typing import List

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Adw, Gdk, GdkPixbuf, GLib, Gio

from essay_builder.texgen import generate, STYLE_DEFAULTS, FONT_OPTIONS
from essay_builder.typstgen import generate as typst_generate
from essay_builder.config import Config
from essay_builder.logger import get_logger

# ---------------------------------------------------------------------------

def _switch_row(title: str, subtitle: str = "") -> Adw.SwitchRow:
    row = Adw.SwitchRow(title=title)
    if subtitle:
        row.set_subtitle(subtitle)
    return row


def _entry_row(title: str, placeholder: str = "") -> Adw.EntryRow:
    row = Adw.EntryRow(title=title)
    if placeholder:
        row.set_text(placeholder)
    return row


def _combo_row(title: str, options: List[str]) -> Adw.ComboRow:
    row = Adw.ComboRow(title=title)
    model = Gtk.StringList()
    for opt in options:
        model.append(opt)
    row.set_model(model)
    return row


def _spin_row(title: str, low: float, high: float, step: float, val: float) -> Adw.SpinRow:
    adj = Gtk.Adjustment(value=val, lower=low, upper=high, step_increment=step)
    row = Adw.SpinRow(title=title, adjustment=adj, digits=0 if step >= 1 else 2)
    return row


def _png_bytes_to_texture(data: bytes) -> Gdk.Texture:
    loader = GdkPixbuf.PixbufLoader()
    loader.write(data)
    loader.close()
    return Gdk.Texture.new_for_pixbuf(loader.get_pixbuf())


# ---------------------------------------------------------------------------
# Feature / language constants
# ---------------------------------------------------------------------------

LATEX_FEATURES = [
    ("dropcaps",     "Drop caps (lettrine)",         r"Decorative \lettrine{L}{etter} first letters"),
    ("marginalia",   "Marginalia (marginnote)",       r"\marginnote{} for margin notes"),
    ("csquotes",     "Smart quotes (csquotes)",       "Contextual quotation marks; recommended with biblatex"),
    ("xcolor",       "Color support (xcolor)",        r"\textcolor{}{} and named colors (dvipsnames)"),
    ("listings",     "Code listings (listings)",      "Typeset source code with syntax highlighting"),
    ("enumitem",     "Enhanced lists (enumitem)",     "Customizable enumerate, itemize, description"),
    ("booktabs",     "Better tables (booktabs)",      "Publication-quality horizontal rules"),
    ("siunitx",      "SI units (siunitx)",            r"\qty{10}{\metre}, \num{1.5e3}"),
    ("epigraph_pkg", "Epigraph (epigraph)",           r"\epigraph{text}{source} command"),
    ("lineno",       "Line numbers (lineno)",          "Margin line numbers for peer review"),
    ("todonotes",    "Todo notes (todonotes)",         r"\todo{} margin annotations"),
]

TYPST_FEATURES = [
    ("dropcaps",   "Drop caps (droplet)",           "Decorative first-letter drop caps"),
    ("marginalia", "Margin notes",                  "Place notes with #place(right + top)[…]"),
    ("codly",      "Code listings (codly)",         "Syntax-highlighted code blocks"),
    ("showybox",   "Styled boxes (showybox)",       "Colored / framed content boxes"),
    ("gentle",     "Callout boxes (gentle-clues)",  "Info, warning, tip callout blocks"),
    ("tablex",     "Enhanced tables (tablex)",      "Column/row spans and merged cells"),
    ("drafting",   "Margin annotations (drafting)", "Margin annotations for draft review"),
]

LANGUAGES = [
    ("russian",  "Russian",       "polyglossia / babel + Cyrillic fonts"),
    ("hebrew",   "Hebrew",        "polyglossia; right-to-left support"),
    ("japanese", "Japanese",      "xeCJK (XeLaTeX) or luatexja (LuaLaTeX)"),
    ("tibetan",  "Tibetan",       "polyglossia + Tibetan font"),
    ("sanskrit", "Sanskrit",      "polyglossia + Devanagari font"),
    ("greek",    "Ancient Greek", "polyglossia variant: ancient"),
    ("chinese",  "Chinese",       "xeCJK (XeLaTeX) or luatexja (LuaLaTeX)"),
]

HEADER_STYLE_KEYS = [
    "auto", "none", "pagenum_bottom",
    "title_left", "section_left", "author_left", "doublesided",
]
HEADER_STYLE_LABELS = [
    "Auto (follows citation style)",
    "None",
    "Page numbers only (bottom centre)",
    "Title  ·  Page number",
    "Section title  ·  Page number",
    "Author  ·  Page number",
    "Double-sided (section / page alternating)",
]


# Per-style layout/font presets applied when the user selects a citation style
_STYLE_PRESETS = {
    "SBL":      dict(font_pkg="times", font_size="12pt", paper="letterpaper",
                     linespace="2", margin=1.0, parindent=1.5, numbered_heads=False,
                     bib_sort="nyt", cite_cmd="autocite"),
    "Chicago":  dict(font_pkg="times", font_size="12pt", paper="letterpaper",
                     linespace="2", margin=1.0, parindent=1.5, numbered_heads=False,
                     bib_sort="nyt", cite_cmd="footcite"),
    "MLA":      dict(font_pkg="times", font_size="12pt", paper="letterpaper",
                     linespace="2", margin=1.0, parindent=1.5, numbered_heads=False,
                     bib_sort="nty", cite_cmd="parencite"),
    "APA":      dict(font_pkg="times", font_size="12pt", paper="letterpaper",
                     linespace="2", margin=1.0, parindent=1.5, numbered_heads=False,
                     bib_sort="nyt", cite_cmd="parencite"),
    "ASA":      dict(font_pkg="times", font_size="12pt", paper="letterpaper",
                     linespace="2", margin=1.0, parindent=0.0, numbered_heads=False,
                     bib_sort="nyt", cite_cmd="parencite"),
    "Turabian": dict(font_pkg="times", font_size="12pt", paper="letterpaper",
                     linespace="2", margin=1.0, parindent=1.5, numbered_heads=False,
                     bib_sort="nyt", cite_cmd="footcite"),
    "Harvard":  dict(font_pkg="times", font_size="12pt", paper="a4paper",
                     linespace="2", margin=1.0, parindent=1.5, numbered_heads=False,
                     bib_sort="nyt", cite_cmd="parencite"),
}

# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class GostWindow(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Gost")

        self._config = Config()
        width, height = self._config.get_window_size()
        self.set_default_size(width, height)

        self._cit_style = self._config.get("citation_style", "SBL")
        self._engine    = self._config.get("engine", "xelatex")
        self._font_size = self._config.get("font_size", "11pt")
        self._paper     = self._config.get("paper", "letterpaper")

        logger = get_logger()
        logger.info(f"Loaded settings: engine={self._engine}, style={self._cit_style}")

        self._toast_overlay: Adw.ToastOverlay | None = None
        self._format = "typst"
        self._copy_btn: Gtk.Button | None = None
        self._gost_font_provider = None
        self._latex_only_widgets: List[Gtk.Widget] = []
        self._latex_feature_switches: dict = {}
        self._typst_feature_switches: dict = {}
        self._lang_switches: dict = {}
        self._preview_dirty = True
        self._compiling = False
        self._live_preview_timeout: int | None = None
        self._chapters: list = []
        self._grammar_checking = False
        self._simple_mode: bool = self._config.get("simple_mode", True)
        self._block_preset = False

        self._build_ui()
        self._check_compiler_deps()

        # Apply saved GOST font preference on startup
        if self._config.get("use_gost_font", False):
            self._apply_gost_font(True)

        self.connect("notify::default-width",  self._on_window_resize)
        self.connect("notify::default-height", self._on_window_resize)

    def _on_window_resize(self, widget, param):
        w = self.get_default_width()
        h = self.get_default_height()
        if w > 0 and h > 0:
            self._config.set_window_size(w, h)

    def _on_gost_font_toggled(self, switch, _param):
        active = switch.get_active()
        self._config.set("use_gost_font", active)
        self._apply_gost_font(active)

    def _apply_gost_font(self, active: bool):
        display = Gdk.Display.get_default()
        if active:
            if self._gost_font_provider is None:
                self._gost_font_provider = Gtk.CssProvider()
                self._gost_font_provider.load_from_data(
                    b'* { font-family: "GOST type B", "GOST Type B", monospace; }'
                )
            Gtk.StyleContext.add_provider_for_display(
                display,
                self._gost_font_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1,
            )
        else:
            if self._gost_font_provider is not None:
                Gtk.StyleContext.remove_provider_for_display(
                    display,
                    self._gost_font_provider,
                )

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(outer)
        self.set_content(self._toast_overlay)

        # ---- Header bar ----
        hbar = Adw.HeaderBar()
        hbar.set_show_end_title_buttons(True)
        hbar.set_title_widget(Adw.WindowTitle(
            title="Gost",
            subtitle="Academic Essay Templater"
        ))

        # Copy button — icon-only; tooltip updated by _on_format_toggled
        self._copy_btn = Gtk.Button()
        self._copy_btn.set_icon_name("edit-copy-symbolic")
        self._copy_btn.add_css_class("flat")
        self._copy_btn.set_tooltip_text("Copy Typst code to clipboard")
        self._copy_btn.connect("clicked", self._on_copy)
        hbar.pack_start(self._copy_btn)

        # Format toggle (Typst / LaTeX)
        fmt_box = Gtk.Box(spacing=0)
        fmt_box.add_css_class("linked")
        fmt_box.set_valign(Gtk.Align.CENTER)
        self._fmt_btns: dict = {}
        fmt_group = None
        for fmt_key, fmt_label in (("typst", "Typst"), ("latex", "LaTeX")):
            btn = Gtk.ToggleButton(label=fmt_label)
            btn.set_tooltip_text(
                "Generate a Typst template" if fmt_key == "typst"
                else "Generate a LaTeX template"
            )
            if fmt_group is None:
                fmt_group = btn
            else:
                btn.set_group(fmt_group)
            btn._fmt_key = fmt_key
            btn.connect("toggled", self._on_format_toggled)
            fmt_box.append(btn)
            self._fmt_btns[fmt_key] = btn
        hbar.pack_start(fmt_box)

        # Export (primary / suggested action)
        export_btn = Gtk.Button(label="Export")
        export_btn.add_css_class("suggested-action")
        export_btn.set_tooltip_text("Save the generated template to a file")
        export_btn.connect("clicked", self._on_export)
        hbar.pack_end(export_btn)

        # Preview (compile & show)
        self._preview_btn = Gtk.Button()
        self._preview_btn.set_icon_name("document-print-preview-symbolic")
        self._preview_btn.add_css_class("flat")
        self._preview_btn.set_tooltip_text("Compile and preview the template as PDF")
        self._preview_btn.connect("clicked", self._on_preview_btn)
        hbar.pack_end(self._preview_btn)

        # Hamburger menu — build sub-popovers first so the menu can embed them
        self._profiles_popover = self._build_profiles_popover()
        self._packs_popover    = self._build_style_packs_popover()
        self._menu_btn = Gtk.MenuButton()
        self._menu_btn.set_icon_name("open-menu-symbolic")
        self._menu_btn.add_css_class("flat")
        self._menu_btn.set_tooltip_text("More options")
        self._menu_btn.set_popover(self._build_menu_popover())
        hbar.pack_end(self._menu_btn)

        outer.append(hbar)

        # ---- Navigation split view ----
        self._nav_view = Adw.NavigationSplitView()
        self._nav_view.set_vexpand(True)
        self._nav_view.set_hexpand(True)
        outer.append(self._nav_view)

        sidebar_page = Adw.NavigationPage(title="Sections")
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_page.set_child(sidebar_box)

        self._nav_list = Gtk.ListBox()
        self._nav_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._nav_list.add_css_class("navigation-sidebar")
        self._nav_list.set_vexpand(True)
        self._nav_list.connect("row-selected", self._on_nav_selected)

        nav_items = [
            ("document-properties-symbolic",        "Citation Style",       "style",
             "Citation format — choosing a style sets font, spacing, margins and bibliography defaults"),
            ("document-edit-symbolic",              "Title &amp; Authors",  "metadata",
             "Paper title, authors, date and affiliation"),
            ("view-grid-symbolic",                  "Layout &amp; Spacing", "layout",
             "Page size, margins, font size and line spacing"),
            ("application-x-addon-symbolic",        "Extra Packages",       "features",
             "Optional LaTeX / Typst packages (drop caps, tables, code listings…)"),
            ("preferences-desktop-locale-symbolic", "Languages",            "languages",
             "Multilingual typesetting: Cyrillic, Hebrew, CJK, Greek…"),
            ("emblem-documents-symbolic",           "Headers &amp; Footers","headers",
             "Running headers, page numbering and footer rules"),
            ("accessories-dictionary-symbolic",     "Bibliography",         "bib",
             "Bibliography file path, sorting and print options"),
            ("view-list-ordered-symbolic",          "Chapters",             "chapters",
             "Chapter list and multi-file project export"),
            ("text-editor-symbolic",                "Custom Code",          "custom_code",
             "Custom LaTeX preamble commands or Typst show rules"),
            ("tools-check-spelling-symbolic",       "Grammar",              "grammar",
             "Grammar and style check via LanguageTool"),
            ("document-print-preview-symbolic",     "Preview",              "preview",
             "Live compiled PDF preview"),
        ]
        self._nav_rows: dict = {}
        for icon, label, key, tip in nav_items:
            row = Adw.ActionRow(title=label)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            row.set_activatable(True)
            row.set_tooltip_text(tip)
            row._nav_key = key
            self._nav_list.append(row)
            self._nav_rows[key] = row

        sidebar_box.append(self._nav_list)

        # GOST Type B font toggle
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(4)
        sidebar_box.append(sep)
        font_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        font_row.set_margin_start(12)
        font_row.set_margin_end(12)
        font_row.set_margin_top(8)
        font_row.set_margin_bottom(8)
        font_lbl = Gtk.Label(label="GOST Type B font")
        font_lbl.set_hexpand(True)
        font_lbl.set_xalign(0)
        self._gost_font_switch = Gtk.Switch()
        self._gost_font_switch.set_valign(Gtk.Align.CENTER)
        self._gost_font_switch.set_active(self._config.get("use_gost_font", False))
        self._gost_font_switch.set_tooltip_text(
            "Apply the GOST Type B monospace font to the Gost interface"
        )
        self._gost_font_switch.connect("notify::active", self._on_gost_font_toggled)
        font_row.append(font_lbl)
        font_row.append(self._gost_font_switch)
        sidebar_box.append(font_row)

        self._nav_view.set_sidebar(sidebar_page)

        content_page = Adw.NavigationPage(title="Gost")
        self._content_stack = Gtk.Stack()
        self._content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        content_page.set_child(self._content_stack)
        self._nav_view.set_content(content_page)

        self._build_style_panel()
        self._build_metadata_panel()
        self._build_layout_panel()
        self._build_features_panel()
        self._build_languages_panel()
        self._build_headers_panel()
        self._build_bib_panel()
        self._build_chapters_panel()
        self._build_custom_code_panel()
        self._build_grammar_panel()
        self._build_preview_panel()

        self._nav_list.select_row(self._nav_list.get_row_at_index(0))

        # Activate initial citation style after all panels exist so _apply_style_preset
        # can reach layout/font/spacing widgets.
        _init_style = self._cit_style if self._cit_style in self._style_btns else "SBL"
        self._style_btns[_init_style].set_active(True)

        # Apply initial format AFTER all panels are built so visibility is correct
        self._fmt_btns[self._format].set_active(True)

        # Apply simple mode (hides Chapters / Custom Code / Grammar when on)
        self._apply_simple_mode(self._simple_mode)

        # CSS for compiled-preview page cards (white background + shadow,
        # so pages look correct regardless of whether GTK theme is dark or light)
        css = Gtk.CssProvider()
        css.load_from_data(b"""
.preview-page-card {
    background-color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.28);
    border-radius: 2px;
    margin: 4px 16px;
}
""")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    # ------------------------------------------------------------------
    # Hamburger menu popover
    # ------------------------------------------------------------------

    def _build_menu_popover(self) -> Gtk.Popover:
        popover = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(8);  box.set_margin_bottom(8)
        box.set_margin_start(4); box.set_margin_end(4)
        box.set_size_request(220, -1)

        # Simple Mode toggle
        mode_row = Gtk.Box(spacing=12)
        mode_row.set_margin_start(12); mode_row.set_margin_end(8)
        mode_row.set_margin_top(4);    mode_row.set_margin_bottom(4)
        mode_lbl = Gtk.Label(label="Simple Mode")
        mode_lbl.set_hexpand(True)
        mode_lbl.set_xalign(0)
        self._simple_mode_switch = Gtk.Switch()
        self._simple_mode_switch.set_active(self._simple_mode)
        self._simple_mode_switch.set_valign(Gtk.Align.CENTER)
        self._simple_mode_switch.set_tooltip_text(
            "Hide Chapters, Custom Code and Grammar — recommended for everyday use"
        )
        self._simple_mode_switch.connect("notify::active", self._on_simple_mode_toggled)
        mode_row.append(mode_lbl)
        mode_row.append(self._simple_mode_switch)
        box.append(mode_row)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Import Journal
        import_btn = Gtk.Button(label="Import Journal…")
        import_btn.add_css_class("flat")
        import_btn.set_tooltip_text("Import a journal's .cls / .tex / .sty template file")
        import_btn.connect("clicked", lambda _b: (popover.popdown(),
                                                   self._on_import_journal(None)))
        box.append(import_btn)

        # Style Packs — nested MenuButton keeps its own popover
        packs_mb = Gtk.MenuButton(label="Style Packs")
        packs_mb.add_css_class("flat")
        packs_mb.set_tooltip_text("Apply a journal preset (JBL, Chicago, APA, MLA…)")
        packs_mb.set_popover(self._packs_popover)
        box.append(packs_mb)

        # Profiles — nested MenuButton keeps its own popover
        profiles_mb = Gtk.MenuButton(label="Profiles")
        profiles_mb.add_css_class("flat")
        profiles_mb.set_tooltip_text("Save and load named template configurations")
        profiles_mb.set_popover(self._profiles_popover)
        box.append(profiles_mb)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        about_btn = Gtk.Button(label="About Gost")
        about_btn.add_css_class("flat")
        about_btn.set_tooltip_text("Version, licence and acknowledgements")
        about_btn.connect("clicked", lambda _b: (popover.popdown(),
                                                  self._show_about(None)))
        box.append(about_btn)

        popover.set_child(box)
        return popover

    def _on_simple_mode_toggled(self, switch, _param):
        self._apply_simple_mode(switch.get_active())

    def _apply_simple_mode(self, active: bool) -> None:
        self._simple_mode = active
        self._config.set("simple_mode", active)
        advanced = ("chapters", "custom_code", "grammar")
        for key in advanced:
            if key in self._nav_rows:
                self._nav_rows[key].set_visible(not active)
        # If the currently shown panel is being hidden, fall back to metadata
        if active and self._content_stack.get_visible_child_name() in advanced:
            self._nav_list.select_row(self._nav_list.get_row_at_index(0))

    # ------------------------------------------------------------------
    # Profiles popover
    # ------------------------------------------------------------------

    def _build_profiles_popover(self) -> Gtk.Popover:
        popover = Gtk.Popover()
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_margin_top(12); outer.set_margin_bottom(12)
        outer.set_margin_start(12); outer.set_margin_end(12)
        outer.set_size_request(240, -1)

        save_box = Gtk.Box(spacing=6)
        self._profile_name_entry = Gtk.Entry()
        self._profile_name_entry.set_placeholder_text("Profile name…")
        self._profile_name_entry.set_hexpand(True)
        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_profile_save)
        save_box.append(self._profile_name_entry)
        save_box.append(save_btn)
        outer.append(save_box)

        outer.append(Gtk.Separator())

        self._profile_list = Gtk.ListBox()
        self._profile_list.add_css_class("boxed-list")
        self._profile_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        outer.append(self._profile_list)

        action_box = Gtk.Box(spacing=6)
        load_btn = Gtk.Button(label="Load")
        load_btn.set_hexpand(True)
        load_btn.connect("clicked", self._on_profile_load)
        del_btn = Gtk.Button(label="Delete")
        del_btn.add_css_class("destructive-action")
        del_btn.set_hexpand(True)
        del_btn.connect("clicked", self._on_profile_delete)
        action_box.append(load_btn)
        action_box.append(del_btn)
        outer.append(action_box)

        popover.set_child(outer)
        popover.connect("show", lambda *_: self._rebuild_profile_list())
        return popover

    def _rebuild_profile_list(self):
        while self._profile_list.get_row_at_index(0) is not None:
            self._profile_list.remove(self._profile_list.get_row_at_index(0))
        for name in sorted(self._config.get_profiles().keys()):
            row = Adw.ActionRow(title=name)
            row._profile_name = name
            self._profile_list.append(row)

    def _on_profile_save(self, _btn):
        name = self._profile_name_entry.get_text().strip()
        if not name:
            self._show_toast("Enter a profile name first")
            return
        self._config.save_profile(name, self._collect_state())
        self._rebuild_profile_list()
        self._profile_name_entry.set_text("")
        self._show_toast(f'Saved profile "{name}"')

    def _on_profile_load(self, _btn):
        row = self._profile_list.get_selected_row()
        if row is None:
            self._show_toast("Select a profile to load")
            return
        state = self._config.get_profiles().get(row._profile_name)
        if state:
            self._apply_state(state)
            self._profiles_popover.popdown()
            self._show_toast(f'Loaded profile "{row._profile_name}"')
        else:
            self._show_toast("Profile not found")

    def _on_profile_delete(self, _btn):
        row = self._profile_list.get_selected_row()
        if row is None:
            self._show_toast("Select a profile to delete")
            return
        name = row._profile_name
        self._config.delete_profile(name)
        self._rebuild_profile_list()
        self._show_toast(f'Deleted profile "{name}"')

    def _apply_state(self, s: dict):
        self._r_title.set_text(s.get("title", ""))
        self._r_subtitle.set_text(s.get("subtitle", ""))
        self._r_authors.set_text(s.get("authors", ""))
        self._r_affil.set_text(s.get("affiliation", ""))
        self._r_course.set_text(s.get("course", ""))
        self._date_entry.set_text(s.get("date", ""))
        self._r_bib_file.set_text(s.get("bib_file", ""))
        self._r_bib_heading.set_text(s.get("bib_heading", "Bibliography"))

        self._r_abstract.set_active(s.get("has_abstract", False))
        self._r_keywords.set_active(s.get("has_keywords", False))
        self._r_toc.set_active(s.get("use_toc", False))
        self._r_numbered.set_active(s.get("numbered_heads", False))
        self._r_style_headings.set_active(s.get("use_style_headings", True))
        self._r_use_parts.set_active(s.get("use_parts", False))
        self._r_print_bib.set_active(s.get("print_bib", True))
        self._r_microtype.set_active(s.get("microtype", True))
        self._r_use_multicol.set_active(s.get("use_multicol", False))
        self._r_col_rule.set_active(s.get("col_rule", False))
        self._r_header_rule.set_active(s.get("header_rule", False))
        self._r_suppress_first.set_active(s.get("suppress_first_header", True))

        self._r_margin.set_value(float(s.get("margin", 1.0)))
        self._r_parindent.set_value(float(s.get("parindent", 1.5)))
        self._r_parskip.set_value(float(s.get("parskip", 0)))
        self._r_num_cols.set_value(float(s.get("num_cols", 2)))
        self._r_col_sep.set_value(float(s.get("col_sep", 14)))

        cit = s.get("cit_style", "SBL")
        self._block_preset = True
        if cit in self._style_btns:
            self._style_btns[cit].set_active(True)
        self._block_preset = False
        self._r_bib_style.set_text(s.get("biblatex_style", ""))
        self._r_notes.set_selected({"footnote": 0, "endnote": 1, "none": 2}.get(
            s.get("notes_mode", "footnote"), 0))
        self._r_typst_notes.set_selected(
            0 if s.get("typst_notes", "footnote") == "footnote" else 1)

        eng_label = {"pdflatex": "pdfLaTeX", "xelatex": "XeLaTeX", "lualatex": "LuaLaTeX"}.get(
            s.get("engine", "xelatex"), "XeLaTeX")
        if eng_label in self._engine_btns:
            self._engine_btns[eng_label].set_active(True)

        paper = s.get("paper", "letterpaper")
        if paper in self._paper_btns:
            self._paper_btns[paper].set_active(True)

        fs = s.get("font_size", "11pt")
        if fs in self._fs_btns:
            self._fs_btns[fs].set_active(True)

        self._r_encoding.set_selected({"utf8": 0, "latin1": 1}.get(s.get("encoding", "utf8"), 0))

        font_key = s.get("font_pkg", "times")
        for i, opt in enumerate(FONT_OPTIONS):
            if opt["key"] == font_key:
                self._r_font_pkg.set_selected(i)
                break

        self._r_linespace.set_selected({"1": 0, "1.5": 1, "2": 2}.get(s.get("linespace", "2"), 2))
        self._r_bib_sort.set_selected(
            {"nyt": 0, "nty": 1, "none": 2, "ynt": 3}.get(s.get("bib_sort", "nyt"), 0))
        self._r_cite_cmd.set_selected(
            {"autocite": 0, "footcite": 1, "parencite": 2, "cite": 3}.get(s.get("cite_cmd", "autocite"), 0))

        hs = s.get("header_style", "auto")
        self._r_header_style.set_selected(
            HEADER_STYLE_KEYS.index(hs) if hs in HEADER_STYLE_KEYS else 0)

        fmt = s.get("format", "typst")
        if fmt in self._fmt_btns:
            self._fmt_btns[fmt].set_active(True)

        for key, sw in self._latex_feature_switches.items():
            sw.set_active(key in s.get("latex_features", []))
        for key, sw in self._typst_feature_switches.items():
            sw.set_active(key in s.get("typst_features", []))
        for key, sw in self._lang_switches.items():
            sw.set_active(key in s.get("languages", []))

        # Chapters
        self._chapters = list(s.get("chapters", []))
        if hasattr(self, "_chapters_list_box"):
            self._rebuild_chapters_ui()

        # Custom preamble
        if hasattr(self, "_r_custom_latex"):
            buf = self._r_custom_latex.get_buffer()
            buf.set_text(s.get("custom_latex_preamble", ""))
        if hasattr(self, "_r_custom_typst"):
            buf = self._r_custom_typst.get_buffer()
            buf.set_text(s.get("custom_typst_preamble", ""))

        # Typst CSL style override
        if hasattr(self, "_r_typst_csl"):
            self._r_typst_csl.set_text(s.get("typst_csl_style", ""))

        self._dirty_preview()

    # ------------------------------------------------------------------
    # Panel: Title & Authors
    # ------------------------------------------------------------------

    def _build_metadata_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="Document Identity")
        box.append(grp)

        self._r_title    = _entry_row("Title")
        self._r_title.set_tooltip_text("Paper title — appears in the running header and PDF metadata")
        self._r_subtitle = _entry_row("Subtitle", "optional")
        self._r_authors  = _entry_row("Author(s)", "Comma-separated for multiple")
        self._r_authors.set_tooltip_text("One author, or comma-separated list: Alice Smith, Bob Jones")
        self._r_affil    = _entry_row("Affiliation", "Atlantic School of Theology")
        self._r_affil.set_tooltip_text("University, department or institution")
        self._r_course   = _entry_row("Course / Context", "e.g. THEO 5210")
        self._r_course.set_tooltip_text("Course code or context line printed below the author")

        saved_authors = self._config.get("authors", "")
        if saved_authors:
            self._r_authors.set_text(saved_authors)

        for r in (self._r_title, self._r_subtitle, self._r_affil, self._r_course):
            r.connect("changed", lambda *_: self._dirty_preview())
        self._r_authors.connect("changed", self._on_authors_changed)

        for r in (self._r_title, self._r_subtitle, self._r_authors, self._r_affil, self._r_course):
            grp.add(r)

        date_row = Adw.ActionRow(title="Date")
        date_row.set_tooltip_text("Leave blank to insert today's date automatically")
        self._date_entry = Gtk.Entry()
        self._date_entry.set_placeholder_text(r"YYYY-MM-DD  or  leave blank for \today")
        self._date_entry.set_valign(Gtk.Align.CENTER)
        self._date_entry.set_hexpand(True)
        self._date_entry.connect("changed", lambda *_: self._dirty_preview())
        today_btn = Gtk.Button(label="Today")
        today_btn.set_valign(Gtk.Align.CENTER)
        today_btn.add_css_class("flat")
        today_btn.set_tooltip_text("Insert today's date (YYYY-MM-DD)")
        today_btn.connect("clicked", self._set_today)
        date_row.add_suffix(self._date_entry)
        date_row.add_suffix(today_btn)
        grp.add(date_row)

        grp2 = Adw.PreferencesGroup(title="Front Matter")
        box.append(grp2)
        self._r_abstract = _switch_row("Include abstract block")
        self._r_keywords = _switch_row("Include keywords line")
        self._r_toc      = _switch_row(
            "Table of contents",
            r"Inserts \tableofcontents / #outline()"
        )
        for r in (self._r_abstract, self._r_keywords, self._r_toc):
            r.connect("notify::active", lambda *_: self._dirty_preview())
            grp2.add(r)

        self._content_stack.add_named(scroll, "metadata")

    def _on_authors_changed(self, row):
        self._config.set("authors", row.get_text())
        self._dirty_preview()

    # ------------------------------------------------------------------
    # Panel: Citation Style
    # ------------------------------------------------------------------

    def _build_style_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="Citation &amp; Formatting Style")
        box.append(grp)

        style_row = Adw.ActionRow(title="Base style")
        style_row.set_tooltip_text(
            "Sets citation format, default heading style and bibliography defaults"
        )
        style_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        style_box.set_valign(Gtk.Align.CENTER)
        style_row1 = Gtk.Box(spacing=4)
        style_row2 = Gtk.Box(spacing=4)
        style_box.append(style_row1)
        style_box.append(style_row2)
        self._style_btns: dict = {}
        style_group = None
        _style_rows = {
            "SBL": style_row1, "Chicago": style_row1,
            "MLA": style_row1, "APA": style_row1,
            "ASA": style_row2, "Turabian": style_row2, "Harvard": style_row2,
        }
        for s in ("SBL", "Chicago", "MLA", "APA", "ASA", "Turabian", "Harvard"):
            btn = Gtk.ToggleButton(label=s)
            btn.add_css_class("flat")
            if style_group is None:
                style_group = btn
            else:
                btn.set_group(style_group)
            btn._style_key = s
            btn.connect("toggled", self._on_style_toggled)
            _style_rows[s].append(btn)
            self._style_btns[s] = btn
        style_row.add_suffix(style_box)
        grp.add(style_row)

        self._r_bib_style = _entry_row("BibLaTeX style string")
        self._r_bib_style.set_tooltip_text(
            "BibLaTeX style key, e.g. verbose-note, chicago-notes, apa, mla"
        )
        self._r_bib_style.set_text("verbose-note")
        self._r_bib_style.connect("changed", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_style)
        self._latex_only_widgets.append(self._r_bib_style)

        self._r_notes = _combo_row("Notes mode (LaTeX)", ["Footnotes", "Endnotes", "None"])
        self._r_notes.set_tooltip_text(
            "Footnotes (default), endnotes, or inline citations with no note apparatus"
        )
        self._r_notes.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_notes)
        self._latex_only_widgets.append(self._r_notes)

        self._r_typst_notes = _combo_row("Notes mode (Typst)", ["Footnotes", "Endnotes"])
        self._r_typst_notes.set_tooltip_text(
            "Footnotes (default) or endnotes for Typst documents"
        )
        self._r_typst_notes.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_typst_notes)
        # will be shown/hidden by _on_format_toggled; start hidden (format starts as typst)
        self._r_typst_notes.set_visible(True)  # visible for typst

        self._r_numbered = _switch_row("Heading numbering")
        self._r_numbered.set_tooltip_text("Number headings: 1. Introduction, 1.1 Background…")
        self._r_numbered.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_numbered)

        self._r_style_headings = _switch_row(
            "Style-appropriate headings",
            "Apply titlesec / #show heading rules for the chosen style"
        )
        self._r_style_headings.set_tooltip_text(
            "Apply font, size and spacing rules for the selected citation style"
        )
        self._r_style_headings.set_active(True)
        self._r_style_headings.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_style_headings)

        self._r_use_parts = _switch_row(r"Include \part level")
        self._r_use_parts.set_tooltip_text(
            r"Add a \part level above chapter — useful for book-length work"
        )
        self._r_use_parts.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_use_parts)
        self._latex_only_widgets.append(self._r_use_parts)

        grp2 = Adw.PreferencesGroup(title="Font &amp; Encoding")
        box.append(grp2)

        font_display_names = [opt["display"] for opt in FONT_OPTIONS]
        self._r_font_pkg = _combo_row("Font", font_display_names)
        self._r_font_pkg.set_tooltip_text(
            "Font package — XeLaTeX or LuaLaTeX required for OpenType (non-pdfLaTeX) fonts"
        )
        # Default to Times (index matches FONT_OPTIONS order)
        _times_idx = next((i for i, o in enumerate(FONT_OPTIONS) if o["key"] == "times"), 3)
        self._r_font_pkg.set_selected(_times_idx)
        self._r_font_pkg.connect("notify::selected", self._on_font_selected)
        grp2.add(self._r_font_pkg)

        self._r_engine_row = Adw.ActionRow(title="Engine")
        self._r_engine_row.set_tooltip_text(
            "LaTeX engine — XeLaTeX is recommended (OpenType fonts, Unicode input)"
        )
        eng_box = Gtk.Box(spacing=4)
        eng_box.set_valign(Gtk.Align.CENTER)
        self._engine_btns: dict = {}
        eng_group = None
        _eng_tips = {
            "pdfLaTeX": "Fast, PDF-native; no OpenType font support",
            "XeLaTeX":  "OpenType fonts, Unicode input — recommended",
            "LuaLaTeX": "OpenType fonts, Lua scripting, slower compile",
        }
        for e in ("pdfLaTeX", "XeLaTeX", "LuaLaTeX"):
            btn = Gtk.ToggleButton(label=e)
            btn.add_css_class("flat")
            btn.set_tooltip_text(_eng_tips[e])
            if eng_group is None:
                eng_group = btn
            else:
                btn.set_group(eng_group)
            btn._eng_key = e
            btn.connect("toggled", self._on_engine_toggled)
            eng_box.append(btn)
            self._engine_btns[e] = btn
        self._engine_btns["XeLaTeX"].set_active(True)
        self._r_engine_row.add_suffix(eng_box)
        grp2.add(self._r_engine_row)
        self._latex_only_widgets.append(self._r_engine_row)

        self._r_encoding = _combo_row("Input encoding", ["utf8", "latin1"])
        self._r_encoding.set_tooltip_text(
            "Source file encoding — use utf8 unless your .tex file was saved as latin1"
        )
        self._r_encoding.connect("notify::selected", lambda *_: self._dirty_preview())
        grp2.add(self._r_encoding)
        self._latex_only_widgets.append(self._r_encoding)

        self._content_stack.add_named(scroll, "style")

    def _on_font_selected(self, *args):
        self._check_font_engine_compatibility()
        self._dirty_preview()

    def _check_font_engine_compatibility(self):
        if self._format == "typst":
            return
        selected = self._r_font_pkg.get_selected()
        if selected < 0:
            return
        font_info = FONT_OPTIONS[selected]
        if font_info["requires_fontspec"] and self._engine == "pdflatex":
            self._show_toast(
                f"⚠️ {font_info['display']} requires XeLaTeX or LuaLaTeX.",
                timeout=4
            )

    # ------------------------------------------------------------------
    # Panel: Layout & Spacing
    # ------------------------------------------------------------------

    def _build_layout_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="Page Layout")
        box.append(grp)

        paper_row = Adw.ActionRow(title="Paper size")
        paper_row.set_tooltip_text(
            "Sets the \\documentclass paper option and Typst page dimensions"
        )
        paper_box = Gtk.Box(spacing=4)
        paper_box.set_valign(Gtk.Align.CENTER)
        self._paper_btns: dict = {}
        pg = None
        for p, lbl in (("letterpaper", "Letter"), ("a4paper", "A4")):
            btn = Gtk.ToggleButton(label=lbl)
            btn.add_css_class("flat")
            if pg is None:
                pg = btn
            else:
                btn.set_group(pg)
            btn._paper_key = p
            btn.connect("toggled", self._on_paper_toggled)
            paper_box.append(btn)
            self._paper_btns[p] = btn
        self._paper_btns["letterpaper"].set_active(True)
        paper_row.add_suffix(paper_box)
        grp.add(paper_row)

        self._r_margin = _spin_row("Margin (inches)", 0.5, 3.0, 0.25, 1.0)
        self._r_margin.set_tooltip_text(
            "Page margin in inches, applied to all four sides via the geometry package"
        )
        self._r_margin.connect("notify::value", lambda *_: self._dirty_preview())
        grp.add(self._r_margin)

        fs_row = Adw.ActionRow(title="Font size")
        fs_row.set_tooltip_text("Base font size for body text")
        fs_box = Gtk.Box(spacing=4)
        fs_box.set_valign(Gtk.Align.CENTER)
        self._fs_btns: dict = {}
        fg = None
        for s in ("10pt", "11pt", "12pt"):
            btn = Gtk.ToggleButton(label=s)
            btn.add_css_class("flat")
            if fg is None:
                fg = btn
            else:
                btn.set_group(fg)
            btn._fs_key = s
            btn.connect("toggled", self._on_fs_toggled)
            fs_box.append(btn)
            self._fs_btns[s] = btn
        self._fs_btns["11pt"].set_active(True)
        fs_row.add_suffix(fs_box)
        grp.add(fs_row)

        self._r_linespace = _combo_row("Line spacing", ["Single", "1.5×", "Double"])
        self._r_linespace.set_tooltip_text(
            "Line spacing — double spacing is standard for most academic submissions"
        )
        self._r_linespace.set_selected(2)
        self._r_linespace.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_linespace)

        self._multicol_grp = Adw.PreferencesGroup(title="Multi-column")
        box.append(self._multicol_grp)
        self._latex_only_widgets.append(self._multicol_grp)

        self._r_use_multicol = _switch_row("Enable multicol")
        self._r_use_multicol.set_tooltip_text(
            "Wrap body text in the multicol environment (LaTeX only)"
        )
        self._r_use_multicol.connect("notify::active", self._on_multicol_toggled)
        self._multicol_grp.add(self._r_use_multicol)

        self._r_num_cols = _spin_row("Number of columns", 2, 4, 1, 2)
        self._r_num_cols.set_tooltip_text("Number of columns (2–4)")
        self._r_num_cols.connect("notify::value", lambda *_: self._dirty_preview())
        self._r_num_cols.set_sensitive(False)
        self._multicol_grp.add(self._r_num_cols)

        self._r_col_rule = _switch_row("Column separator rule")
        self._r_col_rule.set_tooltip_text("Draw a vertical rule between columns")
        self._r_col_rule.connect("notify::active", lambda *_: self._dirty_preview())
        self._r_col_rule.set_sensitive(False)
        self._multicol_grp.add(self._r_col_rule)

        self._r_col_sep = _spin_row("Column sep width (pt)", 4, 40, 1, 14)
        self._r_col_sep.set_tooltip_text("Space between columns in points")
        self._r_col_sep.connect("notify::value", lambda *_: self._dirty_preview())
        self._r_col_sep.set_sensitive(False)
        self._multicol_grp.add(self._r_col_sep)

        grp3 = Adw.PreferencesGroup(title="Paragraph Style")
        box.append(grp3)

        self._r_parindent = _spin_row("Paragraph indent (em)", 0, 4, 0.5, 1.5)
        self._r_parindent.set_tooltip_text("First-line indent at the start of each paragraph in em units")
        self._r_parindent.connect("notify::value", lambda *_: self._dirty_preview())
        grp3.add(self._r_parindent)

        self._r_parskip = _spin_row("Paragraph skip (pt)", 0, 18, 1, 0)
        self._r_parskip.set_tooltip_text("Extra vertical space between paragraphs in points (0 = no extra skip)")
        self._r_parskip.connect("notify::value", lambda *_: self._dirty_preview())
        grp3.add(self._r_parskip)
        self._latex_only_widgets.append(self._r_parskip)

        self._r_microtype = _switch_row("Microtype (protrusion)")
        self._r_microtype.set_tooltip_text(
            "Micro-typographic character protrusion and font expansion — "
            "improves line breaking and justified text (pdfLaTeX / LuaLaTeX)"
        )
        self._r_microtype.set_active(True)
        self._r_microtype.connect("notify::active", lambda *_: self._dirty_preview())
        grp3.add(self._r_microtype)
        self._latex_only_widgets.append(self._r_microtype)

        self._content_stack.add_named(scroll, "layout")

    # ------------------------------------------------------------------
    # Panel: Extra Packages
    # ------------------------------------------------------------------

    def _build_features_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        self._latex_features_grp = Adw.PreferencesGroup(
            title="LaTeX Packages",
            description=r"Adds \usepackage{} calls to the generated preamble"
        )
        box.append(self._latex_features_grp)

        for key, label, desc in LATEX_FEATURES:
            row = _switch_row(label, desc)
            row.connect("notify::active", lambda *_: self._dirty_preview())
            self._latex_features_grp.add(row)
            self._latex_feature_switches[key] = row

        self._typst_features_grp = Adw.PreferencesGroup(
            title="Typst Packages",
            description="Adds #import lines at the top of the generated document"
        )
        box.append(self._typst_features_grp)

        for key, label, desc in TYPST_FEATURES:
            row = _switch_row(label, desc)
            row.connect("notify::active", lambda *_: self._dirty_preview())
            self._typst_features_grp.add(row)
            self._typst_feature_switches[key] = row

        self._content_stack.add_named(scroll, "features")

    # ------------------------------------------------------------------
    # Panel: Languages
    # ------------------------------------------------------------------

    def _build_languages_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(
            title="Language Support",
            description=(
                "LaTeX: adds polyglossia/babel/xeCJK/luatexja packages. "
                "Typst: adds font guidance comments and #set text(lang: …)."
            )
        )
        box.append(grp)

        for key, label, desc in LANGUAGES:
            row = _switch_row(label, desc)
            row.connect("notify::active", lambda *_: self._dirty_preview())
            grp.add(row)
            self._lang_switches[key] = row

        self._content_stack.add_named(scroll, "languages")

    # ------------------------------------------------------------------
    # Panel: Headers & Footers
    # ------------------------------------------------------------------

    def _build_headers_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(
            title="Running Header",
            description=(
                "LaTeX: fancyhdr.  "
                "Typst: #set page(header: …)."
            )
        )
        box.append(grp)

        self._r_header_style = _combo_row("Header style", HEADER_STYLE_LABELS)
        self._r_header_style.set_tooltip_text(
            "What appears in the running header above each page"
        )
        self._r_header_style.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_header_style)

        self._r_header_rule = _switch_row(
            "Header rule",
            "Horizontal rule below the running header (LaTeX only)"
        )
        self._r_header_rule.set_tooltip_text(
            "Draw a \\hrule beneath the running header (LaTeX fancyhdr)"
        )
        self._r_header_rule.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_header_rule)

        self._r_suppress_first = _switch_row(
            "Suppress on first page",
            "No header on the title page"
        )
        self._r_suppress_first.set_tooltip_text(
            "Omit the running header on the title page — standard in most citation styles"
        )
        self._r_suppress_first.set_active(True)
        self._r_suppress_first.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_suppress_first)

        self._content_stack.add_named(scroll, "headers")

    # ------------------------------------------------------------------
    # Panel: Bibliography
    # ------------------------------------------------------------------

    def _build_bib_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18); box.set_margin_bottom(18)
        box.set_margin_start(18); box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="BibLaTeX / Zotero Bibliography")
        box.append(grp)

        self._r_bib_file = _entry_row("Path to .bib file")
        self._r_bib_file.set_tooltip_text(
            "Absolute or relative path to your Zotero-exported .bib file"
        )
        self._r_bib_file.set_show_apply_button(True)
        saved_bib = self._config.get("bib_file", "")
        if saved_bib:
            self._r_bib_file.set_text(saved_bib)
        self._r_bib_file.connect("apply",   self._on_bib_file_apply)
        self._r_bib_file.connect("changed", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_file)

        self._r_print_bib = _switch_row("Print bibliography at end")
        self._r_print_bib.set_tooltip_text(
            r"Append a \printbibliography / bibliography section at the end of the document"
        )
        self._r_print_bib.set_active(True)
        self._r_print_bib.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_print_bib)

        self._r_bib_heading = _entry_row("Bibliography heading")
        self._r_bib_heading.set_tooltip_text(
            "Heading text for the bibliography section (e.g. References, Works Cited)"
        )
        self._r_bib_heading.set_text("Bibliography")
        self._r_bib_heading.connect("changed", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_heading)

        self._r_bib_sort = _combo_row(
            "Sorting",
            ["Author–Year–Title (nyt)", "Author–Title–Year (nty)",
             "None (citation order)", "Year–Name–Title (ynt)"]
        )
        self._r_bib_sort.set_tooltip_text("BibLaTeX sorting scheme for the bibliography list")
        self._r_bib_sort.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_sort)

        self._r_cite_cmd = _combo_row(
            "Default cite command",
            [r"\autocite", r"\footcite", r"\parencite", r"\cite"]
        )
        self._r_cite_cmd.set_tooltip_text(
            "Default citation command used in the generated template body"
        )
        self._r_cite_cmd.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_cite_cmd)

        # LaTeX: manual biblatex style override
        self._r_bib_style_row = self._r_bib_style  # alias for visibility toggling

        # Typst: CSL style selector (hidden in LaTeX mode)
        typst_grp = Adw.PreferencesGroup(title="Typst Bibliography Style")
        box.append(typst_grp)

        csl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self._r_typst_csl = Gtk.Entry()
        self._r_typst_csl.set_placeholder_text("e.g. chicago-notes, apa, ieee …")
        self._r_typst_csl.set_hexpand(True)
        self._r_typst_csl.connect("changed", lambda *_: self._dirty_preview())
        csl_browse_btn = Gtk.Button(label="Browse CSL styles…")
        csl_browse_btn.add_css_class("flat")
        csl_browse_btn.set_tooltip_text("Browse and search the built-in list of CSL citation styles")
        csl_browse_btn.connect("clicked", self._on_csl_browse)
        csl_box.append(self._r_typst_csl)
        csl_box.append(csl_browse_btn)

        csl_row = Adw.ActionRow(title="CSL style override")
        csl_row.set_subtitle("Overrides the default style for this citation format")
        csl_row.add_suffix(csl_box)
        csl_row.set_activatable_widget(self._r_typst_csl)
        typst_grp.add(csl_row)
        self._r_typst_csl_row = typst_grp  # group for visibility toggling

        banner = Adw.Banner(title=(
            "Export from Zotero via BetterBibTeX → Keep Updated, "
            "then paste the absolute path above."
        ))
        banner.set_button_label("Got it")
        banner.connect("button-clicked", lambda b: b.set_revealed(False))
        banner.set_revealed(True)
        box.append(banner)

        self._content_stack.add_named(scroll, "bib")

    def _on_bib_file_apply(self, row):
        path = row.get_text().strip()
        self._config.set("bib_file", path)
        self._dirty_preview()

    # ------------------------------------------------------------------
    # Panel: Preview  (source ↔ compiled)
    # ------------------------------------------------------------------

    def _build_preview_panel(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.set_vexpand(True)

        # Toolbar
        toolbar = Gtk.Box(spacing=6)
        toolbar.set_margin_top(8); toolbar.set_margin_bottom(8)
        toolbar.set_margin_start(12); toolbar.set_margin_end(12)

        # Source / Compiled toggle
        mode_box = Gtk.Box(spacing=0)
        mode_box.add_css_class("linked")
        self._prev_mode_btns: dict = {}
        prev_grp = None
        _mode_tips = {
            "source":   "View the generated source code",
            "compiled": "Compile and display the rendered PDF",
        }
        for mode_key, mode_lbl in (("source", "Source"), ("compiled", "Compiled")):
            btn = Gtk.ToggleButton(label=mode_lbl)
            btn.set_tooltip_text(_mode_tips[mode_key])
            if prev_grp is None:
                prev_grp = btn
            else:
                btn.set_group(prev_grp)
            btn._preview_mode = mode_key
            btn.connect("toggled", self._on_preview_mode_toggled)
            mode_box.append(btn)
            self._prev_mode_btns[mode_key] = btn
        self._prev_mode_btns["source"].set_active(True)
        toolbar.append(mode_box)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.add_css_class("flat")
        refresh_btn.set_tooltip_text("Regenerate the source preview from current settings")
        refresh_btn.connect("clicked", lambda *_: self._refresh_source())
        toolbar.append(refresh_btn)

        self._compile_spinner = Gtk.Spinner()
        toolbar.append(self._compile_spinner)

        open_btn = Gtk.Button(label="Open PDF")
        open_btn.add_css_class("flat")
        open_btn.set_tooltip_text("Compile and open the PDF in your system viewer")
        open_btn.connect("clicked", self._open_in_viewer)
        toolbar.append(open_btn)

        self._compile_status = Gtk.Label(label="")
        self._compile_status.set_hexpand(True)
        self._compile_status.set_xalign(0.0)
        self._compile_status.add_css_class("dim-label")
        toolbar.append(self._compile_status)

        outer.append(toolbar)
        outer.append(Gtk.Separator())

        # Stack: source | compiled
        self._preview_inner_stack = Gtk.Stack()
        self._preview_inner_stack.set_vexpand(True)
        self._preview_inner_stack.set_transition_type(Gtk.StackTransitionType.NONE)

        # Source view
        src_scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        self._preview_buf = Gtk.TextBuffer()
        self._preview_view = Gtk.TextView(buffer=self._preview_buf)
        self._preview_view.set_editable(False)
        self._preview_view.set_monospace(True)
        self._preview_view.set_left_margin(14)
        self._preview_view.set_top_margin(10)
        src_scroll.set_child(self._preview_view)
        self._preview_inner_stack.add_named(src_scroll, "source")

        # Compiled view
        cmp_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        cmp_outer.set_vexpand(True)
        cmp_scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        self._pages_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._pages_box.set_margin_top(12); self._pages_box.set_margin_bottom(12)
        self._pages_box.set_margin_start(12); self._pages_box.set_margin_end(12)
        cmp_scroll.set_child(self._pages_box)
        cmp_outer.append(cmp_scroll)
        self._preview_inner_stack.add_named(cmp_outer, "compiled")

        outer.append(self._preview_inner_stack)

        self._content_stack.add_named(outer, "preview")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_nav_selected(self, listbox, row):
        if row is None:
            return
        key = row._nav_key
        self._content_stack.set_visible_child_name(key)
        if key == "preview":
            cur_mode = "compiled" if self._prev_mode_btns.get("compiled", Gtk.ToggleButton()).get_active() else "source"
            if cur_mode == "source":
                self._refresh_source()

    def _nav_select(self, key: str):
        self._nav_list.select_row(self._nav_rows[key])

    def _on_preview_btn(self, _btn):
        """Header bar Preview button → navigate to preview, start compilation."""
        self._nav_select("preview")
        self._content_stack.set_visible_child_name("preview")
        self._prev_mode_btns["compiled"].set_active(True)
        self._compile_preview()

    def _on_preview_mode_toggled(self, btn):
        if not btn.get_active():
            return
        mode = btn._preview_mode
        self._preview_inner_stack.set_visible_child_name(mode)
        if mode == "source":
            self._refresh_source()
        else:
            self._compile_preview()

    # ------------------------------------------------------------------
    # Source preview
    # ------------------------------------------------------------------

    def _refresh_source(self):
        content = self._build_template()
        self._preview_buf.set_text(content)
        self._preview_dirty = False

    def _dirty_preview(self):
        self._preview_dirty = True
        current_panel = self._content_stack.get_visible_child_name()
        if current_panel != "preview":
            return
        mode = "compiled" if self._prev_mode_btns.get("compiled", Gtk.ToggleButton()).get_active() else "source"
        if mode == "source":
            self._refresh_source()
        elif mode == "compiled" and self._preview_btn.get_sensitive():
            # Cancel any pending debounce and start a fresh 600 ms timer
            if self._live_preview_timeout is not None:
                GLib.source_remove(self._live_preview_timeout)
            self._live_preview_timeout = GLib.timeout_add(600, self._debounced_compile)

    # ------------------------------------------------------------------
    # Compiler dependency check
    # ------------------------------------------------------------------

    def _check_compiler_deps(self):
        from essay_builder.preview_compiler import typst_available, latex_available, image_tools_available
        if self._format == "typst":
            if not typst_available():
                self._preview_btn.set_sensitive(False)
                self._preview_btn.set_tooltip_text(
                    "typst not found in PATH — install from https://typst.app"
                )
                self._compile_status.set_text(
                    "typst not installed — Preview disabled. Install typst and restart."
                )
            else:
                self._preview_btn.set_sensitive(True)
                self._preview_btn.set_tooltip_text("")
                if not self._compile_status.get_text().startswith("typst not"):
                    self._compile_status.set_text("")
        else:
            missing = []
            if not latex_available():
                missing.append("latexmk (install texlive-latexmk)")
            if not image_tools_available():
                missing.append("pdftoppm (install poppler-tools) or convert (ImageMagick)")
            if missing:
                self._preview_btn.set_sensitive(False)
                self._preview_btn.set_tooltip_text("Missing: " + ", ".join(missing))
                self._compile_status.set_text("Missing: " + " · ".join(missing))
            else:
                self._preview_btn.set_sensitive(True)
                self._preview_btn.set_tooltip_text("")
                if self._compile_status.get_text().startswith("Missing:"):
                    self._compile_status.set_text("")

    # ------------------------------------------------------------------
    # Compiled preview
    # ------------------------------------------------------------------

    def _compile_preview(self):
        if self._compiling:
            return
        self._compiling = True
        self._compile_spinner.start()
        self._compile_status.set_text("Compiling…")
        source = self._build_template()
        fmt = self._format
        engine = self._engine
        t = threading.Thread(
            target=self._compile_thread,
            args=(source, fmt, engine),
            daemon=True,
        )
        t.start()

    def _compile_thread(self, source: str, fmt: str, engine: str):
        from essay_builder.preview_compiler import compile_typst, compile_latex
        if fmt == "typst":
            pages, err = compile_typst(source)
        else:
            pages, err = compile_latex(source, engine)
        GLib.idle_add(self._compile_done, pages, err)

    def _compile_done(self, pages: list, err: str):
        self._compiling = False
        self._compile_spinner.stop()

        # Clear previous pages
        child = self._pages_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._pages_box.remove(child)
            child = nxt

        if err:
            self._compile_status.set_text(f"Error — see below")
            lbl = Gtk.Label(label=err, wrap=True, xalign=0.0)
            lbl.set_selectable(True)
            lbl.add_css_class("monospace")
            self._pages_box.append(lbl)
        else:
            self._compile_status.set_text(f"{len(pages)} page(s)")
            for png_bytes in pages:
                try:
                    texture = _png_bytes_to_texture(png_bytes)
                    pic = Gtk.Picture.new_for_paintable(texture)
                    pic.set_content_fit(Gtk.ContentFit.CONTAIN)
                    pic.set_hexpand(True)
                    # Wrap in a white card so pages look correct on dark themes
                    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                    card.add_css_class("preview-page-card")
                    card.append(pic)
                    self._pages_box.append(card)
                except Exception as e:
                    self._pages_box.append(Gtk.Label(label=f"Image error: {e}"))

        return GLib.SOURCE_REMOVE

    # ------------------------------------------------------------------
    # Open in system viewer
    # ------------------------------------------------------------------

    def _open_in_viewer(self, _btn):
        if self._compiling:
            return
        self._compiling = True
        self._compile_spinner.start()
        self._compile_status.set_text("Compiling PDF…")
        source = self._build_template()
        t = threading.Thread(
            target=self._open_pdf_thread,
            args=(source, self._format, self._engine),
            daemon=True,
        )
        t.start()

    def _open_pdf_thread(self, source: str, fmt: str, engine: str):
        from essay_builder.preview_compiler import compile_typst_to_pdf, compile_latex_to_pdf
        if fmt == "typst":
            path, err = compile_typst_to_pdf(source)
        else:
            path, err = compile_latex_to_pdf(source, engine)
        GLib.idle_add(self._open_pdf_done, path, err)

    def _open_pdf_done(self, path: str, err: str):
        self._compiling = False
        self._compile_spinner.stop()
        if err:
            self._compile_status.set_text("PDF compile error")
            self._show_toast(err.split("\n")[0][:80], timeout=5)
        else:
            self._compile_status.set_text("Opened in PDF viewer")
            try:
                import subprocess as _sp
                _sp.Popen(["xdg-open", path])
            except Exception as e:
                self._show_toast(f"Could not open viewer: {e}", timeout=4)
        return GLib.SOURCE_REMOVE

    # ------------------------------------------------------------------
    # State extraction
    # ------------------------------------------------------------------

    def _notes_index_to_str(self, idx):
        return ["footnote", "endnote", "none"][idx]

    def _linespace_index_to_str(self, idx):
        return ["1", "1.5", "2"][idx]

    def _bib_sort_index_to_str(self, idx):
        return ["nyt", "nty", "none", "ynt"][idx]

    def _cite_cmd_index_to_str(self, idx):
        return ["autocite", "footcite", "parencite", "cite"][idx]

    def _font_pkg_key(self, idx):
        if idx < 0:
            return "none"
        return FONT_OPTIONS[idx]["key"]

    def _collect_state(self) -> dict:
        font_idx = self._r_font_pkg.get_selected()
        hs_idx = self._r_header_style.get_selected()
        return {
            "title":        self._r_title.get_text(),
            "subtitle":     self._r_subtitle.get_text(),
            "authors":      self._r_authors.get_text(),
            "affiliation":  self._r_affil.get_text(),
            "date":         self._date_entry.get_text(),
            "course":       self._r_course.get_text(),
            "has_abstract": self._r_abstract.get_active(),
            "has_keywords": self._r_keywords.get_active(),
            "use_toc":      self._r_toc.get_active(),

            "cit_style":          self._cit_style,
            "biblatex_style":     self._r_bib_style.get_text(),
            "notes_mode":         self._notes_index_to_str(self._r_notes.get_selected()),
            "typst_notes":        "footnote" if self._r_typst_notes.get_selected() == 0 else "endnote",
            "numbered_heads":     self._r_numbered.get_active(),
            "use_style_headings": self._r_style_headings.get_active(),
            "use_parts":          self._r_use_parts.get_active(),
            "font_pkg":           self._font_pkg_key(font_idx),
            "engine":             self._engine,
            "encoding":           ["utf8", "latin1"][self._r_encoding.get_selected()],

            "paper":        self._paper,
            "font_size":    self._font_size,
            "margin":       str(self._r_margin.get_value()),
            "linespace":    self._linespace_index_to_str(self._r_linespace.get_selected()),
            "parindent":    str(self._r_parindent.get_value()),
            "parskip":      str(int(self._r_parskip.get_value())),
            "microtype":    self._r_microtype.get_active(),
            "use_multicol": self._r_use_multicol.get_active(),
            "num_cols":     int(self._r_num_cols.get_value()),
            "col_rule":     self._r_col_rule.get_active(),
            "col_sep":      str(int(self._r_col_sep.get_value())),

            "header_style":         HEADER_STYLE_KEYS[hs_idx] if hs_idx < len(HEADER_STYLE_KEYS) else "auto",
            "header_rule":          self._r_header_rule.get_active(),
            "suppress_first_header": self._r_suppress_first.get_active(),

            "bib_file":    self._r_bib_file.get_text(),
            "bib_sort":    self._bib_sort_index_to_str(self._r_bib_sort.get_selected()),
            "bib_heading": self._r_bib_heading.get_text(),
            "cite_cmd":    self._cite_cmd_index_to_str(self._r_cite_cmd.get_selected()),
            "print_bib":   self._r_print_bib.get_active(),

            "latex_features": [k for k, r in self._latex_feature_switches.items() if r.get_active()],
            "typst_features": [k for k, r in self._typst_feature_switches.items() if r.get_active()],
            "languages":      [k for k, sw in self._lang_switches.items() if sw.get_active()],
            "format": self._format,

            "chapters": list(self._chapters),

            "custom_latex_preamble": (
                self._r_custom_latex.get_buffer().get_text(
                    self._r_custom_latex.get_buffer().get_start_iter(),
                    self._r_custom_latex.get_buffer().get_end_iter(), False
                ) if hasattr(self, "_r_custom_latex") else ""
            ),
            "custom_typst_preamble": (
                self._r_custom_typst.get_buffer().get_text(
                    self._r_custom_typst.get_buffer().get_start_iter(),
                    self._r_custom_typst.get_buffer().get_end_iter(), False
                ) if hasattr(self, "_r_custom_typst") else ""
            ),

            "typst_csl_style": (
                self._r_typst_csl.get_text().strip()
                if hasattr(self, "_r_typst_csl") else ""
            ),
        }

    # ------------------------------------------------------------------
    # Template generation
    # ------------------------------------------------------------------

    def _build_template(self) -> str:
        state = self._collect_state()
        if self._format == "typst":
            return typst_generate(state)
        return generate(state)

    # ------------------------------------------------------------------
    # Toggle callbacks
    # ------------------------------------------------------------------

    def _on_style_toggled(self, btn):
        if btn.get_active():
            self._cit_style = btn._style_key
            defaults = STYLE_DEFAULTS.get(self._cit_style, STYLE_DEFAULTS["APA"])
            self._r_bib_style.set_text(defaults["biblatex_style"])
            note_idx = {"footnote": 0, "endnote": 1, "none": 2}.get(defaults["notes"], 0)
            self._r_notes.set_selected(note_idx)
            if not self._block_preset:
                self._apply_style_preset(self._cit_style)
            self._dirty_preview()

    def _apply_style_preset(self, style: str) -> None:
        p = _STYLE_PRESETS.get(style)
        if not p:
            return
        if hasattr(self, "_r_font_pkg"):
            for i, opt in enumerate(FONT_OPTIONS):
                if opt["key"] == p["font_pkg"]:
                    self._r_font_pkg.set_selected(i)
                    break
        if hasattr(self, "_fs_btns") and p["font_size"] in self._fs_btns:
            self._fs_btns[p["font_size"]].set_active(True)
        if hasattr(self, "_paper_btns") and p["paper"] in self._paper_btns:
            self._paper_btns[p["paper"]].set_active(True)
        if hasattr(self, "_r_linespace"):
            self._r_linespace.set_selected({"1": 0, "1.5": 1, "2": 2}.get(p["linespace"], 2))
        if hasattr(self, "_r_margin"):
            self._r_margin.set_value(p["margin"])
        if hasattr(self, "_r_parindent"):
            self._r_parindent.set_value(p["parindent"])
        if hasattr(self, "_r_numbered"):
            self._r_numbered.set_active(p["numbered_heads"])
        if hasattr(self, "_r_bib_sort"):
            self._r_bib_sort.set_selected(
                {"nyt": 0, "nty": 1, "none": 2, "ynt": 3}.get(p["bib_sort"], 0))
        if hasattr(self, "_r_cite_cmd"):
            self._r_cite_cmd.set_selected(
                {"autocite": 0, "footcite": 1, "parencite": 2, "cite": 3}.get(p["cite_cmd"], 0))

    def _on_engine_toggled(self, btn):
        if btn.get_active():
            self._engine = btn._eng_key.lower()
            self._check_font_engine_compatibility()
            self._dirty_preview()

    def _on_paper_toggled(self, btn):
        if btn.get_active():
            self._paper = btn._paper_key
            self._dirty_preview()

    def _on_fs_toggled(self, btn):
        if btn.get_active():
            self._font_size = btn._fs_key
            self._dirty_preview()

    def _on_multicol_toggled(self, row, _):
        on = row.get_active()
        self._r_num_cols.set_sensitive(on)
        self._r_col_rule.set_sensitive(on)
        self._r_col_sep.set_sensitive(on)
        self._dirty_preview()

    def _on_format_toggled(self, btn):
        if not btn.get_active():
            return
        self._format = btn._fmt_key
        is_latex = self._format == "latex"
        self._copy_btn.set_tooltip_text(
            "Copy LaTeX code to clipboard" if is_latex else "Copy Typst code to clipboard"
        )
        for w in self._latex_only_widgets:
            w.set_visible(is_latex)
        # Notes rows: LaTeX notes hidden for typst, typst notes hidden for latex
        if hasattr(self, "_r_notes"):
            self._r_notes.set_visible(is_latex)
        if hasattr(self, "_r_typst_notes"):
            self._r_typst_notes.set_visible(not is_latex)
        if hasattr(self, "_latex_features_grp"):
            self._latex_features_grp.set_visible(is_latex)
        if hasattr(self, "_typst_features_grp"):
            self._typst_features_grp.set_visible(not is_latex)
        if hasattr(self, "_latex_preamble_grp"):
            self._latex_preamble_grp.set_visible(is_latex)
        if hasattr(self, "_typst_preamble_grp"):
            self._typst_preamble_grp.set_visible(not is_latex)
        if hasattr(self, "_r_typst_csl_row"):
            self._r_typst_csl_row.set_visible(not is_latex)
        if hasattr(self, "_r_bib_style_row"):
            self._r_bib_style_row.set_visible(is_latex)
        self._dirty_preview()
        self._check_compiler_deps()

    # ------------------------------------------------------------------
    # Date helper
    # ------------------------------------------------------------------

    def _set_today(self, _btn):
        self._date_entry.set_text(datetime.date.today().isoformat())

    # ------------------------------------------------------------------
    # Journal template import
    # ------------------------------------------------------------------

    def _on_import_journal(self, _btn):
        dialog = Gtk.FileDialog(title="Import journal LaTeX template")
        filt = Gtk.FileFilter()
        filt.add_pattern("*.tex")
        filt.add_pattern("*.cls")
        filt.add_pattern("*.sty")
        filt.set_name("LaTeX files (*.tex, *.cls, *.sty)")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filt)
        dialog.set_filters(filters)
        dialog.open(self, None, self._on_import_done)

    def _on_import_done(self, dialog, result):
        try:
            gfile = dialog.open_finish(result)
        except GLib.Error:
            return
        path = gfile.get_path()
        if not path:
            return
        from essay_builder.journal_importer import parse_template, describe_result
        state = parse_template(path)
        if "_error" in state:
            self._show_toast(f"Import failed: {state['_error']}", timeout=4)
            return

        if "_security_warnings" in state:
            warnings = state["_security_warnings"]
            dlg = Adw.AlertDialog(
                heading="Security warning",
                body=(
                    "This file contains potentially dangerous LaTeX commands:\n\n"
                    + "\n".join(f"  • {w}" for w in warnings)
                    + "\n\nOnly import templates from sources you trust."
                ),
            )
            dlg.add_response("cancel", "Cancel")
            dlg.add_response("import", "Import anyway")
            dlg.set_response_appearance("import", Adw.ResponseAppearance.DESTRUCTIVE)

            def _on_warn_response(d, response, _state=state):
                if response == "import":
                    self._do_apply_import(_state)
            dlg.connect("response", _on_warn_response)
            dlg.present(self)
            return

        self._do_apply_import(state)

    def _do_apply_import(self, state: dict):
        from essay_builder.journal_importer import describe_result
        # Merge into current state
        current = self._collect_state()
        current.update({k: v for k, v in state.items() if not k.startswith("_")})
        self._apply_state(current)
        summary = describe_result(state)
        self._show_toast(summary, timeout=4)

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------

    def _show_about(self, _btn):
        about = Adw.AboutWindow()
        about.set_transient_for(self)
        about.set_application_name("Gost")
        about.set_version("0.1.4")
        about.set_comments(
            "Academic Essay Templater.\n"
            "Generate LaTeX and Typst templates for SBL, Chicago, MLA, and APA."
        )
        about.set_developers(["Cal St Francis"])
        about.set_copyright("© 2025 Cal St Francis")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_website("https://github.com/calstfrancis/gost")
        about.set_issue_url("https://github.com/calstfrancis/gost/issues")
        about.set_release_notes(
            "<p>Version 1.2.0</p>"
            "<ul>"
            "<li>Compiled PDF preview (Typst and LaTeX)</li>"
            "<li>Journal LaTeX template importer with security validation</li>"
            "<li>Running headers and footers panel</li>"
            "<li>Typst endnotes support</li>"
            "<li>Startup compiler dependency check — Preview button disabled with clear warning when typst/latexmk not found</li>"
            "<li>Template profiles (save/load/delete)</li>"
            "<li>Language support: Russian, Hebrew, Japanese, Tibetan, Sanskrit, Greek, Chinese</li>"
            "<li>Defaults to Typst format</li>"
            "</ul>"
        )
        about.present()

    # ------------------------------------------------------------------
    # Export / copy
    # ------------------------------------------------------------------

    def _on_copy(self, _btn):
        content = self._build_template()
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(content)
        fmt_label = "Typst" if self._format == "typst" else "TeX"
        self._show_toast(f"{fmt_label} copied to clipboard")

    def _on_export(self, _btn):
        dialog = Gtk.FileDialog(title="Export template file")

        tex_filt = Gtk.FileFilter()
        tex_filt.add_pattern("*.tex")
        tex_filt.set_name("LaTeX files (*.tex)")

        typ_filt = Gtk.FileFilter()
        typ_filt.add_pattern("*.typ")
        typ_filt.set_name("Typst files (*.typ)")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        if self._format == "typst":
            filters.append(typ_filt)
            filters.append(tex_filt)
        else:
            filters.append(tex_filt)
            filters.append(typ_filt)
        dialog.set_filters(filters)

        ext = ".typ" if self._format == "typst" else ".tex"
        raw_title = self._r_title.get_text() or "essay"
        slug = "".join(c if c.isalnum() else "-" for c in raw_title.lower()).strip("-")
        dialog.set_initial_name(f"{slug}{ext}")
        dialog.save(self, None, self._on_export_done)

    def _on_export_done(self, dialog, result):
        try:
            gfile = dialog.save_finish(result)
        except GLib.Error:
            return
        basename = gfile.get_basename()
        use_typst = basename.endswith(".typ")
        state = self._collect_state()
        content = typst_generate(state) if use_typst else generate(state)
        try:
            gfile.replace_contents(
                content.encode("utf-8"), None, False,
                Gio.FileCreateFlags.REPLACE_DESTINATION, None
            )
            if use_typst:
                self._show_toast(f"Exported {basename}")
            else:
                self._write_latexmkrc(gfile)
                self._show_toast(f"Exported {basename} + .latexmkrc")
        except GLib.Error as e:
            self._show_toast(f"Export failed: {e.message}")

    def _write_latexmkrc(self, tex_gfile):
        engine_map = {
            "pdflatex": ("pdflatex", "$pdflatex"),
            "xelatex":  ("xelatex",  "$xelatex"),
            "lualatex": ("lualatex", "$lualatex"),
        }
        cmd, var = engine_map.get(self._engine, ("pdflatex", "$pdflatex"))
        lines = [
            "# .latexmkrc — generated by Gost",
            f"# Engine: {self._engine}",
            "",
            f"{var} = '{cmd} -interaction=nonstopmode -synctex=1 %O %S';",
            "$biber = 'biber %O %S';",
            "$pdf_mode = 1;",
            "@generated_exts = (@generated_exts, 'bbl', 'bcf', 'run.xml');",
        ]
        parent = tex_gfile.get_parent()
        if parent is None:
            return
        rc_file = parent.get_child(".latexmkrc")
        try:
            rc_file.replace_contents(
                "\n".join(lines).encode("utf-8"), None, False,
                Gio.FileCreateFlags.REPLACE_DESTINATION, None
            )
        except GLib.Error:
            pass

    # ------------------------------------------------------------------
    # Toast
    # ------------------------------------------------------------------

    def notify_fonts_installed(self):
        self._show_toast(
            "GOST Type B font installed — restart Gost to activate it",
            timeout=6,
        )
        return False  # GLib.SOURCE_REMOVE

    # ------------------------------------------------------------------
    # Live preview debounce
    # ------------------------------------------------------------------

    def _debounced_compile(self):
        self._live_preview_timeout = None
        self._compile_preview()
        return GLib.SOURCE_REMOVE

    # ------------------------------------------------------------------
    # Panel: Chapters
    # ------------------------------------------------------------------

    def _build_chapters_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        outer.set_margin_top(18); outer.set_margin_bottom(18)
        outer.set_margin_start(18); outer.set_margin_end(18)
        scroll.set_child(outer)

        grp = Adw.PreferencesGroup(
            title="Chapter List",
            description="Add one entry per chapter. Export → single file generates section stubs; "
                        "Export Folder writes one file per chapter.",
        )
        outer.append(grp)

        self._chapters_grp = grp
        self._chapters_list_box = Gtk.ListBox()
        self._chapters_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self._chapters_list_box.add_css_class("boxed-list")
        outer.append(self._chapters_list_box)

        add_btn = Gtk.Button(label="Add Chapter")
        add_btn.add_css_class("pill")
        add_btn.set_halign(Gtk.Align.START)
        add_btn.set_tooltip_text("Add a new chapter entry to the list")
        add_btn.connect("clicked", lambda *_: self._add_chapter())
        outer.append(add_btn)

        folder_btn = Gtk.Button(label="Export as Project Folder…")
        folder_btn.add_css_class("suggested-action")
        folder_btn.add_css_class("pill")
        folder_btn.set_halign(Gtk.Align.START)
        folder_btn.set_tooltip_text(
            "Export main.tex (or main.typ) plus one file per chapter into a chosen folder"
        )
        folder_btn.connect("clicked", self._on_export_folder)
        outer.append(folder_btn)

        self._rebuild_chapters_ui()
        self._content_stack.add_named(scroll, "chapters")

    def _rebuild_chapters_ui(self):
        lb = self._chapters_list_box
        child = lb.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            lb.remove(child)
            child = nxt
        for title in self._chapters:
            self._add_chapter_row(title)

    def _add_chapter(self, title: str = ""):
        self._chapters.append(title)
        self._add_chapter_row(title)
        self._dirty_preview()

    def _add_chapter_row(self, title: str):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row_box.set_margin_start(6); row_box.set_margin_end(6)
        row_box.set_margin_top(4); row_box.set_margin_bottom(4)

        entry = Gtk.Entry()
        entry.set_text(title)
        entry.set_hexpand(True)
        entry.set_placeholder_text("Chapter title")

        def _on_title_changed(e, idx=len(self._chapters) - 1):
            if idx < len(self._chapters):
                self._chapters[idx] = e.get_text()
            self._dirty_preview()
        entry.connect("changed", _on_title_changed)

        del_btn = Gtk.Button()
        del_btn.set_icon_name("list-remove-symbolic")
        del_btn.add_css_class("flat")
        del_btn.add_css_class("circular")

        def _on_remove(_btn, _box=row_box, _entry=entry):
            text = _entry.get_text()
            if text in self._chapters:
                self._chapters.remove(text)
            elif "" in self._chapters:
                self._chapters.remove("")
            self._chapters_list_box.remove(_box.get_parent() or _box)
            self._dirty_preview()
        del_btn.connect("clicked", _on_remove)

        row_box.append(entry)
        row_box.append(del_btn)

        list_row = Gtk.ListBoxRow()
        list_row.set_child(row_box)
        self._chapters_list_box.append(list_row)

    def _on_export_folder(self, _btn):
        if not self._chapters:
            self._show_toast("Add chapters before exporting a project folder.", timeout=3)
            return
        dialog = Gtk.FileDialog(title="Choose project folder")
        dialog.select_folder(self, None, self._on_export_folder_done)

    def _on_export_folder_done(self, dialog, result):
        import os
        try:
            gfile = dialog.select_folder_finish(result)
        except GLib.Error:
            return
        folder = gfile.get_path()
        if not folder:
            return

        state = self._collect_state()
        is_typst = self._format == "typst"
        ext = ".typ" if is_typst else ".tex"

        # Generate main file with multifile flag
        state["multifile"] = True
        if is_typst:
            from essay_builder.typstgen import generate as typst_gen, generate_chapter_file, _chapter_slug
            main_src = typst_gen(state)
        else:
            from essay_builder.texgen import generate as tex_gen, generate_chapter_file, _chapter_slug
            main_src = tex_gen(state)

        try:
            main_path = os.path.join(folder, "main" + ext)
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(main_src)

            cite_cmd = state.get("cite_cmd", "autocite")
            for i, ch in enumerate(self._chapters, 1):
                slug = _chapter_slug(ch, i)
                ch_path = os.path.join(folder, slug + ext)
                if is_typst:
                    from essay_builder.typstgen import generate_chapter_file as gcf
                    ch_src = gcf(ch)
                else:
                    from essay_builder.texgen import generate_chapter_file as gcf
                    ch_src = gcf(ch, cite_cmd)
                with open(ch_path, "w", encoding="utf-8") as f:
                    f.write(ch_src)

            if not is_typst:
                self._write_latexmkrc(Gio.File.new_for_path(main_path))

            n = len(self._chapters)
            self._show_toast(
                f"Exported main{ext} + {n} chapter file(s) to {os.path.basename(folder)}/",
                timeout=4,
            )
        except OSError as e:
            self._show_toast(f"Export failed: {e}", timeout=5)

    # ------------------------------------------------------------------
    # Panel: Custom Code
    # ------------------------------------------------------------------

    def _build_custom_code_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        outer.set_margin_top(18); outer.set_margin_bottom(18)
        outer.set_margin_start(18); outer.set_margin_end(18)
        scroll.set_child(outer)

        def _make_code_area(placeholder: str) -> Gtk.TextView:
            tv = Gtk.TextView()
            tv.set_monospace(True)
            tv.set_wrap_mode(Gtk.WrapMode.NONE)
            tv.set_top_margin(8); tv.set_bottom_margin(8)
            tv.set_left_margin(10); tv.set_right_margin(10)
            tv.get_buffer().set_text(placeholder)
            tv.get_buffer().connect("changed", lambda *_: self._dirty_preview())
            return tv

        # LaTeX preamble group
        self._latex_preamble_grp = Adw.PreferencesGroup(
            title="LaTeX Preamble Additions",
            description="Inserted just before \\begin{document}. Use for custom \\usepackage, \\newcommand, etc.",
        )
        outer.append(self._latex_preamble_grp)
        latex_sw = Gtk.ScrolledWindow()
        latex_sw.set_min_content_height(160)
        latex_sw.set_vexpand(False)
        latex_sw.add_css_class("card")
        self._r_custom_latex = _make_code_area("")
        self._r_custom_latex.get_buffer().set_text("")
        latex_sw.set_child(self._r_custom_latex)
        self._latex_preamble_grp.add(latex_sw)

        # Typst preamble group
        self._typst_preamble_grp = Adw.PreferencesGroup(
            title="Typst Show Rules / Preamble",
            description="Inserted after heading show rules. Use for #show, #let, custom functions.",
        )
        outer.append(self._typst_preamble_grp)
        typst_sw = Gtk.ScrolledWindow()
        typst_sw.set_min_content_height(160)
        typst_sw.set_vexpand(False)
        typst_sw.add_css_class("card")
        self._r_custom_typst = _make_code_area("")
        self._r_custom_typst.get_buffer().set_text("")
        typst_sw.set_child(self._r_custom_typst)
        self._typst_preamble_grp.add(typst_sw)

        self._content_stack.add_named(scroll, "custom_code")

    # ------------------------------------------------------------------
    # Panel: Grammar check (LanguageTool)
    # ------------------------------------------------------------------

    def _build_grammar_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        outer.set_margin_top(18); outer.set_margin_bottom(18)
        outer.set_margin_start(18); outer.set_margin_end(18)
        scroll.set_child(outer)

        from essay_builder.languagetool import LANGUAGE_NAMES
        grp = Adw.PreferencesGroup(
            title="Grammar & Style Check",
            description="Powered by LanguageTool (public API). Paste or type the text you want to check.",
        )
        outer.append(grp)

        self._r_grammar_lang = _combo_row("Language", LANGUAGE_NAMES)
        self._r_grammar_lang.set_tooltip_text("Language for grammar and style checking")
        grp.add(self._r_grammar_lang)

        api_row = Adw.EntryRow(title="API URL (blank = public)")
        api_row.set_text("")
        api_row.set_show_apply_button(False)
        api_row.set_tooltip_text(
            "Leave blank to use the free public LanguageTool API, "
            "or enter a self-hosted instance URL"
        )
        self._r_grammar_api = api_row
        grp.add(api_row)

        # Text input area
        input_sw = Gtk.ScrolledWindow()
        input_sw.set_min_content_height(140)
        input_sw.set_vexpand(False)
        input_sw.add_css_class("card")
        self._r_grammar_input = Gtk.TextView()
        self._r_grammar_input.set_wrap_mode(Gtk.WrapMode.WORD)
        self._r_grammar_input.set_top_margin(8); self._r_grammar_input.set_bottom_margin(8)
        self._r_grammar_input.set_left_margin(10); self._r_grammar_input.set_right_margin(10)
        input_sw.set_child(self._r_grammar_input)

        input_lbl = Gtk.Label(label="Text to check:")
        input_lbl.set_xalign(0)
        input_lbl.add_css_class("heading")
        outer.append(input_lbl)
        outer.append(input_sw)

        btn_row = Gtk.Box(spacing=8)
        check_btn = Gtk.Button(label="Check Grammar")
        check_btn.add_css_class("suggested-action")
        check_btn.set_tooltip_text(
            "Send the text to LanguageTool for grammar and style analysis"
        )
        check_btn.connect("clicked", self._on_grammar_check)
        self._grammar_spinner = Gtk.Spinner()
        self._grammar_status = Gtk.Label(label="")
        self._grammar_status.set_hexpand(True)
        self._grammar_status.set_xalign(0)
        self._grammar_status.add_css_class("dim-label")
        btn_row.append(check_btn)
        btn_row.append(self._grammar_spinner)
        btn_row.append(self._grammar_status)
        outer.append(btn_row)

        self._grammar_results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        outer.append(self._grammar_results_box)

        self._content_stack.add_named(scroll, "grammar")

    def _on_grammar_check(self, _btn):
        if self._grammar_checking:
            return
        buf = self._r_grammar_input.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        if not text.strip():
            self._show_toast("Paste some text to check first.", timeout=2)
            return

        from essay_builder.languagetool import LANGUAGE_CODES
        lang_idx = self._r_grammar_lang.get_selected()
        lang = LANGUAGE_CODES[lang_idx] if lang_idx < len(LANGUAGE_CODES) else "en-US"
        api_url = self._r_grammar_api.get_text().strip() or None

        self._grammar_checking = True
        self._grammar_spinner.start()
        self._grammar_status.set_text("Checking…")

        child = self._grammar_results_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._grammar_results_box.remove(child)
            child = nxt

        import threading as _thr
        t = _thr.Thread(
            target=self._grammar_thread,
            args=(text, lang, api_url),
            daemon=True,
        )
        t.start()

    def _grammar_thread(self, text: str, lang: str, api_url):
        from essay_builder.languagetool import check_text, PUBLIC_API
        url = api_url or PUBLIC_API
        matches, err = check_text(text, lang, url)
        GLib.idle_add(self._grammar_done, matches, err)

    def _grammar_done(self, matches: list, err: str):
        self._grammar_checking = False
        self._grammar_spinner.stop()

        if err:
            self._grammar_status.set_text(f"Error: {err[:80]}")
            return

        if not matches:
            self._grammar_status.set_text("No issues found.")
            return

        self._grammar_status.set_text(f"{len(matches)} issue(s) found")

        for m in matches:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            card.add_css_class("card")
            card.set_margin_top(2)
            card.set_margin_bottom(2)

            msg_lbl = Gtk.Label(label=m["message"])
            msg_lbl.set_xalign(0)
            msg_lbl.set_wrap(True)
            msg_lbl.add_css_class("body")
            card.append(msg_lbl)

            if m.get("context"):
                ctx_lbl = Gtk.Label(label=f'  "{m["context"]}"')
                ctx_lbl.set_xalign(0)
                ctx_lbl.set_wrap(True)
                ctx_lbl.add_css_class("monospace")
                ctx_lbl.add_css_class("dim-label")
                card.append(ctx_lbl)

            if m.get("replacements"):
                sug = "Suggestions: " + " · ".join(m["replacements"])
                sug_lbl = Gtk.Label(label=sug)
                sug_lbl.set_xalign(0)
                sug_lbl.add_css_class("caption")
                card.append(sug_lbl)

            self._grammar_results_box.append(card)
        return GLib.SOURCE_REMOVE

    # ------------------------------------------------------------------
    # Style packs popover
    # ------------------------------------------------------------------

    def _build_style_packs_popover(self) -> Gtk.Popover:
        from essay_builder.style_packs import STYLE_PACKS
        pop = Gtk.Popover()
        pop.set_has_arrow(True)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        outer.set_margin_top(10); outer.set_margin_bottom(10)
        outer.set_margin_start(10); outer.set_margin_end(10)
        outer.set_size_request(320, -1)

        title_lbl = Gtk.Label(label="Apply a style pack")
        title_lbl.add_css_class("heading")
        title_lbl.set_xalign(0)
        outer.append(title_lbl)

        self._packs_list = Gtk.ListBox()
        self._packs_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self._packs_list.add_css_class("boxed-list")

        for name, vals in STYLE_PACKS.items():
            row = Adw.ActionRow(title=name)
            apply_btn = Gtk.Button(label="Apply")
            apply_btn.add_css_class("flat")
            apply_btn.add_css_class("pill")
            apply_btn.set_valign(Gtk.Align.CENTER)
            apply_btn.connect("clicked", lambda _b, n=name: self._on_style_pack_apply(n))
            row.add_suffix(apply_btn)
            self._packs_list.append(row)

        outer.append(self._packs_list)
        pop.set_child(outer)
        return pop

    def _on_style_pack_apply(self, pack_name: str):
        from essay_builder.style_packs import STYLE_PACKS
        pack = STYLE_PACKS.get(pack_name)
        if not pack:
            return
        current = self._collect_state()
        current.update(pack)
        self._apply_state(current)
        self._packs_popover.popdown()
        self._show_toast(f"Applied: {pack_name}", timeout=2)

    # ------------------------------------------------------------------
    # CSL style browser
    # ------------------------------------------------------------------

    def _on_csl_browse(self, _btn):
        from essay_builder.csl_styles import CSL_STYLES
        dlg = Adw.Dialog()
        dlg.set_title("Browse CSL Styles")
        dlg.set_content_width(420)
        dlg.set_content_height(540)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hbar = Adw.HeaderBar()
        hbar.set_show_end_title_buttons(False)
        outer.append(hbar)

        search = Gtk.SearchEntry()
        search.set_margin_top(8); search.set_margin_bottom(8)
        search.set_margin_start(12); search.set_margin_end(12)
        outer.append(search)

        sw = Gtk.ScrolledWindow(vexpand=True)
        lb = Gtk.ListBox()
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        lb.add_css_class("boxed-list")
        lb.set_margin_start(12); lb.set_margin_end(12)
        lb.set_margin_bottom(12)

        rows = []
        for display, style_id in CSL_STYLES:
            row = Adw.ActionRow(title=display, subtitle=style_id)
            use_btn = Gtk.Button(label="Use")
            use_btn.add_css_class("flat")
            use_btn.set_valign(Gtk.Align.CENTER)
            use_btn.connect(
                "clicked",
                lambda _b, sid=style_id, dname=display, d=dlg: self._apply_csl_style(sid, dname, d),
            )
            row.add_suffix(use_btn)
            lb.append(row)
            rows.append((display.lower(), style_id.lower(), row))

        def _filter(entry):
            q = entry.get_text().lower()
            for disp, sid, row in rows:
                row.set_visible(not q or q in disp or q in sid)
        search.connect("search-changed", _filter)

        sw.set_child(lb)
        outer.append(sw)
        dlg.set_child(outer)
        dlg.present(self)

    def _apply_csl_style(self, style_id: str, display: str, dlg):
        if hasattr(self, "_r_typst_csl"):
            self._r_typst_csl.set_text(style_id)
        dlg.close()
        self._show_toast(f"CSL style: {display}", timeout=2)

    # ------------------------------------------------------------------

    def _show_toast(self, msg: str, timeout: int = 2):
        if self._toast_overlay:
            self._toast_overlay.add_toast(Adw.Toast(title=msg, timeout=timeout))
        else:
            print(f"TOAST: {msg}")
