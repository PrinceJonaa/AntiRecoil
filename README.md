## AntiRecoil
Anti-recoil script built in Python to reduce recoil in FPS games.

### Overview
This script simulates mouse clicks to counteract recoil patterns in various weapons. It reads recoil patterns from `.txt` files in the `/Pattern` directory and allows selecting between them using a GUI. The timing between clicks can be adjusted using the min and max uniform sliders.

### Usage
1. Install the required Python libraries using `pip install -r requirements.txt`
2. Run `python PerfectRecoil1.0.py` to start the script
3. Select a recoil pattern using the Pattern Selector slider
4. Adjust the min and max uniform sliders as needed
5. Press the Toggle Anti-Recoil button to enable/disable the anti-recoil
6. Fire your weapon, and the script will automatically move the mouse to counteract the recoil

### Adding Patterns
To add a new recoil pattern:
1. Create a `.txt` file named after the weapon in the `/Pattern` directory
2. Add lines to the file with 3 comma-separated values: x offset, y offset, timing
3. For example, a pattern could look like:
    ```
     0, 0, 0.05
    -5, 8, 0.07
    -7, 6, 0.06

    (x, y, time_sleep)
    ```
4. The new pattern will automatically be loaded and selectable in the GUI

### Improvements
Some potential improvements to the script:
- Add more recoil patterns for different weapons
- Improve the timing calibration for more accurate recoil compensation
- Add options to adjust the X and Y sensitivity separately
- Improve the variable names and add more comments for clarity
- Add the option to save user settings like selected pattern, min/max uniform, etc.
