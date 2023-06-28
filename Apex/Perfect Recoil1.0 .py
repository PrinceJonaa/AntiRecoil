## Someone elses code that I use as a base


import random
import time
from threading import Thread

import keyboard
import mouse
toggle_button = "delete"
active_state = False
last_toggle_state = False

recoil_patterns = {
    "R-301": [[0, 0, 0.0], [-5, 8, 0.0], [-7, 6, 0.0], [-1, 8, 0.0], [-5, 9, 0.0], [-2, 9, 0.0],
              [0, 6, 0.0], [0, 5, 0.0], [6, 2, 0.0], [-7, 3,
                                                      0.0], [1, 2, 0.0], [2, 5, 0.0], [0, 6, 0.0],
              [-2, 5, 0.0], [1, 4, 0.0], [-2, 4, 0.0], [-3, 1,
                                                        0.0], [-4, 4, 0.0], [-6, -2, 0.0], [-1, -4, 0.0],
              [3, 0, 0.0], [2, 1, 0.0], [-2, 0, 0.0], [-2, -3, 0.0]]
}

enabled = False
last_state = False
last_space_press_time = 0


def left_click():
    mouse.click(button='left')


def left_click_state():
    return mouse.is_pressed(button='left')


def anti_recoil_loop():
    global enabled, last_state
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

        if left_click_state() and enabled:
            for i in range(len(recoil_patterns["R-301"])):
                left_click()
                mouse.move(recoil_patterns["R-301"][i][0],
                           int(recoil_patterns["R-301"][i][1] / 1.5))
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
