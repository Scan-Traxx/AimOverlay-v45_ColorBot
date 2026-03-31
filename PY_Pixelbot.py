import tkinter as tk
from tkinter import colorchooser
import mss
import numpy as np
import keyboard
import threading
import time
import ctypes
import json
import os

# DPI Awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

# API Konstanten
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_TOPMOST = 0x8
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
CONFIG_FILE = "bot_settings.json"

class PixelBotV45:
    def __init__(self):
        self.defaults = {
            "target_color": [255, 0, 0],
            "radius": 100,
            "tolerance": 25,
            "smoothing": 5.0,
            "deadzone": 30,
            "height_correction": 15,
            "show_line": True,
            "line_color": "#FFFF00",
            "show_radius": True,
            "fov_color": "#FFFFFF",
            "show_marker": True,
            "marker_color": "#00FF00",
            "marker_size": 10,
            "autofire": False,
            "activation_key": "left alt",
            "gui_bg": "#5b84c4",
            "gui_fg": "#ffffff",
            "gui_geometry": "340x880+100+100"
        }
        
        self.settings = self.load_settings()
        self.root = tk.Tk()
        self.root.withdraw() 
        
        self.overlay = tk.Toplevel(self.root)
        self.trans_color = '#000001' 
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.overlay.geometry(f"{self.sw}x{self.sh}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True, "-transparentcolor", self.trans_color)
        self.overlay.config(bg=self.trans_color)
        
        self.canvas = tk.Canvas(self.overlay, width=self.sw, height=self.sh, bg=self.trans_color, highlightthickness=0)
        self.canvas.pack()

        self.radius = tk.IntVar(value=self.settings["radius"])
        self.tolerance = tk.IntVar(value=self.settings["tolerance"])
        self.smoothing = tk.DoubleVar(value=self.settings["smoothing"])
        self.deadzone = tk.IntVar(value=max(30, self.settings["deadzone"])) 
        self.height_corr = tk.IntVar(value=self.settings["height_correction"])
        self.show_line = tk.BooleanVar(value=self.settings["show_line"])
        self.show_radius = tk.BooleanVar(value=self.settings["show_radius"])
        self.show_marker = tk.BooleanVar(value=self.settings["show_marker"])
        self.marker_size = tk.IntVar(value=self.settings.get("marker_size", 10))
        self.autofire = tk.BooleanVar(value=self.settings["autofire"])
        self.activation_key = tk.StringVar(value=self.settings["activation_key"])
        
        self.target_color = self.settings["target_color"]
        self.line_color = self.settings.get("line_color", "#FFFF00")
        self.fov_color = self.settings.get("fov_color", "#FFFFFF")
        self.marker_color = self.settings.get("marker_color", "#00FF00")
        self.gui_bg = self.settings["gui_bg"]
        self.gui_fg = self.settings["gui_fg"]

        self.is_binding = False
        self.running = True
        self.gui_visible = True
        self.last_shot = 0
        
        self.create_objects()
        self.overlay.after(200, self.force_click_through)
        self.setup_controls()
        
        keyboard.add_hotkey('ctrl+x', self.pick_color_at_mouse)
        keyboard.add_hotkey('end', self.toggle_gui)
        
        threading.Thread(target=self.search_loop, daemon=True).start()
        self.root.mainloop()

    def toggle_gui(self):
        if self.gui_visible:
            self.win.withdraw()
            self.gui_visible = False
        else:
            self.win.deiconify()
            self.win.attributes("-topmost", True)
            self.gui_visible = True

    def force_click_through(self):
        hwnd = ctypes.windll.user32.GetParent(self.overlay.winfo_id()) or self.overlay.winfo_id()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return {**self.defaults, **json.load(f)}
            except: return self.defaults
        return self.defaults

    def save_settings(self):
        try: geo = self.win.geometry()
        except: geo = self.settings.get("gui_geometry", self.defaults["gui_geometry"])

        config = {
            "target_color": self.target_color, "radius": self.radius.get(),
            "tolerance": self.tolerance.get(), "smoothing": self.smoothing.get(),
            "deadzone": self.deadzone.get(), "height_correction": self.height_corr.get(),
            "show_line": self.show_line.get(), "line_color": self.line_color,
            "show_radius": self.show_radius.get(), "fov_color": self.fov_color,
            "show_marker": self.show_marker.get(), "marker_size": self.marker_size.get(),
            "marker_color": self.marker_color, "autofire": self.autofire.get(),
            "activation_key": self.activation_key.get(), "gui_bg": self.gui_bg, "gui_fg": self.gui_fg,
            "gui_geometry": geo
        }
        with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)

    def setup_controls(self):
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True) 
        self.win.geometry(self.settings.get("gui_geometry", "340x880+100+100"))
        self.win.configure(bg=self.gui_bg)
        self.win.attributes("-topmost", True)
        
        style = {"bg": self.gui_bg, "fg": self.gui_fg, "font": ("Arial", 9, "bold")}
        inner_style = {"bg": self.gui_bg, "fg": self.gui_fg, "font": ("Arial", 8)}

        # --- TITELLEISTE (NUR HIER IST DRAG ERLAUBT) ---
        self.header = tk.Label(self.win, text="AimOverlay v45 | END to Hide", **style, pady=12, cursor="fleur")
        self.header.pack(fill="x")
        
        # Binding nur an das Header-Label
        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        # --- REST DER GUI ---
        sec_bot = tk.LabelFrame(self.win, text=" BOT CONTROL ", **style)
        sec_bot.pack(fill="x", padx=10, pady=5)
        
        tk.Label(sec_bot, text="Activation Key:", **inner_style).pack(anchor="w", padx=5)
        self.bind_btn = tk.Button(sec_bot, text=f"Key: {self.activation_key.get().upper()}", 
                                  command=self.start_key_bind, bg="#444", fg="white", relief="flat")
        self.bind_btn.pack(fill="x", padx=5, pady=5)
        
        tk.Checkbutton(sec_bot, text="Autofire (Active)", variable=self.autofire, **inner_style, selectcolor="#444").pack(anchor="w", padx=5, pady=5)
        
        tk.Scale(sec_bot, from_=1.0, to=20.0, resolution=0.1, orient="horizontal", variable=self.smoothing, label="Smoothing", **inner_style, highlightthickness=0).pack(fill="x", padx=5)
        tk.Scale(sec_bot, from_=30, to=300, orient="horizontal", variable=self.deadzone, label="Trigger Range (Min: 30)", **inner_style, highlightthickness=0).pack(fill="x", padx=5)
        tk.Scale(sec_bot, from_=0, to=150, orient="horizontal", variable=self.height_corr, label="Height Correction", **inner_style, highlightthickness=0).pack(fill="x", padx=5)

        sec_vis = tk.LabelFrame(self.win, text=" VISUALS & COLORS ", **style)
        sec_vis.pack(fill="x", padx=10, pady=5)
        sub = tk.Frame(sec_vis, bg=self.gui_bg)
        sub.pack(fill="x", padx=10, pady=5)

        target_hex = '#%02x%02x%02x' % tuple(self.target_color)
        items = [
            ("Target Color", self.choose_target_color, target_hex, None),
            ("Target Line", self.choose_line_color, self.line_color, self.show_line),
            ("ESP Marker", self.choose_marker_color, self.marker_color, self.show_marker),
            ("FOV Circle", self.choose_fov_color, self.fov_color, self.show_radius)
        ]

        for i, (txt, cmd, col, var) in enumerate(items):
            if var: tk.Checkbutton(sub, text=txt, variable=var, **inner_style, selectcolor="#444", command=self.update_circle_ui).grid(row=i, column=0, sticky="w")
            else: tk.Label(sub, text=txt, **inner_style).grid(row=i, column=0, sticky="w")
            tk.Button(sub, text="", bg=col, width=2, relief="flat", command=cmd).grid(row=i, column=1, padx=30, pady=3)

        tk.Scale(sec_vis, from_=2, to=100, orient="horizontal", variable=self.marker_size, label="ESP Marker Size", **inner_style, highlightthickness=0).pack(fill="x", padx=5)
        tk.Scale(sec_vis, from_=20, to=500, orient="horizontal", variable=self.radius, label="FOV Size", command=self.update_circle_ui, **inner_style, highlightthickness=0).pack(fill="x", padx=5)
        tk.Scale(sec_vis, from_=0, to=100, orient="horizontal", variable=self.tolerance, label="Color Tolerance", **inner_style, highlightthickness=0).pack(fill="x", padx=5)

        tk.Button(self.win, text="SAVE & EXIT", command=self.stop_bot, bg="#d9534f", fg="white", font=("Arial", 9, "bold"), pady=10).pack(side="bottom", fill="x", padx=10, pady=10)

    # Verschiebe-Logik (strikt auf Header begrenzt)
    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.win.winfo_x() + (event.x - self.offset_x)
        y = self.win.winfo_y() + (event.y - self.offset_y)
        self.win.geometry(f"+{x}+{y}")

    def start_key_bind(self):
        self.is_binding = True
        self.bind_btn.config(text="... PRESS KEY ...", bg="#ff4d4d")
        threading.Thread(target=self.wait_for_key, daemon=True).start()

    def wait_for_key(self):
        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            new_key = event.name
            self.activation_key.set(new_key)
            self.is_binding = False
            self.root.after(0, lambda: self.bind_btn.config(text=f"Key: {new_key.upper()}", bg="#444"))
            self.save_settings()

    def choose_target_color(self):
        c = colorchooser.askcolor(title="Target Color")[0]
        if c: self.target_color = [int(x) for x in c]; self.save_settings(); self.refresh_gui()

    def choose_line_color(self):
        c = colorchooser.askcolor(title="Line Color")[1]
        if c: self.line_color = c; self.save_settings(); self.refresh_gui()

    def choose_marker_color(self):
        c = colorchooser.askcolor(title="Marker Color")[1]
        if c: self.marker_color = c; self.save_settings(); self.refresh_gui()

    def choose_fov_color(self):
        c = colorchooser.askcolor(title="FOV Color")[1]
        if c: self.fov_color = c; self.save_settings(); self.refresh_gui(); self.update_circle_ui()

    def refresh_gui(self):
        self.settings["gui_geometry"] = self.win.geometry()
        self.win.destroy(); self.setup_controls()

    def pick_color_at_mouse(self):
        import pyautogui
        x, y = pyautogui.position()
        with mss.mss() as sct:
            img = sct.grab({"top": y, "left": x, "width": 1, "height": 1})
            self.target_color = [img.pixel(0,0)[2], img.pixel(0,0)[1], img.pixel(0,0)[0]]
            self.save_settings(); self.refresh_gui()

    def create_objects(self):
        mx, my = self.sw // 2, self.sh // 2
        r = self.radius.get()
        self.circle_id = self.canvas.create_oval(mx-r, my-r, mx+r, my+r, outline=self.fov_color, width=1, dash=(4,2))
        self.line_id = self.canvas.create_line(0,0,0,0, fill=self.line_color, width=1)
        self.marker_id = self.canvas.create_rectangle(0,0,0,0, outline=self.marker_color, width=1)
        self.update_circle_ui()

    def click_action(self):
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05) 
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.last_shot = time.time()

    def search_loop(self):
        with mss.mss() as sct:
            while self.running:
                if self.is_binding: 
                    time.sleep(0.1)
                    continue
                    
                key = self.activation_key.get().lower()
                if keyboard.is_pressed(key if key else "left alt"):
                    r = self.radius.get()
                    mx, my = self.sw // 2, self.sh // 2
                    region = {"top": my - r, "left": mx - r, "width": r*2, "height": r*2}
                    img = np.array(sct.grab(region))[:,:,:3]
                    target = np.array([self.target_color[2], self.target_color[1], self.target_color[0]], dtype=np.uint8)
                    diff = np.abs(img.astype(np.int16) - target.astype(np.int16))
                    mask = np.all(diff <= self.tolerance.get(), axis=-1)
                    y_idx, x_idx = np.where(mask)
                    
                    if len(x_idx) > 0:
                        dist_sq = (x_idx - r)**2 + (y_idx - r)**2
                        best = np.argmin(dist_sq)
                        tx_rel, ty_rel = x_idx[best], y_idx[best] - self.height_corr.get()
                        fx, fy = (mx - r) + tx_rel, (my - r) + ty_rel
                        self.move_mouse(fx, fy)
                        dist_to_center = np.sqrt((tx_rel - r)**2 + (ty_rel - r)**2)
                        is_shooting = (dist_to_center <= self.deadzone.get())
                        if is_shooting and self.autofire.get() and (time.time() - self.last_shot > 0.18):
                            self.click_action()
                        self.overlay.after(0, self.update_visuals, fx, fy, is_shooting)
                    else: self.overlay.after(0, self.clear_visuals)
                else: 
                    self.overlay.after(0, self.clear_visuals)
                    time.sleep(0.01)
                time.sleep(0.005)

    def move_mouse(self, tx, ty):
        class POINT(ctypes.Structure): _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        diff_x, diff_y = tx - pt.x, ty - pt.y
        smooth = max(1.1, self.smoothing.get())
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, int(diff_x/smooth), int(diff_y/smooth), 0, 0)

    def update_visuals(self, fx, fy, is_shooting):
        if self.show_marker.get():
            s = self.marker_size.get()
            color = "#FF0000" if is_shooting else self.marker_color
            self.canvas.coords(self.marker_id, fx-s, fy-s, fx+s, fy+s)
            self.canvas.itemconfig(self.marker_id, state="normal", outline=color, width=1)
        if self.show_line.get():
            self.canvas.coords(self.line_id, self.sw//2, self.sh//2, fx, fy)
            self.canvas.itemconfig(self.line_id, state="normal", fill=self.line_color)

    def clear_visuals(self):
        self.canvas.itemconfig(self.marker_id, state="hidden")
        self.canvas.itemconfig(self.line_id, state="hidden")

    def update_circle_ui(self, *args):
        r = self.radius.get()
        mx, my = self.sw // 2, self.sh // 2
        self.canvas.coords(self.circle_id, mx-r, my-r, mx+r, my+r)
        self.canvas.itemconfig(self.circle_id, state="normal" if self.show_radius.get() else "hidden", outline=self.fov_color)

    def stop_bot(self):
        self.save_settings(); self.running = False; self.root.quit()

if __name__ == "__main__":
    PixelBotV45()