import sys
import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
from bot_logic import set_setting, set_map_region, load_settings
from fishbot import FishBot
from overlay import MapSelectorOverlay
from farmbot import FarmBot  # Make sure this is the correct path to your FarmBot class
from message import MessageDetector

# Global variables to hold the selected window and bot states
selected_window = None
fish_bot_running = False
farm_bot_running = False
message_detector_running = False

# Load saved settings
settings = load_settings()
tolerance = settings.get('tolerance', 5)
map_region = settings.get('map_region', (1150, 50, 110, 110))

def update_window_list():
    windows = gw.getAllTitles()
    metin_windows = [window for window in windows if 'metin' in window.lower()]
    window_dropdown['values'] = metin_windows

def select_window(event):
    global selected_window
    for window in gw.getAllWindows():
        if window.title == window_var.get():
            selected_window = window
            print(f"Selected window: {selected_window}")
            break

# Initialize farm_bot variable
farm_bot = None
fish_bot = None
message_detector = None

def start_message_detector():
    global selected_window, message_detector_running, message_detector
    if not message_detector_running:
        #window_dropdown.config(state="disabled")
        message_detector_running = True
        message_detector = MessageDetector(selected_window.title)
        message_detector.start()
    else:
        print("Message Detector is already running.")

def start_fish_bot():
    global selected_window, fish_bot_running, fish_bot
    if selected_window and not fish_bot_running:
        window_dropdown.config(state="disabled")
        fish_bot_running = True
        fish_bot = FishBot(selected_window.title)
        fish_bot.start()
        start_message_detector()
    else:
        print("Please select a window.")



def stop_fish_bot():
    global fish_bot_running, fish_bot
    if fish_bot_running:
        print("Stopping Fish Bot...")
        fish_bot_running = False
        fish_bot.stop()
        fish_bot.join(timeout=1)
        fish_bot = None
    else:
        print("Fish Bot is not running.")

        
def start_farm_bot():
    global selected_window, farm_bot_running, farm_bot
    if selected_window and not farm_bot_running:
        print("Starting Farm Bot...")
        farm_bot_running = True
        farm_bot = FarmBot(selected_window, mask_label, ps_label)
        farm_bot.start()

        # Disable settings and controls
        tolerance_entry.config(state='disabled')
        set_tolerance_button.config(state='disabled')
        map_selector_button.config(state='disabled')
        window_dropdown.config(state="disabled")
    else:
        print("Please select a window.")

def stop_farm_bot():
    global farm_bot_running, farm_bot
    if farm_bot_running:
        print("Stopping Farm Bot...")
        farm_bot_running = False
        farm_bot.stop_farming()
        farm_bot.join(timeout=1)
        farm_bot = None

        # Enable settings and controls
        tolerance_entry.config(state='normal')
        set_tolerance_button.config(state='normal')
        map_selector_button.config(state='normal')
    else:
        print("Farm Bot is not running.")

def open_map_selector():
    global selected_window
    if selected_window:
        overlay = tk.Toplevel()
        game_window_position = selected_window.topleft
        MapSelectorOverlay(overlay, selected_window, game_window_position, set_map_region)
    else:
        print("Please select a window first.")

class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

# Create the main window
root = tk.Tk()
root.title("Bot Controller")
root.geometry('+1200+100')

# Define global variables for widgets
tolerance_entry = None
set_tolerance_button = None
map_selector_button = None

# Window selection
tk.Label(root, text="Select Game Window:").grid(row=0, column=0, padx=10, pady=10)
window_var = tk.StringVar()
window_dropdown = ttk.Combobox(root, textvariable=window_var)
window_dropdown.grid(row=0, column=1, padx=10, pady=10)
window_dropdown.bind("<<ComboboxSelected>>", select_window)
update_window_list()

# Create tab control
tab_control = ttk.Notebook(root)
fish_bot_tab = ttk.Frame(tab_control)
farm_bot_tab = ttk.Frame(tab_control)
tab_control.add(fish_bot_tab, text='Fish Bot')
tab_control.add(farm_bot_tab, text='Farm Bot')
tab_control.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Fish Bot tab
tk.Label(fish_bot_tab, text="Fish Bot Controls").grid(row=0, column=0, padx=10, pady=10)
tk.Button(fish_bot_tab, text="Start Fish Bot", command=start_fish_bot).grid(row=1, column=0, padx=10, pady=10)
tk.Button(fish_bot_tab, text="Stop Fish Bot", command=stop_fish_bot).grid(row=1, column=1, padx=10, pady=10)

# Farm Bot tab
tk.Label(farm_bot_tab, text="Farm Bot Controls").grid(row=0, column=0, padx=10, pady=10)
start_farm_button = tk.Button(farm_bot_tab, text="Start Farm Bot", command=start_farm_bot)
start_farm_button.grid(row=1, column=0, padx=10, pady=10)
stop_farm_button = tk.Button(farm_bot_tab, text="Stop Farm Bot", command=stop_farm_bot)
stop_farm_button.grid(row=1, column=1, padx=10, pady=10)

tk.Label(farm_bot_tab, text="Farm Bot Settings:").grid(row=2, column=0, padx=10, pady=10)
tolerance_var = tk.IntVar(value=tolerance)
tk.Label(farm_bot_tab, text="Tolerance:").grid(row=3, column=0, padx=10, pady=10)
tolerance_entry = tk.Entry(farm_bot_tab, textvariable=tolerance_var)
tolerance_entry.grid(row=3, column=1, padx=10, pady=10)

def set_tolerance():
    global tolerance
    tolerance = tolerance_var.get()
    set_setting('tolerance', tolerance)
    print(f"Tolerance set to: {tolerance}")

set_tolerance_button = tk.Button(farm_bot_tab, text="Set Tolerance", command=set_tolerance)
set_tolerance_button.grid(row=3, column=2, padx=10, pady=10)

# Map Selector
map_selector_button = tk.Button(farm_bot_tab, text="Map Selector", command=open_map_selector)
map_selector_button.grid(row=4, column=0, padx=10, pady=10)

# Mask image label
mask_label = tk.Label(farm_bot_tab)
mask_label.grid(row=5, column=0, padx=10, pady=10)

# ps_map image label
ps_label = tk.Label(farm_bot_tab)
ps_label.grid(row=5, column=1, padx=10, pady=10)


# Log output text widget
log_output = tk.Text(root, height=10, wrap='word', state='normal')
log_output.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Redirect print statements to the log output text widget
sys.stdout = PrintRedirector(log_output)

# Run the main loop
root.mainloop()