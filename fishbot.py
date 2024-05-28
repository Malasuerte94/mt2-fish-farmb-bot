import cv2
import numpy as np
import time
import pyautogui
from pywinauto.mouse import move, click
import pygetwindow as gw
import random
from pywinauto.keyboard import send_keys
from threading import Thread, Event
from bot_logic import focus_game_window, ps_fish, take_screenshot

class FishBot(Thread):
    def __init__(self, window_title):
        super().__init__()
        self.window_title = window_title
        self.stop_event = Event()
        self.game_window = focus_game_window(self.window_title)
        self.fish_image = cv2.imread('fish.png')
        self.momeala_image = cv2.imread('momeala.png')
        self.fisherman = cv2.imread('pescar.png')
        self.buy = cv2.imread('buy.png')
        self.yes = cv2.imread('yes.png')
        self.ok = cv2.imread('ok.png')
        self.pasta = cv2.imread('pasta.png')
        self.open1 = cv2.imread('open1.png')
        self.open2 = cv2.imread('open2.png')
        self.open3 = cv2.imread('open3.png')
        self.fishing_wait = 2.3

    def run(self):
        if not self.game_window:
            print(f"Could not find game window: {self.window_title}")
            return
        
        self.press_f3_or_use_fish()
        self.press_space()

        last_detection_time = time.time()
        detection_timeout = 30

        while not self.stop_event.is_set():
            screenshot = ps_fish(self.game_window)
            if self.detect_fish(screenshot):
                print("Fish detected")
                self.fish_catch()
                time.sleep(5)
                self.press_f3_or_use_fish()
                self.press_space()
                last_detection_time = time.time()
            else:
                if time.time() - last_detection_time > detection_timeout:
                    print("No fish detected for 10 seconds, restarting...")
                    last_detection_time = time.time()  # Reset the detection timer
                    self.press_f3_or_use_fish()
                    self.press_space()
            time.sleep(0.01)

    def stop(self):
        self.stop_event.set()

    def detect_fish(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_fish = cv2.cvtColor(self.fish_image, cv2.COLOR_BGR2GRAY)

        best_match_val = float('-inf')
        best_match_loc = None
        best_match_scale = None

        min_scale = 0.2
        max_scale = 3.0

        for scale in np.linspace(min_scale, max_scale, 20):
            resized_fish = cv2.resize(gray_fish, None, fx=scale, fy=scale)
            result = cv2.matchTemplate(gray_image, resized_fish, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = max_loc
                best_match_scale = scale

        threshold = 0.8
        return best_match_val >= threshold

    def fish_catch(self):
        time.sleep(self.fishing_wait)
        self.press_space()
        print("Finished fishing")
    
    def press_f3_or_use_fish(self):
        window_left, window_top = self.game_window.left, self.game_window.top
        screenshot = take_screenshot(self.game_window)
        if self.detect_small_fish(screenshot):
            print("Found fish bait")
            self.use_fish()
        else:
            screenshot = take_screenshot(self.game_window)
            if self.detect_bait(screenshot):
                print("Found bait")
                x, y = self.pasta_loc
                click_pos = (window_left + x, window_top + y)
                pyautogui.moveTo(window_left + x, window_top + y, 0.2)
                click(button='right', coords=click_pos)
                self.move_mouse_back()
            else:
                self.refuel()

    def detect_small_fish(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_momeala = cv2.cvtColor(self.momeala_image, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_momeala, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val >= threshold:
            self.momeala_loc = max_loc
            return True
        else:
            return False
        
    
    def refuel(self):
        self.open_fish()
        window_left, window_top = self.game_window.left, self.game_window.top
        screenshot = take_screenshot(self.game_window)
        if self.detect_pescar(screenshot):
            print('Pescar detected')
            x, y = self.pescar_loc
            click_pos = (window_left + x, window_top + y)
            pyautogui.moveTo(window_left + x, window_top + y, 0.2)
            click(button='left', coords=click_pos)
            time.sleep(1)
            screenshot = take_screenshot(self.game_window)
            if self.detect_buy(screenshot):
                print('Buy option detected')
                x, y = self.buy_loc
                click_pos = (window_left + x, window_top + y)
                pyautogui.moveTo(window_left + x, window_top + y, 0.2)
                click(button='left', coords=click_pos)
                time.sleep(1)
                screenshot = take_screenshot(self.game_window)
                if self.detect_yes(screenshot):
                    print('YES detected')
                    x, y = self.yes_loc
                    click_pos = (window_left + x, window_top + y)
                    pyautogui.moveTo(window_left + x, window_top + y, 0.2)
                    click(button='left', coords=click_pos)
                    time.sleep(1)

                    screenshot = take_screenshot(self.game_window)
                    if self.detect_ok(screenshot):
                        print('OK detected')
                        x, y = self.ok_loc
                        click_pos = (window_left + x, window_top + y)
                        pyautogui.moveTo(window_left + x, window_top + y, 0.2)
                        click(button='left', coords=click_pos)
                        time.sleep(1)
                        self.use_bait()
                    else:
                        print('No ok detected')
                        time.sleep(1)
                        self.use_bait()
                else:
                    print('Yes, not detected')
            else:
                print('No buy option')
        else:
            print('No pescar')

    def open_fish(self):
        window_left, window_top = self.game_window.left, self.game_window.top
        def process_open_fish(template):
            while True:
                screenshot = take_screenshot(self.game_window)
                open_location = self.detect_open_fish(screenshot, template)
                if open_location:
                    print(f'{template} detected')
                    x, y = open_location
                    click_pos = (window_left + x, window_top + y)
                    pyautogui.moveTo(click_pos, duration=0.2)
                    pyautogui.click(button='right')
                    time.sleep(0.5)
                else:
                    break

        process_open_fish(self.open1)
        process_open_fish(self.open2)
        process_open_fish(self.open3)

        print('All fish processed')


    def use_bait(self):
        window_left, window_top = self.game_window.left, self.game_window.top
        screenshot = take_screenshot(self.game_window)
        if self.detect_bait(screenshot):
            print("Found bait")
            x, y = self.pasta_loc
            click_pos = (window_left + x, window_top + y)
            pyautogui.moveTo(window_left + x, window_top + y, 0.2)
            click(button='right', coords=click_pos)
            self.move_mouse_back()
        else:
            print('We have a problem!')

    def move_mouse_back(self):
        game_center_x = self.game_window.left + self.game_window.width // 2
        game_center_y = self.game_window.top + self.game_window.height // 2
        pyautogui.moveTo(game_center_x, game_center_y, 0.2)
        

    def detect_bait(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_momeala = cv2.cvtColor(self.pasta, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_momeala, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.9
        if max_val >= threshold:
            self.pasta_loc = max_loc
            return True
        else:
            return False
        

    def detect_open_fish(self, image, template):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.9
        if max_val >= threshold:
            return max_loc
        else:
            return None


    def detect_pescar(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_momeala = cv2.cvtColor(self.fisherman, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_momeala, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val >= threshold:
            self.pescar_loc = max_loc
            return True
        else:
            return False
        
    
    def detect_yes(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_momeala = cv2.cvtColor(self.yes, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_momeala, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val >= threshold:
            self.yes_loc = max_loc
            return True
        else:
            return False


    def detect_buy(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_momeala = cv2.cvtColor(self.buy, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_momeala, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val >= threshold:
            self.buy_loc = max_loc
            return True
        else:
            return False
    
    def detect_ok(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_momeala = cv2.cvtColor(self.ok, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_momeala, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val >= threshold:
            self.ok_loc = max_loc
            return True
        else:
            return False

    def press_f3(self):
        send_keys('{F3 down}')
        press_duration = random.uniform(0.2, 0.4)
        print(f"Hit F3")
        time.sleep(press_duration)
        send_keys('{F3 up}')
    

    def use_fish(self):
        print("Used momeala")
        x, y = self.momeala_loc
        window_left, window_top = self.game_window.left, self.game_window.top
        pyautogui.moveTo(window_left + x, window_top + y, 0.2)
        click(button='right', coords=(window_left + x, window_top + y))
        self.move_mouse_back()

    def press_space(self):
        send_keys('{SPACE down}')
        press_duration = random.uniform(0.2, 0.4)
        print(f"Hit Space")
        time.sleep(press_duration)
        send_keys('{SPACE up}')
