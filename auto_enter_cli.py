#!/usr/bin/env python3
"""
Antigravity CLI - Auto Enter Script (Version Console Léger)
-----------------------------------------------------------
Exécute des appuis automatiques sur la touche [Entrée] pour valider
automatiquement les commandes et les demandes de permission dans le terminal.
Compatible Windows et Linux.

Usage:
    python3 auto_enter_cli.py
    python3 auto_enter_cli.py --interval 0.5
    python3 auto_enter_cli.py --delay 5 --interval 1.0

Raccourci:
    [F8]    : Mettre en pause / Reprendre (Windows)
    [Ctrl+C]: Quitter
"""

import sys
import time
import argparse
import shutil
import subprocess

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    VK_RETURN = 0x0D
    VK_F8 = 0x77
    KEYEVENTF_KEYUP = 0x0002
else:
    user32 = None


def press_enter_key() -> bool:
    if IS_WINDOWS:
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        return True
    else:
        # Linux implementation: xdotool (X11) or ydotool (Wayland)
        if shutil.which("xdotool"):
            subprocess.run(["xdotool", "key", "Return"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        elif shutil.which("ydotool"):
            subprocess.run(["ydotool", "key", "28:1", "28:0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        else:
            return False


def get_foreground_window_title() -> str:
    if IS_WINDOWS:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    else:
        if shutil.which("xdotool"):
            try:
                res = subprocess.check_output(["xdotool", "getactivewindow", "getwindowname"], stderr=subprocess.DEVNULL)
                return res.decode("utf-8", errors="ignore").strip()
            except Exception:
                return "Terminal"
        return "Terminal (Linux)"


def check_f8_pressed(was_down: bool):
    if IS_WINDOWS:
        f8_state = (user32.GetAsyncKeyState(VK_F8) & 0x8000) != 0
        return f8_state, (f8_state and not was_down)
    return False, False


def main():
    parser = argparse.ArgumentParser(description="Auto-Enter pour Antigravity CLI et terminaux (Windows / Linux)")
    parser.add_argument("--interval", "-i", type=float, default=1.0, help="Délai entre chaque appui sur Entrée en secondes (défaut: 1.0)")
    parser.add_argument("--delay", "-d", type=int, default=3, help="Délai initial avant de commencer en secondes (défaut: 3)")
    parser.add_argument("--count", "-c", type=int, default=0, help="Nombre max d'appuis (0 = infini, défaut: 0)")
    parser.add_argument("--all-windows", action="store_true", help="Appuyer quelle que soit la fenêtre active (par défaut filtre sur terminaux/agy)")
    args = parser.parse_args()

    terminal_keywords = ["agy", "antigravity", "powershell", "cmd", "terminal", "bash", "zsh", "mintty", "conhost", "pts"]

    print("=" * 60)
    print("  Antigravity CLI - Script Auto-Enter")
    print("=" * 60)
    print(f" * Système        : {'Windows' if IS_WINDOWS else 'Linux'}")
    print(f" * Intervalle     : {args.interval}s")
    print(f" * Délai initial  : {args.delay}s")
    print(f" * Filtre fenêtre : {'Toutes les fenêtres' if args.all_windows else 'Terminaux (agy, bash, terminal, etc.)'}")
    if IS_WINDOWS:
        print(" * Raccourci      : [F8] pour Mettre en pause / Reprendre")
    print(" * Arrêt          : [Ctrl + C]")
    if not IS_WINDOWS and not shutil.which("xdotool") and not shutil.which("ydotool"):
        print("\n [ATTENTION] Ni 'xdotool' (pour X11) ni 'ydotool' (pour Wayland) n'est installé.")
        print("             Pour simuler des frappes clavier : sudo apt install -y xdotool")
        print("\n             Astuce : La méthode recommandée et native sous Linux est simplement :")
        print("             $ agy-auto")
        print("             (Auto-approbation native, aucun outil externe requis)")
        print("=" * 60)

    if args.delay > 0:
        print(f"\nDémarrage dans {args.delay} secondes (basculez sur votre terminal)...")
        for remaining in range(args.delay, 0, -1):
            print(f" > {remaining}s...", end="\r", flush=True)
            time.sleep(1)
        print(" > Actif !          \n")

    count = 0
    paused = False
    was_f8_down = False

    try:
        while True:
            # Vérification de la touche F8 (Windows)
            f8_state, f8_triggered = check_f8_pressed(was_f8_down)
            was_f8_down = f8_state
            if f8_triggered:
                paused = not paused
                status_str = "PAUSE (Appuyez sur F8 pour reprendre)" if paused else "REPRISE"
                print(f"\n[F8] => {status_str}")

            if not paused:
                active_title = get_foreground_window_title()
                should_press = False

                if args.all_windows or not IS_WINDOWS:
                    should_press = True
                else:
                    title_lower = active_title.lower()
                    if any(kw in title_lower for kw in terminal_keywords):
                        should_press = True

                if should_press:
                    sent = press_enter_key()
                    count += 1
                    short_title = (active_title[:30] + "..") if len(active_title) > 32 else active_title
                    timestamp = time.strftime("%H:%M:%S")
                    status_text = "[Entrée envoyée]" if sent else "[Simulation ignorée: installez xdotool]"
                    print(f"[{timestamp}] [#{count}] {status_text} -> '{short_title}'")

                    if args.count > 0 and count >= args.count:
                        print(f"\nLimite atteinte ({count} appuis). Fin.")
                        break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\nInterruption manuelle. Total d'appuis envoyés: {count}")


if __name__ == "__main__":
    main()
