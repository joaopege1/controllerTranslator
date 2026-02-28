```markdown
# Generic USB Controller Translator (macOS)

A lightweight Python software that reads raw USB HID data from generic gamepads (like cheap SNES USB clones) and translates them into continuous keyboard inputs. 

This project was built specifically to bypass macOS's strict native GameController framework, allowing unsupported controllers to work perfectly on emulators like **Delta** or **RetroArch**.

## Features
* **Raw HID Reading:** Bypasses the OS and reads data directly from the USB port.
* **Auto-Detection:** Automatically scans and connects to gamepads (no hardcoding Vendor/Product IDs required).
* **Hold-State Support:** Continuously spams the keystroke while a button is held down (essential for running/jumping in platformers like Super Mario).
* **Zero Input Lag:** Runs an optimized non-blocking loop for instantaneous response times.

## Prerequisites
Because this script simulates a virtual keyboard on macOS, you need a few system-level dependencies.

1. **Python 3.x** installed.
2. **Homebrew** (macOS package manager).
3. **C-Level HID Library:** macOS requires the underlying C library to read raw USB data.
   ```bash
   brew install hidapi

```

## Installation

1. Clone or download this repository.
2. (Optional but recommended) Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate

```


3. Install the required Python packages. *Note: We use the pre-compiled `hidapi` package instead of `hid` to prevent macOS missing library errors.*
```bash
pip install hidapi pynput

```



## Usage

1. Plug in your USB Controller.
2. Run the main script:
```bash
python3 main.py

```


3. **⚠️ CRITICAL MACOS STEP:** The first time you run this, macOS will block the script from simulating keyboard presses.
* Go to **System Settings > Privacy & Security > Accessibility**.
* Toggle the switch ON for your Terminal (or the Code Editor you are running the script from, e.g., VS Code or Sublime Text).
* Restart the script.


4. Minimize the terminal and open your emulator!

## ⚙️ Configuration (Key Mapping)

You can easily change which controller button presses which keyboard key. Open `main.py` and modify the `KEY_MAP` dictionary to match your emulator's settings:

```python
KEY_MAP = {
    'up': 'w',
    'down': 's',
    'left': 'a',
    'right': 'd',
    'A': 'l',
    'B': 'k',
    'X': 'i',
    'Y': 'j',
    'start': Key.enter,   # Use Key.xyz for special keys
    'select': Key.space
}

```

## File Structure

* `main.py`: The core loop. Handles the state memory (pressed/released) and triggers the virtual keyboard using `pynput`.
* `controllerGetter.py`: Contains the auto-detection logic (`hid.enumerate()`) to find the Vendor ID and Product ID of your controller automatically based on keyword matching.

## Troubleshooting

* **`ImportError: Unable to load any of the following libraries: libhidapi.dylib`**: You installed the `hid` package instead of `hidapi`, or you forgot to run `brew install hidapi`. Run `pip uninstall hid` followed by `pip install hidapi`.
* **The terminal says "Pressed" but the game isn't responding:** You haven't granted Accessibility permissions in macOS System Settings.
* **The character only moves one step when I hold the D-pad:** Ensure you are using the latest version of `main.py` which includes the "Forced Hold" logic (bypassing macOS's default key-repeat disabling).

```
