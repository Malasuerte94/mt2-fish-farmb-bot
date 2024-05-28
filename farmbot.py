import random
import time
from threading import Thread, Event
from bot_inputs.detect_mobs import detect_red_squares, ps_map
from bot_logic import focus_game_window, load_settings
from pywinauto.keyboard import send_keys
import pygetwindow as gw
import numpy as np
from PIL import Image, ImageTk

stop_event = Event()
pause_event = Event()

class FarmBot(Thread):
    def __init__(self, selected_window, mask_label, ps_label):
        super().__init__()
        self.selected_window = selected_window
        self.mask_label = mask_label
        self.ps_label = ps_label
        self.z_press_thread = None
        self.game_window = focus_game_window(selected_window.title)
        self.settings = load_settings()
        self.tolerance = self.settings.get('tolerance')
        self.region = self.settings.get('map_region')
        self._stop_event = Event()  # Local stop event for the class

    def run(self):
        if not self.game_window:
            print("Game window not focused properly.")
            return

        self._stop_event.clear()
        pause_event.set()
        self.z_press_thread = Thread(target=self.press_z_continuously, daemon=True)
        self.z_press_thread.start()

        # Start monitoring window focus
        focus_monitor_thread = Thread(target=self.monitor_window_focus, args=(self.game_window,), daemon=True)
        focus_monitor_thread.start()

        try:
            while not self._stop_event.is_set():
                pause_event.wait()
                self.move_towards_position()
                self.fight()
        except Exception as e:
            print(f"Exception in farm bot loop: {e}")

    def monitor_window_focus(self, window):
        while not self._stop_event.is_set():
            if self.is_game_window_focused(window):
                pause_event.set()
            else:
                pause_event.clear()
            time.sleep(1)

    def press_z_continuously(self):
        while not self._stop_event.is_set():
            if pause_event.is_set():
                press_duration = random.uniform(0.2, 0.4)
                send_keys('{z down}')
                time.sleep(press_duration)
                send_keys('{z up}')
                time.sleep(random.uniform(0.1, 0.3))
            else:
                time.sleep(1)

    def stop_farming(self):
        print("Stopping Farm Bot...")
        self._stop_event.set()

        if self.z_press_thread and self.z_press_thread.is_alive():
            self.z_press_thread.join(timeout=1)

        print("Farm Bot stopped.")

    def is_game_window_focused(self, window):
        focused_window = gw.getActiveWindow()
        return focused_window == window

    def fight(self):
        print(f"Lure")
        start_time = time.time()
        space_end_time = start_time + 30  # Hold space for 30 seconds
        stationary_end_time = start_time + 35  # Stay stationary for 5 seconds
        loottime = 8

        send_keys('{F1 down}')
        press_duration = random.uniform(0.2, 0.5)
        time.sleep(press_duration)
        send_keys('{F1 up}')

        while time.time() < stationary_end_time and not self._stop_event.is_set():
            if time.time() < space_end_time:
                send_keys('{SPACE down}')
            else:
                send_keys('{SPACE up}')
            time.sleep(random.uniform(3, 4))
        print("Finished stationary period")
        send_keys('{SPACE up}')

        start_time2 = time.time()
        print("Looting")
        send_keys('{W down}')
        time.sleep(1)
        send_keys('{W up}')
        while time.time() - start_time2 < loottime and not self._stop_event.is_set():
            send_keys('{D down}')
            time.sleep(7)
        send_keys('{D up}')
        print("Stopped looting")

    def move_towards_position(self):
        try:
            rotation_duration = 0.3
            stuck_count = 0
            previous_distance = float('inf')
            while not self._stop_event.is_set():
                pause_event.wait()
                screenshot = ps_map(self.game_window, self.region)
                red_squares, mask = detect_red_squares(screenshot)
                region_center = (self.region[2] // 2, self.region[3] // 2)

                if red_squares:
                    closest_square = min(red_squares, key=lambda pos: (pos[0] - region_center[0]) ** 2 + (pos[1] - region_center[1]) ** 2)
                    if abs(closest_square[0] - region_center[0]) <= self.tolerance and abs(closest_square[1] - region_center[1]) <= self.tolerance:
                        print("Target reached. Stopping.")
                        break  # Exit the loop when target is reached
                    else:
                        print("Bright red squares detected. Moving forward.")
                        send_keys('{W down}')
                        time.sleep(0.5)
                        send_keys('{W up}')
                        print("Continuing towards target.")

                        # Check if we are stuck (distance not decreasing)
                        current_distance = np.hypot(closest_square[0] - region_center[0], closest_square[1] - region_center[1])
                        if current_distance >= previous_distance * 0.95:
                            stuck_count += 1
                            if stuck_count >= 3:  # If stuck for 3 consecutive iterations
                                print("Stuck detected. Reversing and rotating.")
                                send_keys('{S down}')
                                time.sleep(2)
                                send_keys('{S up}')
                                send_keys('{D down}')
                                time.sleep(1)
                                send_keys('{D up}')
                                stuck_count = 0
                        else:
                            stuck_count = 0
                        previous_distance = current_distance
                else:
                    # Press D for 0.2 seconds and check for red squares
                    print("No red squares detected. Rotating to search.")
                    send_keys('{D down}')
                    time.sleep(rotation_duration)
                    send_keys('{D up}')

            ps_image = Image.fromarray(screenshot)
            ps_image_tk = ImageTk.PhotoImage(image=ps_image)
            self.ps_label.config(image=ps_image_tk)
            self.ps_label.image = ps_image_tk
            mask_image = Image.fromarray(mask)
            mask_image_tk = ImageTk.PhotoImage(image=mask_image)
            self.mask_label.config(image=mask_image_tk)
            self.mask_label.image = mask_image_tk

        except Exception as e:
            print(f"Exception in move towards position: {e}")
