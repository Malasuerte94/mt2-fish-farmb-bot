import json
from threading import Event
from bot_inputs.detect_mobs import ps_map
import pygetwindow as gw
import numpy as np
import cv2
import pyscreenshot as ImageGrab

# Event to control the bot's running state
stop_event = Event()

# Global variable to hold map region
map_region = (1150, 50, 110, 110)


def set_map_region(region, selected_window):
    global map_region
    map_region = region

    # Capture the game window's position and dimensions
    game_window_position = selected_window.topleft
    game_window_dimensions = (selected_window.width, selected_window.height)

    # Calculate the relative position of the map region
    relative_position = (
        map_region[0] - game_window_position[0] + 9,
        map_region[1] - game_window_position[1] + 29,
        map_region[2],
        map_region[3]
    )

    # Update the map region setting
    set_setting('map_region', relative_position)
    print(f"Map region set to: {map_region}")


def focus_game_window(window_title):
    print(f"Window title: {window_title}")
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            window.activate()
            return window
        else:
            print(f"No window found with title: {window_title}")
            return None
    except Exception as e:
        print(f"Error occurred while getting window: {e}")
        return None


def ps_fish(window):
    left, top, width, height = window.left, window.top, window.width, window.height
    center_y = top + height // 2
    center_x = left + width // 2
    bbox = (center_x - 150, center_y - 300, center_x + 150, center_y)
    screenshot = np.array(ImageGrab.grab(bbox))
    img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    # cv2.imshow('Captured Image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return img


def take_screenshot(window):
    left, top, width, height = window.left, window.top, window.width, window.height
    screenshot = np.array(ImageGrab.grab(bbox=(left, top, left + width, top + height)))
    img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return img


def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)


def save_settings(settings):
    with open("settings.json", "r+") as file:
        data = json.load(file)
        data.update(settings)
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def load_settings():
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/invalid JSON, initialize with default settings
        settings = {
            "map_region": None,
            "tolerance": 17,
            # Add more default settings as needed
        }
    return settings
