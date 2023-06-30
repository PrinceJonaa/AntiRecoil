import os
import random
import time
import tkinter as tk
from ctypes import CDLL, Structure, c_long, c_uint16, c_int, pointer, sizeof
from threading import Thread
from tkinter import ttk
from PIL import ImageGrab

import keyboard
import mouse

libc = CDLL("libc.so.6")


class TimeVal(Structure):
    _fields_ = [("sec", c_long), ("u_sec", c_long)]


class InputEvent(Structure):
    _fields_ = [("time", TimeVal), ("type", c_uint16),
                ("code", c_uint16), ("value", c_int)]


class MouseInput:
    """
    MouseInput class to simulate mouse input.
    
    Parameters:
    device_name (str): The device name to search for, set to "event-mouse".
    
    Functionality:
    - Searches for a device in /dev/input/by-path/ that ends with the device_name.
    - Opens the device file for writing.
    - Raises an Exception if the device is not found.
    - Sends input events to the device to simulate clicks and movement.
    - click() simulates a left mouse click by sending press and release events.
    - move(x, y) moves the mouse cursor by x and y coordinates.
    """
    def __init__(self):
        self.handle = -1
        device_name = "event-mouse"
        for device in os.listdir("/dev/input/by-path/"):
            if device[-len(device_name):] == device_name:
                self.handle = os.open(
                    "/dev/input/by-path/" + device, os.O_WRONLY)
                return
        raise Exception("Input [" + device_name + "] not found!")

    def __del__(self):
        if self.handle != -1:
            os.close(self.handle)

    def __send_input(self, input_type, code, value):
        start = InputEvent()
        end = InputEvent()
        libc.gettimeofday(pointer(start.time), 0)
        start.type = input_type
        start.code = code
        start.value = value
        libc.gettimeofday(pointer(end.time), 0)
        libc.write(self.handle, pointer(start), sizeof(start))
        libc.write(self.handle, pointer(end), sizeof(end))

    def click(self):
        self.__send_input(0x01, 0x110, 1)
        libc.usleep(50000)
        self.__send_input(0x01, 0x110, 0)

    def move(self, x, y):
        self.__send_input(0x02, 0, x)
        self.__send_input(0x02, 1, y)


mouse_input = MouseInput()

triggerbot_button = '0'
# Set the coordinates for the crosshair position
crosshair_x = 500
crosshair_y = 300
# Set the pixel color threshold for enemy detection
enemy_color_threshold = 50
triggerbot_button = '0'

# Function to check if an enemy is within the crosshair
def is_enemy_in_crosshair():
    # Capture the game screen
    screen = ImageGrab.grab()

    # Get the pixel color at the crosshair position
    pixel_color = screen.getpixel((crosshair_x, crosshair_y))

    # Check if the pixel color indicates an enemy player
    if pixel_color[0] < enemy_color_threshold and pixel_color[1] < enemy_color_threshold and pixel_color[2] < enemy_color_threshold:
        return True

    return False


# Function to perform a mouse click
def perform_mouse_click():
    mouse.click('left')



# Triggerbot function
def triggerbot():
    while True:
        # Check if the triggerbot button is held (e.g., c)
        if keyboard.is_pressed(triggerbot_button):
            # Check if an enemy is within the crosshair
            if is_enemy_in_crosshair():
                # Perform a mouse click
                perform_mouse_click()

        # Sleep for a short duration before checking again
        time.sleep(0.01)

# Create a thread for the triggerbot function
triggerbot_thread = Thread(target=triggerbot)
triggerbot_thread.daemon = True
triggerbot_thread.start()

def update_triggerbot_button(*args):
    global triggerbot_button
    triggerbot_button = triggerbot_button_var.get()
    
def update_crosshair_x(val):
    global crosshair_x
    crosshair_x = int(val)


def update_enemy_color_threshold(val):
    global enemy_color_threshold
    enemy_color_threshold = int(val)


def update_crosshair_y(val):
    global crosshair_y
    crosshair_y = int(val)

root = tk.Tk()
root.title("Anti-Recoil Script")

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

    
triggerbot_frame = tk.Frame(main_frame)
triggerbot_frame.grid(row=2, column=0, columnspan=2)

triggerbot_label = tk.Label(triggerbot_frame, text="Triggerbot Key:")
triggerbot_label.grid(row=0, column=0, padx=(0, 5))

triggerbot_button_var = tk.StringVar()
triggerbot_button_var.trace("w", update_triggerbot_button)
triggerbot_dropdown = ttk.Combobox(triggerbot_frame, textvariable=triggerbot_button_var, values=[
    'a', 'b', 'c', 'd', '0'], width=10)
triggerbot_dropdown.set(triggerbot_button)
triggerbot_dropdown.grid(row=0, column=1)

crosshair_frame = tk.Frame(main_frame)
crosshair_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

crosshair_x_slider = tk.Scale(crosshair_frame, from_=0, to=1920, orient=tk.HORIZONTAL, label="Crosshair X",
                              command=update_crosshair_x)
crosshair_x_slider.set(crosshair_x)
crosshair_x_slider.pack(side=tk.LEFT, padx=(0, 10))

crosshair_y_slider = tk.Scale(crosshair_frame, from_=0, to=1080, orient=tk.HORIZONTAL, label="Crosshair Y",
                              command=update_crosshair_y)
crosshair_y_slider.set(crosshair_y)
crosshair_y_slider.pack(side=tk.LEFT, padx=(0, 10))

enemy_color_threshold_slider = tk.Scale(main_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                        label="Enemy Color Threshold", command=update_enemy_color_threshold)
enemy_color_threshold_slider.set(enemy_color_threshold)
enemy_color_threshold_slider.grid(row=4, column=0, columnspan=2, pady=(10, 5))

# Function to validate and set a default value if the input is invalid
def validate_and_set(var, values, default):
    if var.get() not in values:
        var.set(default)

# Validate and set default value for triggerbot_button_var
triggerbot_values = ['a', 'b', 'c', 'd', '0']
validate_and_set(triggerbot_button_var, triggerbot_values, triggerbot_values[-1])

# Validate and set default value for enemy_color_threshold_slider
if enemy_color_threshold_slider.get() < 0 or enemy_color_threshold_slider.get() > 100:
    enemy_color_threshold_slider.set(50)  # Default to 50 if the value is invalid
    
root.mainloop()