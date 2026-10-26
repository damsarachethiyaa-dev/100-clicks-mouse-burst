"""
⚡ 100-Clicks Mouse Burst Multiplier - Cyber Elite Edition (Custom Value Support)
Built with CustomTkinter & High-Performance Canvas Animation Engine
Includes custom editable Delay & Speed inputs, quick presets, and live CPS calculations.
"""

import sys
import os
import time
import math
import random
import threading
import ctypes
from ctypes import wintypes
import winsound
import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Set 1ms high-precision Windows multimedia timer
try:
    ctypes.windll.winmm.timeBeginPeriod(1)
except Exception:
    pass

# Win32 Virtual Key Constants
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_ESCAPE  = 0x1B
VK_F6      = 0x75
VK_F8      = 0x77

# Win32 Mouse Event Flags
MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040

BUTTON_CONFIGS = {
    "Right Click": {
        "vk": VK_RBUTTON,
        "down": MOUSEEVENTF_RIGHTDOWN,
        "up": MOUSEEVENTF_RIGHTUP,
        "label": "Right Click"
    },
    "Left Click": {
        "vk": VK_LBUTTON,
        "down": MOUSEEVENTF_LEFTDOWN,
        "up": MOUSEEVENTF_LEFTUP,
        "label": "Left Click"
    },
    "Middle Click": {
        "vk": VK_MBUTTON,
        "down": MOUSEEVENTF_MIDDLEDOWN,
        "up": MOUSEEVENTF_MIDDLEUP,
        "label": "Middle Click"
    }
}

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3.0, 8.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(3.5, 7.0)
        self.color = color
        self.life = random.randint(25, 45)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.vy += 0.14
        self.size *= 0.94
        self.life -= 1
        return self.life > 0

class Shockwave:
    def __init__(self, x, y, max_radius=95, color="#00f0ff"):
        self.x = x
        self.y = y
        self.radius = 8
        self.max_radius = max_radius
        self.color = color
        self.life = 22
        self.max_life = 22

    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.22
        self.life -= 1
        return self.life > 0

class BurstClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("100-Clicks Multiplier • Cyber Edition")
        self.root.geometry("520x810")
        self.root.resizable(False, False)

        # Set CustomTkinter Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.root.configure(fg_color="#0a0c13")

        # Set Title Bar Icon with Win32 API
        self._apply_native_icon()

        # Engine State - ACTIVE BY DEFAULT
        self.is_active = True
        self.is_bursting = False
        self.running = True
        self.total_delivered_clicks = 0
        self.arena_registered_clicks = 0
        self.burst_progress = 0.0

        # Animation states
        self.anim_frame = 0
        self.particles = []
        self.shockwaves = []
        self.recent_clicks_timestamps = []
        self.current_cps = 0

        # Settings Variables
        self.selected_button = "Right Click"
        self.burst_count_var = tk.StringVar(value="100")
        self.delay_ms_var = tk.StringVar(value="3.0")
        self.slider_delay_val = tk.DoubleVar(value=3.0)
        self.sound_var = tk.BooleanVar(value=True)
        self.always_on_top_var = tk.BooleanVar(value=True)
        self.trigger_on_click_var = tk.BooleanVar(value=True)

        self._updating_internally = False

        self._build_ui()
        self._apply_always_on_top()

        # Watch custom delay text changes
        self.delay_ms_var.trace_add("write", self._on_delay_text_changed)

        # Audio confirmation on startup
        if self.sound_var.get():
            threading.Thread(target=lambda: (winsound.Beep(900, 80), winsound.Beep(1400, 120)), daemon=True).start()

        # Start 60 FPS animation loop
        self._animation_tick()

        # Start background listener thread
        self.listener_thread = threading.Thread(target=self._mouse_listener_loop, daemon=True)
        self.listener_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_native_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
            try:
                self.root.update_idletasks()
                hwnd = user32.GetParent(self.root.winfo_id())
                if not hwnd:
                    hwnd = self.root.winfo_id()
                WM_SETICON = 0x0080
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010
                LR_DEFAULTSIZE = 0x00000040
                h_icon = user32.LoadImageW(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
                if h_icon:
                    user32.SendMessageW(hwnd, WM_SETICON, 0, h_icon)
                    user32.SendMessageW(hwnd, WM_SETICON, 1, h_icon)
            except Exception:
                pass

    def _build_ui(self):
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=16, pady=12)

        # 1. Top Header Card
        header_card = ctk.CTkFrame(container, fg_color="#121522", corner_radius=14, border_width=1, border_color="#20263b")
        header_card.pack(fill="x", pady=(0, 10))

        header_inner = ctk.CTkFrame(header_card, fg_color="transparent")
        header_inner.pack(fill="x", padx=16, pady=12)

        title_box = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="⚡ 100-CLICKS MULTIPLIER",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#00f0ff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="HYPER-SPEED HARDWARE BURST ENGINE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#9aa2c4"
        ).pack(anchor="w", pady=(1, 0))

        # Status Badge Pill
        self.status_pill = ctk.CTkLabel(
            header_inner,
            text="🟢 ACTIVE",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#00ff88",
            fg_color="#0d2b20",
            corner_radius=20,
            padx=14,
            pady=4
        )
        self.status_pill.pack(side="right")

        # 2. Hero Action Button (Start / Pause Toggle)
        self.toggle_btn = ctk.CTkButton(
            container,
            text="⚡ BURST MODE ACTIVE  •  PRESS [F6] TO PAUSE",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#00e676",
            hover_color="#00c853",
            text_color="#0a120d",
            corner_radius=12,
            height=44,
            command=self.toggle_active,
            cursor="hand2"
        )
        self.toggle_btn.pack(fill="x", pady=(0, 10))

        # 3. Interactive Click Arena
        arena_card = ctk.CTkFrame(container, fg_color="#121522", corner_radius=14, border_width=1, border_color="#22283d")
        arena_card.pack(fill="x", pady=(0, 10))

        arena_header = ctk.CTkFrame(arena_card, fg_color="transparent")
        arena_header.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            arena_header,
            text="🎯 LIVE CLICK ARENA",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#ffd600"
        ).pack(side="left")

        self.cps_badge = ctk.CTkLabel(
            arena_header,
            text="⚡ 0 CPS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#00f0ff",
            fg_color="#182338",
            corner_radius=10,
            padx=10,
            pady=2
        )
        self.cps_badge.pack(side="right")

        # Canvas Arena
        self.arena_canvas = tk.Canvas(
            arena_card,
            width=488,
            height=150,
            bg="#0c0e17",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.arena_canvas.pack(fill="x", padx=10, pady=(0, 10))
        self.arena_canvas.bind("<Button-3>", lambda e: self._on_arena_user_click(e, "Right Click"))
        self.arena_canvas.bind("<Button-1>", lambda e: self._on_arena_user_click(e, "Left Click"))

        # 4. Target Mouse Button Selector (Custom 3-Button Selector with High Contrast)
        btn_selector_card = ctk.CTkFrame(container, fg_color="#121522", corner_radius=12, border_width=1, border_color="#1e2336")
        btn_selector_card.pack(fill="x", pady=(0, 10), ipady=6)

        ctk.CTkLabel(
            btn_selector_card,
            text="TARGET MOUSE BUTTON TO BURST:",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#b8c0e2"
        ).pack(anchor="w", padx=14, pady=(6, 6))

        btn_row = ctk.CTkFrame(btn_selector_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 6))

        self.btn_right = ctk.CTkButton(
            btn_row,
            text="🖱️ Right Click",
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda: self._select_button("Right Click")
        )
        self.btn_right.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_left = ctk.CTkButton(
            btn_row,
            text="🖱️ Left Click",
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda: self._select_button("Left Click")
        )
        self.btn_left.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_mid = ctk.CTkButton(
            btn_row,
            text="🖱️ Middle Click",
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda: self._select_button("Middle Click")
        )
        self.btn_mid.pack(side="left", expand=True, fill="x", padx=3)

        self._refresh_button_selector_colors()

        # 5. Clicks Count & Speed Settings Card
        settings_card = ctk.CTkFrame(container, fg_color="#121522", corner_radius=12, border_width=1, border_color="#1e2336")
        settings_card.pack(fill="x", pady=(0, 10), ipady=6)

        # Row A: Clicks Presets & Stepper
        row_preset = ctk.CTkFrame(settings_card, fg_color="transparent")
        row_preset.pack(fill="x", padx=14, pady=(6, 4))

        ctk.CTkLabel(
            row_preset,
            text="CLICKS PER BURST:",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#b8c0e2"
        ).pack(side="left")

        # Stepper & Value
        stepper_box = ctk.CTkFrame(row_preset, fg_color="transparent")
        stepper_box.pack(side="right")

        ctk.CTkButton(
            stepper_box, text="-", width=28, height=26, corner_radius=6,
            fg_color="#22283e", hover_color="#2f3757", text_color="#00f0ff",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._adjust_clicks(-10)
        ).pack(side="left", padx=2)

        self.click_entry = ctk.CTkEntry(
            stepper_box, textvariable=self.burst_count_var, width=64, height=26,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            justify="center", fg_color="#161928", text_color="#ffffff",
            border_color="#00f0ff", border_width=1, corner_radius=6
        )
        self.click_entry.pack(side="left", padx=2)

        ctk.CTkButton(
            stepper_box, text="+", width=28, height=26, corner_radius=6,
            fg_color="#22283e", hover_color="#2f3757", text_color="#00f0ff",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._adjust_clicks(10)
        ).pack(side="left", padx=2)

        # Quick Preset Pills
        pills_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        pills_row.pack(fill="x", padx=14, pady=(2, 8))

        for count in [50, 100, 250, 500, 1000]:
            btn = ctk.CTkButton(
                pills_row,
                text=f"{count}",
                width=54,
                height=26,
                corner_radius=6,
                fg_color="#1c2136",
                hover_color="#2c3456",
                text_color="#ffffff",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                command=lambda c=count: self.burst_count_var.set(str(c))
            )
            btn.pack(side="left", expand=True, padx=2)

        # Row B: CLICK DELAY / SPEED with CUSTOM INPUT BOX & PRESETS
        speed_header_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        speed_header_row.pack(fill="x", padx=14, pady=(4, 2))

        ctk.CTkLabel(
            speed_header_row,
            text="CLICK DELAY / SPEED:",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#b8c0e2"
        ).pack(side="left")

        # Custom Delay Stepper & Input Entry (ANY value user likes!)
        delay_stepper_box = ctk.CTkFrame(speed_header_row, fg_color="transparent")
        delay_stepper_box.pack(side="right")

        ctk.CTkButton(
            delay_stepper_box, text="-", width=28, height=26, corner_radius=6,
            fg_color="#22283e", hover_color="#2f3757", text_color="#00f0ff",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._adjust_delay(-1.0)
        ).pack(side="left", padx=2)

        self.delay_entry = ctk.CTkEntry(
            delay_stepper_box, textvariable=self.delay_ms_var, width=64, height=26,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            justify="center", fg_color="#161928", text_color="#ffffff",
            border_color="#00f0ff", border_width=1, corner_radius=6
        )
        self.delay_entry.pack(side="left", padx=2)

        ctk.CTkLabel(
            delay_stepper_box,
            text="ms",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#00f0ff"
        ).pack(side="left", padx=(1, 2))

        ctk.CTkButton(
            delay_stepper_box, text="+", width=28, height=26, corner_radius=6,
            fg_color="#22283e", hover_color="#2f3757", text_color="#00f0ff",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._adjust_delay(1.0)
        ).pack(side="left", padx=2)

        # Quick Speed Presets Pills
        speed_pills_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        speed_pills_row.pack(fill="x", padx=14, pady=(2, 6))

        for spd in [1.0, 3.0, 5.0, 10.0, 15.0, 25.0, 50.0]:
            label_text = f"{int(spd)}ms" if spd.is_integer() else f"{spd}ms"
            btn = ctk.CTkButton(
                speed_pills_row,
                text=label_text,
                width=42,
                height=24,
                corner_radius=6,
                fg_color="#1c2136",
                hover_color="#2c3456",
                text_color="#ffffff",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                command=lambda s=spd: self._set_delay_preset(s)
            )
            btn.pack(side="left", expand=True, padx=2)

        # Speed Slider
        slider_card = ctk.CTkFrame(settings_card, fg_color="transparent")
        slider_card.pack(fill="x", padx=14, pady=(2, 4))

        self.speed_slider = ctk.CTkSlider(
            slider_card,
            from_=0.5,
            to=100.0,
            number_of_steps=199,
            variable=self.slider_delay_val,
            command=self._on_slider_change,
            button_color="#00f0ff",
            button_hover_color="#33f5ff",
            progress_color="#00f0ff",
            fg_color="#1c2136",
            height=16
        )
        self.speed_slider.pack(fill="x", pady=(2, 2))

        # Live Dynamic Speed & CPS Rating Description
        self.speed_lbl = ctk.CTkLabel(
            slider_card,
            text="Rating: 3.0 ms (Fast • ~250 CPS)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#00f0ff"
        )
        self.speed_lbl.pack(anchor="w", pady=(1, 2))

        # 6. Feature Switches Row (Crisp White Text)
        switches_row = ctk.CTkFrame(container, fg_color="transparent")
        switches_row.pack(fill="x", pady=(0, 8))

        ctk.CTkSwitch(
            switches_row,
            text="Audio Chimes",
            variable=self.sound_var,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#ffffff",
            progress_color="#00f0ff",
            button_color="#ffffff",
            fg_color="#1c2033"
        ).pack(side="left", padx=4)

        ctk.CTkSwitch(
            switches_row,
            text="Always on Top",
            variable=self.always_on_top_var,
            command=self._apply_always_on_top,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#ffffff",
            progress_color="#00f0ff",
            button_color="#ffffff",
            fg_color="#1c2033"
        ).pack(side="right", padx=4)

        # 7. Hotkeys HUD Card (High Contrast Glowing Keycaps & Crisp Text)
        hotkey_card = ctk.CTkFrame(container, fg_color="#0e101a", corner_radius=10, border_width=1, border_color="#1a1d2e")
        hotkey_card.pack(fill="x", pady=(0, 6), ipady=4)

        hotkey_inner = ctk.CTkFrame(hotkey_card, fg_color="transparent")
        hotkey_inner.pack(expand=True)

        for key, desc in [("[F6]", "Pause/Resume"), ("[F8]", "Instant Burst"), ("[ESC]", "Emergency Stop")]:
            kbox = ctk.CTkFrame(hotkey_inner, fg_color="transparent")
            kbox.pack(side="left", padx=10)
            ctk.CTkLabel(
                kbox, text=key,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="#ffd600", fg_color="#202740", corner_radius=6, padx=6, pady=2
            ).pack(side="left", padx=(0, 4))
            ctk.CTkLabel(
                kbox, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="#e0e5f7"
            ).pack(side="left")

        # 8. Footer Counter
        self.footer_lbl = ctk.CTkLabel(
            container,
            text="⚡ Total Delivered: 0 Clicks  |  Mode: Right Click Multiplier",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#9da7ce"
        )
        self.footer_lbl.pack(side="bottom", pady=(2, 0))

    def _select_button(self, name):
        self.selected_button = name
        self._refresh_button_selector_colors()

    def _refresh_button_selector_colors(self):
        buttons = [
            ("Right Click", self.btn_right),
            ("Left Click", self.btn_left),
            ("Middle Click", self.btn_mid)
        ]
        for btn_name, btn_widget in buttons:
            if self.selected_button == btn_name:
                btn_widget.configure(
                    fg_color="#00f0ff",
                    hover_color="#33f5ff",
                    text_color="#0a0c13"
                )
            else:
                btn_widget.configure(
                    fg_color="#1c2136",
                    hover_color="#2a3252",
                    text_color="#ffffff"
                )

    def _apply_always_on_top(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def _adjust_clicks(self, delta):
        val = self._get_burst_count() + delta
        val = max(1, min(10000, val))
        self.burst_count_var.set(str(val))

    def _adjust_delay(self, delta):
        curr = self._get_delay_ms()
        new_val = max(0.1, round(curr + delta, 1))
        self.delay_ms_var.set(f"{new_val:.1f}")

    def _set_delay_preset(self, spd):
        self.delay_ms_var.set(f"{spd:.1f}")

    def _on_slider_change(self, val):
        if self._updating_internally:
            return
        self._updating_internally = True
        ms = round(val, 1)
        self.delay_ms_var.set(f"{ms:.1f}")
        self._update_speed_label(ms)
        self._updating_internally = False

    def _on_delay_text_changed(self, *args):
        if self._updating_internally:
            return
        try:
            val_str = self.delay_ms_var.get().strip()
            if not val_str:
                return
            ms = float(val_str)
            self._updating_internally = True
            # Update slider if within range
            clamped = max(0.5, min(100.0, ms))
            self.slider_delay_val.set(clamped)
            self._update_speed_label(ms)
            self._updating_internally = False
        except ValueError:
            pass

    def _update_speed_label(self, ms):
        est_cps = int(1000.0 / max(0.2, (1.0 + ms)))
        if ms <= 1.0:
            desc = "Extreme"
        elif ms <= 3.0:
            desc = "Fast / Game Safe"
        elif ms <= 6.0:
            desc = "Moderate"
        elif ms <= 15.0:
            desc = "Controlled"
        elif ms <= 30.0:
            desc = "Steady"
        else:
            desc = "Slow / Paced"
        self.speed_lbl.configure(text=f"Rating: {ms} ms ({desc} • ~{est_cps} CPS)")

    def _get_delay_ms(self):
        try:
            val = float(self.delay_ms_var.get())
            return max(0.1, min(60000.0, val))
        except ValueError:
            return 3.0

    def _get_delay(self):
        ms = self._get_delay_ms()
        return max(0.0001, min(60.0, ms / 1000.0))

    def _get_burst_count(self):
        try:
            val = int(self.burst_count_var.get())
            return max(1, min(10000, val))
        except ValueError:
            return 100

    def toggle_active(self):
        self.is_active = not self.is_active

        if self.is_active:
            self.status_pill.configure(
                text="🟢 ACTIVE",
                text_color="#00ff88",
                fg_color="#0d2b20"
            )
            self.toggle_btn.configure(
                text="⚡ BURST MODE ACTIVE  •  PRESS [F6] TO PAUSE",
                fg_color="#00e676",
                hover_color="#00c853",
                text_color="#0a120d"
            )
            if self.sound_var.get():
                threading.Thread(target=lambda: (winsound.Beep(900, 80), winsound.Beep(1400, 120)), daemon=True).start()
        else:
            self.status_pill.configure(
                text="⏸️ PAUSED",
                text_color="#f38ba8",
                fg_color="#2b1318"
            )
            self.toggle_btn.configure(
                text="▶️ RESUME BURST MODE  •  PRESS [F6] TO START",
                fg_color="#ff3366",
                hover_color="#e91e63",
                text_color="#ffffff"
            )
            if self.sound_var.get():
                threading.Thread(target=lambda: (winsound.Beep(1200, 80), winsound.Beep(700, 120)), daemon=True).start()

    def _on_arena_user_click(self, event, click_type):
        self.arena_registered_clicks += 1
        self._record_cps_click()
        color = "#00f0ff" if click_type == "Right Click" else "#ffd600"
        self._spawn_burst_effects(event.x, event.y, color=color, count=25)

    def _record_cps_click(self):
        now = time.perf_counter()
        self.recent_clicks_timestamps.append(now)

    def _spawn_burst_effects(self, x, y, color="#00f0ff", count=30):
        palette = ["#00f0ff", "#ffd600", "#ff3366", "#00ff88", "#b4befe"]
        for _ in range(count):
            p_color = random.choice(palette)
            self.particles.append(Particle(x, y, p_color))
        self.shockwaves.append(Shockwave(x, y, max_radius=random.uniform(70, 110), color=color))

    def _execute_burst(self, is_mouse_triggered=True):
        if self.is_bursting:
            return
        self.is_bursting = True

        cfg = BUTTON_CONFIGS.get(self.selected_button, BUTTON_CONFIGS["Right Click"])
        down_flag = cfg["down"]
        up_flag = cfg["up"]
        vk = cfg["vk"]

        burst_total = self._get_burst_count()
        delay_sec = self._get_delay()

        clicks_to_fire = max(1, burst_total - 1 if is_mouse_triggered else burst_total)

        cx, cy = 244, 75
        self._spawn_burst_effects(cx, cy, color="#ffd600", count=35)

        def run_clicks():
            try:
                for i in range(clicks_to_fire):
                    if not self.running or not self.is_active:
                        break

                    user32.mouse_event(down_flag, 0, 0, 0, 0)
                    time.sleep(0.001)
                    user32.mouse_event(up_flag, 0, 0, 0, 0)
                    time.sleep(delay_sec)

                    self.burst_progress = (i + 1) / clicks_to_fire
                    self.arena_registered_clicks += 1
                    self._record_cps_click()

                self.total_delivered_clicks += (clicks_to_fire + (1 if is_mouse_triggered else 0))

                if is_mouse_triggered:
                    while user32.GetAsyncKeyState(vk) & 0x8000:
                        time.sleep(0.01)
                    time.sleep(0.05)
            finally:
                self.burst_progress = 0.0
                self.is_bursting = False

        threading.Thread(target=run_clicks, daemon=True).start()

    def _mouse_listener_loop(self):
        last_f6 = False
        last_f8 = False
        last_esc = False
        last_target_btn = False

        while self.running:
            try:
                f6_down = bool(user32.GetAsyncKeyState(VK_F6) & 0x8000)
                if f6_down and not last_f6:
                    self.root.after(0, self.toggle_active)
                last_f6 = f6_down

                esc_down = bool(user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000)
                if esc_down and not last_esc:
                    if self.is_active:
                        self.root.after(0, self.toggle_active)
                last_esc = esc_down

                f8_down = bool(user32.GetAsyncKeyState(VK_F8) & 0x8000)
                if f8_down and not last_f8:
                    if self.is_active and not self.is_bursting:
                        self._execute_burst(is_mouse_triggered=False)
                last_f8 = f8_down

                cfg = BUTTON_CONFIGS.get(self.selected_button, BUTTON_CONFIGS["Right Click"])
                target_vk = cfg["vk"]

                if self.is_active and self.trigger_on_click_var.get():
                    mbtn_down = bool(user32.GetAsyncKeyState(target_vk) & 0x8000)
                    if mbtn_down and not last_target_btn and not self.is_bursting:
                        self._execute_burst(is_mouse_triggered=True)
                    last_target_btn = mbtn_down
                else:
                    last_target_btn = False

            except Exception:
                pass

            time.sleep(0.002)

    def _animation_tick(self):
        if not self.running:
            return

        self.anim_frame += 1
        t = self.anim_frame * 0.06

        now = time.perf_counter()
        self.recent_clicks_timestamps = [ts for ts in self.recent_clicks_timestamps if now - ts <= 1.0]
        self.current_cps = len(self.recent_clicks_timestamps)
        self.cps_badge.configure(text=f"⚡ {self.current_cps} CPS")

        self._render_arena(t)

        self.footer_lbl.configure(
            text=f"⚡ Total Delivered: {self.total_delivered_clicks:,} Clicks  |  Mode: {self.selected_button} Multiplier"
        )

        self.root.after(16, self._animation_tick)

    def _render_arena(self, t):
        self.arena_canvas.delete("all")
        w, h = 488, 150
        cx, cy = w // 2, h // 2

        grid_step = 26
        for x in range(0, w, grid_step):
            self.arena_canvas.create_line(x, 0, x, h, fill="#131623", width=1)
        for y in range(0, h, grid_step):
            self.arena_canvas.create_line(0, y, w, y, fill="#131623", width=1)

        radar_angle = t * 1.8
        radar_len = 65
        rx = cx + math.cos(radar_angle) * radar_len
        ry = cy + math.sin(radar_angle) * radar_len
        self.arena_canvas.create_line(cx, cy, rx, ry, fill="#1e2538", width=1)

        pulse = (math.sin(t * 3.0) + 1.0) * 0.5
        ring_r = 55 + pulse * 4
        self.arena_canvas.create_oval(cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r, outline="#1d2238", width=1)
        self.arena_canvas.create_oval(cx - 25, cy - 25, cx + 25, cy + 25, outline="#2a3250", width=1)
        self.arena_canvas.create_line(cx - 35, cy, cx + 35, cy, fill="#2a3250", width=1)
        self.arena_canvas.create_line(cx, cy - 35, cx, cy + 35, fill="#2a3250", width=1)

        active_waves = []
        for wave in self.shockwaves:
            if wave.update():
                active_waves.append(wave)
                r = wave.radius
                self.arena_canvas.create_oval(
                    wave.x - r, wave.y - r, wave.x + r, wave.y + r,
                    outline=wave.color, width=2
                )
        self.shockwaves = active_waves

        active_particles = []
        for p in self.particles:
            if p.update():
                active_particles.append(p)
                s = p.size
                self.arena_canvas.create_oval(
                    p.x - s, p.y - s, p.x + s, p.y + s,
                    fill=p.color, outline=""
                )
        self.particles = active_particles

        counter_text = f"{self.arena_registered_clicks:,}"
        btn = self.selected_button.upper()

        text_color = "#ffd600" if self.is_bursting else "#00f0ff"
        self.arena_canvas.create_text(
            cx, cy - 14,
            text=counter_text,
            font=("Segoe UI", 34, "bold"),
            fill=text_color
        )

        sub_text = "⚡ BURSTING 100 CLICKS..." if self.is_bursting else f"👉 CLICK WITH {btn} TO TEST 👈"
        sub_color = "#ffd600" if self.is_bursting else "#a6e3a1"
        self.arena_canvas.create_text(
            cx, cy + 24,
            text=sub_text,
            font=("Segoe UI", 9, "bold"),
            fill=sub_color
        )

    def _on_close(self):
        self.running = False
        self.is_active = False
        try:
            ctypes.windll.winmm.timeEndPeriod(1)
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = BurstClickerApp(root)
    root.mainloop()
