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
from ultralytics import YOLO

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
def is_enemy_in_crosshair(model):
    # Capture the game screen
    screen = ImageGrab.grab()

    # Define the region of interest based on the crosshair position
    left = crosshair_x - 10  # Adjust the left coordinate as needed
    top = crosshair_y - 10  # Adjust the top coordinate as needed
    right = crosshair_x + 10  # Adjust the right coordinate as needed
    bottom = crosshair_y + 10  # Adjust the bottom coordinate as needed

    # Crop the image to the specified region of interest
    roi = screen.crop((left, top, right, bottom))

    # Get the pixel color at the crosshair position in the cropped image
    pixel_color = roi.getpixel((10, 10))  # Assuming the crosshair is at the center of the cropped image

    # Check if the pixel color indicates an enemy player
    if pixel_color[0] < enemy_color_threshold and pixel_color[1] < enemy_color_threshold and pixel_color[2] < enemy_color_threshold:
        # Perform object detection on the cropped region of interest
        image_path = 'screen.jpg'  # Save the cropped image to a file
        roi.save(image_path)
        results = model(image_path)  # Perform object detection using YOLOv5

        # Check if any enemy objects are detected
        if results.xyxy[0] is not None:
            return True

    return False


def triggerbot_thread():
    # Load the YOLOv5 model for object detection
    model = YOLO('yolov8n-seg.pt')

    while True:
        if keyboard.is_pressed(triggerbot_button):
            if is_enemy_in_crosshair(model):
                mouse_input.click()
        time.sleep(0.01)


def main():
    triggerbot_thread_instance = Thread(target=triggerbot_thread)
    triggerbot_thread_instance.start()

    root = tk.Tk()
    root.title("Triggerbot Settings")
    root.geometry("300x150")

    def start_triggerbot():
        global triggerbot_button
        triggerbot_button = button_entry.get()
        button_entry.delete(0, "end")
        button_entry.insert(0, "Press any key...")
        button_entry.config(state="disabled")
        start_button.config(state="disabled")
        stop_button.config(state="normal")
        triggerbot_thread_instance.start()

    def stop_triggerbot():
        global triggerbot_button
        triggerbot_button = '0'
        button_entry.delete(0, "end")
        button_entry.insert(0, "Not active")
        button_entry.config(state="normal")
        start_button.config(state="normal")
        stop_button.config(state="disabled")

    label = ttk.Label(root, text="Button to activate Triggerbot:")
    label.pack(pady=10)

    button_entry = ttk.Entry(root, width=20)
    button_entry.pack(pady=10)
    button_entry.insert(0, "Press any key...")
    button_entry.config(state="disabled")

    start_button = ttk.Button(root, text="Start Triggerbot", command=start_triggerbot)
    start_button.pack(pady=10)

    stop_button = ttk.Button(root, text="Stop Triggerbot", command=stop_triggerbot)
    stop_button.pack(pady=10)
    stop_button.config(state="disabled")

    root.mainloop()


if __name__ == "__main__":
    main()
