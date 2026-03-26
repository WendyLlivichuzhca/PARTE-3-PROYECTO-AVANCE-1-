import os
import sqlite3
import subprocess
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse
from urllib.request import urlretrieve

import customtkinter as ctk

from utils.app_paths import get_downloads_dir
from utils.i18n import tr

# ══════════════════════════════════════════════════════════════
#  PALETTE — Colorido & Amigable (light, vibrant, friendly)
# ══════════════════════════════════════════════════════════════
P = {
    "bg":           "#f0f4ff",     # Soft blue-white background
    "surface":      "#ffffff",     # White card surface
    "surface2":     "#f8f9ff",     # Slightly off-white
    "sidebar":      "#ffffff",     # White sidebar
    "sidebar2":     "#f0f4ff",     # Light bg for sidebar bottom
    "sidebar_act":  "#4f46e5",     # Indigo active
    "primary":      "#4f46e5",     # Indigo 600
    "primary_dark": "#3730a3",     # Indigo 700
    "primary_soft": "#eef2ff",     # Light indigo tint
    "green":        "#10b981",     # Emerald 500
    "green_soft":   "#ecfdf5",     # Light emerald tint
    "purple":       "#8b5cf6",     # Purple 500
    "purple_soft":  "#f5f3ff",     # Light purple tint
    "orange":       "#f97316",     # Orange 500
    "orange_soft":  "#fff7ed",     # Light orange tint
    "red":          "#ef4444",     # Red 500
    "red_soft":     "#fef2f2",     # Light red tint
    "pink":         "#ec4899",     # Pink 500
    "pink_soft":    "#fdf2f8",     # Light pink tint
    "teal":         "#14b8a6",     # Teal 500
    "teal_soft":    "#f0fdfa",     # Light teal tint
    "accent":       "#1a1a3e",     # Dark navy text
    "muted":        "#6b7280",     # Gray-500 muted text
    "border":       "#e5e7f0",     # Light border
    "border2":      "#c7d2fe",     # Indigo-200 border
}

# Typography
F_FAMILY = "Segoe UI"
F_BOLD   = (F_FAMILY, 13, "bold")
F_REG    = (F_FAMILY, 12)
F_TITLE  = (F_FAMILY, 24, "bold")
F_SUB    = (F_FAMILY, 11)

# level → (text color, bg color)
LEVEL_BADGE = {
    "Basico":      (P["green"],  P["green_soft"]),
    "Intermedio":  (P["orange"], P["orange_soft"]),
    "Avanzado":    (P["pink"],   P["pink_soft"]),
}
PAYMENT_BADGE = {
    "Pagado":    (P["green"],  P["green_soft"]),
    "Pendiente": (P["orange"], P["orange_soft"]),
}

NAV_ADMIN = [
    ("instructors", "👤",  "Instructores"),
    ("students",    "🎓",  "Estudiantes"),
    ("courses",     "📚",  "Cursos"),
]
NAV_ACADEMIA = [
    ("learning",   "💳",  "Ventas e Inscripciones"),
    ("payments",   "📖",  "Aprendizaje"),
    ("library",    "📂",  "Biblioteca del Curso"),
    ("community",  "💬",  "Comunidad del Curso"),
    ("quizbank",   "📝",  "Banco de Preguntas"),
    ("exams",      "🚀",  "Evaluaciones"),
    ("reviews",    "⭐",  "Reseñas"),
]


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def _sep(parent, color=None, padx=0, pady=6):
    ctk.CTkFrame(parent, height=1,
                 fg_color=color or P["border"]
                 ).pack(fill="x", padx=padx, pady=pady)


def _label(parent, text, size=12, bold=False, color=None,
           anchor="w", pady=0, padx=0):
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
        text_color=color or P["accent"],
        anchor=anchor,
    ).pack(anchor=anchor, padx=padx, pady=pady)


class View(ctk.CTk):
    # ──────────────────────────────────────────────────────────
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.language   = "es"
        self._data      = {}
        self._maps      = {}
        self._sec_lbl   = {}   # section title labels (i18n)
        self._tree_lbl  = {}   # tree section title labels (i18n)

        self.title("EduCampus — Sistema de Cursos Online")
        self.geometry("1440x860")
        self.minsize(1200, 720)
        self.configure(fg_color=P["bg"])

        self._style_treeview()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_pages()
        self._apply_styles()
        self.change_page("dashboard")
        self.refresh_all()

    # ─── Treeview global style ───────────────────────────────
    def _style_treeview(self):
        s = ttk.Style()
        s.theme_use("default")
        # ── Filas ──────────────────────────────────────────────
        s.configure("Treeview",
                    rowheight=44, font=("Segoe UI", 10),
                    background="#ffffff", foreground="#1a1a3e",
                    fieldbackground="#ffffff", borderwidth=0,
                    relief="flat")
        # ── Encabezados ────────────────────────────────────────
        s.configure("Treeview.Heading",
                    font=("Segoe UI", 9, "bold"),
                    background="#f0f4ff", foreground="#6b7280",
                    relief="flat", borderwidth=0,
                    padding=(8, 6))
        s.map("Treeview.Heading",
              background=[("active", "#eef2ff")],
              foreground=[("active", "#4f46e5")])
        # ── Selección ─────────────────────────────────────────
        s.map("Treeview",
              background=[("selected", "#eef2ff")],
              foreground=[("selected", "#4f46e5")])
        # ── Scrollbars claras ──────────────────────────────────
        s.configure("Vertical.TScrollbar",
                    background="#e5e7f0", troughcolor="#f0f4ff",
                    arrowcolor="#6b7280", borderwidth=0, relief="flat")
        s.configure("Horizontal.TScrollbar",
                    background="#e5e7f0", troughcolor="#f0f4ff",
                    arrowcolor="#6b7280", borderwidth=0, relief="flat")
        s.map("Vertical.TScrollbar",
              background=[("active", "#c7d2fe"), ("pressed", "#818cf8")])
        s.map("Horizontal.TScrollbar",
              background=[("active", "#c7d2fe"), ("pressed", "#818cf8")])

    # ══════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=240, corner_radius=0,
                          fg_color=P["sidebar"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.pack_propagate(False)
        self._sb = sb
        self.nav_buttons = {}
        self.nav_counts  = {}   # badge labels for live counts

        # ── Top accent stripe ────────────────────────────────
        ctk.CTkFrame(sb, height=4, fg_color=P["sidebar_act"],
                     corner_radius=0).pack(fill="x", side="top")

        # ── Logo pill (gradient-like with primary bg) ─────────
        logo_pill = ctk.CTkFrame(sb, fg_color=P["primary"], corner_radius=14)
        logo_pill.pack(fill="x", padx=16, pady=(20, 0))
        lp_inner = ctk.CTkFrame(logo_pill, fg_color="transparent")
        lp_inner.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(lp_inner, text="🎓 EduCampus",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left")

        self.logo_sub = ctk.CTkLabel(sb, text="Plataforma de Cursos Online",
                                     font=ctk.CTkFont(size=10),
                                     text_color=P["muted"])
        self.logo_sub.pack(anchor="w", padx=20, pady=(8, 10))

        # Dashed-style separator
        ctk.CTkFrame(sb, height=1, fg_color=P["border"]).pack(fill="x", padx=14)

        # ── PRINCIPAL ─────────────────────────────────────────
        ctk.CTkLabel(sb, text="PRINCIPAL",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=20, pady=(14, 4))

        # Dashboard row (button + "Hoy" badge)
        dash_row = ctk.CTkFrame(sb, fg_color="transparent")
        dash_row.pack(fill="x", padx=12, pady=2)
        dash_row.grid_columnconfigure(0, weight=1)
        dash_btn = ctk.CTkButton(
            dash_row, text="  🏠   Panel Principal", anchor="w",
            fg_color=P["primary_soft"], hover_color=P["border2"],
            text_color=P["primary"], font=ctk.CTkFont(size=13, weight="bold"),
            height=42, corner_radius=10, border_spacing=10,
            command=lambda: self.change_page("dashboard")
        )
        dash_btn.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(dash_row, text=" Hoy ",
                     font=ctk.CTkFont(size=8, weight="bold"),
                     fg_color=P["primary"], text_color="#ffffff",
                     corner_radius=8, height=18).grid(row=0, column=1, padx=(4, 2))
        self.nav_buttons["dashboard"] = dash_btn

        # ── ADMINISTRACIÓN ────────────────────────────────────
        ctk.CTkLabel(sb, text="ADMINISTRACIÓN",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=20, pady=(14, 4))
        for key, icon, label in NAV_ADMIN:
            self._add_nav_btn_counted(sb, key, icon, label)

        # ── ACADEMIA ──────────────────────────────────────────
        ctk.CTkLabel(sb, text="ACADEMIA",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=20, pady=(14, 4))
        for key, icon, label in NAV_ACADEMIA:
            self._add_nav_btn(sb, key, icon, label)

        # ── Spacer ────────────────────────────────────────────
        ctk.CTkFrame(sb, fg_color="transparent").pack(fill="both", expand=True)

        # ── Promo card ────────────────────────────────────────
        promo = ctk.CTkFrame(sb, fg_color=P["primary"], corner_radius=14)
        promo.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkLabel(promo, text="🎉  ¡Nuevo módulo disponible!",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", padx=14, pady=(14, 2))
        ctk.CTkLabel(promo, text="Reportes avanzados con\ngráficas interactivas",
                     font=ctk.CTkFont(size=10), text_color="#c7d2fe",
                     justify="left").pack(anchor="w", padx=14, pady=(0, 8))
        ctk.CTkButton(promo, text="Explorar →",
                      height=28, corner_radius=8,
                      fg_color=P["primary_dark"], hover_color="#312e81",
                      text_color="#ffffff",
                      font=ctk.CTkFont(size=10, weight="bold")
                      ).pack(fill="x", padx=14, pady=(0, 14))

        # ── Language selector ─────────────────────────────────
        ctk.CTkFrame(sb, height=1, fg_color=P["border"]).pack(fill="x", padx=14)
        self.lang_label = ctk.CTkLabel(sb, text="Idioma / Language",
                                       font=ctk.CTkFont(size=10),
                                       text_color=P["muted"])
        self.lang_label.pack(anchor="w", padx=20, pady=(8, 2))
        self.lang = ctk.CTkOptionMenu(
            sb, values=["es", "en"],
            command=self.set_language,
            fg_color=P["primary_soft"],
            button_color=P["border2"],
            button_hover_color="#818cf8",
            text_color=P["primary"],
            font=ctk.CTkFont(size=12),
        )
        self.lang.set("es")
        self.lang.pack(fill="x", padx=14, pady=(0, 8))

        # ── User profile ──────────────────────────────────────
        ctk.CTkFrame(sb, height=1, fg_color=P["border"]).pack(fill="x", padx=14)
        user_row = ctk.CTkFrame(sb, fg_color="transparent")
        user_row.pack(fill="x", padx=14, pady=(10, 14))
        # Avatar circle
        ctk.CTkLabel(user_row, text="EC",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     fg_color=P["primary"], text_color="#ffffff",
                     corner_radius=10, width=40, height=40).pack(side="left")
        # Name + role
        info_col = ctk.CTkFrame(user_row, fg_color="transparent")
        info_col.pack(side="left", padx=(10, 0), expand=True, fill="x")
        ctk.CTkLabel(info_col, text="Administrador",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=P["accent"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_col, text="Plataforma de Cursos",
                     font=ctk.CTkFont(size=10),
                     text_color=P["muted"], anchor="w").pack(anchor="w")
        # Online dot
        ctk.CTkLabel(user_row, text="⬤",
                     font=ctk.CTkFont(size=9),
                     text_color=P["green"]).pack(side="right", padx=(0, 4))

    def _add_nav_btn(self, sb, key, icon, label):
        btn = ctk.CTkButton(
            sb, text=f"  {icon}   {label}", anchor="w",
            fg_color="transparent", hover_color=P["primary_soft"],
            text_color=P["muted"], font=ctk.CTkFont(size=13, weight="normal"),
            height=42, corner_radius=10, border_spacing=10,
            command=lambda k=key: self.change_page(k),
        )
        btn.pack(fill="x", padx=12, pady=1)
        self.nav_buttons[key] = btn

    def _add_nav_btn_counted(self, sb, key, icon, label):
        """Nav button with a live-count badge on the right."""
        row = ctk.CTkFrame(sb, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=1)
        row.grid_columnconfigure(0, weight=1)
        btn = ctk.CTkButton(
            row, text=f"  {icon}   {label}", anchor="w",
            fg_color="transparent", hover_color=P["primary_soft"],
            text_color=P["muted"], font=ctk.CTkFont(size=13, weight="normal"),
            height=42, corner_radius=10, border_spacing=10,
            command=lambda k=key: self.change_page(k),
        )
        btn.grid(row=0, column=0, sticky="ew")
        badge = ctk.CTkLabel(row, text="",
                             font=ctk.CTkFont(size=9, weight="bold"),
                             fg_color=P["bg"], text_color=P["muted"],
                             corner_radius=8, width=32, height=18)
        badge.grid(row=0, column=1, padx=(4, 2))
        self.nav_buttons[key]  = btn
        self.nav_counts[key]   = badge

    # ══════════════════════════════════════════════════════════
    #  PAGE FACTORY
    # ══════════════════════════════════════════════════════════
    def _build_pages(self):
        self.content = ctk.CTkFrame(self, fg_color=P["bg"],
                                    corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        self.pages      = {}
        self.page_titles = {}
        self._build_dashboard()
        self._build_instructors()
        self._build_students()
        self._build_courses()
        self._build_learning()
        self._build_payments()
        self._build_library()
        self._build_community()
        self._build_quizbank()
        self._build_exams()
        self._build_reviews()

    def _make_page(self, key, icon, title_es, subtitle_es):
        """
        Returns the body frame.
        page row=0: top-bar  (fixed, compact)
        page row=1: body     (expands)
        """
        page = ctk.CTkFrame(self.content, fg_color=P["bg"],
                            corner_radius=0)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        # ── Top bar ─────────────────────────────────────────
        topbar = ctk.CTkFrame(page, fg_color=P["surface"],
                              corner_radius=0, height=72,
                              border_width=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        # Icon badge
        icon_badge = ctk.CTkLabel(topbar,
                        text=f" {icon} ",
                        font=ctk.CTkFont(size=22),
                        fg_color=P["primary_soft"],
                        text_color=P["primary"],
                        corner_radius=12,
                        width=48, height=48)
        icon_badge.grid(row=0, column=0, padx=(24, 16),
                        pady=12, rowspan=1)

        title_lbl = ctk.CTkLabel(topbar, text=title_es,
                                 font=ctk.CTkFont(size=22, weight="bold"),
                                 text_color=P["accent"],
                                 anchor="w")
        title_lbl.grid(row=0, column=1, sticky="sw",
                       padx=0, pady=(16, 0))

        sub_lbl = ctk.CTkLabel(topbar, text=subtitle_es,
                               font=ctk.CTkFont(size=12),
                               text_color=P["muted"],
                               anchor="w")
        sub_lbl.grid(row=0, column=2, sticky="sw",
                     padx=(10, 24), pady=(16, 0))

        # Bottom shadow line
        ctk.CTkFrame(page, height=1,
                     fg_color=P["border"], corner_radius=0
                     ).grid(row=0, column=0, sticky="sew")

        # ── Body ────────────────────────────────────────────
        body = ctk.CTkFrame(page, fg_color=P["bg"], corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew",
                  padx=28, pady=24)

        self.pages[key]       = page
        self.page_titles[key] = (title_lbl, sub_lbl)
        return body

    # ══════════════════════════════════════════════════════════
    #  WIDGET BUILDERS
    # ══════════════════════════════════════════════════════════
    def _card(self, parent, title_key, color=None):
        """White form card packed into left column."""
        wrap = ctk.CTkFrame(parent, fg_color=P["surface"],
                            corner_radius=16, border_width=1,
                            border_color=P["border"])
        wrap.pack(fill="x", pady=(0, 16))

        # Colored top line
        ctk.CTkFrame(wrap, height=4, corner_radius=4,
                     fg_color=color or P["primary"]
                     ).pack(fill="x", padx=0, pady=0)

        lbl = ctk.CTkLabel(wrap,
                           text=tr(self.language, title_key),
                           font=ctk.CTkFont(size=14, weight="bold"),
                           text_color=P["accent"])
        lbl.pack(anchor="w", padx=20, pady=(16, 10))
        self._sec_lbl[title_key] = lbl
        return wrap

    def _field(self, parent, label_text, widget):
        """Label above a form widget, packed into card."""
        ctk.CTkLabel(parent, text=label_text.upper(),
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=20, pady=(0, 4))
        widget.pack(fill="x", padx=20, pady=(0, 14))

    def _right_card(self, body, col=1):
        """White card for the table side."""
        f = ctk.CTkFrame(body, fg_color=P["surface"],
                         corner_radius=14, border_width=1,
                         border_color=P["border"])
        f.grid(row=0, column=col, sticky="nsew", padx=(10, 0))
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)
        return f

    def _left_plain(self, body):
        """Plain (non-scroll) left card."""
        f = ctk.CTkFrame(body, fg_color=P["surface"],
                         corner_radius=14, border_width=1,
                         border_color=P["border"])
        f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        f.grid_columnconfigure(0, weight=1)
        return f

    def _left_scroll(self, body):
        f = ctk.CTkScrollableFrame(body, fg_color=P["bg"],
                                   corner_radius=0,
                                   scrollbar_button_color=P["border2"],
                                   scrollbar_button_hover_color="#818cf8")
        f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        f.grid_columnconfigure(0, weight=1)
        return f

    def _table_header(self, parent, title_key, row=0,
                      color=None, hint=""):
        """Title + optional hint above a table."""
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.grid(row=row, column=0, sticky="ew",
                 padx=16, pady=(16, 6))
        hdr.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(hdr,
                           text=tr(self.language, title_key),
                           font=ctk.CTkFont(size=14, weight="bold"),
                           text_color=color or P["accent"])
        lbl.grid(row=0, column=0, sticky="w")
        self._tree_lbl[title_key] = lbl

        if hint:
            ctk.CTkLabel(hdr, text=hint,
                         font=ctk.CTkFont(size=10),
                         text_color=P["muted"]
                         ).grid(row=1, column=0, sticky="w")

    # Ancho y alineación según nombre de columna
    _COL_CFG = {
        "id":          (45,  "center"),
        "id ":         (45,  "center"),
        "precio":      (80,  "center"),
        "puntaje":     (72,  "center"),
        "progreso":    (80,  "center"),
        "pago":        (90,  "center"),
        "estado":      (90,  "center"),
        "nivel":       (90,  "center"),
        "estrellas":   (75,  "center"),
        "edad":        (55,  "center"),
        "respondió":   (80,  "center"),
        "correcta":    (75,  "center"),
        "cert.":       (55,  "center"),
        "fecha":       (130, "center"),
        "nombre":      (160, "w"),
        "estudiante":  (140, "w"),
        "instructor":  (140, "w"),
        "curso":       (150, "w"),
        "pregunta":    (220, "w"),
        "comentario":  (200, "w"),
        "correo":      (170, "w"),
        "especialidad":(150, "w"),
        "categoria":   (120, "w"),
        "mensaje":     (250, "w"),
        "remitente":   (90,  "w"),
        "alumnos":     (70,  "center"),
        "ingresos":    (90,  "center"),
        "tipo":        (90,  "center"),
        "enlace":      (200, "w"),
    }

    def _tree_frame(self, parent, cols, row=1):
        """Treeview mejorado: anchos inteligentes, orden por clic, scrollbars oscuras."""
        outer = tk.Frame(parent, bg=P["surface"],
                         bd=0, highlightthickness=0)
        outer.grid(row=row, column=0,
                   sticky="nsew", padx=16, pady=(0, 16))
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(outer, columns=cols, show="headings",
                            selectmode="browse")

        # ── Anchos, alineación y ocultar ID ───────────────────
        for c in cols:
            key = c.lower().strip()
            if key == "id":
                # ID oculto: columna de 0px, sin encabezado visible
                tree.heading(c, text="")
                tree.column(c, width=0, minwidth=0, stretch=False)
                continue
            w, anchor = self._COL_CFG.get(key, (120, "w"))
            tree.heading(c, text=c,
                         command=lambda col=c: self._sort_tree(tree, col, False))
            tree.column(c, width=w, anchor=anchor, minwidth=40, stretch=True)

        # ── Scrollbars ────────────────────────────────────────
        sy = ttk.Scrollbar(outer, orient="vertical",   command=tree.yview,
                           style="Vertical.TScrollbar")
        sx = ttk.Scrollbar(outer, orient="horizontal", command=tree.xview,
                           style="Horizontal.TScrollbar")
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        # ── Tags de color ─────────────────────────────────────
        tree.tag_configure("even",       background="#ffffff")
        tree.tag_configure("odd",        background="#f8f9ff")
        tree.tag_configure("pagado",     foreground="#059669",
                           background="#ecfdf5")
        tree.tag_configure("pendiente",  foreground="#d97706",
                           background="#fff7ed")
        tree.tag_configure("aprobado",   foreground="#059669",
                           background="#ecfdf5")
        tree.tag_configure("reprobado",  foreground="#dc2626",
                           background="#fef2f2")
        tree.tag_configure("basico",     foreground="#059669")
        tree.tag_configure("intermedio", foreground="#d97706")
        tree.tag_configure("avanzado",   foreground="#be185d")

        # ── Estado vacío ──────────────────────────────────────
        empty = tk.Label(outer,
                         text="📭   Sin datos aún",
                         font=("Segoe UI", 11), fg="#6b7280",
                         bg=P["surface"], justify="center")
        outer._empty_lbl = empty
        outer._tree      = tree
        return outer

    def _sort_tree(self, tree, col, reverse):
        """Ordena la tabla al hacer clic en el encabezado."""
        try:
            data = [(tree.set(k, col), k) for k in tree.get_children("")]
            try:
                data.sort(key=lambda t: float(t[0].replace("$","").replace("%","").replace(" pts","")),
                          reverse=reverse)
            except ValueError:
                data.sort(key=lambda t: t[0].lower(), reverse=reverse)
            for i, (_, k) in enumerate(data):
                tree.move(k, "", i)
                tag = "even" if i % 2 == 0 else "odd"
                tree.item(k, tags=(tag,))
            tree.heading(col,
                         command=lambda: self._sort_tree(tree, col, not reverse))
        except Exception:
            pass

    # Compat alias
    def _tree(self, parent, cols):
        return self._tree_frame(parent, cols, row=0)

    # ══════════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════════
    def _build_dashboard(self):
        from datetime import datetime
        # Build custom page (no _make_page — has its own greeting topbar)
        page = ctk.CTkFrame(self.content, fg_color=P["bg"], corner_radius=0)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        # ── Custom topbar ─────────────────────────────────────
        topbar = ctk.CTkFrame(page, fg_color=P["surface"],
                              corner_radius=0, height=76, border_width=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)

        # Left: greeting
        greet_col = ctk.CTkFrame(topbar, fg_color="transparent")
        greet_col.grid(row=0, column=0, sticky="w", padx=(28, 0), pady=12)
        ctk.CTkLabel(greet_col, text="👋  ¡Bienvenido a EduCampus!",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=P["accent"]).pack(anchor="w")
        today = datetime.now()
        _days   = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        _months = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                   "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        date_str = f"{_days[today.weekday()]}, {today.day} de {_months[today.month-1]} — todo va muy bien hoy ✨"
        ctk.CTkLabel(greet_col, text=date_str,
                     font=ctk.CTkFont(size=11),
                     text_color=P["muted"]).pack(anchor="w")

        # Right: search (decorative) + buttons
        right_top = ctk.CTkFrame(topbar, fg_color="transparent")
        right_top.grid(row=0, column=1, sticky="e", padx=(0, 28))
        search_wrap = ctk.CTkFrame(right_top, fg_color=P["bg"],
                                   corner_radius=12, border_width=1,
                                   border_color=P["border"])
        search_wrap.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(search_wrap, text="🔍  Buscar en el sistema...",
                     font=ctk.CTkFont(size=11),
                     text_color=P["muted"]).pack(padx=16, pady=10)
        ctk.CTkButton(right_top, text="📊  Reportes",
                      height=38, corner_radius=10,
                      fg_color=P["surface"], hover_color=P["primary_soft"],
                      text_color=P["muted"], border_width=1, border_color=P["border"],
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=lambda: None).pack(side="left", padx=(0, 10))
        ctk.CTkButton(right_top, text="  + Nuevo Curso",
                      height=38, corner_radius=10,
                      fg_color=P["primary"], hover_color=P["primary_dark"],
                      text_color="#ffffff",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=lambda: self.change_page("courses")).pack(side="left")

        # Bottom border
        ctk.CTkFrame(page, height=1, fg_color=P["border"],
                     corner_radius=0).grid(row=0, column=0, sticky="sew")

        # ── Scrollable body ───────────────────────────────────
        scroll = ctk.CTkScrollableFrame(page, fg_color=P["bg"],
                                        scrollbar_button_color=P["border2"],
                                        scrollbar_button_hover_color="#818cf8")
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=22)
        inner.grid_columnconfigure(0, weight=1)

        # ── Row 1: Quick-action cards ─────────────────────────
        qa_frame = ctk.CTkFrame(inner, fg_color="transparent")
        qa_frame.pack(fill="x", pady=(0, 18))
        qa_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="qa")
        quick_actions = [
            ("🎨", "Agregar Instructor", "Gestionar equipo",  "instructors", P["primary_soft"], P["primary"]),
            ("📚", "Crear curso",        "Nuevo contenido",    "courses",     P["green_soft"],   P["green"]),
            ("💳", "Ver inscripciones",  "Gestionar pagos",    "learning",    P["orange_soft"],  P["orange"]),
            ("📝", "Nueva evaluación",   "Crear quiz",         "quizbank",    P["purple_soft"],  P["purple"]),
        ]
        for col, (ico, title, sub, pg, bg, fg) in enumerate(quick_actions):
            card = ctk.CTkFrame(qa_frame, fg_color=P["surface"], corner_radius=16,
                                border_width=1, border_color=P["border"])
            card.grid(row=0, column=col, padx=(0 if col == 0 else 12, 0), sticky="nsew")
            ico_lbl = ctk.CTkLabel(card, text=ico, font=ctk.CTkFont(size=28),
                                   fg_color=bg, corner_radius=12, width=54, height=54)
            ico_lbl.pack(padx=20, pady=(20, 10))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=P["accent"]).pack(padx=16)
            ctk.CTkLabel(card, text=sub, font=ctk.CTkFont(size=10),
                         text_color=P["muted"]).pack(padx=16, pady=(2, 18))
            for w in (card, ico_lbl):
                w.bind("<Button-1>", lambda e, p=pg: self.change_page(p))

        # ── Row 2: KPI stat cards ─────────────────────────────
        kpi_frame = ctk.CTkFrame(inner, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 18))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kp")
        self.stats = {}
        kpi_cfg = [
            ("instructors", "🎨", "Instructores",    P["primary"], P["primary_soft"]),
            ("students",    "🎓", "Estudiantes",      P["purple"],  P["purple_soft"]),
            ("courses",     "📚", "Cursos activos",   P["green"],   P["green_soft"]),
            ("revenue",     "💰", "Ingresos del mes", P["orange"],  P["orange_soft"]),
        ]
        for col, (k, ico, lbl, fg, bg) in enumerate(kpi_cfg):
            card = ctk.CTkFrame(kpi_frame, fg_color=P["surface"], corner_radius=18,
                                border_width=1, border_color=P["border"])
            card.grid(row=0, column=col, padx=(0 if col == 0 else 12, 0), sticky="nsew")
            # Top row: icon + trend badge
            top_r = ctk.CTkFrame(card, fg_color="transparent")
            top_r.pack(fill="x", padx=18, pady=(18, 8))
            ctk.CTkLabel(top_r, text=ico, font=ctk.CTkFont(size=22),
                         fg_color=bg, corner_radius=12,
                         width=46, height=46).pack(side="left")
            ctk.CTkLabel(top_r, text=" +3% ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=P["green_soft"], text_color=P["green"],
                         corner_radius=8, height=20).pack(side="right")
            val = ctk.CTkLabel(card, text="0",
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color=fg, anchor="w")
            val.pack(anchor="w", padx=18, pady=(0, 4))
            ctk.CTkLabel(card, text=lbl, font=ctk.CTkFont(size=11),
                         text_color=P["muted"], anchor="w").pack(anchor="w", padx=18, pady=(0, 16))
            self.stats[k] = val
        # Dummy labels for keys expected by old refresh (paid_enrollments, completed_enrollments)
        self.stats["paid_enrollments"]      = ctk.CTkLabel(inner, text="0")
        self.stats["completed_enrollments"] = ctk.CTkLabel(inner, text="0")

        # ── Row 3: Courses list + Top Students ────────────────
        mid = ctk.CTkFrame(inner, fg_color="transparent")
        mid.pack(fill="x", pady=(0, 18))
        mid.grid_columnconfigure(0, weight=6)
        mid.grid_columnconfigure(1, weight=4)
        mid.grid_rowconfigure(0, weight=1)

        # Left: Cursos activos
        c_card = ctk.CTkFrame(mid, fg_color=P["surface"], corner_radius=16,
                              border_width=1, border_color=P["border"])
        c_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        c_card.grid_columnconfigure(0, weight=1)
        c_hdr = ctk.CTkFrame(c_card, fg_color="transparent")
        c_hdr.pack(fill="x", padx=18, pady=(16, 4))
        c_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(c_hdr, text="📚  Cursos activos",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=P["accent"]).pack(side="left")
        ctk.CTkButton(c_hdr, text="Ver todos →", height=26, corner_radius=8,
                      fg_color=P["primary_soft"], hover_color=P["border2"],
                      text_color=P["primary"], font=ctk.CTkFont(size=10, weight="bold"),
                      command=lambda: self.change_page("courses")).pack(side="right")
        ctk.CTkLabel(c_card, text="Seguimiento de progreso semanal",
                     font=ctk.CTkFont(size=10), text_color=P["muted"]
                     ).pack(anchor="w", padx=18, pady=(0, 10))
        ctk.CTkFrame(c_card, height=1, fg_color=P["border"]).pack(fill="x", padx=18)
        self.dash_courses_frame = ctk.CTkFrame(c_card, fg_color="transparent")
        self.dash_courses_frame.pack(fill="both", expand=True)

        # Right: Top Estudiantes
        s_card = ctk.CTkFrame(mid, fg_color=P["surface"], corner_radius=16,
                              border_width=1, border_color=P["border"])
        s_card.grid(row=0, column=1, sticky="nsew")
        s_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(s_card, text="🏆  Top Estudiantes",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=P["accent"]).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(s_card, text="Mejores puntuaciones esta semana",
                     font=ctk.CTkFont(size=10), text_color=P["muted"]
                     ).pack(anchor="w", padx=18, pady=(0, 10))
        ctk.CTkFrame(s_card, height=1, fg_color=P["border"]).pack(fill="x", padx=18)
        self.dash_students_frame = ctk.CTkFrame(s_card, fg_color="transparent")
        self.dash_students_frame.pack(fill="both", expand=True)

        # ── Row 4: Panel del Instructor ───────────────────────
        instr_card = ctk.CTkFrame(inner, fg_color=P["surface"], corner_radius=16,
                                  border_width=1, border_color=P["border"])
        instr_card.pack(fill="x", pady=(0, 18))
        instr_card.grid_columnconfigure(0, weight=1)

        instr_hdr = ctk.CTkFrame(instr_card, fg_color="transparent")
        instr_hdr.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(instr_hdr, text="🎨  Panel del Instructor",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=P["accent"]).pack(side="left")
        ctk.CTkLabel(instr_hdr, text="Estadísticas de ingresos y alumnos activos",
                     font=ctk.CTkFont(size=10),
                     text_color=P["muted"]).pack(side="left", padx=(10, 0))
        ctk.CTkFrame(instr_card, height=1, fg_color=P["border"]).pack(fill="x", padx=18)

        # Treeview del panel instructor
        from tkinter import ttk as _ttk
        instr_tree_wrap = tk.Frame(instr_card, bg=P["surface"], bd=0, highlightthickness=0)
        instr_tree_wrap.pack(fill="both", expand=True, padx=18, pady=(8, 14))
        instr_tree_wrap.grid_rowconfigure(0, weight=1)
        instr_tree_wrap.grid_columnconfigure(0, weight=1)
        self.instructor_panel_tree = _ttk.Treeview(
            instr_tree_wrap,
            columns=("Instructor", "Alumnos Activos", "Ingresos"),
            show="headings",
            height=5,
        )
        for col, w, anchor in [("Instructor", 260, "w"),
                                ("Alumnos Activos", 130, "center"),
                                ("Ingresos", 120, "center")]:
            self.instructor_panel_tree.heading(col, text=col)
            self.instructor_panel_tree.column(col, width=w, anchor=anchor, minwidth=60)
        instr_sy = _ttk.Scrollbar(instr_tree_wrap, orient="vertical",
                                   command=self.instructor_panel_tree.yview,
                                   style="Vertical.TScrollbar")
        self.instructor_panel_tree.configure(yscrollcommand=instr_sy.set)
        self.instructor_panel_tree.grid(row=0, column=0, sticky="nsew")
        instr_sy.grid(row=0, column=1, sticky="ns")

        # ── Row 5: Bottom mini-stats ──────────────────────────
        bot = ctk.CTkFrame(inner, fg_color="transparent")
        bot.pack(fill="x")
        bot.grid_columnconfigure((0, 1, 2), weight=1, uniform="bt")
        bot_cfg = [
            ("materials",  "📁", "Materiales subidos",   P["orange"], P["orange_soft"], "+8 esta semana"),
            ("quizzes_a",  "📝", "Evaluaciones activas", P["purple"], P["purple_soft"], "+3 nuevas"),
            ("satisf",     "⭐", "Satisfacción general", P["green"],  P["green_soft"],  "+2% vs mes anterior"),
        ]
        self.bottom_stats = {}
        for col, (k, ico, lbl, fg, bg, hint) in enumerate(bot_cfg):
            bcard = ctk.CTkFrame(bot, fg_color=P["surface"], corner_radius=16,
                                 border_width=1, border_color=P["border"])
            bcard.grid(row=0, column=col, padx=(0 if col == 0 else 12, 0), sticky="nsew")
            b_row = ctk.CTkFrame(bcard, fg_color="transparent")
            b_row.pack(fill="x", padx=18, pady=(18, 6))
            ctk.CTkLabel(b_row, text=ico, font=ctk.CTkFont(size=22),
                         fg_color=bg, corner_radius=10,
                         width=44, height=44).pack(side="left")
            val_col = ctk.CTkFrame(b_row, fg_color="transparent")
            val_col.pack(side="left", padx=(12, 0))
            bval = ctk.CTkLabel(val_col, text="0",
                                font=ctk.CTkFont(size=22, weight="bold"),
                                text_color=P["accent"], anchor="w")
            bval.pack(anchor="w")
            ctk.CTkLabel(val_col, text=lbl, font=ctk.CTkFont(size=10),
                         text_color=P["muted"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(bcard, text=hint,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=P["green"], anchor="w").pack(anchor="w", padx=18, pady=(0, 14))
            self.bottom_stats[k] = bval

        self.pages["dashboard"]       = page
        self.page_titles["dashboard"] = (ctk.CTkLabel(page, text=""),
                                         ctk.CTkLabel(page, text=""))

    # ══════════════════════════════════════════════════════════
    #  INSTRUCTORES
    # ══════════════════════════════════════════════════════════
    def _build_instructors(self):
        body = self._make_page(
            "instructors", "\u25A1",
            "Instructores",
            "Gestiona el equipo docente de la plataforma")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        # Left
        left = self._left_plain(body)

        ctk.CTkLabel(left,
                     text="Nuevo Instructor",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=P["accent"]
                     ).pack(anchor="w", padx=18, pady=(22, 4))
        ctk.CTkLabel(left,
                     text="Completa los datos del docente",
                     font=ctk.CTkFont(size=11),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=18, pady=(0, 14))
        ctk.CTkFrame(left, height=1,
                     fg_color=P["border"]
                     ).pack(fill="x", padx=18, pady=(0, 14))

        ctk.CTkLabel(left, text="Nombre completo",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=18)
        self.i_name = ctk.CTkEntry(left, height=40, corner_radius=8,
                                   placeholder_text="Ej. Ana Martinez")
        self.i_name.pack(fill="x", padx=18, pady=(4, 12))

        ctk.CTkLabel(left, text="Especialidad",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=18)
        self.i_spec = ctk.CTkEntry(left, height=40, corner_radius=8,
                                   placeholder_text="Ej. Python, Data Science")
        self.i_spec.pack(fill="x", padx=18, pady=(4, 18))

        self.i_save_button = ctk.CTkButton(
            left, text="  + Registrar Instructor",
            height=42, corner_radius=10,
            fg_color=P["primary"], hover_color=P["primary_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.handle_create_instructor)
        self.i_save_button.pack(fill="x", padx=18, pady=(0, 12))

        self.instr_count_label = ctk.CTkLabel(
            left, text="",
            font=ctk.CTkFont(size=11), text_color=P["muted"])
        self.instr_count_label.pack(anchor="w", padx=18, pady=(0, 18))

        # Right
        right = self._right_card(body)
        self._table_header(right, "instructors", row=0)
        self.instructors_tree = self._tree_frame(
            right, ("ID", "Nombre", "Especialidad"), row=1)

    # ══════════════════════════════════════════════════════════
    #  ESTUDIANTES
    # ══════════════════════════════════════════════════════════
    def _build_students(self):
        body = self._make_page(
            "students", "\u25CF",
            "Estudiantes",
            "Administra los estudiantes registrados en la plataforma")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_plain(body)

        ctk.CTkLabel(left, text="Nuevo Estudiante",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=P["accent"]
                     ).pack(anchor="w", padx=18, pady=(22, 4))
        ctk.CTkLabel(left, text="Completa los datos del alumno",
                     font=ctk.CTkFont(size=11), text_color=P["muted"]
                     ).pack(anchor="w", padx=18, pady=(0, 14))
        ctk.CTkFrame(left, height=1, fg_color=P["border"]
                     ).pack(fill="x", padx=18, pady=(0, 14))

        for lbl_text, attr, ph in [
            ("Paso 1: Nombre del alumno", "s_name", "Nombre y Apellido del estudiante"),
            ("Paso 2: Edad",            "s_age",  "Ejem: 20"),
            ("Paso 3: Correo de contacto", "s_email", "correo@ejemplo.com"),
        ]:
            ctk.CTkLabel(left, text=lbl_text,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=P["muted"]
                         ).pack(anchor="w", padx=18)
            entry = ctk.CTkEntry(left, height=40, corner_radius=8,
                                 placeholder_text=ph)
            entry.pack(fill="x", padx=18, pady=(4, 12))
            setattr(self, attr, entry)

        self.s_save_button = ctk.CTkButton(
            left, text="  + Registrar Estudiante",
            height=42, corner_radius=10,
            fg_color=P["green"], hover_color="#047857",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.handle_create_student)
        self.s_save_button.pack(fill="x", padx=18, pady=(6, 12))

        self.student_count_label = ctk.CTkLabel(
            left, text="",
            font=ctk.CTkFont(size=11), text_color=P["muted"])
        self.student_count_label.pack(anchor="w", padx=18, pady=(0, 18))

        right = self._right_card(body)
        self._table_header(right, "students", row=0)
        self.students_tree = self._tree_frame(
            right, ("ID", "Nombre", "Edad", "Correo"), row=1)

    # ══════════════════════════════════════════════════════════
    #  CURSOS
    # ══════════════════════════════════════════════════════════
    def _build_courses(self):
        body = self._make_page(
            "courses", "\u25B6",
            "Catalogo de Cursos",
            "Crea y organiza los cursos disponibles para inscripcion")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)
        c_card = self._card(left, "create_course", color=P["purple"])

        fields = [
            ("Nombre del curso",  "c_name",  ctk.CTkEntry,   {"placeholder_text": "Ej: Excel, Java, etc."}),
            ("Categoria / Área",  "c_cat",   ctk.CTkEntry,   {"placeholder_text": "Ej: Ofimática, IT"}),
            ("Precio (USD)",      "c_price", ctk.CTkEntry,   {"placeholder_text": "Ej. 49.99"}),
        ]
        for lbl, attr, Widget, kwargs in fields:
            ctk.CTkLabel(c_card, text=lbl,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=P["muted"]
                         ).pack(anchor="w", padx=16)
            w = Widget(c_card, height=40, corner_radius=8, **kwargs)
            w.pack(fill="x", padx=16, pady=(4, 10))
            setattr(self, attr, w)

        ctk.CTkLabel(c_card, text="Nivel",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=16)
        self.c_level = ctk.CTkOptionMenu(
            c_card, values=["Basico", "Intermedio", "Avanzado"],
            height=40, corner_radius=8)
        self.c_level.set("Basico")
        self.c_level.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(c_card, text="Instructor",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=16)
        self.c_instructor = ctk.CTkComboBox(c_card, values=[], height=40,
                                            corner_radius=8)
        self.c_instructor.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(c_card, text="Descripcion",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]
                     ).pack(anchor="w", padx=16)
        self.c_desc = ctk.CTkTextbox(c_card, height=72, corner_radius=8)
        self.c_desc.pack(fill="x", padx=16, pady=(4, 12))

        self.c_save_button = ctk.CTkButton(
            c_card, text="  + Publicar Curso",
            height=42, corner_radius=10,
            fg_color=P["purple"], hover_color="#6d28d9",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.handle_create_course)
        self.c_save_button.pack(fill="x", padx=16, pady=(0, 16))

        self.course_count_label = ctk.CTkLabel(
            left, text="", font=ctk.CTkFont(size=11), text_color=P["muted"])
        self.course_count_label.pack(anchor="w", padx=4, pady=(4, 8))

        # Right
        right = ctk.CTkFrame(body, fg_color=P["surface"],
                             corner_radius=14, border_width=1,
                             border_color=P["border"])
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Header with filter and Search
        hdr = ctk.CTkFrame(right, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))
        hdr.grid_columnconfigure(1, weight=1)

        lbl_c = ctk.CTkLabel(hdr, text="📚 " + tr(self.language, "courses"),
                             font=ctk.CTkFont(size=15, weight="bold"),
                             text_color=P["accent"])
        lbl_c.grid(row=0, column=0, sticky="w")
        self._tree_lbl["courses"] = lbl_c

        # Search bar
        self.c_search = ctk.CTkEntry(hdr, placeholder_text="🔍 Buscar curso...",
                                     height=36, width=200, corner_radius=10)
        self.c_search.grid(row=0, column=1, sticky="e", padx=(0, 16))
        self.c_search.bind("<KeyRelease>", lambda e: self.refresh_courses_tree())

        # Etiqueta del filtro de nivel (requerida por set_language para i18n)
        self.level_filter_label = ctk.CTkLabel(
            hdr,
            text=tr(self.language, "level_filter"),
            font=ctk.CTkFont(size=11),
            text_color=P["muted"],
        )
        self.level_filter_label.grid(row=1, column=2, sticky="e", pady=(2, 0))

        self.course_filter = ctk.CTkOptionMenu(
            hdr, values=["Todos", "Basico", "Intermedio", "Avanzado"],
            command=lambda _: self.refresh_courses_tree(),
            height=36, corner_radius=10,
            width=120)
        self.course_filter.set("Todos")
        self.course_filter.grid(row=0, column=2, sticky="e")

        self.courses_tree = self._tree_frame(
            right,
            ("ID", "Curso", "Categoria", "Nivel", "Precio", "Instructor"),
            row=1)

    # ══════════════════════════════════════════════════════════
    #  VENTAS E INSCRIPCIONES
    # ══════════════════════════════════════════════════════════
    def _build_learning(self):
        body = self._make_page(
            "learning", "💳",
            "Ventas e Inscripciones",
            "Registra nuevas inscripciones y gestiona los pagos")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        e_card = self._card(left, "enrollment_payments", color=P["primary"])
        ctk.CTkLabel(e_card, text="Paso 1: Selecciona al estudiante",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.e_student = ctk.CTkComboBox(e_card, values=[], height=40,
                                         corner_radius=8)
        self.e_student.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(e_card, text="Paso 2: ¿A qué curso lo inscribes?",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.e_course = ctk.CTkComboBox(e_card, values=[], height=40,
                                        corner_radius=8)
        self.e_course.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(e_card, text="Estado de pago",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.e_payment = ctk.CTkOptionMenu(e_card, values=["Pendiente", "Pagado"],
                                           height=40, corner_radius=8)
        self.e_payment.set("Pendiente")
        self.e_payment.pack(fill="x", padx=16, pady=(4, 10))

        self.e_save_button = ctk.CTkButton(
            e_card, text="  + Registrar Inscripcion",
            height=42, corner_radius=10,
            fg_color=P["primary"], hover_color=P["primary_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.handle_create_enrollment)
        self.e_save_button.pack(fill="x", padx=16, pady=(0, 16))

        right = self._right_card(body)
        self.enrollments_label = ctk.CTkLabel(
            right, text=tr(self.language, "active_enrollments"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=P["accent"])
        self.enrollments_label.grid(row=0, column=0,
                                    padx=18, pady=(18, 6), sticky="w")
        self.learning_tree = self._tree_frame(
            right,
            ("ID", "Estudiante", "Curso", "Precio", "Pago", "Cert."),
            row=1)
        self.enrollments_tree = self.learning_tree   # backward compat

    # ══════════════════════════════════════════════════════════
    #  APRENDIZAJE  (progreso + pago + certificado)
    # ══════════════════════════════════════════════════════════
    def _build_payments(self):
        body = self._make_page(
            "payments", "📖",
            "Aprendizaje",
            "Seguimiento del progreso, pagos y certificados del estudiante")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        # ── Ruta de Aprendizaje ────────────────────────────────
        p_card = self._card(left, "course_progress", color=P["green"])
        ctk.CTkLabel(p_card, text="Inscripcion",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.p_enrollment = ctk.CTkComboBox(p_card, values=[],
                                            command=self.select_enrollment,
                                            height=40, corner_radius=8)
        self.p_enrollment.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(p_card, text="Porcentaje completado (0-100)",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.p_value = ctk.CTkEntry(p_card, height=40, corner_radius=8,
                                    placeholder_text="0 - 100")
        self.p_value.pack(fill="x", padx=16, pady=(4, 8))

        self.p_bar = ctk.CTkProgressBar(p_card, height=8, corner_radius=4,
                                        progress_color=P["green"],
                                        fg_color=P["green_soft"])
        self.p_bar.pack(fill="x", padx=16, pady=(0, 4))
        self.p_bar.set(0)
        self.p_label = ctk.CTkLabel(p_card, text="0%",
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    text_color=P["green"])
        self.p_label.pack(anchor="e", padx=16, pady=(0, 8))

        self.p_update_button = ctk.CTkButton(
            p_card, text="  Actualizar progreso",
            height=40, corner_radius=10,
            fg_color=P["green"], hover_color="#047857",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_update_progress)
        self.p_update_button.pack(fill="x", padx=16, pady=(0, 8))

        self.p_payment_button = ctk.CTkButton(
            p_card, text="  Registrar pago",
            height=40, corner_radius=10,
            fg_color=P["orange"], hover_color="#b45309",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_register_payment)
        self.p_payment_button.pack(fill="x", padx=16, pady=(0, 8))

        self.p_certificate_button = ctk.CTkButton(
            p_card, text="  🏆 Generar Certificado PDF",
            height=40, corner_radius=10,
            fg_color=P["purple"], hover_color="#6d28d9",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_generate_certificate)
        self.p_certificate_button.pack(fill="x", padx=16, pady=(0, 16))

        right = self._right_card(body)
        ctk.CTkLabel(right, text="Inscripciones activas",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=P["accent"]
                     ).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")
        self.payments_tree = self._tree_frame(
            right,
            ("ID", "Estudiante", "Curso", "Progreso", "Estado"),
            row=1)

    # ══════════════════════════════════════════════════════════
    #  BIBLIOTECA DEL CURSO
    # ══════════════════════════════════════════════════════════
    def _build_library(self):
        body = self._make_page(
            "library", "📂",
            "Biblioteca del Curso",
            "Recursos didacticos y materiales por curso")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        m_card = self._card(left, "materials_management", color=P["orange"])
        ctk.CTkLabel(m_card, text="Curso",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.m_course = ctk.CTkComboBox(m_card, values=[], height=40,
                                        corner_radius=8)
        self.m_course.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(m_card, text="Titulo del material",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.m_title = ctk.CTkEntry(m_card, height=40, corner_radius=8,
                                    placeholder_text="Ej. Introduccion a Python")
        self.m_title.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(m_card, text="Tipo",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.m_type = ctk.CTkOptionMenu(
            m_card, values=["Video", "Documento", "PDF", "Repositorio"],
            height=40, corner_radius=8,
            command=self._on_material_type_change)
        self.m_type.set("Video")
        self.m_type.pack(fill="x", padx=16, pady=(4, 10))

        # ── Enlace URL (visible para Video y Repositorio) ──────
        self.m_url_label = ctk.CTkLabel(m_card, text="Enlace URL",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"])
        self.m_url_label.pack(anchor="w", padx=16)
        self.m_url = ctk.CTkEntry(m_card, height=40, corner_radius=8,
                                  placeholder_text="https://...")
        self.m_url.pack(fill="x", padx=16, pady=(4, 10))

        # ── Botón Examinar (visible para PDF y Documento) ──────
        self.m_browse_button = ctk.CTkButton(
            m_card, text="📁  Examinar archivo...",
            height=40, corner_radius=10,
            fg_color=P["surface2"], hover_color=P["border"],
            text_color=P["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_browse_material)
        # empieza oculto (tipo inicial = Video)
        # self.m_browse_button no se empaqueta aquí — se muestra dinámicamente

        self.m_save_button = ctk.CTkButton(
            m_card, text="  + Guardar material",
            height=40, corner_radius=10,
            fg_color=P["orange"], hover_color="#b45309",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_create_material)
        self.m_save_button.pack(fill="x", padx=16, pady=(0, 8))
        self.m_download_button = ctk.CTkButton(
            m_card, text="Descargar seleccionado",
            height=40, corner_radius=10,
            fg_color=P["surface2"], hover_color=P["border"],
            text_color=P["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_download_material)
        self.m_download_button.pack(fill="x", padx=16, pady=(0, 16))

        # Right — materials table
        right_col = ctk.CTkFrame(body, fg_color=P["bg"], corner_radius=0)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=1)

        mat_card = ctk.CTkFrame(right_col, fg_color=P["surface"],
                                corner_radius=14, border_width=1,
                                border_color=P["border"])
        mat_card.grid(row=0, column=0, sticky="nsew")
        mat_card.grid_columnconfigure(0, weight=1)
        mat_card.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(mat_card, height=3, fg_color=P["orange"],
                     corner_radius=3).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(mat_card, text="📂  " + tr(self.language, "materials"),
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=P["primary"]
                     ).grid(row=0, column=0, padx=18, pady=(12, 8), sticky="w")
        self.materials_tree = self._tree_frame(
            mat_card, ("ID", "Curso", "Titulo", "Tipo", "Enlace"), row=1)

    # ══════════════════════════════════════════════════════════
    #  COMUNIDAD DEL CURSO
    # ══════════════════════════════════════════════════════════
    def _build_community(self):
        body = self._make_page(
            "community", "💬",
            "Comunidad del Curso",
            "Espacio de comunicacion y foro por curso")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        f_card = self._card(left, "forum", color=P["primary"])
        ctk.CTkLabel(f_card, text="Curso",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.f_course = ctk.CTkComboBox(f_card, values=[], height=40,
                                        corner_radius=8)
        self.f_course.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(f_card, text="Tipo de remitente",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.f_sender = ctk.CTkOptionMenu(f_card,
                                          values=["Estudiante", "Instructor"],
                                          height=40, corner_radius=8)
        self.f_sender.set("Estudiante")
        self.f_sender.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(f_card, text="Estudiante",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.f_student = ctk.CTkComboBox(f_card, values=[], height=40,
                                         corner_radius=8)
        self.f_student.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(f_card, text="Instructor",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.f_instructor = ctk.CTkComboBox(f_card, values=[], height=40,
                                            corner_radius=8)
        self.f_instructor.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(f_card, text="Mensaje",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.f_msg = ctk.CTkTextbox(f_card, height=80, corner_radius=8)
        self.f_msg.pack(fill="x", padx=16, pady=(4, 10))
        self.f_post_button = ctk.CTkButton(
            f_card, text="  Publicar mensaje",
            height=40, corner_radius=10,
            fg_color=P["primary"], hover_color=P["primary_dark"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_create_forum_message)
        self.f_post_button.pack(fill="x", padx=16, pady=(0, 16))

        # Right — messages table
        right_col = ctk.CTkFrame(body, fg_color=P["bg"], corner_radius=0)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=1)

        msg_card = ctk.CTkFrame(right_col, fg_color=P["surface"],
                                corner_radius=14, border_width=1,
                                border_color=P["border"])
        msg_card.grid(row=0, column=0, sticky="nsew")
        msg_card.grid_columnconfigure(0, weight=1)
        msg_card.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(msg_card, height=3, fg_color=P["primary"],
                     corner_radius=3).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(msg_card, text="💬  " + tr(self.language, "messages"),
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=P["primary"]
                     ).grid(row=0, column=0, padx=18, pady=(12, 8), sticky="w")
        self.messages_tree = self._tree_frame(
            msg_card, ("ID", "Curso", "Remitente", "Mensaje", "Fecha"), row=1)

    # ══════════════════════════════════════════════════════════
    #  BANCO DE PREGUNTAS
    # ══════════════════════════════════════════════════════════
    def _build_quizbank(self):
        body = self._make_page(
            "quizbank", "📝",
            "Banco de Preguntas",
            "Crea y administra preguntas de opcion multiple por curso")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        q_card = self._card(left, "create_question", color=P["purple"])
        ctk.CTkLabel(q_card, text="Curso",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.q_course = ctk.CTkComboBox(q_card, values=[], height=40,
                                        corner_radius=8)
        self.q_course.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(q_card, text="Pregunta",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.q_question = ctk.CTkTextbox(q_card, height=66, corner_radius=8)
        self.q_question.pack(fill="x", padx=16, pady=(4, 10))
        for opt_label, attr in [("Opcion A", "q_a"), ("Opcion B", "q_b"),
                                 ("Opcion C", "q_c"), ("Opcion D", "q_d")]:
            ctk.CTkLabel(q_card, text=opt_label,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=P["muted"]).pack(anchor="w", padx=16)
            e = ctk.CTkEntry(q_card, height=38, corner_radius=8)
            e.pack(fill="x", padx=16, pady=(2, 8))
            setattr(self, attr, e)
        ctk.CTkLabel(q_card, text="Respuesta correcta",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.q_ok = ctk.CTkOptionMenu(q_card, values=["A", "B", "C", "D"],
                                      height=40, corner_radius=8)
        self.q_ok.set("A")
        self.q_ok.pack(fill="x", padx=16, pady=(4, 10))
        self.q_save_button = ctk.CTkButton(
            q_card, text="  + Guardar pregunta",
            height=40, corner_radius=10,
            fg_color=P["purple"], hover_color="#6d28d9",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_create_quiz_question)
        self.q_save_button.pack(fill="x", padx=16, pady=(0, 16))

        # Right — tabla de preguntas publicadas
        right_col = ctk.CTkFrame(body, fg_color=P["bg"], corner_radius=0)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=1)

        q_right = ctk.CTkFrame(right_col, fg_color=P["surface"],
                               corner_radius=14, border_width=1,
                               border_color=P["border"])
        q_right.grid(row=0, column=0, sticky="nsew")
        q_right.grid_columnconfigure(0, weight=1)
        q_right.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(q_right, height=3, fg_color=P["purple"],
                     corner_radius=3).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(q_right, text="📝  " + tr(self.language, "questions"),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=P["accent"]
                     ).grid(row=0, column=0, padx=18, pady=(10, 6), sticky="w")
        self.quiz_tree = self._tree_frame(
            q_right, ("ID", "Curso", "Pregunta", "Correcta"), row=1)

    # ══════════════════════════════════════════════════════════
    #  EVALUACIONES
    # ══════════════════════════════════════════════════════════
    def _build_exams(self):
        body = self._make_page(
            "exams", "🚀",
            "Evaluaciones",
            "Lanza examenes y consulta el historial de intentos por estudiante")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        a_card = self._card(left, "solve_quiz", color=P["green"])
        ctk.CTkLabel(a_card,
                     text="Selecciona la inscripcion del estudiante\nque va a rendir el examen:",
                     font=ctk.CTkFont(size=11),
                     text_color=P["muted"],
                     justify="left").pack(anchor="w", padx=16, pady=(0, 6))
        self.a_enrollment = ctk.CTkComboBox(a_card, values=[], height=40,
                                            corner_radius=8)
        self.a_enrollment.pack(fill="x", padx=16, pady=(4, 10))

        # Atributos ocultos para no romper _refresh_quizzes / handle_submit_quiz
        self.a_question = ctk.CTkComboBox(a_card, values=[], height=0)
        self.a_option   = ctk.CTkOptionMenu(a_card,
                                            values=["A", "B", "C", "D"],
                                            height=0)
        self.quiz_result = ctk.CTkLabel(a_card, text="",
                                        font=ctk.CTkFont(size=1))
        self.a_grade_button = ctk.CTkButton(a_card, text="", height=0,
                                            fg_color="transparent",
                                            command=self.handle_submit_quiz)

        self.a_start_button = ctk.CTkButton(
            a_card,
            text="  🚀  Iniciar Evaluacion del Estudiante",
            height=44, corner_radius=10,
            fg_color=P["green"], hover_color="#047857",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.open_quiz_wizard)
        self.a_start_button.pack(fill="x", padx=16, pady=(0, 16))

        # Right — historial de evaluaciones
        right_col = ctk.CTkFrame(body, fg_color=P["bg"], corner_radius=0)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=1)

        h_right = ctk.CTkFrame(right_col, fg_color=P["surface"],
                               corner_radius=14, border_width=1,
                               border_color=P["border"])
        h_right.grid(row=0, column=0, sticky="nsew")
        h_right.grid_columnconfigure(0, weight=1)
        h_right.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(h_right, height=3, fg_color=P["green"],
                     corner_radius=3).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(h_right, text="📊  Historial de Evaluaciones",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=P["accent"]
                     ).grid(row=0, column=0, padx=18, pady=(10, 6), sticky="w")
        self.attempts_tree = self._tree_frame(
            h_right,
            ("ID", "Estudiante", "Curso", "Pregunta", "Respondio", "Correcta",
             "Puntaje", "Estado", "Fecha"),
            row=1)

    # ══════════════════════════════════════════════════════════
    #  RESEÑAS
    # ══════════════════════════════════════════════════════════
    def _build_reviews(self):
        body = self._make_page(
            "reviews", "⭐",
            "Resenas",
            "Valoraciones y comentarios de los estudiantes sobre los cursos")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=8)
        body.grid_rowconfigure(0, weight=1)

        left = self._left_scroll(body)

        r_card = self._card(left, "review_course", color=P["orange"])
        ctk.CTkLabel(r_card, text="Curso",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.r_course = ctk.CTkComboBox(r_card, values=[], height=40,
                                        corner_radius=8)
        self.r_course.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(r_card, text="Estudiante",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.r_student = ctk.CTkComboBox(r_card, values=[], height=40,
                                         corner_radius=8)
        self.r_student.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(r_card, text="Calificacion (estrellas)",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.r_rating = ctk.CTkOptionMenu(r_card, values=["1","2","3","4","5"],
                                          height=40, corner_radius=8)
        self.r_rating.set("5")
        self.r_rating.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(r_card, text="Comentario",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["muted"]).pack(anchor="w", padx=16)
        self.r_comment = ctk.CTkTextbox(r_card, height=72, corner_radius=8)
        self.r_comment.pack(fill="x", padx=16, pady=(4, 10))
        self.r_save_button = ctk.CTkButton(
            r_card, text="  Guardar valoracion",
            height=40, corner_radius=10,
            fg_color=P["orange"], hover_color="#b45309",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.handle_create_review)
        self.r_save_button.pack(fill="x", padx=16, pady=(0, 16))

        # Right — tabla de reseñas
        right_col = ctk.CTkFrame(body, fg_color=P["bg"], corner_radius=0)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=1)

        r_right = ctk.CTkFrame(right_col, fg_color=P["surface"],
                               corner_radius=14, border_width=1,
                               border_color=P["border"])
        r_right.grid(row=0, column=0, sticky="nsew")
        r_right.grid_columnconfigure(0, weight=1)
        r_right.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(r_right, height=3, fg_color=P["orange"],
                     corner_radius=3).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(r_right, text="⭐  " + tr(self.language, "reviews"),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=P["accent"]
                     ).grid(row=0, column=0, padx=18, pady=(10, 6), sticky="w")
        self.reviews_tree = self._tree_frame(
            r_right, ("ID", "Curso", "Estudiante", "Estrellas", "Comentario", "Fecha"),
            row=1)

    def open_quiz_wizard(self):
        """Opens a top-level window for the interactive quiz."""
        eid_raw = self.a_enrollment.get()
        if not eid_raw or "|" not in eid_raw:
            self._toast("Seleccione una inscripción en el panel lateral", False)
            return
        
        try:
            # Parse ID from "#123 | Student -> Course"
            self.curr_wizard_enroll_id = int(eid_raw.split("|")[0].replace("#", "").strip())
            
            # Find the enrollment to get course_id
            enrollment = next((e for e in self._data.get("enrollments", []) if e["id"] == self.curr_wizard_enroll_id), None)
            if not enrollment:
                self._toast("Inscripción no encontrada", False)
                return
            
            course_id = enrollment["course_id"]
            
            # Filter questions for THIS course
            self.quiz_data = [q for q in self._data.get("questions", []) if q["course_id"] == course_id]
            
            if not self.quiz_data:
                 self._toast("No hay preguntas para este curso", False)
                 return
        except Exception as e:
            self._toast(f"Error al cargar examen: {e}", False)
            return

        try:
            self.wizard = ctk.CTkToplevel(self)
            self.wizard.title("EduCampus — Evaluación en Curso")
            self.wizard.geometry("800x600")
            self.wizard.after(100, lambda: self.wizard.focus_force())
            self.wizard.configure(fg_color=P["bg"])
            self.wizard.grid_columnconfigure(0, weight=1)
            self.wizard.grid_rowconfigure(1, weight=1)

            # Header
            hdr = ctk.CTkFrame(self.wizard, fg_color=P["surface"], height=60, corner_radius=0)
            hdr.grid(row=0, column=0, sticky="ew")
            hdr.grid_propagate(False)
            ctk.CTkLabel(hdr, text="📝 MODO EXAMEN / EXAM MODE",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=P["sidebar_act"]).pack(side="left", padx=20)

            self.w_progress = ctk.CTkProgressBar(self.wizard, height=10, corner_radius=0,
                                                 progress_color=P["primary"])
            self.w_progress.grid(row=1, column=0, sticky="new")
            self.w_progress.set(0)

            # Body Container
            self.w_body = ctk.CTkFrame(self.wizard, fg_color="transparent")
            self.w_body.grid(row=1, column=0, sticky="nsew", padx=40, pady=(30, 40))
            self.w_body.grid_columnconfigure(0, weight=1)

            # State
            self.curr_q_idx = 0
            # quiz_data is already filtered above
            self._show_question(idx=0)
        except Exception as e:
            print(f"Wizard error: {e}")
            self._toast(f"Error: {e}", False)

    def _show_question(self, idx):
        for w in self.w_body.winfo_children(): w.destroy()
        q = self.quiz_data[idx]
        self.w_progress.set((idx + 1) / len(self.quiz_data))

        # Centered container for the question
        q_container = ctk.CTkFrame(self.w_body, fg_color="transparent")
        q_container.pack(expand=True, fill="both")

        ctk.CTkLabel(q_container, text=f"PREGUNTA {idx+1} DE {len(self.quiz_data)}",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=P["primary"]).pack(pady=(0, 5))

        ctk.CTkLabel(q_container, text=q.get("question", "N/A"), wraplength=650,
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=P["accent"], justify="center").pack(pady=(0, 40))

        # Options Container
        opt_frame = ctk.CTkFrame(q_container, fg_color="transparent")
        opt_frame.pack(fill="x", padx=100)

        for opt in ["A", "B", "C", "D"]:
            key = f"option_{opt.lower()}"
            txt = q.get(key, "...")
            # Card-style button
            btn = ctk.CTkButton(opt_frame, 
                                text=f"{opt}   {txt}",
                                height=54, corner_radius=15,
                                fg_color=P["surface"], 
                                border_width=1,
                                border_color=P["border"],
                                text_color=P["accent"],
                                font=ctk.CTkFont(size=14, weight="bold"),
                                anchor="w", 
                                hover_color=P["surface2"],
                                command=lambda o=opt: self._submit_step(o))
            btn.pack(fill="x", pady=8)

    def _submit_step(self, opt):
        """Graba la respuesta en la BD y avanza a la siguiente pregunta."""
        q = self.quiz_data[self.curr_q_idx]
        try:
            score, status = self.controller.submit_quiz_attempt(
                self.curr_wizard_enroll_id, q["id"], opt)
            # Acumular puntaje para mostrar al final
            if not hasattr(self, "_quiz_scores"):
                self._quiz_scores = []
            self._quiz_scores.append(score)
        except Exception as e:
            self._toast(f"Error al guardar respuesta: {e}", False)

        if self.curr_q_idx < len(self.quiz_data) - 1:
            self.curr_q_idx += 1
            self._show_question(self.curr_q_idx)
        else:
            self._finish_wizard(self.curr_wizard_enroll_id)

    def _finish_wizard(self, enroll_id):
        """Calcula puntaje final, actualiza progreso y muestra resultado."""
        scores = getattr(self, "_quiz_scores", [])
        total_qs = len(self.quiz_data)
        correct  = sum(1 for s in scores if s == 100)
        pct      = int((correct / total_qs) * 100) if total_qs > 0 else 0
        passed   = pct >= 60

        try:
            self.controller.update_progress(enroll_id, pct)
            self.refresh_all()
        except Exception:
            pass

        # Limpiar acumulador para próxima vez
        self._quiz_scores = []

        for w in self.w_body.winfo_children():
            w.destroy()

        self.w_progress.set(1.0)
        self.w_progress.configure(
            progress_color=P["green"] if passed else P["red"])

        emoji = "🎊" if passed else "😔"
        result_text = "¡Aprobado!" if passed else "Reprobado"
        result_color = P["green"] if passed else P["red"]

        ctk.CTkLabel(self.w_body, text=emoji,
                     font=ctk.CTkFont(size=90)).pack(pady=(40, 10))

        ctk.CTkLabel(self.w_body, text=result_text,
                     font=ctk.CTkFont(size=32, weight="bold"),
                     text_color=result_color).pack()

        ctk.CTkLabel(self.w_body,
                     text=f"Respondiste {correct} de {total_qs} preguntas correctamente",
                     font=ctk.CTkFont(size=16),
                     text_color=P["muted"]).pack(pady=(8, 4))

        # Barra de puntaje visual
        score_frame = ctk.CTkFrame(self.w_body, fg_color="transparent")
        score_frame.pack(pady=16, fill="x", padx=120)
        ctk.CTkLabel(score_frame,
                     text=f"Puntaje: {pct}%",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=P["accent"]).pack()
        bar = ctk.CTkProgressBar(score_frame, height=10, corner_radius=5,
                                 progress_color=result_color,
                                 fg_color=P["surface2"])
        bar.pack(fill="x", pady=(8, 0))
        bar.set(pct / 100)

        note = ("¡Tu progreso ha sido actualizado! Puedes generar tu certificado desde Aprendizaje."
                if passed else
                "Tu progreso fue registrado. Repasa los materiales e inténtalo de nuevo.")
        ctk.CTkLabel(self.w_body, text=note,
                     font=ctk.CTkFont(size=12),
                     text_color=P["muted"],
                     wraplength=500, justify="center").pack(pady=12)

        ctk.CTkButton(self.w_body, text="Cerrar",
                      height=46, width=200, corner_radius=12,
                      fg_color=P["primary"], hover_color=P["primary_dark"],
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.wizard.destroy).pack(pady=20)

    # ══════════════════════════════════════════════════════════
    #  COMPONENT STYLES (post-build pass)
    # ══════════════════════════════════════════════════════════
    def _apply_styles(self):
        """Apply uniform styles to all form widgets in content area."""
        self._style_walk(self.content)

    def _style_walk(self, widget):
        for child in widget.winfo_children():
            cls = type(child).__name__
            if cls == "CTkEntry":
                child.configure(
                    height=42, corner_radius=10,
                    fg_color=P["surface2"],
                    border_color=P["border"],
                    border_width=1,
                    text_color=P["accent"],
                    font=ctk.CTkFont(size=13),
                    placeholder_text_color=P["muted"]
                )
            elif cls == "CTkComboBox":
                child.configure(
                    height=42, corner_radius=10,
                    fg_color=P["surface"],
                    border_color=P["border"],
                    border_width=1,
                    button_color=P["surface2"],
                    button_hover_color=P["border"],
                    text_color=P["accent"],
                    font=ctk.CTkFont(size=13)
                )
            elif cls == "CTkOptionMenu":
                child.configure(
                    height=42, corner_radius=10,
                    fg_color=P["surface"],
                    button_color=P["surface2"],
                    button_hover_color=P["border"],
                    text_color=P["accent"],
                    font=ctk.CTkFont(size=13)
                )
            elif cls == "CTkTextbox":
                child.configure(
                    fg_color=P["surface"],
                    border_color=P["border"],
                    border_width=1, corner_radius=12,
                    text_color=P["accent"],
                    font=ctk.CTkFont(size=13)
                )
            elif cls == "CTkButton":
                # Only style buttons in the content area, not sidebar
                if "content" in str(child):
                    child.configure(height=42, corner_radius=10)
            self._style_walk(child)

    # ══════════════════════════════════════════════════════════
    #  TOAST NOTIFICATIONS
    # ══════════════════════════════════════════════════════════
    def _toast(self, msg: str, ok: bool = True):
        """Premium floating notification."""
        bg     = P["green_soft"] if ok else P["red_soft"]
        accent = P["green"] if ok else P["red"]
        icon   = "✓" if ok else "⚠"

        if hasattr(self, "_toast_frame") and self._toast_frame.winfo_exists():
            self._toast_frame.destroy()

        tf = ctk.CTkFrame(self, fg_color=bg, corner_radius=16, border_width=2,
                          border_color=accent)
        tf.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-30)

        ctk.CTkLabel(tf, text=icon, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=accent, fg_color=P["surface"], width=32, height=32,
                     corner_radius=16).pack(side="left", padx=(12, 8), pady=12)

        ctk.CTkLabel(tf, text=msg, font=ctk.CTkFont(size=13),
                     text_color=P["accent"]).pack(side="left", padx=(0, 16), pady=12)

        self._toast_frame = tf
        self.after(4000, lambda: tf.destroy() if tf.winfo_exists() else None)

    # ══════════════════════════════════════════════════════════
    #  NAVIGATION
    # ══════════════════════════════════════════════════════════
    def change_page(self, key):
        for name, page in self.pages.items():
            btn = self.nav_buttons[name]
            if name == key:
                page.grid()
                btn.configure(fg_color=P["primary_soft"],
                              text_color=P["sidebar_act"],
                              font=ctk.CTkFont(size=13, weight="bold"))
            else:
                page.grid_remove()
                btn.configure(fg_color="transparent",
                              text_color=P["muted"],
                              font=ctk.CTkFont(size=13, weight="normal"))

    # ══════════════════════════════════════════════════════════
    #  LANGUAGE
    # ══════════════════════════════════════════════════════════
    def set_language(self, lang):
        self.language = lang
        self.title("EduCampus — Sistema de Cursos Online")

        nav_texts = {
            "es": {
                "dashboard":   "  🏠   Panel Principal",
                "instructors": "  👤   Instructores",
                "students":    "  🎓   Estudiantes",
                "courses":     "  📚   Cursos",
                "learning":    "  💳   Ventas e Inscripciones",
                "payments":    "  📖   Aprendizaje",
                "library":     "  📂   Biblioteca del Curso",
                "community":   "  💬   Comunidad del Curso",
                "quizbank":    "  📝   Banco de Preguntas",
                "exams":       "  🚀   Evaluaciones",
                "reviews":     "  ⭐   Reseñas",
            },
            "en": {
                "dashboard":   "  🏠   Dashboard",
                "instructors": "  👤   Instructors",
                "students":    "  🎓   Students",
                "courses":     "  📚   Courses",
                "learning":    "  💳   Sales & Enrollments",
                "payments":    "  📖   Learning",
                "library":     "  📂   Course Library",
                "community":   "  💬   Course Community",
                "quizbank":    "  📝   Question Bank",
                "exams":       "  🚀   Assessments",
                "reviews":     "  ⭐   Reviews",
            }
        }
        for key, btn in self.nav_buttons.items():
            btn.configure(text=nav_texts.get(lang, nav_texts["es"])[key])

        for key, (t_lbl, s_lbl) in self.page_titles.items():
            t_lbl.configure(text=tr(lang, key) if tr(lang, key) != key
                            else t_lbl.cget("text"))

        for key, lbl in self._sec_lbl.items():
            lbl.configure(text=tr(lang, key))
        for key, lbl in self._tree_lbl.items():
            lbl.configure(text=tr(lang, key))

        self.enrollments_label.configure(
            text=tr(lang, "active_enrollments"))
        self.level_filter_label.configure(
            text=tr(lang, "level_filter"))

        widgets_map = [
            (self.i_name,           "placeholder_text", tr(lang, "name")),
            (self.i_spec,           "placeholder_text", tr(lang, "specialty")),
            (self.s_name,           "placeholder_text", tr(lang, "name")),
            (self.s_age,            "placeholder_text", tr(lang, "age")),
            (self.s_email,          "placeholder_text", tr(lang, "email")),
            (self.c_name,           "placeholder_text", tr(lang, "course_name")),
            (self.c_cat,            "placeholder_text", tr(lang, "category")),
            (self.c_price,          "placeholder_text", tr(lang, "price")),
            (self.m_title,          "placeholder_text", tr(lang, "material_title")),
            (self.m_url,            "placeholder_text", tr(lang, "material_link")),
            (self.i_save_button,    "text", "  + " + tr(lang, "save_instructor")),
            (self.s_save_button,    "text", "  + " + tr(lang, "save_student")),
            (self.c_save_button,    "text", "  + " + tr(lang, "save_course")),
            (self.e_save_button,    "text", "  + " + tr(lang, "save_enrollment")),
            (self.p_update_button,  "text", tr(lang, "update_progress")),
            (self.p_payment_button, "text", tr(lang, "register_payment")),
            (self.p_certificate_button, "text", "  " + tr(lang, "generate_certificate")),
            (self.m_save_button,    "text", "  + " + tr(lang, "save_material")),
            (self.m_download_button,"text", tr(lang, "download_material")),
            (self.f_post_button,    "text", "  " + tr(lang, "post_message")),
            (self.q_save_button,    "text", "  + " + tr(lang, "save_question")),
            (self.a_grade_button,   "text", "  " + tr(lang, "auto_grade")),
            (self.r_save_button,    "text", "  " + tr(lang, "save_review")),
            (self.quiz_result,      "text", tr(lang, "pending_result")),
        ]
        for widget, prop, val in widgets_map:
            try:
                widget.configure(**{prop: val})
            except Exception:
                pass

    # ══════════════════════════════════════════════════════════
    #  DATA UTILITIES
    # ══════════════════════════════════════════════════════════
    def _tree_widget(self, outer_frame):
        """Return the ttk.Treeview from a _tree_frame outer Frame."""
        if hasattr(outer_frame, "_tree"):
            return outer_frame._tree
        for child in outer_frame.winfo_children():
            if isinstance(child, ttk.Treeview):
                return child

    def _fill(self, outer_frame, rows):
        tree = self._tree_widget(outer_frame)
        if tree is None:
            return
        tree.delete(*tree.get_children())
        empty_lbl = getattr(outer_frame, "_empty_lbl", None)
        if not rows:
            # Show empty state overlay
            tree.grid_remove()
            if empty_lbl:
                empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
            return
        # Has data — hide empty state, show tree
        if empty_lbl:
            empty_lbl.place_forget()
        tree.grid()
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            row_str = " ".join(str(v).lower() for v in row)
            if "aprobado"   in row_str: tag = "aprobado"
            elif "reprobado" in row_str: tag = "reprobado"
            elif "pagado"    in row_str: tag = "pagado"
            elif "pendiente" in row_str: tag = "pendiente"
            tree.insert("", "end", values=row, tags=(tag,))

    def _set_combo(self, widget, items, fmt):
        mapping, values = {}, []
        for item in items:
            lbl = fmt(item)
            mapping[lbl] = item["id"]
            values.append(lbl)
        widget.configure(values=values or [""])
        widget.set(values[0] if values else "")
        return mapping

    def _id(self, widget, mapping):
        return mapping.get(widget.get().strip())

    # ══════════════════════════════════════════════════════════
    #  REFRESH
    # ══════════════════════════════════════════════════════════
    def refresh_all(self):
        self._data["instructors"]  = self.controller.get_instructors()
        self._data["students"]     = self.controller.get_students()
        self._data["courses_all"]  = self.controller.get_courses()
        lvl = self.course_filter.get() if hasattr(self, "course_filter") else "Todos"
        self._data["courses"]      = self.controller.get_courses(
            None if lvl == "Todos" else lvl)
        self._data["enrollments"]  = self.controller.get_enrollments()
        self._data["questions"]    = self.controller.get_quiz_questions()
        self._refresh_dashboard()
        self._refresh_catalog()
        self._refresh_enrollments()
        self._refresh_materials()
        self._refresh_quizzes()

    def _refresh_dashboard(self):
        totals, panel, top_students_db = self.controller.get_dashboard_stats()

        # ── KPI stat labels ────────────────────────────────────
        for key, widget in self.stats.items():
            if not widget.winfo_exists():
                continue
            if key == "revenue":
                widget.configure(text=f"${totals.get(key, 0):,.0f}")
            elif key in totals:
                widget.configure(text=str(totals[key]))

        # ── Sidebar count badges ───────────────────────────────
        count_map = {
            "instructors": totals.get("instructors", 0),
            "students":    totals.get("students", 0),
            "courses":     totals.get("courses", 0),
        }
        for nav_key, count in count_map.items():
            if nav_key in self.nav_counts:
                self.nav_counts[nav_key].configure(text=str(count))

        # ── Panel del Instructor ───────────────────────────────
        if hasattr(self, "instructor_panel_tree"):
            self.instructor_panel_tree.delete(*self.instructor_panel_tree.get_children())
            for i, row in enumerate(panel):
                tag = "even" if i % 2 == 0 else "odd"
                self.instructor_panel_tree.insert(
                    "", "end",
                    values=(
                        row.get("name", ""),
                        row.get("active_students", 0),
                        f"${row.get('revenue', 0):,.2f}",
                    ),
                    tags=(tag,),
                )
            self.instructor_panel_tree.tag_configure("even", background="#ffffff")
            self.instructor_panel_tree.tag_configure("odd",  background="#f8f9ff")

        # ── Cursos activos panel ───────────────────────────────
        for w in self.dash_courses_frame.winfo_children():
            w.destroy()
        courses = self._data.get("courses_all", [])[:5]
        enrollments = self._data.get("enrollments", [])
        # Count enrollments per course
        from collections import Counter
        enroll_count = Counter(e.get("course_id") or e.get("course") for e in enrollments)
        level_colors = {
            "Basico":      (P["green"],  P["green_soft"],  "Activo"),
            "Intermedio":  (P["orange"], P["orange_soft"], "En curso"),
            "Avanzado":    (P["purple"], P["purple_soft"], "Avanzado"),
        }
        for i, c in enumerate(courses):
            row = ctk.CTkFrame(self.dash_courses_frame, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=(10 if i == 0 else 4, 0))
            row.grid_columnconfigure(1, weight=1)
            # Course icon
            ctk.CTkLabel(row, text="📘",
                         font=ctk.CTkFont(size=18),
                         fg_color=P["primary_soft"], corner_radius=8,
                         width=36, height=36).grid(row=0, column=0, rowspan=2, padx=(0, 12))
            # Name + instructor
            ctk.CTkLabel(row, text=c.get("name", ""),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=P["accent"], anchor="w"
                         ).grid(row=0, column=1, sticky="w")
            instr = c.get("instructor", c.get("instructor_name", ""))
            n_enroll = enroll_count.get(c.get("id")) or 0
            ctk.CTkLabel(row, text=f"{instr}  ·  {n_enroll} estudiantes",
                         font=ctk.CTkFont(size=10),
                         text_color=P["muted"], anchor="w"
                         ).grid(row=1, column=1, sticky="w")
            # Progress bar + % + status badge
            prog_row = ctk.CTkFrame(self.dash_courses_frame, fg_color="transparent")
            prog_row.pack(fill="x", padx=18, pady=(4, 0))
            prog_row.grid_columnconfigure(0, weight=1)
            level = c.get("level", "Basico")
            fg_c, bg_c, status_txt = level_colors.get(level, (P["primary"], P["primary_soft"], "Activo"))
            progress_val = min(1.0, (n_enroll / 50)) if n_enroll else 0.15
            pct = int(progress_val * 100)
            prog = ctk.CTkProgressBar(prog_row, height=6, corner_radius=3,
                                      progress_color=fg_c, fg_color=P["bg"])
            prog.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            prog.set(progress_val)
            ctk.CTkLabel(prog_row, text=f"{pct}%",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=fg_c).grid(row=0, column=1, padx=(0, 8))
            ctk.CTkLabel(prog_row, text=f" {status_txt} ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=bg_c, text_color=fg_c,
                         corner_radius=6, height=18).grid(row=0, column=2)
            if i < len(courses) - 1:
                ctk.CTkFrame(self.dash_courses_frame, height=1,
                             fg_color=P["border"]).pack(fill="x", padx=18, pady=(8, 0))

        # ── Top Estudiantes panel ──────────────────────────────
        for w in self.dash_students_frame.winfo_children():
            w.destroy()
        avatars_colors = [P["pink"], P["primary"], P["green"], P["orange"]]
        medals = ["🥇", "🥈", "🥉", "  "]
        for i, s in enumerate(top_students_db):
            row = ctk.CTkFrame(self.dash_students_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=(10 if i == 0 else 6, 0))
            row.grid_columnconfigure(1, weight=1)
            # Medal
            ctk.CTkLabel(row, text=medals[i],
                         font=ctk.CTkFont(size=14)).grid(row=0, column=0, rowspan=2, padx=(0, 6))
            # Avatar
            initial = s.get("name", "?")[0].upper()
            ctk.CTkLabel(row, text=initial,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         fg_color=avatars_colors[i % len(avatars_colors)],
                         text_color="#ffffff", corner_radius=10,
                         width=36, height=36).grid(row=0, column=1, rowspan=2, padx=(0, 10), sticky="w")
            # Name + courses count
            courses_txt = f"{s.get('courses_count', 0)} curso{'s' if s.get('courses_count', 0) != 1 else ''}"
            ctk.CTkLabel(row, text=s.get("name", ""),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=P["accent"], anchor="w"
                         ).grid(row=0, column=2, sticky="w")
            ctk.CTkLabel(row, text=courses_txt,
                         font=ctk.CTkFont(size=10),
                         text_color=P["muted"], anchor="w"
                         ).grid(row=1, column=2, sticky="w")
            # Points + stars based on real score
            pts = s.get("total_pts", 0)
            star_count = min(5, max(1, int(pts // 20))) if pts > 0 else 1
            stars = "★" * star_count + "☆" * (5 - star_count)
            ctk.CTkLabel(row, text=f"{pts} pts\n{stars}",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=P["orange"], anchor="e",
                         justify="right").grid(row=0, column=3, rowspan=2, padx=(8, 0), sticky="e")

        # ── Bottom mini-stats ─────────────────────────────────
        mats  = totals.get("materials_count", 0)
        quizz = totals.get("paid_enrollments", 0)
        compl = totals.get("completion_rate", 0)
        if hasattr(self, "bottom_stats"):
            if "materials"  in self.bottom_stats:
                self.bottom_stats["materials"].configure(text=str(mats))
            if "quizzes_a"  in self.bottom_stats:
                self.bottom_stats["quizzes_a"].configure(text=str(quizz))
            if "satisf"     in self.bottom_stats:
                self.bottom_stats["satisf"].configure(text=f"{compl}%")

    def _refresh_catalog(self):
        instructors  = self._data["instructors"]
        students     = self._data["students"]
        courses_all  = self._data["courses_all"]

        n_i = len(instructors)
        n_s = len(students)
        n_c = len(courses_all)
        self.instr_count_label.configure(
            text=f"{n_i} instructor{'es' if n_i != 1 else ''} registrado{'s' if n_i != 1 else ''}")
        self.student_count_label.configure(
            text=f"{n_s} estudiante{'s' if n_s != 1 else ''} registrado{'s' if n_s != 1 else ''}")
        self.course_count_label.configure(
            text=f"{n_c} curso{'s' if n_c != 1 else ''} en catalogo")

        self._maps["instructor"]      = self._set_combo(self.c_instructor, instructors, lambda x: f"{x['name']} | {x['specialty']}")
        self._maps["student"]         = self._set_combo(self.e_student,    students,    lambda x: f"{x['name']} | {x['email']}")
        self._maps["course"]          = self._set_combo(self.e_course,     courses_all, lambda x: f"{x['name']} | {x['level']} | ${x['price']:.2f}")
        self._maps["material_course"] = self._set_combo(self.m_course,     courses_all, lambda x: f"{x['name']} | {x['level']}")
        self._maps["forum_course"]    = self._set_combo(self.f_course,     courses_all, lambda x: f"{x['name']} | {x['level']}")
        self._maps["quiz_course"]     = self._set_combo(self.q_course,     courses_all, lambda x: f"{x['name']} | {x['level']}")
        self._maps["review_course"]   = self._set_combo(self.r_course,     courses_all, lambda x: f"{x['name']} | {x['level']}")
        self._maps["forum_student"]   = self._set_combo(self.f_student,    students,    lambda x: f"{x['name']} | {x['email']}")
        self._maps["forum_instructor"]= self._set_combo(self.f_instructor, instructors, lambda x: f"{x['name']} | {x['specialty']}")
        self._maps["review_student"]  = self._set_combo(self.r_student,    students,    lambda x: f"{x['name']} | {x['email']}")

        self._fill(self.instructors_tree, [(x["id"], x["name"], x["specialty"]) for x in instructors])
        self._fill(self.students_tree,    [(x["id"], x["name"], x["age"], x["email"]) for x in students])
        self.refresh_courses_tree()

    def refresh_courses_tree(self):
        lvl = self.course_filter.get()
        query = self.c_search.get().lower() if hasattr(self, "c_search") else ""
        
        filter_val = None if lvl == "Todos" else lvl
        rows = self.controller.get_courses(filter_val)

        filtered = []
        for x in rows:
            if query and query not in x["name"].lower() and query not in x["category"].lower():
                continue
            filtered.append((
                x["id"], x["name"], x["category"], x["level"],
                f"${x['price']:.2f}", x["instructor_name"]
            ))
            
        self._fill(self.courses_tree, filtered)
        if hasattr(self, "course_count_label"):
            self.course_count_label.configure(text=f"{len(filtered)} cursos encontrados")

    def _refresh_enrollments(self):
        enrollments = self._data["enrollments"]
        fmt_enroll  = lambda x: f"#{x['id']} | {x['student_name']} -> {x['course_name']}"

        # Aprendizaje: combo de progreso
        self._maps["enrollment"] = self._set_combo(
            self.p_enrollment, enrollments, fmt_enroll)

        # Quiz combo
        self._set_combo(self.a_enrollment, enrollments, fmt_enroll)

        # Ventas e Inscripciones tree: Precio, Pago, Cert.
        ventas_rows = [
            (x["id"], x["student_name"], x["course_name"],
             f"${x['price']:.2f}",
             x["payment_status"],
             tr(self.language, "yes") if x["certificate_path"]
             else tr(self.language, "no"))
            for x in enrollments
        ]
        self._fill(self.learning_tree, ventas_rows)

        # Aprendizaje tree: Progreso, Estado
        aprendizaje_rows = [
            (x["id"], x["student_name"], x["course_name"],
             f"{x['progress']}%",
             tr(self.language, "passed") if x["completed"]
             else tr(self.language, "in_progress"))
            for x in enrollments
        ]
        self._fill(self.payments_tree, aprendizaje_rows)

        self.select_enrollment(self.p_enrollment.get())

    def _refresh_materials(self):
        mats  = self.controller.get_materials()
        msgs  = self.controller.get_forum_messages()
        self._fill(self.materials_tree,
                   [(x["id"], x["course_name"], x["title"],
                     x["material_type"], x["url"]) for x in mats])
        self._fill(self.messages_tree,
                   [(x["id"], x["course_name"], x["sender_type"],
                     x["message"], x["created_at"]) for x in msgs])

    def _refresh_quizzes(self):
        questions = self._data["questions"]
        # Mantener el combo de preguntas actualizado (oculto pero necesario)
        self._maps["question"] = self._set_combo(
            self.a_question, questions,
            lambda x: f"#{x['id']} | {x['course_name']} | {x['question'][:35]}")

        # Historial de evaluaciones — Aprobado / Reprobado
        attempts = self.controller.get_quiz_attempts()
        self._fill(self.attempts_tree,
                   [(x["id"], x["student_name"], x["course_name"],
                     x["question"][:30] + ("…" if len(x["question"]) > 30 else ""),
                     x["selected_option"], x["correct_option"],
                     f"{x['score']} pts", x["status"],
                     x["attempted_at"][:16])
                    for x in attempts])

        # Preguntas publicadas
        self._fill(self.quiz_tree,
                   [(x["id"], x["course_name"],
                     x["question"], x["correct_option"]) for x in questions])

        # Reseñas
        reviews = self.controller.get_reviews()
        self._fill(self.reviews_tree,
                   [(x["id"], x["course_name"], x["student_name"],
                     x["rating"], x["comment"], x["created_at"]) for x in reviews])

    def select_enrollment(self, _v):
        try:
            eid  = self._id(self.p_enrollment,
                            self._maps.get("enrollment", {}))
            cur  = next((x for x in self._data.get("enrollments", [])
                         if x["id"] == eid), None)
            prog = int(cur["progress"]) if cur else 0
            self.p_value.delete(0, "end")
            self.p_value.insert(0, str(prog))
            self.p_bar.set(prog / 100)
            self.p_label.configure(text=f"{prog}%")
        except Exception:
            self.p_bar.set(0)
            self.p_label.configure(text="0%")

    # ══════════════════════════════════════════════════════════
    #  HANDLERS
    # ══════════════════════════════════════════════════════════
    def handle_create_instructor(self):
        try:
            self.controller.create_instructor(
                self.i_name.get(), self.i_spec.get())
            self.i_name.delete(0, "end")
            self.i_spec.delete(0, "end")
            self.refresh_all()
            self._toast("Instructor registrado correctamente.", ok=True)
            messagebox.showinfo("Éxito", "Instructor registrado correctamente.")
        except Exception as e:
            self._toast(str(e), ok=False)
            messagebox.showerror("Error", str(e))

    def handle_create_student(self):
        try:
            self.controller.create_student(
                self.s_name.get(), int(self.s_age.get()), self.s_email.get())
            self.s_name.delete(0, "end")
            self.s_age.delete(0, "end")
            self.s_email.delete(0, "end")
            self.refresh_all()
            self._toast("Estudiante registrado correctamente.", ok=True)
            messagebox.showinfo("Éxito", "Estudiante registrado correctamente.")
        except Exception as e:
            self._toast(str(e), ok=False)
            messagebox.showerror("Error", str(e))

    def handle_create_course(self):
        try:
            self.controller.create_course(
                self.c_name.get(), self.c_cat.get(), self.c_level.get(),
                self._id(self.c_instructor, self._maps.get("instructor", {})),
                float(self.c_price.get()),
                self.c_desc.get("1.0", "end").strip())
            self.c_name.delete(0, "end")
            self.c_cat.delete(0, "end")
            self.c_price.delete(0, "end")
            self.c_desc.delete("1.0", "end")
            self.refresh_all()
            self._toast("Curso publicado correctamente.", ok=True)
            messagebox.showinfo("Éxito", "Curso publicado correctamente.")
        except Exception as e:
            self._toast(str(e), ok=False)
            messagebox.showerror("Error", str(e))

    def handle_create_enrollment(self):
        try:
            self.controller.create_enrollment(
                self._id(self.e_student, self._maps.get("student", {})),
                self._id(self.e_course,  self._maps.get("course", {})),
                self.e_payment.get())
            self.refresh_all()
            self._toast("Inscripcion registrada.", ok=True)
        except sqlite3.IntegrityError:
            self._toast("La inscripcion ya existe.", ok=False)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_update_progress(self):
        try:
            self.controller.update_progress(
                self._id(self.p_enrollment,
                         self._maps.get("enrollment", {})),
                int(self.p_value.get()))
            self.refresh_all()
            self._toast("Progreso actualizado.", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_register_payment(self):
        try:
            self.controller.register_payment(
                self._id(self.p_enrollment,
                         self._maps.get("enrollment", {})))
            self.refresh_all()
            self._toast("Pago registrado.", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_generate_certificate(self):
        try:
            path = self.controller.generate_certificate(
                self._id(self.p_enrollment,
                         self._maps.get("enrollment", {})))
            self.refresh_all()
            self._toast(f"PDF generado en:\n{path}", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def _on_material_type_change(self, selected_type):
        """Muestra URL o botón Examinar según el tipo de material."""
        needs_file = selected_type in ("PDF", "Documento")
        if needs_file:
            # Ocultar campo URL, mostrar botón Examinar
            self.m_url_label.pack_forget()
            self.m_url.pack_forget()
            self.m_browse_button.pack(fill="x", padx=16, pady=(4, 10),
                                      before=self.m_save_button)
        else:
            # Mostrar campo URL, ocultar botón Examinar
            self.m_browse_button.pack_forget()
            self.m_url_label.pack(anchor="w", padx=16,
                                  before=self.m_save_button)
            self.m_url.pack(fill="x", padx=16, pady=(4, 10),
                            before=self.m_save_button)
            # Limpiar ruta previa si la había
            self.m_url.delete(0, "end")

    def handle_browse_material(self):
        """Abre el explorador de archivos según el tipo seleccionado."""
        mat_type = self.m_type.get()
        if mat_type == "PDF":
            filetypes = [("Archivos PDF", "*.pdf"), ("Todos", "*.*")]
        else:  # Documento
            filetypes = [
                ("Documentos", "*.docx *.doc *.txt *.pptx *.xlsx *.odt"),
                ("Word", "*.docx *.doc"),
                ("Texto", "*.txt"),
                ("Todos", "*.*"),
            ]
        filepath = filedialog.askopenfilename(
            title=f"Seleccionar {mat_type}",
            filetypes=filetypes)
        if filepath:
            # Guardar la ruta en el campo URL (oculto pero funcional)
            self.m_url.pack_forget()   # asegurarse que no está visible
            self._m_local_path = filepath
            # Mostrar nombre del archivo en el botón
            fname = Path(filepath).name
            self.m_browse_button.configure(text=f"📄  {fname}")

    def handle_create_material(self):
        try:
            # Recuperar la ruta local si se usó el explorador
            mat_type = self.m_type.get()
            if mat_type in ("PDF", "Documento"):
                url_val = getattr(self, "_m_local_path", "").strip()
                if not url_val:
                    raise ValueError("Seleccione un archivo con '📁 Examinar archivo...'")
            else:
                url_val = self.m_url.get().strip()

            self.controller.create_material(
                self._id(self.m_course,
                         self._maps.get("material_course", {})),
                self.m_title.get(), url_val, mat_type)
            self.m_title.delete(0, "end")
            self.m_url.delete(0, "end")
            self._m_local_path = ""
            self.m_browse_button.configure(text="📁  Examinar archivo...")
            self.refresh_all()
            self._toast("Material guardado.", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_create_forum_message(self):
        try:
            self.controller.create_forum_message(
                self._id(self.f_course,
                         self._maps.get("forum_course", {})),
                self.f_sender.get(),
                self.f_msg.get("1.0", "end").strip(),
                self._id(self.f_student,
                         self._maps.get("forum_student", {})),
                self._id(self.f_instructor,
                         self._maps.get("forum_instructor", {})))
            self.f_msg.delete("1.0", "end")
            self.refresh_all()
            self._toast("Mensaje publicado.", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_create_quiz_question(self):
        try:
            self.controller.create_quiz_question(
                self._id(self.q_course,
                         self._maps.get("quiz_course", {})),
                self.q_question.get("1.0", "end").strip(),
                self.q_a.get(), self.q_b.get(),
                self.q_c.get(), self.q_d.get(),
                self.q_ok.get())
            self.q_question.delete("1.0", "end")
            for e in (self.q_a, self.q_b, self.q_c, self.q_d):
                e.delete(0, "end")
            self.refresh_all()
            self._toast("Pregunta guardada.", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_submit_quiz(self):
        try:
            score, status = self.controller.submit_quiz_attempt(
                self._id(self.a_enrollment,
                         self._maps.get("enrollment", {})),
                self._id(self.a_question,
                         self._maps.get("question", {})),
                self.a_option.get())
            color = P["green"] if status == "Aprobado" else P["red"]
            self.quiz_result.configure(
                text=f"  {status}  ({score} pts)", text_color=color)
            self._toast(f"Calificacion: {status} ({score} pts)", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def handle_create_review(self):
        try:
            stars = "\u2605" * int(self.r_rating.get()) + \
                    "\u2606" * (5 - int(self.r_rating.get()))
            self.controller.create_review(
                self._id(self.r_course,
                         self._maps.get("review_course", {})),
                self._id(self.r_student,
                         self._maps.get("review_student", {})),
                int(self.r_rating.get()),
                self.r_comment.get("1.0", "end").strip())
            self.r_comment.delete("1.0", "end")
            self.refresh_all()
            self._toast(f"Valoracion guardada  {stars}", ok=True)
        except Exception as e:
            self._toast(str(e), ok=False)

    def _open_local_file(self, path: str):
        """Abre un archivo local con el programa predeterminado del SO."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"No se encontro el archivo:\n{path}")
        if sys.platform == "win32":
            os.startfile(str(p))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])

    def handle_download_material(self):
        try:
            tree = self._tree_widget(self.materials_tree)
            sel  = tree.selection()
            if not sel:
                raise ValueError(tr(self.language, "download_error"))
            values   = tree.item(sel[0], "values")
            # values: (id, course_name, title, material_type, url)
            mat_type = str(values[3]).strip() if len(values) > 3 else ""
            url      = str(values[4]).strip() if len(values) > 4 else ""

            if not url:
                raise ValueError("Este material no tiene enlace registrado.")

            is_local = not url.startswith("http://") and not url.startswith("https://")

            # ── Video → siempre abrir en navegador ──────────────
            if mat_type == "Video":
                if is_local:
                    self._open_local_file(url)
                    self._toast("🎬  Abriendo video con el reproductor...", ok=True)
                else:
                    webbrowser.open(url)
                    self._toast("🎬  Abriendo video en el navegador...", ok=True)

            # ── Repositorio → siempre abrir en navegador ────────
            elif mat_type == "Repositorio":
                webbrowser.open(url)
                self._toast("🔗  Abriendo repositorio en el navegador...", ok=True)

            # ── PDF → archivo local o descarga web ──────────────
            elif mat_type == "PDF":
                if is_local:
                    self._open_local_file(url)
                    self._toast(f"📄  Abriendo PDF: {Path(url).name}", ok=True)
                else:
                    parsed = urlparse(url)
                    fname  = Path(parsed.path).name or f"material_{values[0]}.pdf"
                    dl_dir = get_downloads_dir()
                    dl_dir.mkdir(parents=True, exist_ok=True)
                    dest   = dl_dir / fname
                    urlretrieve(url, dest)
                    self._open_local_file(str(dest))
                    self._toast(f"📄  PDF descargado y abierto: {fname}", ok=True)

            # ── Documento → archivo local o descarga web ─────────
            elif mat_type == "Documento":
                if is_local:
                    self._open_local_file(url)
                    self._toast(f"📝  Abriendo documento: {Path(url).name}", ok=True)
                else:
                    parsed = urlparse(url)
                    fname  = Path(parsed.path).name or f"material_{values[0]}"
                    dl_dir = get_downloads_dir()
                    dl_dir.mkdir(parents=True, exist_ok=True)
                    dest   = dl_dir / fname
                    urlretrieve(url, dest)
                    self._open_local_file(str(dest))
                    self._toast(f"📝  Documento descargado y abierto: {fname}", ok=True)

            # ── Tipo desconocido ─────────────────────────────────
            else:
                if is_local:
                    self._open_local_file(url)
                else:
                    webbrowser.open(url)
                self._toast("🌐  Abriendo material...", ok=True)

        except Exception as e:
            self._toast(str(e), ok=False)
