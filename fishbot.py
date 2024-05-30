import cv2
import time

import numpy as np
import pyautogui
from pywinauto.mouse import click
import random
from pywinauto.keyboard import send_keys
from threading import Thread, Event
from bot_logic import focus_game_window, ps_fish, take_screenshot, load_settings
import matplotlib.pyplot as plt

def press_space():
    send_keys('{SPACE down}')
    press_duration = random.uniform(0.2, 0.4)
    print(f"Hit Space")
    time.sleep(press_duration)
    send_keys('{SPACE up}')


settings = load_settings()


class FishBot(Thread):
    def __init__(self, window_title):
        super().__init__()
        self.window_title = window_title
        self.stop_event = Event()
        self.game_window = focus_game_window(self.window_title)
        self.images = {
            'message': cv2.imread('images/message.png'),
            'fish': cv2.imread('images/fish.png'),
            'small_fish': cv2.imread('images/small_fish.png'),
            'fisherman': cv2.imread('images/pescar.png'),
            'buy': cv2.imread('images/buy.png'),
            'yes': cv2.imread('images/yes.png'),
            'ok': cv2.imread('images/ok.png'),
            'pasta': cv2.imread('images/pasta.png'),
            'open1': cv2.imread('images/open1.png'),
            'open2': cv2.imread('images/open2.png'),
            'open3': cv2.imread('images/open3.png'),
            'open4': cv2.imread('images/open4.png'),
            'open5': cv2.imread('images/open5.png')
        }
        self.locations = {}
        self.fishing_wait = settings.get('pull_time', 1.3)

    def run(self):
        if not self.game_window:
            print(f"Could not find game window: {self.window_title}")
            return

        print("Running FishBot module...")
        # Testing screenshot offsets
        # screenshot = ps_fish(self.game_window)

        self.use_bait_or_fish()
        press_space()

        last_detection_time = time.time()
        detection_timeout = 30

        while not self.stop_event.is_set():
            screenshot = ps_fish(self.game_window)
            if self.detect_fish(screenshot, 'fish'):
                print("Fish detected")
                self.fish_catch()
                time.sleep(5)
                self.use_bait_or_fish()
                press_space()
                last_detection_time = time.time()
            else:
                if time.time() - last_detection_time > detection_timeout:
                    print("No fish detected for 30 seconds, restarting...")
                    last_detection_time = time.time()
                    self.use_bait_or_fish()
                    press_space()
            time.sleep(0.01)

    def stop(self):
        self.stop_event.set()

    def detect_fish(self, image, name):
        resized_image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = [cnt for cnt in contours if 1 <= cv2.boundingRect(cnt)[2] <= 15 and 1 <= cv2.boundingRect(cnt)[3] <= 15]
        
        return len(filtered_contours) > 0

    def detect_image(self, image, name, threshold=0.8):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(self.images[name], cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            self.locations[name] = max_loc
            return True
        return False

    def fish_catch(self):
        time.sleep(self.fishing_wait)
        press_space()
        print("Finished fishing")

    def use_bait_or_fish(self):
        screenshot = take_screenshot(self.game_window)
        if self.detect_image(screenshot, 'small_fish', 0.8):
            print("Found fish bait")
            self.use_item('small_fish')
        else:
            screenshot = take_screenshot(self.game_window)
            if self.detect_image(screenshot, 'pasta', 0.9):
                print("Found bait")
                self.use_item('pasta')
            else:
                self.refuel()

    def use_item(self, item_name):
        x, y = self.locations[item_name]
        window_left, window_top = self.game_window.left, self.game_window.top
        pyautogui.moveTo(window_left + x, window_top + y, 0.2)
        click(button='right', coords=(window_left + x, window_top + y))
        self.move_mouse_back()

    def refuel(self):
        self.open_fish()
        screenshot = take_screenshot(self.game_window)
        if self.detect_image(screenshot, 'fisherman'):
            self.handle_purchase_sequence()

    def handle_purchase_sequence(self):
        self.click_image('fisherman', 'left')
        time.sleep(1)
        if self.detect_image(take_screenshot(self.game_window), 'buy'):
            self.click_image('buy', 'left')
            time.sleep(1)
            if self.detect_image(take_screenshot(self.game_window), 'yes'):
                self.click_image('yes', 'left')
                time.sleep(1)
                if self.detect_image(take_screenshot(self.game_window), 'ok'):
                    self.click_image('ok', 'left')
                    time.sleep(1)

                    screenshot = take_screenshot(self.game_window)
                    if self.detect_image(screenshot, 'pasta', 0.9):
                        print("Found bait")
                        self.use_item('pasta')
                    else:
                        print('We have a problem!')
                else:
                    screenshot = take_screenshot(self.game_window)
                    if self.detect_image(screenshot, 'pasta', 0.9):
                        print("Found bait")
                        self.use_item('pasta')
                    else:
                        print('We have a problem!')
            else:
                print('Yes, not detected')
        else:
            print('No buy option')

    def open_fish(self):
        def process_open_fish(template_name):
            while self.detect_image(take_screenshot(self.game_window), template_name, 0.9):
                self.click_image(template_name, 'right')
                time.sleep(0.1)

        process_open_fish('open1')
        process_open_fish('open2')
        process_open_fish('open3')
        process_open_fish('open4')
        process_open_fish('open5')

        print('All fish processed')

    def click_image(self, name, button):
        window_left, window_top = self.game_window.left, self.game_window.top
        x, y = self.locations[name]
        click_pos = (window_left + x, window_top + y)
        pyautogui.moveTo(click_pos, duration=0.1)
        click(button=button, coords=click_pos)

    def move_mouse_back(self):
        game_center_x = self.game_window.left + self.game_window.width // 2
        game_center_y = self.game_window.top + self.game_window.height // 2
        pyautogui.moveTo(game_center_x // 2, game_center_y // 2, 0.2)
