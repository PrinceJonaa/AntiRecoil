import os
import time
import random
import keyboard
import mouse
from ctypes import *
import tkinter as tk
from tkinter import ttk
from threading import Thread

libc = CDLL("libc.so.6")

class TimeVal(Structure):
    _fields_ = [("sec", c_long), ("u_sec", c_long)]

class InputEvent(Structure):
    _fields_ = [("time", TimeVal), ("type", c_uint16), ("code", c_uint16), ("value", c_int)]

class MouseInput:
    def __init__(self):
        self.handle = -1
        device_name = "event-mouse"
        for device in os.listdir("/dev/input/by-path/"):
            if device[-len(device_name):] == device_name:
                self.handle = os.open("/dev/input/by-path/" + device, os.O_WRONLY)
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

mouseIpt = MouseInput()

# Configuration
horizontal_range = 1
min_vertical = 1
max_vertical = 4
min_firerate = 0.01
max_firerate = 0.03
toggle_button = 'num lock'
enabled = False
tap_strafe_key = 'w'
tap_strafe_button = 'space'
tap_strafe_enabled = False
tap_strafe_repeat_rate = 40
tap_strafe_repeat_interval = 1 / tap_strafe_repeat_rate


def anti_recoil_loop():
    global enabled, last_state, tap_strafe_enabled
    last_state = False
    last_space_press_time = 0

    while True:
        key_down = keyboard.is_pressed(toggle_button)
        # If the toggle button is pressed, toggle the enabled value and print
        if key_down != last_state:
            last_state = key_down
            if last_state:
                enabled = not enabled
                if enabled:
                    print("Anti-recoil ENABLED")
                else:
                    print("Anti-recoil DISABLED")

        if mouse.is_pressed(button='left') and enabled:
            # Offsets are generated every shot between the min and max config settings
            offset_const = 1000
            horizontal_offset = random.randrange(-horizontal_range * offset_const, horizontal_range * offset_const, 1) / offset_const
            vertical_offset = random.randrange(min_vertical * offset_const, max_vertical * offset_const, 1) / offset_const

            # Move the mouse with these offsets
            mouseIpt.move(int(horizontal_offset), int(vertical_offset))

            # Generate random time offset with the config settings
            time_offset = random.randrange(min_firerate * offset_const, max_firerate * offset_const, 1) / offset_const
            time.sleep(time_offset)
        
        if keyboard.is_pressed(tap_strafe_button) and tap_strafe_enabled:
            if time.time() - last_space_press_time >= tap_strafe_repeat_interval:
                last_space_press_time = time.time()
                with keyboard.pressed(tap_strafe_key):
                    time.sleep(tap_strafe_repeat_interval)

        time.sleep(0.001)

def start_anti_recoil():
    global enabled
    enabled = True

def stop_anti_recoil():
    global enabled
    enabled = False

def start_tap_strafe():
    global tap_strafe_enabled
    tap_strafe_enabled = True

def stop_tap_strafe():
    global tap_strafe_enabled
    tap_strafe_enabled = False

def update_toggle_button(*args):
    global toggle_button
    toggle_button = toggle_button_var.get()

def update_tap_strafe_button(*args):
    global tap_strafe_button
    tap_strafe_button = tap_strafe_button_var.get()

def update_min_vertical(val):
    global min_vertical, max_vertical
    min_vertical = float(val)
    if min_vertical > max_vertical:
        max_vertical = min_vertical
        max_vertical_slider.set(max_vertical)

def update_max_vertical(val):
    global min_vertical, max_vertical
    max_vertical = float(val)
    if max_vertical < min_vertical:
        min_vertical = max_vertical
        min_vertical_slider.set(min_vertical)


def update_min_firerate(val):
    global min_firerate, max_firerate
    min_firerate = float(val)
    if min_firerate > max_firerate:
        max_firerate = min_firerate
        max_firerate_slider.set(max_firerate)

def update_max_firerate(val):
    global min_firerate, max_firerate
    max_firerate = float(val)
    if max_firerate < min_firerate:
        min_firerate = max_firerate
        min_firerate_slider.set(min_firerate)


anti_recoil_thread = Thread(target=anti_recoil_loop)
anti_recoil_thread.daemon = True
anti_recoil_thread.start()

root = tk.Tk()
root.title("Anti-Recoil Script")

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

button_frame = tk.Frame(main_frame)
button_frame.pack(side=tk.TOP, pady=(0, 10))

start_button = tk.Button(button_frame, text="Start", command=start_anti_recoil)
start_button.pack(side=tk.LEFT, padx=(0, 5))

stop_button = tk.Button(button_frame, text="Stop", command=stop_anti_recoil)
stop_button.pack(side=tk.LEFT)

start_tap_strafe_button = tk.Button(button_frame, text="Start Tap Strafe", command=start_tap_strafe)
start_tap_strafe_button.pack(side=tk.LEFT, padx=(10, 5))

stop_tap_strafe_button = tk.Button(button_frame, text="Stop Tap Strafe", command=stop_tap_strafe)
stop_tap_strafe_button.pack(side=tk.LEFT)

toggle_button_var = tk.StringVar()
toggle_button_var.trace("w", update_toggle_button)
toggle_button_entry = ttk.Combobox(button_frame, textvariable=toggle_button_var, values=['num lock', 'caps lock', 'scroll lock'], width=10)
toggle_button_entry.set(toggle_button)
toggle_button_entry.pack(side=tk.LEFT, padx=(10, 5))

tap_strafe_button_var = tk.StringVar()
tap_strafe_button_var.trace("w", update_tap_strafe_button)
tap_strafe_button_entry = ttk.Combobox(button_frame, textvariable=tap_strafe_button_var, values=['a', 's', 'w','space'], width=5)
tap_strafe_button_entry.set(tap_strafe_button)
tap_strafe_button_entry.pack(side=tk.LEFT)

slider_frame = tk.Frame(main_frame)
slider_frame.pack(side=tk.TOP)

min_vertical_slider = tk.Scale(slider_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Min Vertical", command=update_min_vertical)
min_vertical_slider.set(min_vertical)
min_vertical_slider.pack(side=tk.TOP, pady=(0, 5))

max_vertical_slider = tk.Scale(slider_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Max Vertical", command=update_max_vertical)
max_vertical_slider.set(max_vertical)
max_vertical_slider.pack(side=tk.TOP, pady=(0, 5))

min_firerate_slider = tk.Scale(slider_frame, from_=0, to=0.1, resolution=0.001, orient=tk.HORIZONTAL, label="Min Fire Rate", command=update_min_firerate)
min_firerate_slider.set(min_firerate)
min_firerate_slider.pack(side=tk.TOP, pady=(0, 5))

max_firerate_slider = tk.Scale(slider_frame, from_=0, to=0.1, resolution=0.001, orient=tk.HORIZONTAL, label="Max Fire Rate", command=update_max_firerate)
max_firerate_slider.set(max_firerate)
max_firerate_slider.pack(side=tk.TOP, pady=(0, 5))

root.mainloop()
