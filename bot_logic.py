import json
import mss
import pygetwindow as gw
import numpy as np
import cv2

# Global variable to hold map region

def update_window_list():
    windows = gw.getAllTitles()
    metin_windows = [window for window in windows if 'metin' in window.lower()]
    return metin_windows


def set_tolerance(tolerance):
    set_setting('tolerance', tolerance)
    print(f"Tolerance set to: {tolerance}")


def set_gm_detector(state):
    set_setting('gm_detector', state)
    print(f"GM Detector set to: {state}")


def set_pull_time(pull_time):
    try:
        pull_time_value = float(pull_time)
        if 0.5 <= pull_time_value <= 3:
            set_setting('pull_time', pull_time_value)
            print(f"Pull Time set to: {pull_time_value}")
        else:
            print("Pull Time must be between 0.5 and 3 seconds.")
    except ValueError:
        print("Invalid input for Pull Time.")


def set_map_region(region, selected_window):
    map_region = region

    game_window_position = selected_window.topleft
    game_window_dimensions = (selected_window.width, selected_window.height)

    relative_position = (
        map_region[0] - game_window_position[0] + 9,
        map_region[1] - game_window_position[1] + 29,
        map_region[2],
        map_region[3]
    )

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
    bbox = {
        'left': center_x - 20,
        'top': center_y - 20,
        'width': 40,
        'height': 40
    }
    
    with mss.mss() as sct:
        screenshot = sct.grab(bbox)
        img = np.array(screenshot)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        resized_img = cv2.resize(gray_image, (0, 0), fx=0.5, fy=0.5)
    
    return resized_img


def take_screenshot(window):
    left, top, width, height = window.left, window.top, window.width, window.height
    bbox = {
        'left': left,
        'top': top,
        'width': width,
        'height': height
    }
    
    with mss.mss() as sct:
        screenshot = sct.grab(bbox)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
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
