import os
import random
import time
from ctypes import *
from threading import Thread

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

toggle_button = "delete"
active_state = False
last_toggle_state = False

recoil_patterns = {
    "R-301": [[0, 0, 0.0], [-5, 8, 0.0], [-7, 6, 0.0], [-1, 8, 0.0], [-5, 9, 0.0], [-2, 9, 0.0],
               [0, 6, 0.0], [0, 5, 0.0], [6, 2, 0.0], [-7, 3, 0.0], [1, 2, 0.0], [2, 5, 0.0], [0, 6, 0.0],
               [-2, 5, 0.0], [1, 4, 0.0], [-2, 4, 0.0], [-3, 1, 0.0], [-4, 4, 0.0], [-6, -2, 0.0], [-1, -4, 0.0],
               [3, 0, 0.0], [2, 1, 0.0], [-2, 0, 0.0], [-2, -3, 0.0]]
}

enabled = False
last_state = False
last_space_press_time = 0


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
            for pattern in recoil_patterns["R-301"]:
                mouse_input.click()
                mouse_input.move(pattern[0], int(pattern[1] / 1.5))
                time.sleep(random.uniform(0.072, 0.081))

        time.sleep(0.001)


def main():
    keyboard.add_hotkey(toggle_button, anti_recoil_loop)
    while True:
        time.sleep(0.1)


anti_recoil_thread = Thread(target=anti_recoil_loop)
anti_recoil_thread.daemon = True
anti_recoil_thread.start()

if __name__ == "__main__":
    main()