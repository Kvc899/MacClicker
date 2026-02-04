import time
import threading
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

# --- Auto-Install Logic ---
try:
    from pynput import mouse, keyboard
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput import mouse, keyboard

# --- Global Flags ---
clicks_per_sec = 20
START_DELAY = 8
clicking = True
paused_by_hover = False
app_running = True
master_switch = 0 # 0 = Disarmed, 1 = Armed

# --- Window Tracking ---
current_x = 1100
current_y = 100
current_w = 240
current_h = 240 # Little taller for spacing

# --- The Clicking Engine ---
def clicker_logic():
    global clicking, paused_by_hover, clicks_per_sec, app_running, master_switch, current_x, current_y, current_w, current_h
    
    time.sleep(START_DELAY)
    m_controller = mouse.Controller()
    
    while app_running:
        # LOGIC: Only click if Master Switch is ON (1)
        if clicking and master_switch == 1 and clicks_per_sec > 0:
            
            # Safety Check: Is mouse inside the dashboard?
            mx, my = m_controller.position
            inside_dashboard = (current_x <= mx <= current_x + current_w) and \
                               (current_y <= my <= current_y + current_h)
            
            if paused_by_hover or inside_dashboard:
                time.sleep(0.05)
                continue 
            
            # Click
            start_time = time.perf_counter()
            m_controller.click(mouse.Button.left)
            
            target_interval = 1.0 / clicks_per_sec
            while (time.perf_counter() - start_time) < target_interval:
                 time.sleep(0.0001)
        else:
            time.sleep(0.1)

def on_press(key):
    global clicking
    try:
        if hasattr(key, 'char') and key.char == 's':
            clicking = False # Soft stop
    except: pass

# --- UI Setup ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.95) # Slightly less transparent to see text better
root.config(bg="#F5F5F7")
root.geometry(f"{current_w}x{current_h}+{current_x}+{current_y}")

# --- FIX: DRAGGING LOGIC ---
lastClickX = 0
lastClickY = 0

def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y

def Dragging(event):
    # Move the window
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry(f"+{x}+{y}")

# Helper to make widgets draggable
def make_draggable(widget):
    widget.bind('<Button-1>', SaveLastClickPos)
    widget.bind('<B1-Motion>', Dragging)

# Make the main background draggable
make_draggable(root)

# --- TRACKING ---
def on_move(event):
    global current_x, current_y
    if event.widget == root:
        current_x = root.winfo_x()
        current_y = root.winfo_y()
root.bind("<Configure>", on_move)

# --- WIDGETS ---

# 1. Status Label
status_label = tk.Label(root, text=f"STARTING: {START_DELAY}", 
                        font=("Helvetica Neue", 14, "bold"), fg="#FF3B30", bg="#F5F5F7")
status_label.pack(pady=(15, 5))
make_draggable(status_label) # FIX: Now you can drag by clicking this text

# 2. Speed Slider
speed_label = tk.Label(root, text=f"Speed: {clicks_per_sec} CPS", 
                       font=("Helvetica Neue", 11), fg="#8E8E93", bg="#F5F5F7")
speed_label.pack()
make_draggable(speed_label) # FIX: Drag by clicking "Speed"

def update_speed(val):
    global clicks_per_sec
    clicks_per_sec = int(float(val))
    speed_label.config(text=f"Speed: {clicks_per_sec} CPS")

style = ttk.Style()
speed_slider = ttk.Scale(root, from_=1, to=100, orient="horizontal", command=update_speed)
speed_slider.set(clicks_per_sec)
speed_slider.pack(pady=5, fill="x", padx=25)
# Note: We do NOT make the slider draggable, or you couldn't slide it!

# Divider
divider = tk.Frame(root, height=1, bg="#D1D1D6")
divider.pack(fill="x", padx=20, pady=10)
make_draggable(divider)

# 3. SAFETY SWITCH (Renamed)
power_label = tk.Label(root, text="⛔️ DISARMED", 
                       font=("Helvetica Neue", 12, "bold"), fg="#FF3B30", bg="#F5F5F7")
power_label.pack()
make_draggable(power_label)

def toggle_power(val):
    global master_switch
    value = float(val)
    if value > 0.9: 
        master_switch = 1
        power_label.config(text="✅ ARMED (READY)", fg="#34C759")
    else:
        master_switch = 0
        power_label.config(text="⛔️ DISARMED", fg="#FF3B30")

power_slider = ttk.Scale(root, from_=0, to=1, orient="horizontal", command=toggle_power)
power_slider.set(0) # Default to OFF
power_slider.pack(pady=5, fill="x", padx=25)

helper_text = tk.Label(root, text="(Slide Right to Enable)", font=("Arial", 9), fg="#aaa", bg="#F5F5F7")
helper_text.pack(pady=5)
make_draggable(helper_text)

# --- EVENTS ---
def update_countdown(count):
    if count > 0:
        status_label.config(text=f"STARTING: {count}", fg="#FF9500")
        root.after(1000, update_countdown, count - 1)
    else:
        # Check master switch status
        if master_switch == 0:
            status_label.config(text="WAITING FOR ARM", fg="#FF3B30")
        else:
            status_label.config(text="● ACTIVE", fg="#34C759")

def on_enter(event):
    global paused_by_hover
    paused_by_hover = True
    status_label.config(text="|| PAUSED", fg="#007AFF")

def on_leave(event):
    global paused_by_hover
    time.sleep(0.1) 
    paused_by_hover = False
    if master_switch == 0:
         status_label.config(text="WAITING FOR ARM", fg="#FF3B30")
    elif app_running and clicking:
        status_label.config(text="● ACTIVE", fg="#34C759")

root.bind("<Enter>", on_enter)
root.bind("<Leave>", on_leave)

# Start Threads
threading.Thread(target=clicker_logic, daemon=True).start()
threading.Thread(target=lambda: keyboard.Listener(on_press=on_press).start(), daemon=True).start()

update_countdown(START_DELAY)
root.mainloop()
