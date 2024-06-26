import os
from threading import Thread, Event
import time

import cv2
import telebot
import numpy as np
import matplotlib.pyplot as plt
from bot_logic import focus_game_window, take_screenshot
from PIL import ImageGrab
from dotenv import load_dotenv

load_dotenv()


class MessageDetector(Thread):
    def __init__(self, game_title):
        super().__init__()
        self.game_window = focus_game_window(game_title)
        self.stop_event = Event()
        self.images = {
            'message': cv2.imread('images/message.png'),
            'local_gm': cv2.imread('images/gm_local.png')
        }
        self.locations = {}
        self.credentials = {
            'bot_token': os.getenv('BOT_TOKEN'),
            'chat_id': os.getenv('CHAT_ID')
        }

    def run(self):
        if not self.game_window:
            print(f"Could not find game window: {self.window_title}")
            return
        print("Running Message Detector module...")

        while not self.stop_event.is_set():
            self.detect_message()
            self.detect_local_message()
            time.sleep(1)

    def stop(self):
        self.stop_event.set()

    def detect_message(self):
        #screenshot = take_screenshot(self.game_window)
        self.img = self.take_message_screenshot(self.game_window)
        if self.detect_image(self.img, 'message', 0.8):
            print("Message detected")
            #self.img = self.ps_message()
            self.send_telegram_message("Mesaj privat detectat!")
            time.sleep(10)

    def detect_local_message(self):
        screenshot = take_screenshot(self.game_window)
        if self.detect_image(screenshot, 'local_gm', 0.8):
            print("Message local detected")
            self.img = self.ps_message()
            self.send_telegram_message("Mesaj pe chat detectat!")
            time.sleep(10)

    def detect_image(self, image, name, threshold=0.8):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(self.images[name], cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            self.locations = max_loc
            return True
        return False

    def take_message_screenshot(self, window):
        bbox = (window.width - 100, window.top + 200, window.width, window.height - 300)
        img = np.array(ImageGrab.grab(bbox))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
         
        # plt.imshow(img, cmap='gray')  # Use cmap='gray' for grayscale images
        # plt.axis('off')  # Hide the axis
        # plt.show()
        
        return img

    #not used anymore
    def ps_message(self):
        left, top = self.locations
        left += self.game_window.left
        top += self.game_window.top
        height = 100
        width = 100

        center_x = left
        center_y = top

        bbox = (center_x - width // 2, center_y, center_x + width // 2, center_y + height // 2)
        screenshot = np.array(ImageGrab.grab(bbox))

        img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # for plotting image
        # cv2.imshow('Captured Image', img) 
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # # img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        return img

    def send_telegram_message(self, message="Mesaj nou!"):
        bot = telebot.TeleBot(self.credentials['bot_token'])

        temp_file_path = "temp_screenshot.png"
        cv2.imwrite(temp_file_path, self.img)

        with open(temp_file_path, 'rb') as photo:
            # bot.send_message(self.credentials['chat_id'], "Ai primit un mesaj nou!")
            bot.send_photo(self.credentials['chat_id'], photo, caption={message})
            
        os.remove(temp_file_path)

