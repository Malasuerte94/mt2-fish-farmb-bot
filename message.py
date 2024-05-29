from threading import Thread, Event
import time

import cv2
from bot_logic import focus_game_window, take_screenshot

class MessageDetector(Thread):
    def __init__(self, game_title):
        super().__init__()
        self.game_window = focus_game_window(game_title)
        self.stop_event = Event()
        self.images = {
                'message': cv2.imread('images/message.png')
            }

    def run(self):
        if not self.game_window:
            print(f"Could not find game window: {self.window_title}")
            return
        print("Running Message Detector module...")
        
        while not self.stop_event.is_set():
            self.detect_message()
            time.sleep(1)

    def stop(self):
        self.stop_event.set()

    def detect_message(self):
        screenshot = take_screenshot(self.game_window)
        if self.detect_image(screenshot, 'message', 0.8):
                    print("Message detected")
                    
    def detect_image(self, image, name, threshold=0.8):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(self.images[name], cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            #self.locations[name] = max_loc
            return True
        return False