"""
window.py — GTK4 / libadwaita UI for the Academic Essay Builder.
"""

import datetime
from typing import List, Optional, Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GLib, Gio, GObject

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


# ---------------------------------------------------------------------------
# Structure list item
# ---------------------------------------------------------------------------

ELEM_DEFS = [
    ("\\part",          "part",          "Part"),
    ("\\section",       "section",       "Section"),
    ("\\subsection",    "subsection",    "Subsection"),
    ("\\subsubsection", "subsubsection", "Sub-subsection"),
    ("multicol block",  "multicol",      "Multicol"),
    ("blockquote",      "quote",         "Block quote"),
    ("figure",          "figure",        "Figure"),
    ("table",           "table",         "Table"),
    ("epigraph",        "epigraph",      "Epigraph"),
    ("\\appendix",      "appendix",      "Appendix"),
]


class StructItem(GObject.Object):
    __gtype_name__ = "StructItem"

    def __init__(self, elem_type: str, label: str = ""):
        super().__init__()
        self.elem_type = elem_type
        self.label = label


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class EssayBuilderWindow(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Academic Essay Builder")
        
        # Load settings
        self._config = Config()
        width, height = self._config.get_window_size()
        self.set_default_size(width, height)
        
        # Load saved preferences
        self._cit_style = self._config.get("citation_style", "SBL")
        self._engine = self._config.get("engine", "xelatex")
        self._font_size = self._config.get("font_size", "11pt")
        self._paper = self._config.get("paper", "letterpaper")
        
        logger = get_logger()
        logger.info(f"Loaded settings: engine={self._engine}, style={self._cit_style}")

        self._struct_items: List[StructItem] = []
        self._toast_overlay = None   # set by app.py
        self._format = "latex"
        self._copy_btn = None

        self._build_ui()
        
        # Save window size on resize
        self.connect("notify::default-width", self._on_window_resize)
        self.connect("notify::default-height", self._on_window_resize)
    
    def _on_window_resize(self, widget, param):
        """Save window size when changed."""
        width = self.get_default_width()
        height = self.get_default_height()
        if width > 0 and height > 0:
            self._config.set_window_size(width, height)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(outer)
        self.set_content(self._toast_overlay)

        # --- Header bar ---
        hbar = Adw.HeaderBar()
        hbar.set_show_end_title_buttons(True)

        title_widget = Adw.WindowTitle(
            title="Academic Essay Builder",
            subtitle="LaTeX & Typst"
        )
        hbar.set_title_widget(title_widget)

        self._copy_btn = Gtk.Button(label="Copy TeX")
        self._copy_btn.add_css_class("flat")
        self._copy_btn.connect("clicked", self._on_copy)
        hbar.pack_start(self._copy_btn)

        export_btn = Gtk.Button(label="Export")
        export_btn.add_css_class("suggested-action")
        export_btn.connect("clicked", self._on_export)
        hbar.pack_end(export_btn)

        preview_btn = Gtk.Button(label="Preview")
        preview_btn.add_css_class("flat")
        preview_btn.connect("clicked", lambda *_: self._nav_select("preview"))
        hbar.pack_end(preview_btn)

        # Format toggle: LaTeX / Typst
        fmt_box = Gtk.Box(spacing=0)
        fmt_box.add_css_class("linked")
        fmt_box.set_valign(Gtk.Align.CENTER)
        self._fmt_btns = {}
        fmt_group = None
        for fmt_key, fmt_label in (("latex", "LaTeX"), ("typst", "Typst")):
            btn = Gtk.ToggleButton(label=fmt_label)
            if fmt_group is None:
                fmt_group = btn
            else:
                btn.set_group(fmt_group)
            btn._fmt_key = fmt_key
            btn.connect("toggled", self._on_format_toggled)
            fmt_box.append(btn)
            self._fmt_btns[fmt_key] = btn
        self._fmt_btns["latex"].set_active(True)
        hbar.pack_end(fmt_box)

        outer.append(hbar)

        # --- Navigation split view ---
        self._nav_view = Adw.NavigationSplitView()
        outer.append(self._nav_view)

        # Sidebar
        sidebar_page = Adw.NavigationPage(title="Sections")
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_page.set_child(sidebar_box)

        sidebar_hbar = Adw.HeaderBar()
        sidebar_hbar.set_show_end_title_buttons(False)
        sidebar_box.append(sidebar_hbar)

        self._nav_list = Gtk.ListBox()
        self._nav_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._nav_list.add_css_class("navigation-sidebar")
        self._nav_list.connect("row-selected", self._on_nav_selected)

        nav_items = [
            ("document-edit-symbolic",    "Title &amp; Authors",   "metadata"),
            ("document-properties-symbolic", "Citation Style", "style"),
            ("view-grid-symbolic",       "Layout &amp; Spacing",  "layout"),
            ("view-list-ordered-symbolic", "Document Structure", "structure"),
            ("accessories-dictionary-symbolic", "Bibliography", "bib"),
            ("document-print-preview-symbolic", "Preview", "preview"),
        ]
        self._nav_rows = {}
        for icon, label, key in nav_items:
            row = Adw.ActionRow(title=label)
            img = Gtk.Image.new_from_icon_name(icon)
            row.add_prefix(img)
            row.set_activatable(True)
            row._nav_key = key
            self._nav_list.append(row)
            self._nav_rows[key] = row

        sidebar_box.append(self._nav_list)
        self._nav_view.set_sidebar(sidebar_page)

        # Content area (stack)
        content_page = Adw.NavigationPage(title="Essay Builder")
        self._content_stack = Gtk.Stack()
        self._content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        content_page.set_child(self._content_stack)
        self._nav_view.set_content(content_page)

        # Build panels
        self._build_metadata_panel()
        self._build_style_panel()
        self._build_layout_panel()
        self._build_structure_panel()
        self._build_bib_panel()
        self._build_preview_panel()

        # Select first row
        self._nav_list.select_row(self._nav_list.get_row_at_index(0))

    # ------------------------------------------------------------------
    # Panel: Title & Authors
    # ------------------------------------------------------------------

    def _build_metadata_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="Document Identity")
        box.append(grp)

        self._r_title = _entry_row("Title")
        self._r_subtitle = _entry_row("Subtitle", "optional")
        self._r_authors = _entry_row("Author(s)", "Comma-separated for multiple")
        self._r_affil = _entry_row("Affiliation", "Atlantic School of Theology")
        self._r_course = _entry_row("Course / Context", "e.g. THEO 5210")

        for r in (self._r_title, self._r_subtitle, self._r_authors,
                  self._r_affil, self._r_course):
            r.connect("changed", lambda *_: self._dirty_preview())
            grp.add(r)

        # Date row
        date_row = Adw.ActionRow(title="Date")
        self._date_entry = Gtk.Entry()
        self._date_entry.set_placeholder_text("YYYY-MM-DD  or  leave blank for \\today")
        self._date_entry.set_valign(Gtk.Align.CENTER)
        self._date_entry.set_hexpand(True)
        self._date_entry.connect("changed", lambda *_: self._dirty_preview())
        today_btn = Gtk.Button(label="Today")
        today_btn.set_valign(Gtk.Align.CENTER)
        today_btn.add_css_class("flat")
        today_btn.connect("clicked", self._set_today)
        date_row.add_suffix(self._date_entry)
        date_row.add_suffix(today_btn)
        grp.add(date_row)

        grp2 = Adw.PreferencesGroup(title="Front Matter")
        box.append(grp2)
        self._r_abstract = _switch_row("Include abstract block")
        self._r_keywords = _switch_row("Include keywords line")
        for r in (self._r_abstract, self._r_keywords):
            r.connect("notify::active", lambda *_: self._dirty_preview())
            grp2.add(r)

        self._content_stack.add_named(scroll, "metadata")

    # ------------------------------------------------------------------
    # Panel: Citation Style
    # ------------------------------------------------------------------

    def _build_style_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="Citation &amp; Formatting Style")
        box.append(grp)

        # Style selector
        style_row = Adw.ActionRow(title="Base style")
        style_box = Gtk.Box(spacing=4)
        style_box.set_valign(Gtk.Align.CENTER)
        self._style_btns = {}
        style_group = None
        for s in ("SBL", "Chicago", "MLA", "APA"):
            btn = Gtk.ToggleButton(label=s)
            btn.add_css_class("flat")
            if style_group is None:
                style_group = btn
            else:
                btn.set_group(style_group)
            btn._style_key = s
            btn.connect("toggled", self._on_style_toggled)
            style_box.append(btn)
            self._style_btns[s] = btn
        style_row.add_suffix(style_box)
        grp.add(style_row)

        self._r_bib_style = _entry_row("BibLaTeX style string")
        self._r_bib_style.set_text("verbose-note")
        self._r_bib_style.connect("changed", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_style)

        self._r_notes = _combo_row("Notes mode", ["Footnotes", "Endnotes", "None"])
        self._r_notes.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_notes)

        self._r_numbered = _switch_row("Heading numbering")
        self._r_numbered.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_numbered)

        self._r_use_parts = _switch_row("Include \\part level")
        self._r_use_parts.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_use_parts)

        grp2 = Adw.PreferencesGroup(title="Font &amp; Encoding")
        box.append(grp2)

        # Font combo – now using all options from texgen
        font_display_names = [opt["display"] for opt in FONT_OPTIONS]
        self._r_font_pkg = _combo_row("Font package", font_display_names)
        self._r_font_pkg.connect("notify::selected", self._on_font_selected)
        grp2.add(self._r_font_pkg)

        eng_row = Adw.ActionRow(title="Engine")
        eng_box = Gtk.Box(spacing=4)
        eng_box.set_valign(Gtk.Align.CENTER)
        self._engine_btns = {}
        eng_group = None
        for e in ("pdfLaTeX", "XeLaTeX", "LuaLaTeX"):
            btn = Gtk.ToggleButton(label=e)
            btn.add_css_class("flat")
            if eng_group is None:
                eng_group = btn
            else:
                btn.set_group(eng_group)
            btn._eng_key = e
            btn.connect("toggled", self._on_engine_toggled)
            eng_box.append(btn)
            self._engine_btns[e] = btn
        self._engine_btns["XeLaTeX"].set_active(True)
        eng_row.add_suffix(eng_box)
        grp2.add(eng_row)

        self._r_encoding = _combo_row("Input encoding", ["utf8", "latin1"])
        self._r_encoding.connect("notify::selected", lambda *_: self._dirty_preview())
        grp2.add(self._r_encoding)

        # Set active after all rows are created so the toggled callback can access them
        self._style_btns["SBL"].set_active(True)

        self._content_stack.add_named(scroll, "style")

    def _on_font_selected(self, *args):
        self._check_font_engine_compatibility()
        self._dirty_preview()

    def _check_font_engine_compatibility(self):
        selected = self._r_font_pkg.get_selected()
        if selected < 0:
            return
        font_info = FONT_OPTIONS[selected]
        if font_info["requires_fontspec"] and self._engine == "pdflatex":
            self._show_toast(f"⚠️ {font_info['display']} requires XeLaTeX or LuaLaTeX. Switching engine is recommended.",
                             timeout=4)

    # ------------------------------------------------------------------
    # Panel: Layout & Spacing
    # ------------------------------------------------------------------

    def _build_layout_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="Page Layout")
        box.append(grp)

        paper_row = Adw.ActionRow(title="Paper size")
        paper_box = Gtk.Box(spacing=4)
        paper_box.set_valign(Gtk.Align.CENTER)
        self._paper_btns = {}
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
        self._r_margin.connect("notify::value", lambda *_: self._dirty_preview())
        grp.add(self._r_margin)

        fs_row = Adw.ActionRow(title="Font size")
        fs_box = Gtk.Box(spacing=4)
        fs_box.set_valign(Gtk.Align.CENTER)
        self._fs_btns = {}
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
        self._r_linespace.set_selected(1)
        self._r_linespace.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_linespace)

        grp2 = Adw.PreferencesGroup(title="Multi-column")
        box.append(grp2)
        self._r_use_multicol = _switch_row("Enable multicol")
        self._r_use_multicol.connect("notify::active", self._on_multicol_toggled)
        grp2.add(self._r_use_multicol)

        self._r_num_cols = _spin_row("Number of columns", 2, 4, 1, 2)
        self._r_num_cols.connect("notify::value", lambda *_: self._dirty_preview())
        self._r_num_cols.set_sensitive(False)
        grp2.add(self._r_num_cols)

        self._r_col_rule = _switch_row("Column separator rule")
        self._r_col_rule.connect("notify::active", lambda *_: self._dirty_preview())
        self._r_col_rule.set_sensitive(False)
        grp2.add(self._r_col_rule)

        self._r_col_sep = _spin_row("Column sep width (pt)", 4, 40, 1, 14)
        self._r_col_sep.connect("notify::value", lambda *_: self._dirty_preview())
        self._r_col_sep.set_sensitive(False)
        grp2.add(self._r_col_sep)

        grp3 = Adw.PreferencesGroup(title="Paragraph Style")
        box.append(grp3)

        self._r_parindent = _spin_row("Paragraph indent (em)", 0, 4, 0.5, 1.5)
        self._r_parindent.connect("notify::value", lambda *_: self._dirty_preview())
        grp3.add(self._r_parindent)

        self._r_parskip = _spin_row("Paragraph skip (pt)", 0, 18, 1, 0)
        self._r_parskip.connect("notify::value", lambda *_: self._dirty_preview())
        grp3.add(self._r_parskip)

        self._r_microtype = _switch_row("Microtype (protrusion)")
        self._r_microtype.set_active(True)
        self._r_microtype.connect("notify::active", lambda *_: self._dirty_preview())
        grp3.add(self._r_microtype)

        self._content_stack.add_named(scroll, "layout")

    # ------------------------------------------------------------------
    # Panel: Document Structure
    # ------------------------------------------------------------------

    def _build_structure_panel(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Chip toolbar
        toolbar_scroll = Gtk.ScrolledWindow()
        toolbar_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        toolbar_scroll.set_margin_top(10)
        toolbar_scroll.set_margin_bottom(6)
        toolbar_scroll.set_margin_start(12)
        toolbar_scroll.set_margin_end(12)
        chip_box = Gtk.FlowBox()
        chip_box.set_selection_mode(Gtk.SelectionMode.NONE)
        chip_box.set_column_spacing(6)
        chip_box.set_row_spacing(6)

        for cmd, etype, display in ELEM_DEFS:
            btn = Gtk.Button(label=cmd)
            btn.add_css_class("pill")
            btn.set_tooltip_text(f"Add {display}")
            btn._elem_type = etype
            btn.connect("clicked", self._on_elem_add)
            chip_box.append(btn)

        toolbar_scroll.set_child(chip_box)
        outer.append(toolbar_scroll)

        sep = Gtk.Separator()
        outer.append(sep)

        # Structure list
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_margin_top(10)
        scroll.set_margin_bottom(10)
        scroll.set_margin_start(12)
        scroll.set_margin_end(12)

        self._struct_list_box = Gtk.ListBox()
        self._struct_list_box.add_css_class("boxed-list")
        self._struct_list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        self._struct_placeholder = Adw.StatusPage(
            title="No structure yet",
            description="Click elements above to add sections, figures, and more.",
            icon_name="view-list-ordered-symbolic",
        )
        self._struct_placeholder.set_vexpand(True)

        self._struct_stack = Gtk.Stack()
        self._struct_stack.add_named(self._struct_placeholder, "empty")
        self._struct_stack.add_named(self._struct_list_box, "list")
        scroll.set_child(self._struct_stack)
        outer.append(scroll)

        self._content_stack.add_named(outer, "structure")

    # ------------------------------------------------------------------
    # Panel: Bibliography
    # ------------------------------------------------------------------

    def _build_bib_panel(self):
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        box.set_margin_start(18)
        box.set_margin_end(18)
        scroll.set_child(box)

        grp = Adw.PreferencesGroup(title="BibLaTeX / Zotero Bibliography")
        box.append(grp)

        self._r_bib_file = _entry_row("Path to .bib file")
        self._r_bib_file.set_show_apply_button(True)
        self._r_bib_file.connect("apply", lambda *_: self._dirty_preview())
        self._r_bib_file.connect("changed", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_file)

        self._r_print_bib = _switch_row("Print bibliography at end")
        self._r_print_bib.set_active(True)
        self._r_print_bib.connect("notify::active", lambda *_: self._dirty_preview())
        grp.add(self._r_print_bib)

        self._r_bib_heading = _entry_row("Bibliography heading")
        self._r_bib_heading.set_text("Bibliography")
        self._r_bib_heading.connect("changed", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_heading)

        self._r_bib_sort = _combo_row(
            "Sorting",
            ["Author–Year–Title (nyt)", "Author–Title–Year (nty)",
             "None (citation order)", "Year–Name–Title (ynt)"]
        )
        self._r_bib_sort.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_bib_sort)

        self._r_cite_cmd = _combo_row(
            "Default cite command",
            ["\\autocite", "\\footcite", "\\parencite", "\\cite"]
        )
        self._r_cite_cmd.connect("notify::selected", lambda *_: self._dirty_preview())
        grp.add(self._r_cite_cmd)

        # Info banner – make it dismissible
        banner = Adw.Banner(title=(
            "Export from Zotero via BetterBibTeX → Keep Updated, "
            "then paste the absolute path to the .bib file above."
        ))
        banner.set_button_label("Got it")
        banner.connect("button-clicked", lambda b: b.set_revealed(False))
        banner.set_revealed(True)
        box.append(banner)

        self._content_stack.add_named(scroll, "bib")

    # ------------------------------------------------------------------
    # Panel: TeX Preview
    # ------------------------------------------------------------------

    def _build_preview_panel(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        toolbar = Gtk.Box(spacing=6)
        toolbar.set_margin_top(8)
        toolbar.set_margin_bottom(8)
        toolbar.set_margin_start(12)
        toolbar.set_margin_end(12)
        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.add_css_class("flat")
        refresh_btn.connect("clicked", lambda *_: self._refresh_preview())
        toolbar.append(refresh_btn)
        box.append(toolbar)
        box.append(Gtk.Separator())

        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        self._preview_buf = Gtk.TextBuffer()
        self._preview_view = Gtk.TextView(buffer=self._preview_buf)
        self._preview_view.set_editable(False)
        self._preview_view.set_monospace(True)
        self._preview_view.set_left_margin(14)
        self._preview_view.set_top_margin(10)
        scroll.set_child(self._preview_view)
        box.append(scroll)

        self._content_stack.add_named(box, "preview")
        self._preview_dirty = True

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_nav_selected(self, listbox, row):
        if row is None:
            return
        key = row._nav_key
        self._content_stack.set_visible_child_name(key)
        if key == "preview":
            self._refresh_preview()

    def _nav_select(self, key):
        self._nav_list.select_row(self._nav_rows[key])

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
        """Return the internal key for the selected font."""
        if idx < 0:
            return "none"
        return FONT_OPTIONS[idx]["key"]

    def _collect_state(self) -> dict:
        font_idx = self._r_font_pkg.get_selected()
        return {
            "title": self._r_title.get_text(),
            "subtitle": self._r_subtitle.get_text(),
            "authors": self._r_authors.get_text(),
            "affiliation": self._r_affil.get_text(),
            "date": self._date_entry.get_text(),
            "course": self._r_course.get_text(),
            "has_abstract": self._r_abstract.get_active(),
            "has_keywords": self._r_keywords.get_active(),

            "cit_style": self._cit_style,
            "biblatex_style": self._r_bib_style.get_text(),
            "notes_mode": self._notes_index_to_str(self._r_notes.get_selected()),
            "numbered_heads": self._r_numbered.get_active(),
            "use_parts": self._r_use_parts.get_active(),
            "font_pkg": self._font_pkg_key(font_idx),
            "engine": self._engine,
            "encoding": ["utf8", "latin1"][self._r_encoding.get_selected()],

            "paper": self._paper,
            "font_size": self._font_size,
            "margin": str(self._r_margin.get_value()),
            "linespace": self._linespace_index_to_str(self._r_linespace.get_selected()),
            "parindent": str(self._r_parindent.get_value()),
            "parskip": str(int(self._r_parskip.get_value())),
            "microtype": self._r_microtype.get_active(),
            "use_multicol": self._r_use_multicol.get_active(),
            "num_cols": int(self._r_num_cols.get_value()),
            "col_rule": self._r_col_rule.get_active(),
            "col_sep": str(int(self._r_col_sep.get_value())),

            "bib_file": self._r_bib_file.get_text(),
            "bib_sort": self._bib_sort_index_to_str(self._r_bib_sort.get_selected()),
            "bib_heading": self._r_bib_heading.get_text(),
            "cite_cmd": self._cite_cmd_index_to_str(self._r_cite_cmd.get_selected()),
            "print_bib": self._r_print_bib.get_active(),

            "struct_items": [
                {"type": item.elem_type, "label": item.label}
                for item in self._struct_items
            ],
        }

    # ------------------------------------------------------------------
    # Template generation
    # ------------------------------------------------------------------

    def _build_template(self) -> str:
        state = self._collect_state()
        if self._format == "typst":
            return typst_generate(state)
        return generate(state)

    def _dirty_preview(self):
        self._preview_dirty = True

    def _refresh_preview(self):
        content = self._build_template()
        self._preview_buf.set_text(content)
        self._preview_dirty = False

    # ------------------------------------------------------------------
    # Structure panel helpers
    # ------------------------------------------------------------------

    def _on_elem_add(self, btn):
        item = StructItem(btn._elem_type)
        self._struct_items.append(item)
        self._append_struct_row(item)
        self._struct_stack.set_visible_child_name("list")
        self._dirty_preview()

    def _append_struct_row(self, item: StructItem):
        row = Adw.EntryRow(title=item.elem_type)
        row.set_text(item.label)
        row.connect("changed", lambda r, i=item: self._on_struct_label_changed(r, i))

        del_btn = Gtk.Button()
        del_btn.set_icon_name("user-trash-symbolic")
        del_btn.add_css_class("flat")
        del_btn.add_css_class("destructive-action")
        del_btn.set_valign(Gtk.Align.CENTER)
        del_btn.connect("clicked", lambda _, r=row, i=item: self._on_struct_remove(r, i))
        row.add_suffix(del_btn)

        self._struct_list_box.append(row)
        row._struct_item = item

    def _on_struct_label_changed(self, entry_row, item):
        item.label = entry_row.get_text()
        self._dirty_preview()

    def _on_struct_remove(self, row, item):
        self._struct_items.remove(item)
        self._struct_list_box.remove(row)
        if not self._struct_items:
            self._struct_stack.set_visible_child_name("empty")
        self._dirty_preview()

    # ------------------------------------------------------------------
    # Toggle callbacks
    # ------------------------------------------------------------------

    def _on_style_toggled(self, btn):
        if btn.get_active():
            self._cit_style = btn._style_key
            defaults = STYLE_DEFAULTS[self._cit_style]
            self._r_bib_style.set_text(defaults["biblatex_style"])
            note_idx = {"footnote": 0, "endnote": 1, "none": 2}[defaults["notes"]]
            self._r_notes.set_selected(note_idx)
            self._dirty_preview()

    def _on_engine_toggled(self, btn):
        if btn.get_active():
            # Simply lower case: pdfLaTeX -> pdflatex, XeLaTeX -> xelatex, etc.
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
        if btn.get_active():
            self._format = btn._fmt_key
            self._copy_btn.set_label("Copy Typst" if self._format == "typst" else "Copy TeX")
            self._dirty_preview()

    # ------------------------------------------------------------------
    # Date helper
    # ------------------------------------------------------------------

    def _set_today(self, _btn):
        self._date_entry.set_text(datetime.date.today().isoformat())

    # ------------------------------------------------------------------
    # Export / copy with latexmkrc
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
                content.encode("utf-8"),
                None, False,
                Gio.FileCreateFlags.REPLACE_DESTINATION,
                None
            )
            if use_typst:
                self._show_toast(f"Exported {basename}")
            else:
                self._write_latexmkrc(gfile)
                self._show_toast(f"Exported {basename} + .latexmkrc")
        except GLib.Error as e:
            self._show_toast(f"Export failed: {e.message}")

    def _write_latexmkrc(self, tex_gfile):
        """Write a .latexmkrc next to the exported .tex file."""
        engine_map = {
            "pdflatex": ("pdflatex", "$pdflatex"),
            "xelatex":  ("xelatex",  "$xelatex"),
            "lualatex": ("lualatex", "$lualatex"),
        }
        cmd, var = engine_map.get(self._engine, ("pdflatex", "$pdflatex"))

        lines = [
            "# .latexmkrc — generated by Academic Essay Builder",
            f"# Handles the full {self._engine} -> biber -> {self._engine} loop automatically.",
            "# Usage: latexmk -pdf <file>.tex",
            "#        latexmk -pvc <file>.tex   (continuous preview)",
            "",
            f"# Engine: {self._engine}",
            f"{var} = '{cmd} -interaction=nonstopmode -synctex=1 %O %S';",
            "",
            "# Use biber as the bibliography backend",
            "$biber = 'biber %O %S';",
            "",
            "# Generate PDF output",
            "$pdf_mode = 1;",
            "",
            "# Clean up extra biber/biblatex artifacts on latexmk -c",
            "@generated_exts = (@generated_exts, 'bbl', 'bcf', 'run.xml');",
        ]
        rc_content = "\n".join(lines)

        parent = tex_gfile.get_parent()
        if parent is None:
            return
        rc_file = parent.get_child(".latexmkrc")
        try:
            rc_file.replace_contents(
                rc_content.encode("utf-8"), None, False,
                Gio.FileCreateFlags.REPLACE_DESTINATION, None
            )
        except GLib.Error:
            pass  # non-fatal, user can create manually

    # ------------------------------------------------------------------
    # Toast helper (uses overlay set by app.py)
    # ------------------------------------------------------------------

    def _show_toast(self, msg: str, timeout: int = 2):
        if hasattr(self, "_toast_overlay") and self._toast_overlay:
            toast = Adw.Toast(title=msg, timeout=timeout)
            self._toast_overlay.add_toast(toast)
        else:
            # Fallback: print to console
            print(f"TOAST: {msg}")
