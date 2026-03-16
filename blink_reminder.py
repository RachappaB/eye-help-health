#!/usr/bin/env python3
"""
Eye Blink Reminder — Ubuntu Desktop
-------------------------------------
Screen goes INSTANTLY black → holds → instantly disappears.
Zero brightness changes. Zero color transitions. Pure black only.

Requirements:
    sudo apt install python3-tk libnotify-bin

Optional tray icon:
    pip install pystray pillow

Auto-start on login:
    python3 blink_reminder.py --install
    python3 blink_reminder.py --remove
"""

import tkinter as tk
import threading
import random
import time
import subprocess
import sys
import os
import signal

try:
    from PIL import Image, ImageDraw
    import pystray
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ── Config ────────────────────────────────────────────────────────────────────
CFG = {
    "min_interval":  120,    # seconds between reminders
    "max_interval":  240,
    "hold_ms":       1500,  # how long screen stays black (ms)
    "notify":        True,
    "rule_20_20_20": False,
}

INTERVALS = {
    "30-50 s  (frequent)": (30,  50),
    "60-80 s  (default)":  (60,  80),
    "2-3 min  (relaxed)":  (120, 180),
}

# ── Notification ──────────────────────────────────────────────────────────────
def notify(title, body):
    if not CFG["notify"]:
        return
    try:
        subprocess.Popen(
            ["notify-send", "-t", "2500", "-i", "dialog-information", title, body],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


# ── Overlay ───────────────────────────────────────────────────────────────────
class BlinkOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self._build_window()
        self._paused    = False
        self._stop_evt  = threading.Event()
        self._animating = False

    def _build_window(self):
        r = self.root
        r.overrideredirect(True)   # no title bar
        r.withdraw()               # hidden at start
        r.update_idletasks()

        sw = r.winfo_screenwidth()
        sh = r.winfo_screenheight()
        r.geometry(f"{sw}x{sh}+0+0")
        r.attributes("-topmost", True)

        # ── Everything is BLACK from the start. Never changes color. ──
        r.configure(bg="#000000")
        self._canvas = tk.Canvas(
            r, width=sw, height=sh,
            bg="#000000",           # pure black — always
            highlightthickness=0
        )
        self._canvas.pack(fill="both", expand=True)

        # Subtle white text shown only while black
        self._label = tk.Label(
            r, text="",
            font=("Sans", 26, "bold"),
            fg="#cccccc",
            bg="#000000",
        )
        self._canvas.create_window(sw // 2, sh // 2,
                                   window=self._label, anchor="center")

        r.bind("<Escape>", lambda _: self.quit())

    # ── Show: instantly black ─────────────────────────────────────────────────
    def _show_black(self, msg, hold_ms):
        self._label.config(text=msg)
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.update()
        # After holding, instantly vanish
        self.root.after(hold_ms, self._instant_hide)

    # ── Hide: instantly gone ──────────────────────────────────────────────────
    def _instant_hide(self):
        self.root.withdraw()
        self._animating = False

    # ── Trigger (called from timer thread via after) ──────────────────────────
    def trigger_blink(self, rule_20=False):
        if self._animating:
            return
        self._animating = True
        msg     = ("Look 20 ft away for 20 seconds..."
                   if rule_20 else "Blink slowly — relax your eyes")
        hold_ms = 20_000 if rule_20 else CFG["hold_ms"]
        self.root.after(0, self._show_black, msg, hold_ms)

    # ── Timer thread ──────────────────────────────────────────────────────────
    def _timer_loop(self):
        count = 0
        while not self._stop_evt.is_set():
            wait = random.randint(CFG["min_interval"], CFG["max_interval"])
            for _ in range(wait * 2):
                if self._stop_evt.is_set():
                    return
                time.sleep(0.5)

            if self._paused:
                continue

            count += 1
            rule_20 = CFG["rule_20_20_20"] and (count % 20 == 0)

            if rule_20:
                notify("20-20-20 Rule", "Look 20 ft away for 20 seconds.")
            else:
                notify("Eye Blink Reminder", "Relax your eyes.")

            self.trigger_blink(rule_20=rule_20)

            hold_s = (20 if rule_20 else CFG["hold_ms"] / 1000) + 1
            time.sleep(hold_s)

    def start(self):
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def quit(self):
        self._stop_evt.set()
        self.root.after(0, self.root.destroy)

    def run(self):
        self.root.mainloop()


# ── Tray ──────────────────────────────────────────────────────────────────────
def _make_eye_icon():
    sz = 64
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    d.ellipse([ 4, 18, 60, 46], fill="#1a1a2e", outline="#e0e0e0", width=3)
    d.ellipse([20, 22, 44, 42], fill="#3a8eef")
    d.ellipse([27, 28, 37, 38], fill="#000000")
    d.ellipse([29, 30, 33, 34], fill="#ffffff")
    return img


def build_tray(overlay):
    if not HAS_TRAY:
        return None

    def on_pause(icon, item):
        overlay.pause()
        icon.title = "Blink Reminder [Paused]"
        notify("Blink Reminder", "Paused")

    def on_resume(icon, item):
        overlay.resume()
        icon.title = "Blink Reminder [Running]"
        notify("Blink Reminder", "Resumed")

    def on_blink_now(icon, item):
        overlay.trigger_blink()

    def on_quit(icon, item):
        icon.stop()
        overlay.quit()

    def set_interval(lo, hi):
        def _fn(icon, item):
            CFG["min_interval"] = lo
            CFG["max_interval"] = hi
            notify("Blink Reminder", f"Interval: {lo}-{hi} s")
        return _fn

    def toggle_20(icon, item):
        CFG["rule_20_20_20"] = not CFG["rule_20_20_20"]
        notify("Blink Reminder",
               "20-20-20 ON" if CFG["rule_20_20_20"] else "20-20-20 OFF")

    interval_items = [
        pystray.MenuItem(label, set_interval(lo, hi))
        for label, (lo, hi) in INTERVALS.items()
    ]
    menu = pystray.Menu(
        pystray.MenuItem("Pause",         on_pause),
        pystray.MenuItem("Resume",        on_resume),
        pystray.MenuItem("Blink Now",     on_blink_now),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Set Interval",  pystray.Menu(*interval_items)),
        pystray.MenuItem("20-20-20 Rule", toggle_20),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit",          on_quit),
    )
    return pystray.Icon("blink", _make_eye_icon(),
                        "Blink Reminder [Running]", menu)


# ── Auto-start ────────────────────────────────────────────────────────────────
def install_autostart():
    d = os.path.expanduser("~/.config/autostart")
    f = os.path.join(d, "blink_reminder.desktop")
    os.makedirs(d, exist_ok=True)
    with open(f, "w") as fp:
        fp.write(f"""[Desktop Entry]
Type=Application
Name=Eye Blink Reminder
Exec={sys.executable} {os.path.abspath(__file__)}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Reminds you to blink and rest your eyes
""")
    print(f"Auto-start installed: {f}")


def remove_autostart():
    f = os.path.expanduser("~/.config/autostart/blink_reminder.desktop")
    if os.path.exists(f):
        os.remove(f)
        print("Auto-start removed.")
    else:
        print("No auto-start entry found.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) > 1:
        a = sys.argv[1]
        if a == "--install":  install_autostart(); return
        if a == "--remove":   remove_autostart();  return
        print("Usage: python3 blink_reminder.py [--install | --remove]")
        return

    signal.signal(signal.SIGINT, lambda *_: os.kill(os.getpid(), signal.SIGTERM))

    overlay = BlinkOverlay()
    overlay.start()

    tray = build_tray(overlay)
    if tray:
        threading.Thread(target=tray.run, daemon=True).start()
        print("Tray icon active.")
    else:
        print("No tray (pip install pystray pillow to enable).")

    lo, hi = CFG["min_interval"], CFG["max_interval"]
    notify("Eye Blink Reminder", f"Started. First blink in {lo}-{hi} s.")
    print(f"Running — first blink in {lo}-{hi} s. ESC or Ctrl-C to quit.")
    overlay.run()


if __name__ == "__main__":
    main()