import os
import random
import time
from ctypes import *
from threading import Thread
from tkinter import Tk, Scale, Label, Button, HORIZONTAL

import keyboard
import mouse

libc = CDLL("libc.so.6")


class TimeVal(Structure):
    _fields_ = [("sec", c_long), ("u_sec", c_long)]


class InputEvent(Structure):
    _fields_ = [("time", TimeVal), ("type", c_uint16),
                ("code", c_uint16), ("value", c_int)]


class MouseInput:
    def __init__(self):
        self.handle = -1
        device_name = "event-mouse"
        for device in os.listdir("/dev/input/by-path/"):
            if device.endswith(device_name):
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


mouse_input = MouseInput()

pattern_directory = "/Pattern"

recoil_patterns = {}
pattern_files = os.listdir(pattern_directory)
for pattern_file in pattern_files:
    pattern_name = pattern_file.split(".")[0]
    pattern_path = os.path.join(pattern_directory, pattern_file)
    with open(pattern_path, "r") as file:
        lines = file.readlines()
        pattern = [[float(value) for value in line.strip().split(",")] for line in lines]
        recoil_patterns[pattern_name] = pattern

enabled = False
last_state = False
last_space_press_time = 0
toggle_button = "delete"  # Default toggle button


min_uniform = 0.05  # Minimum value for random.uniform
max_uniform = 0.06  # Maximum value for random.uniform

selected_pattern = "R301"  # Default pattern


def on_pattern_change(value):
    global selected_pattern
    pattern_names = list(recoil_patterns.keys())
    selected_pattern = pattern_names[int(value)]


def on_min_uniform_change(value):
    global min_uniform
    min_uniform = float(value)


def on_max_uniform_change(value):
    global max_uniform
    max_uniform = float(value)


def anti_recoil_loop():
    global enabled, last_state, last_space_press_time

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

        if mouse.is_pressed(button="left") and enabled:
            for pattern in recoil_patterns[selected_pattern]:
                mouse_input.click()
                mouse_input.move(pattern[0], int(pattern[1] / 1.5))
                time.sleep(random.uniform(min_uniform, max_uniform))

        time.sleep(0.001)


def main():
    global selected_pattern

    root = Tk()
    root.title("Pattern Selector")

    pattern_names = list(recoil_patterns.keys())

    pattern_slider_label = Label(root, text="Pattern Selector")
    pattern_slider_label.pack()

    pattern_slider = Scale(root, from_=0, to=len(pattern_names) - 1, orient=HORIZONTAL, command=on_pattern_change)
    pattern_slider.pack()

    min_uniform_label = Label(root, text="Min Uniform")
    min_uniform_label.pack()

    min_uniform_slider = Scale(root, from_=0.0, to=1.0, resolution=0.01, orient=HORIZONTAL,
                               command=on_min_uniform_change)
    min_uniform_slider.pack()

    max_uniform_label = Label(root, text="Max Uniform")
    max_uniform_label.pack()

    max_uniform_slider = Scale(root, from_=0.0, to=1.0, resolution=0.01, orient=HORIZONTAL,
                               command=on_max_uniform_change)
    max_uniform_slider.pack()

    toggle_button = Button(root, text="Toggle Anti-Recoil", command=toggle_anti_recoil)
    toggle_button.pack()

    root.mainloop()


anti_recoil_thread = Thread(target=anti_recoil_loop)
anti_recoil_thread.daemon = True
anti_recoil_thread.start()

if __name__ == "__main__":
    main()