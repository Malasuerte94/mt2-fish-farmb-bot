import tkinter as tk
from PIL import Image, ImageTk
from bot_logic import set_map_region
import pygetwindow as gw

class MapSelectorOverlay:
    def __init__(self, root, selected_window, game_window_position, set_map_region):
        self.root = root
        self.selected_window = selected_window
        self.game_window_position = game_window_position
        self.set_map_region = set_map_region

        # Load the map.png image
        self.map_image = Image.open("map.png").convert("RGBA")  # Ensure transparency
        self.map_photo = ImageTk.PhotoImage(self.map_image)

        # Create a label to display the map image
        self.map_label = tk.Label(self.root, image=self.map_photo)
        self.map_label.pack()

        # Add the "Set" button
        self.set_button = tk.Button(self.root, text="Set", command=self.save_settings)
        self.set_button.pack()

        # Set opacity to 50%
        self.root.attributes('-alpha', 0.5)

        # Bind events
        self.map_label.bind("<Button-1>", self.move_overlay)
        self.map_label.bind("<B1-Motion>", self.move_overlay)
        self.map_label.bind("<ButtonRelease-1>", self.move_overlay)

        # Initialize position and dimensions
        self.start_x = 0
        self.start_y = 0
        self.width = self.map_image.width
        self.height = self.map_image.height

    def move_overlay(self, event):
        # Get the position relative to the game window
        self.start_x = event.x_root - self.selected_window.left
        self.start_y = event.y_root - self.selected_window.top

        # Update the position of the map overlay
        self.root.geometry(f"+{self.start_x}+{self.start_y}")

    def save_settings(self):
        # Save the position and dimensions of the map overlay
        region = (
            self.start_x,
            self.start_y,
            self.width,
            self.height
        )
        self.set_map_region(region, self.selected_window)

        # Hide the overlay
        self.root.destroy()

# Test
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    selected_window = gw.getActiveWindow()  # Assuming the game window is active
    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)  # Remove window decorations
    overlay.attributes("-topmost", True)  # Ensure it stays on top
    app = MapSelectorOverlay(overlay, selected_window)
    root.mainloop()
