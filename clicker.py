import time
import threading
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

try:
    from pynput import mouse, keyboard
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput import mouse, keyboard

# --- Logic Variables ---
clicks_per_sec = 20
total_clicks = 0
START_DELAY = 8
clicking = True
paused_by_hover = False
app_running = True
master_switch = 0 

# Window tracking
current_x, current_y = 1100, 100
current_w, current_h = 240, 260

def clicker_logic():
    global clicking, paused_by_hover, clicks_per_sec, app_running, master_switch, total_clicks
    time.sleep(START_DELAY)
    m_controller = mouse.Controller()
    
    while app_running:
        if clicking and master_switch == 1 and clicks_per_sec > 0:
            mx, my = m_controller.position
            inside_dashboard = (current_x <= mx <= current_x + current_w) and \
                               (current_y <= my <= current_y + current_h)
            
            if paused_by_hover or inside_dashboard:
                time.sleep(0.05)
                continue 
            
            start_time = time.perf_counter()
            m_controller.click(mouse.Button.left)
            total_clicks += 1
            
            # Update the stats label in the UI thread
            if total_clicks % 5 == 0: # Update every 5 clicks to save CPU
                root.after(0, lambda: stats_label.config(text=f"Total Clicks: {total_clicks}"))

            target_interval = 1.0 / clicks_per_sec
            while (time.perf_counter() - start_time) < target_interval:
                 time.sleep(0.0001)
        else:
            time.sleep(0.1)

# --- NEW: HOTKEY LISTENER ---
def on_press(key):
    global clicks_per_sec, master_switch
    try:
        if key == keyboard.Key.up:
            clicks_per_sec = min(100, clicks_per_sec + 5)
            root.after(0, lambda: speed_slider.set(clicks_per_sec))
        elif key == keyboard.Key.down:
            clicks_per_sec = max(1, clicks_per_sec - 5)
            root.after(0, lambda: speed_slider.set(clicks_per_sec))
    except: pass

# --- UI Setup ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True, "-alpha", 0.95)
root.config(bg="#F5F5F7")
root.geometry(f"{current_w}x{current_h}+{current_x}+{current_y}")

# Dragging Helper
lastX, lastY = 0, 0
def start_drag(e): global lastX, lastY; lastX, lastY = e.x, e.y
def do_drag(e): root.geometry(f"+{e.x - lastX + root.winfo_x()}+{e.y - lastY + root.winfo_y()}")
def make_drag(w): w.bind('<Button-1>', start_drag); w.bind('<B1-Motion>', do_drag)

make_drag(root)

def on_move(e):
    global current_x, current_y
    if e.widget == root: current_x, current_y = root.winfo_x(), root.winfo_y()
root.bind("<Configure>", on_move)

# --- UI Elements ---
status_label = tk.Label(root, text=f"STARTING: {START_DELAY}", font=("Helvetica", 14, "bold"), fg="#FF3B30", bg="#F5F5F7")
status_label.pack(pady=(15, 5))
make_drag(status_label)

speed_label = tk.Label(root, text=f"Speed: {clicks_per_sec} CPS", font=("Helvetica", 11), fg="#8E8E93", bg="#F5F5F7")
speed_label.pack()
make_drag(speed_label)

def update_speed(val):
    global clicks_per_sec
    clicks_per_sec = int(float(val))
    speed_label.config(text=f"Speed: {clicks_per_sec} CPS")

speed_slider = ttk.Scale(root, from_=1, to=100, orient="horizontal", command=update_speed)
speed_slider.set(clicks_per_sec)
speed_slider.pack(pady=5, fill="x", padx=25)

# STATS LABEL
stats_label = tk.Label(root, text="Total Clicks: 0", font=("Helvetica", 10), fg="#8E8E93", bg="#F5F5F7")
stats_label.pack(pady=5)
make_drag(stats_label)

divider = tk.Frame(root, height=1, bg="#D1D1D6")
divider.pack(fill="x", padx=20, pady=5)

power_label = tk.Label(root, text="⛔️ DISARMED", font=("Helvetica", 12, "bold"), fg="#FF3B30", bg="#F5F5F7")
power_label.pack()
make_drag(power_label)

def toggle_power(val):
    global master_switch
    if float(val) > 0.9: 
        master_switch = 1
        power_label.config(text="✅ ARMED (READY)", fg="#34C759")
    else:
        master_switch = 0
        power_label.config(text="⛔️ DISARMED", fg="#FF3B30")

power_slider = ttk.Scale(root, from_=0, to=1, orient="horizontal", command=toggle_power)
power_slider.set(0)
power_slider.pack(pady=5, fill="x", padx=25)

# --- Hover Logic ---
def update_countdown(count):
    if count > 0:
        status_label.config(text=f"STARTING: {count}", fg="#FF9500")
        root.after(1000, update_countdown, count - 1)
    else:
        status_label.config(text="● ACTIVE" if master_switch else "WAITING FOR ARM", fg="#34C759" if master_switch else "#FF3B30")

def on_enter(e):
    global paused_by_hover
    paused_by_hover = True
    status_label.config(text="|| PAUSED", fg="#007AFF")

def on_leave(e):
    global paused_by_hover
    time.sleep(0.1) 
    paused_by_hover = False
    update_countdown(0)

root.bind("<Enter>", on_enter)
root.bind("<Leave>", on_leave)

threading.Thread(target=clicker_logic, daemon=True).start()
threading.Thread(target=lambda: keyboard.Listener(on_press=on_press).start(), daemon=True).start()

update_countdown(START_DELAY)
root.mainloop()
