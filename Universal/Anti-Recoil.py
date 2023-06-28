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

# Configuration
horizontal_range = 4
min_vertical = 6.6
max_vertical = 7.2
min_firerate = 0.01
max_firerate = 0.03
toggle_button = 'num lock'
anti_recoil_enabled = False
vertical_speed = 3.0
# Set the coordinates for the crosshair position
crosshair_x = 500
crosshair_y = 300
# Set the pixel color threshold for enemy detection
enemy_color_threshold = 50
triggerbot_button = '0'


def anti_recoil_loop():
    global anti_recoil_enabled, last_state
    last_state = False
    last_space_press_time = 0

    while True:
        key_down = keyboard.is_pressed(toggle_button)
        # If the toggle button is pressed, toggle the anti_recoil_enabled value and print
        if key_down != last_state:
            last_state = key_down
            if last_state:
                anti_recoil_enabled = not anti_recoil_enabled
                if anti_recoil_enabled:
                    print("Anti-recoil anti_recoil_enabled")
                else:
                    print("Anti-recoil DISABLED")
        
        

        if mouse.is_pressed(button='left') and anti_recoil_enabled:
            # Offsets are generated every shot between the min and max config settings
            offset_const = 1000
            horizontal_offset = random.randrange(
                int(-horizontal_range * offset_const), int(horizontal_range * offset_const)) / offset_const
            vertical_offset = random.randrange(
                int(min_vertical * offset_const), int(max_vertical * offset_const)) / offset_const

            # Move the mouse with these offsets
            mouse_input.move(int(horizontal_offset), int(vertical_offset))
            
            # Generate random time offset with the config settings
            time_offset = random.randrange(int(min_firerate * offset_const), int(max_firerate * offset_const)) / offset_const
            time.sleep(time_offset)

        if mouse.is_pressed(button='left') and mouse.is_pressed(button='right'):
            while mouse.is_pressed(button='left'):
                offset_const = 1000
                # Generate random time offset with the config settings
                time_offset = random.randrange(int(min_firerate * offset_const), int(max_firerate * offset_const)) / offset_const
                time.sleep(time_offset)
                # Adjust the y-offset with the vertical speed
                mouse_input.move(-10, int(12 * vertical_speed))
                time.sleep(time_offset)
                # Adjust the y-offset with the vertical speed
                mouse_input.move(10, int(-10 * vertical_speed))
                time.sleep(time_offset)
                
                

        time.sleep(0.001)


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


def start_anti_recoil():
    global anti_recoil_enabled
    anti_recoil_enabled = True


def stop_anti_recoil():
    global anti_recoil_enabled
    anti_recoil_enabled = False


def update_toggle_button(*args):
    global toggle_button
    toggle_button = toggle_button_var.get()


def update_triggerbot_button(*args):
    global triggerbot_button
    triggerbot_button = triggerbot_button_var.get()


def update_vertical_speed(val):
    global vertical_speed
    vertical_speed = float(val)


def update_crosshair_x(val):
    global crosshair_x
    crosshair_x = int(val)


def update_enemy_color_threshold(val):
    global enemy_color_threshold
    enemy_color_threshold = int(val)


def update_crosshair_y(val):
    global crosshair_y
    crosshair_y = int(val)


def update_horizontal_range(val):
    global horizontal_range
    horizontal_range = float(val)


def update_min_vertical(val):
    global min_vertical, max_vertical
    min_vertical = float(val)
    if min_vertical > max_vertical - 0.1:
        max_vertical = min_vertical + 0.1
        if max_vertical < min_vertical + 0.2:
            max_vertical = min_vertical + 0.2
        max_vertical_slider.set(max_vertical)
    if min_vertical < 0.1:
        min_vertical = 0.1
    min_vertical_slider.set(min_vertical)


def update_max_vertical(val):
    """
    Updates the max_vertical value and ensures it remains within the valid range.

    Parameters:
    val (float): The new max_vertical value from the slider.

    Functionality:
    - Sets the global max_vertical variable to the val from the slider.
    - Ensures max_vertical remains at least 0.1 higher than min_vertical. If not, 
      updates min_vertical to max_vertical - 0.1.
    - Ensures min_vertical remains at least 0.2 lower than max_vertical. If not, 
      updates min_vertical to max_vertical - 0.2.
    - Ensures max_vertical is at least 0.2. If not, sets max_vertical to 0.2.
    - Updates the slider to the new max_vertical value.
    """

    global min_vertical, max_vertical
    max_vertical = float(val)
    if max_vertical < min_vertical + 0.1:
        min_vertical = max_vertical - 0.1
        if min_vertical > max_vertical - 0.2:
            min_vertical = max_vertical - 0.2
        min_vertical_slider.set(min_vertical)
    if max_vertical < 0.2:
        max_vertical = 0.2
    max_vertical_slider.set(max_vertical)



def update_min_firerate(val):
    """
    Updates the min_firerate value and ensures it remains within the valid range.
    
    Parameters:
    val (float): The new min_firerate value from the slider.
    
    Functionality:
    - Sets the global min_firerate variable to the val from the slider.
    - Ensures min_firerate remains at least 0.001 lower than max_firerate. If not, 
      updates max_firerate to min_firerate + 0.001.
    - Ensures min_firerate is at least 0.001. If not, sets min_firerate to 0.001.
    - Updates the slider to the new min_firerate value.
    """
    global min_firerate, max_firerate
    min_firerate = float(val)
    if min_firerate > max_firerate - 0.001:
        max_firerate = min_firerate + 0.001
        max_firerate_slider.set(max_firerate)
    if min_firerate <= 0:
        min_firerate = 0.001
    min_firerate_slider.set(min_firerate)


def update_max_firerate(val):
    global min_firerate, max_firerate
    max_firerate = float(val)
    if max_firerate < min_firerate + 0.001:
        min_firerate = max_firerate - 0.001
        min_firerate_slider.set(min_firerate)
    if max_firerate < 0.001:
        max_firerate = 0.001
    max_firerate_slider.set(max_firerate)


anti_recoil_thread = Thread(target=anti_recoil_loop)
anti_recoil_thread.daemon = True
anti_recoil_thread.start()

# Create a thread for the triggerbot function
triggerbot_thread = Thread(target=triggerbot)
triggerbot_thread.daemon = True
triggerbot_thread.start()

root = tk.Tk()
root.title("Anti-Recoil Script")

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

button_frame = tk.Frame(main_frame)
button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))

start_button = tk.Button(button_frame, text="Start", command=start_anti_recoil)
start_button.grid(row=0, column=0, padx=(0, 5))

stop_button = tk.Button(button_frame, text="Stop", command=stop_anti_recoil)
stop_button.grid(row=0, column=1)

toggle_button_var = tk.StringVar()
toggle_button_var.trace("w", update_toggle_button)
toggle_button_entry = ttk.Combobox(button_frame, textvariable=toggle_button_var, values=[
                                   'num lock', 'caps lock', 'scroll lock'], width=10)
toggle_button_entry.set(toggle_button)
toggle_button_entry.grid(row=0, column=2, padx=(10, 5))

slider_frame = tk.Frame(main_frame)
slider_frame.grid(row=1, column=0, columnspan=2)

min_vertical_slider = tk.Scale(slider_frame, from_=0, to=10, resolution=0.1,
                               orient=tk.HORIZONTAL, label="Min Vertical", command=update_min_vertical)
min_vertical_slider.set(min_vertical)
min_vertical_slider.pack(side=tk.LEFT, padx=(0, 5))

max_vertical_slider = tk.Scale(slider_frame, from_=0, to=10, resolution=0.1,
                               orient=tk.HORIZONTAL, label="Max Vertical", command=update_max_vertical)
max_vertical_slider.set(max_vertical)
max_vertical_slider.pack(side=tk.LEFT, padx=(0, 5))

min_firerate_slider = tk.Scale(slider_frame, from_=0, to=0.1, resolution=0.001,
                               orient=tk.HORIZONTAL, label="Min Fire Rate", command=update_min_firerate)
min_firerate_slider.set(min_firerate)
min_firerate_slider.pack(side=tk.LEFT, padx=(0, 5))

max_firerate_slider = tk.Scale(slider_frame, from_=0, to=0.1, resolution=0.001,
                               orient=tk.HORIZONTAL, label="Max Fire Rate", command=update_max_firerate)
max_firerate_slider.set(max_firerate)
max_firerate_slider.pack(side=tk.LEFT, padx=(0, 5))

vertical_speed_slider = tk.Scale(slider_frame, from_=1, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Jiggle Vertical",
                                 command=update_vertical_speed)
vertical_speed_slider.set(vertical_speed)
vertical_speed_slider.pack(side=tk.LEFT, padx=(0, 5))

horizontal_range_slider = tk.Scale(slider_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Jiggle Horizontal",
                                   command=update_horizontal_range)
horizontal_range_slider.set(horizontal_range)
horizontal_range_slider.pack(side=tk.LEFT, padx=(0, 5))

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

# Validate and set default value for toggle_button_var
toggle_button_values = ['num lock', 'caps lock', 'scroll lock']
validate_and_set(toggle_button_var, toggle_button_values, toggle_button_values[0])

# Validate and set default value for triggerbot_button_var
triggerbot_values = ['a', 'b', 'c', 'd', '0']
validate_and_set(triggerbot_button_var, triggerbot_values, triggerbot_values[-1])

# Validate and set default value for enemy_color_threshold_slider
if enemy_color_threshold_slider.get() < 0 or enemy_color_threshold_slider.get() > 100:
    enemy_color_threshold_slider.set(50)  # Default to 50 if the value is invalid

root.mainloop()