import sys
import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
from bot_logic import set_map_region, load_settings, update_window_list, set_tolerance, set_gm_detector, set_pull_time
from fishbot import FishBot
from overlay import MapSelectorOverlay
from farmbot import FarmBot  # Make sure this is the correct path to your FarmBot class
from message import MessageDetector
from ttkthemes import ThemedStyle

# Global variables to hold the selected window and bot states
selected_window = None
fish_bot_running = False
farm_bot_running = False
message_detector_running = False

# Load saved settings
settings = load_settings()

# Initialize Threads
farm_bot = None
fish_bot = None
message_detector = None


def start_message_detector():
    global selected_window, message_detector_running, message_detector
    if not message_detector_running:
        message_detector_running = True
        message_detector = MessageDetector(selected_window.title)
        message_detector.start()
    else:
        print("Message Detector is already running.")


def stop_message_detector():
    global selected_window, message_detector_running, message_detector
    if message_detector_running:
        message_detector_running = False
        message_detector.stop()
        message_detector.join(timeout=1)
        message_detector = None
    else:
        print("Message Detector is not running.")


def start_fish_bot():
    global selected_window, fish_bot_running, fish_bot
    if selected_window and not fish_bot_running:
        window_dropdown.config(state="disabled")
        fish_bot_running = True
        fish_bot = FishBot(selected_window.title)
        fish_bot.start()
        if settings.get('tolerance', True):
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


def select_window(event):
    global selected_window
    for window in gw.getAllWindows():
        if window.title == window_var.get():
            selected_window = window
            print(f"Selected window: {selected_window}")
            break


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
root.resizable(False, False)  # Disable window resizing
root.configure(bg="grey")

# Define global variables for widgets
tolerance_entry = None
set_tolerance_button = None
map_selector_button = None

# Dark mode theme colors
dark_bg = "#282828"
dark_fg = "#FFFFFF"

# Style configuration
style = ThemedStyle(root)
style.theme_use('black')

style.configure('TButton', padding=6)
style.configure('TLabel', padding=6)
style.configure('TCheckbutton', padding=6)
style.configure('TEntry', padding=6)
style.configure('TNotebook', padding=6)
style.configure('TNotebook.Tab', padding=6)

# Window selection
ttk.Label(root, text="Select Game Window:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
window_var = tk.StringVar()
window_dropdown = ttk.Combobox(root, textvariable=window_var)
window_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky='we')
window_dropdown.bind("<<ComboboxSelected>>", select_window)
window_dropdown['values'] = update_window_list()

# Create tab control
tab_control = ttk.Notebook(root)
fish_bot_tab = ttk.Frame(tab_control)
farm_bot_tab = ttk.Frame(tab_control)
tab_control.add(fish_bot_tab, text='Fish Bot')
tab_control.add(farm_bot_tab, text='Farm Bot')
tab_control.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

# Fish Bot tab
ttk.Label(fish_bot_tab, text="Fish Bot Controls").grid(row=0, column=0, padx=10, pady=10, sticky='w')
ttk.Button(fish_bot_tab, text="Start Fish Bot", command=start_fish_bot).grid(row=1, column=0, padx=10, pady=10, sticky='w')
ttk.Button(fish_bot_tab, text="Stop Fish Bot", command=stop_fish_bot).grid(row=1, column=1, padx=10, pady=10, sticky='w')

# GM Detector checkbox
gm_detector_var = tk.BooleanVar(value=settings.get('gm_detector', False))
gm_detector_checkbox = ttk.Checkbutton(fish_bot_tab, text="GM Detector", variable=gm_detector_var, command=lambda: set_gm_detector(gm_detector_var.get()))
gm_detector_checkbox.grid(row=2, column=0, padx=10, pady=10, sticky='w')

# Pull Time input and set button
ttk.Label(fish_bot_tab, text="Pull Time (0.5 to 3 seconds):").grid(row=3, column=0, padx=10, pady=10, sticky='w')
pull_time_var = tk.StringVar(value=str(settings.get('pull_time', 1.0)))
pull_time_entry = ttk.Entry(fish_bot_tab, textvariable=pull_time_var)
pull_time_entry.grid(row=3, column=1, padx=10, pady=10, sticky='w')

set_pull_time_button = ttk.Button(fish_bot_tab, text="Set", command=lambda: set_pull_time(pull_time_var.get()))
set_pull_time_button.grid(row=3, column=2, padx=10, pady=10, sticky='w')

# Farm Bot tab
ttk.Label(farm_bot_tab, text="Farm Bot Controls").grid(row=0, column=0, padx=10, pady=10, sticky='w')
start_farm_button = ttk.Button(farm_bot_tab, text="Start Farm Bot", command=start_farm_bot)
start_farm_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')
stop_farm_button = ttk.Button(farm_bot_tab, text="Stop Farm Bot", command=stop_farm_bot)
stop_farm_button.grid(row=1, column=1, padx=10, pady=10, sticky='w')

ttk.Label(farm_bot_tab, text="Farm Bot Settings:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
tolerance_var = tk.IntVar(value=settings.get('tolerance', 5))
ttk.Label(farm_bot_tab, text="Tolerance:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
tolerance_entry = ttk.Entry(farm_bot_tab, textvariable=tolerance_var)
tolerance_entry.grid(row=3, column=1, padx=10, pady=10, sticky='w')

set_tolerance_button = ttk.Button(farm_bot_tab, text="Set Tolerance", command=lambda: set_tolerance(tolerance_var.get()))
set_tolerance_button.grid(row=3, column=2, padx=10, pady=10, sticky='w')

# Map Selector
map_selector_button = ttk.Button(farm_bot_tab, text="Map Selector", command=open_map_selector)
map_selector_button.grid(row=4, column=0, padx=10, pady=10, sticky='w')

# Mask image label
mask_label = ttk.Label(farm_bot_tab)
mask_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')

# ps_map image label
ps_label = ttk.Label(farm_bot_tab)
ps_label.grid(row=5, column=1, padx=10, pady=10, sticky='w')

# Log output text widget
log_output = tk.Text(root, height=10, wrap='word', state='normal')
log_output.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

# Redirect print statements to the log output text widget
sys.stdout = PrintRedirector(log_output)


# Run the main loop
root.mainloop()
