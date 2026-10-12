"""
Antigravity CLI - Auto Enter & Auto Permission App
--------------------------------------------------
Application graphique Windows (Tkinter + ctypes natif) permettant de:
1. Simuler automatiquement l'appui sur la touche Entrée pour valider les invites du CLI Antigravity.
2. Détecter et cibler automatiquement la fenêtre de terminal (Windows Terminal, PowerShell, CMD, etc.).
3. Activer / Désactiver à tout moment via le raccourci clavier global [F8].
4. Lancer directement le CLI Antigravity en mode sans permissions (--dangerously-skip-permissions).
"""

import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from ctypes import wintypes

# Windows API Constants & Functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_RETURN = 0x0D
VK_F8 = 0x77
KEYEVENTF_KEYUP = 0x0002

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def press_enter_key():
    """Envoie un événement d'appui puis de relâchement de la touche Entrée."""
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)


def get_foreground_window_title() -> str:
    """Récupère le titre de la fenêtre actuellement au premier plan."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value


def find_windows_matching(keyword: str):
    """Trouve toutes les fenêtres visibles dont le titre contient le mot-clé (insensible à la casse)."""
    matches = []
    kw_lower = keyword.strip().lower()

    def enum_cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                if kw_lower in title.lower():
                    matches.append((hwnd, title))
        return True

    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return matches


def activate_window(hwnd):
    """Met la fenêtre spécifiée au premier plan."""
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)


class AutoEnterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Antigravity Auto-Enter & Permissions")
        self.geometry("540x620")
        self.minsize(500, 560)
        self.configure(bg="#1e1e2e")

        self.is_running = False
        self.press_count = 0
        self.worker_thread = None
        self.hotkey_thread = None
        self.stop_requested = False

        self._init_styles()
        self._build_ui()
        self._start_hotkey_listener()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _init_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(".", background="#1e1e2e", foreground="#cdd6f4")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#89b4fa")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#a6adc8")
        self.style.configure("BadgeActive.TLabel", font=("Segoe UI", 11, "bold"), foreground="#a6e3a1", background="#313244", padding=6)
        self.style.configure("BadgeInactive.TLabel", font=("Segoe UI", 11, "bold"), foreground="#f38ba8", background="#313244", padding=6)

        self.style.configure("TCheckbutton", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("TRadiobutton", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("Card.TFrame", background="#26273a", relief="flat")

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=16)
        main_frame.pack(fill="both", expand=True)

        # En-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        title_lbl = ttk.Label(header_frame, text="Antigravity CLI - Auto-Enter Bot", style="Header.TLabel")
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(
            header_frame,
            text="Valide automatiquement les commandes et demandes de confirmation.",
            style="SubHeader.TLabel",
        )
        sub_lbl.pack(anchor="w")

        # Statut + Compteur
        status_card = ttk.Frame(main_frame, style="Card.TFrame", padding=12)
        status_card.pack(fill="x", pady=(0, 12))

        status_row = ttk.Frame(status_card, style="Card.TFrame")
        status_row.pack(fill="x")

        self.status_badge = ttk.Label(status_row, text="● INACTIF", style="BadgeInactive.TLabel")
        self.status_badge.pack(side="left")

        self.counter_lbl = ttk.Label(
            status_row,
            text="Entrées envoyées: 0",
            font=("Segoe UI", 11, "bold"),
            background="#26273a",
            foreground="#fab387",
        )
        self.counter_lbl.pack(side="right")

        hotkey_hint = ttk.Label(
            status_card,
            text="Raccourci global: Appuyez sur [F8] pour Activer / Mettre en pause",
            font=("Segoe UI", 9, "italic"),
            background="#26273a",
            foreground="#94e2d5",
        )
        hotkey_hint.pack(anchor="w", pady=(8, 0))

        # Bouton Principal Start / Stop
        self.btn_toggle = tk.Button(
            main_frame,
            text="▶ DÉMARRER (ou appuyer sur F8)",
            font=("Segoe UI", 12, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            activebackground="#94e2d5",
            activeforeground="#11111b",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=10,
            command=self.toggle_running,
        )
        self.btn_toggle.pack(fill="x", pady=(0, 12))

        # Options de configuration
        config_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=12)
        config_frame.pack(fill="x", pady=(0, 12))

        # Intervalle
        interval_row = ttk.Frame(config_frame, style="Card.TFrame")
        interval_row.pack(fill="x", pady=(0, 8))

        ttk.Label(interval_row, text="Intervalle entre chaque Entrée:", background="#26273a").pack(side="left")
        self.interval_var = tk.DoubleVar(value=1.0)
        self.interval_spin = ttk.Spinbox(
            interval_row,
            from_=0.2,
            to=10.0,
            increment=0.2,
            textvariable=self.interval_var,
            width=6,
            font=("Segoe UI", 10),
        )
        self.interval_spin.pack(side="left", padx=8)
        ttk.Label(interval_row, text="secondes", background="#26273a").pack(side="left")

        # Compte à rebours avant 1er appui
        delay_row = ttk.Frame(config_frame, style="Card.TFrame")
        delay_row.pack(fill="x", pady=(0, 8))

        ttk.Label(delay_row, text="Délai initial au démarrage:", background="#26273a").pack(side="left")
        self.delay_var = tk.IntVar(value=2)
        self.delay_spin = ttk.Spinbox(
            delay_row,
            from_=0,
            to=15,
            increment=1,
            textvariable=self.delay_var,
            width=6,
            font=("Segoe UI", 10),
        )
        self.delay_spin.pack(side="left", padx=8)
        ttk.Label(delay_row, text="secondes (pour basculer sur le terminal)", background="#26273a").pack(side="left")

        # Mode de ciblage
        mode_label = ttk.Label(config_frame, text="Mode de ciblage:", font=("Segoe UI", 10, "bold"), background="#26273a")
        mode_label.pack(anchor="w", pady=(4, 4))

        self.target_mode_var = tk.StringVar(value="foreground_filter")

        rb1 = ttk.Radiobutton(
            config_frame,
            text="Uniquement si la fenêtre active est un terminal (agy, powershell, cmd, terminal)",
            variable=self.target_mode_var,
            value="foreground_filter",
        )
        rb1.pack(anchor="w", pady=2)

        rb2 = ttk.Radiobutton(
            config_frame,
            text="N'importe quelle fenêtre active au premier plan",
            variable=self.target_mode_var,
            value="foreground_any",
        )
        rb2.pack(anchor="w", pady=2)

        # Raccourci Always on Top
        self.ontop_var = tk.BooleanVar(value=True)
        cb_ontop = ttk.Checkbutton(
            config_frame,
            text="Garder cette fenêtre toujours au-dessus (Always on Top)",
            variable=self.ontop_var,
            command=self._apply_always_on_top,
        )
        cb_ontop.pack(anchor="w", pady=(6, 2))
        self._apply_always_on_top()

        # Actions Rapides
        actions_row = ttk.Frame(main_frame)
        actions_row.pack(fill="x", pady=(0, 8))

        btn_manual = tk.Button(
            actions_row,
            text="Valider 1 fois maintenant",
            font=("Segoe UI", 9),
            bg="#313244",
            fg="#cdd6f4",
            relief="flat",
            padx=10,
            pady=4,
            command=self.manual_press_once,
        )
        btn_manual.pack(side="left", padx=(0, 8))

        btn_launch_agy = tk.Button(
            actions_row,
            text="⚡ Ouvrir agy-auto (Mode sans permissions)",
            font=("Segoe UI", 9, "bold"),
            bg="#f9e2af",
            fg="#11111b",
            relief="flat",
            padx=10,
            pady=4,
            command=self.launch_agy_auto_terminal,
        )
        btn_launch_agy.pack(side="right")

        # Zone Journal / Logs
        log_label = ttk.Label(main_frame, text="Journal d'activité:", font=("Segoe UI", 9, "bold"))
        log_label.pack(anchor="w", pady=(4, 2))

        self.log_text = tk.Text(
            main_frame,
            height=7,
            bg="#181825",
            fg="#cdd6f4",
            font=("Consolas", 9),
            relief="flat",
            padx=6,
            pady=6,
        )
        self.log_text.pack(fill="both", expand=True)

        self._log("Prêt. Appuyez sur [F8] ou sur le bouton pour démarrer.")

    def _apply_always_on_top(self):
        self.attributes("-topmost", self.ontop_var.get())

    def _log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def toggle_running(self):
        if self.is_running:
            self.stop_automation()
        else:
            self.start_automation()

    def start_automation(self):
        if self.is_running:
            return

        self.is_running = True
        self.stop_requested = False
        self.status_badge.configure(text="● ACTIF", style="BadgeActive.TLabel")
        self.btn_toggle.configure(
            text="⏹ ARRÊTER (ou appuyer sur F8)",
            bg="#f38ba8",
            fg="#11111b",
        )

        interval = max(0.1, float(self.interval_var.get()))
        delay = max(0, int(self.delay_var.get()))
        mode = self.target_mode_var.get()

        self._log(f"Démarrage. Intervalle={interval}s, Délai initial={delay}s, Mode={mode}")

        self.worker_thread = threading.Thread(
            target=self._automation_loop,
            args=(interval, delay, mode),
            daemon=True,
        )
        self.worker_thread.start()

    def stop_automation(self):
        if not self.is_running:
            return

        self.stop_requested = True
        self.is_running = False
        self.status_badge.configure(text="● EN PAUSE", style="BadgeInactive.TLabel")
        self.btn_toggle.configure(
            text="▶ DÉMARRER (ou appuyer sur F8)",
            bg="#a6e3a1",
            fg="#11111b",
        )
        self._log("Arrêté.")

    def _automation_loop(self, interval: float, delay: int, mode: str):
        if delay > 0:
            for i in range(delay, 0, -1):
                if self.stop_requested:
                    return
                self.after(0, self._log, f"Démarrage dans {i}s...")
                time.sleep(1)

        terminal_keywords = ["agy", "antigravity", "powershell", "cmd", "terminal", "bash", "mintty", "conhost"]

        while not self.stop_requested:
            try:
                active_title = get_foreground_window_title()
                should_press = False

                if mode == "foreground_any":
                    should_press = True
                elif mode == "foreground_filter":
                    title_lower = active_title.lower()
                    if any(kw in title_lower for kw in terminal_keywords):
                        should_press = True

                if should_press:
                    press_enter_key()
                    self.press_count += 1
                    count = self.press_count
                    self.after(0, self._update_count_ui, count, active_title)

            except Exception as e:
                self.after(0, self._log, f"Erreur: {e}")

            time.sleep(interval)

    def _update_count_ui(self, count: int, window_title: str):
        self.counter_lbl.configure(text=f"Entrées envoyées: {count}")
        short_title = (window_title[:32] + "..") if len(window_title) > 34 else window_title
        if not short_title:
            short_title = "(Fenêtre active)"
        self._log(f"Entrée #{count} envoyée à: {short_title}")

    def manual_press_once(self):
        """Valide 1 fois après 0.5 seconde pour permettre de changer de fenêtre."""
        self._log("Envoi manuel dans 1 seconde...")

        def _delayed():
            time.sleep(1.0)
            press_enter_key()
            self.press_count += 1
            self.after(0, self._update_count_ui, self.press_count, get_foreground_window_title())

        threading.Thread(target=_delayed, daemon=True).start()

    def launch_agy_auto_terminal(self):
        """Ouvre une nouvelle fenêtre de terminal avec agy-auto."""
        try:
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "cmd.exe", "/k", "agy-auto"],
                shell=True,
            )
            self._log("Terminal agy-auto lancé dans une nouvelle fenêtre!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer agy-auto: {e}")

    def _start_hotkey_listener(self):
        """Écoute la touche globale F8 pour basculer Marche/Arrêt."""
        def listener():
            was_pressed = False
            while True:
                # 0x77 = VK_F8
                state = user32.GetAsyncKeyState(VK_F8)
                is_pressed = (state & 0x8000) != 0

                if is_pressed and not was_pressed:
                    # Basculer l'état
                    self.after(0, self.toggle_running)

                was_pressed = is_pressed
                time.sleep(0.05)

        self.hotkey_thread = threading.Thread(target=listener, daemon=True)
        self.hotkey_thread.start()

    def on_close(self):
        self.stop_requested = True
        self.is_running = False
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = AutoEnterApp()
    app.mainloop()
