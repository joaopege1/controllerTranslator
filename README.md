# Generic USB Controller Translator (macOS)

A lightweight Python application that reads raw USB HID data from generic gamepads (like cheap SNES USB clones) and translates them into keyboard inputs. Built to bypass macOS's strict native GameController framework, allowing unsupported controllers to work with emulators such as **Delta**.

## Features

**Core Translation**
- **Raw HID Reading:** Bypasses the OS and reads data directly from the USB port.
- **Auto-Detection:** Scans and connects to gamepads automatically using keyword matching (gamepad, joystick, controller, snes, retrolink). No hardcoded Vendor/Product IDs required.
- **Multiplayer Support:** Connect up to 2 USB controllers simultaneously with independent key mappings for each player.
- **Per-Player Key Mapping:** Each controller has its own customizable key map (D-pad, face buttons A/B/X/Y, shoulders L/R, start, select).
- **Hold-State Support:** Maintains key press while a button is held and releases when released, essential for running and jumping in platformers.
- **Zero Input Lag:** Optimized non-blocking loop with minimal polling delay for responsive input.

**Calibration**
- **Automatic Controller Calibration:** Built-in calibration tool auto-detects button mappings for any controller. Captures idle state, guides you through pressing each button, and saves index, mask, and idle value for precise recognition.
- **Profile-Based Configuration:** Calibration data is stored in `profiles.json` and loaded at runtime. Recalibrate only when switching controllers.

**Graphical Interface**
- **Desktop Application:** Modern GUI built with CustomTkinter. Single window with Calibrate, Start Translator, and Stop controls.
- **System Console:** Live output panel showing calibration progress and translator activity.
- **System Appearance:** Follows macOS light/dark mode.
- **Background Execution:** Calibration and translation run in separate threads so the interface stays responsive.

**Packaging**
- **Standalone App:** Can be built as `UniversalGamepad.app` with PyInstaller for distribution without Python installed.
- **Portable Profiles:** When running as a bundled app, `profiles.json` is resolved relative to the application bundle.

**Developer Tools**
- **Raw HID Debugging:** `unlimitedOutputs.py` streams raw HID data from a controller (requires Vendor/Product ID) for reverse-engineering unmapped controllers.
- **Input Validation:** `mappingInputs.py` tests button detection and mapping verification.
- **Reference Documentation:** `mapping.py` documents raw HID data patterns for common button combinations.

## Prerequisites

1. **Python 3.x** installed.
2. **Homebrew** (macOS package manager).
3. **C-Level HID Library:** Required for raw USB access.
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
3. Install the required Python packages. Use `hidapi` instead of `hid` to avoid macOS library errors.
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install hidapi pynput customtkinter
   ```

## Controller Calibration (Recommended)

If your controller buttons do not map correctly, run calibration first:

1. Launch the application (`python3 main.py` or open `UniversalGamepad.app`).
2. Click **Calibrate Controllers**.
3. The tool will:
   - Auto-detect connected controllers (up to 2).
   - Ask you not to touch any buttons while it captures the idle state.
   - Guide you through pressing and holding each button (up, down, left, right, A, B, X, Y, L, R, select, start).
   - Save the calibration to `profiles.json`.

Once calibrated, the translator uses these profiles for accurate button recognition.

## Usage

1. **Plug in your USB controller(s)** – up to 2 supported.
2. Run the application:
   ```bash
   python3 main.py
   ```
   Or open `UniversalGamepad.app` if you have built the standalone bundle.
3. **macOS Accessibility:** The first time you run, macOS may block keyboard simulation.
   - Go to **System Settings > Privacy & Security > Accessibility**.
   - Enable access for Terminal (or your code editor if running from there).
   - Restart the application.
4. Click **Start Translator** and minimize the window.
5. Open your emulator. Controller input is translated to keyboard keys.

**Multiplayer:** Plug in both controllers before starting. They are assigned as Player 1 and Player 2 with separate key mappings.

## Configuration (Key Mapping)

Key mappings are defined in `engines/translator.py` in the `PLAYER_KEY_MAPS` list. Each element corresponds to a player:

```python
PLAYER_KEY_MAPS = [
    {  # PLAYER 1
        'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
        'A': 'v', 'B': 'c', 'X': 'f', 'Y': 'x',
        'L': '1', 'R': '2', 'start': '3', 'select': '4'
    },
    {  # PLAYER 2
        'up': 'w', 'down': 's', 'left': 'a', 'right': 'd',
        'A': 'l', 'B': 'k', 'X': 'i', 'Y': 'j',
        'L': 'q', 'R': 'e', 'start': Key.enter, 'select': Key.space
    }
]
```

Use character strings like `'w'` for letter keys or `Key.enter` for special keys. The system supports up to 2 players.

## File Structure

- `main.py`: GUI launcher. Runs calibration and translator in background threads, displays console output.
- `engines/controllerGetter.py`: Auto-detection logic using `hid.enumerate()` and keyword matching. Filters duplicate USB interfaces.
- `engines/translator.py`: Controller-to-keyboard translation. Loads profiles, manages per-player state, sends key press/release via pynput.
- `engines/configurator.py`: Calibration tool. Captures idle state and button mappings, writes `profiles.json`.
- `profiles.json`: Calibrated button mappings for up to 2 controllers (index, mask, idle_value per button).
- `mappingAndTesting/`:
  - `mapping.py`: Reference documentation for raw HID data patterns.
  - `unlimitedOutputs.py`: Debug utility to stream raw HID data (requires Vendor/Product ID).
  - `mappingInputs.py`: Input validation and mapping verification tool.

## Building the Standalone App

To create `UniversalGamepad.app`:

```bash
pip install pyinstaller
pyinstaller UniversalGamepad.spec
```

The app will be in `dist/UniversalGamepad.app`. Place `profiles.json` next to the app or run calibration from the app first.

## Troubleshooting

- **`ImportError: Unable to load any of the following libraries: libhidapi.dylib`:** Install `hidapi` via Homebrew and use the `hidapi` Python package, not `hid`. Run `pip uninstall hid` and `pip install hidapi`.
- **"Pressed" in console but game does not respond:** Grant Accessibility permissions in System Settings.
- **Character moves only one step when holding D-pad:** Ensure the translator is running and that the emulator accepts the mapped keys. The translator uses proper press/release, not key repeat.
- **Second controller not detected:** Plug both controllers in before starting. Check **System Information > USB** to confirm they are recognized.
- **Player 2 inputs not working:** Verify `PLAYER_KEY_MAPS` in `engines/translator.py` has correct bindings for Player 2.
- **Buttons detected incorrectly:** Run calibration again. It works with any controller model.
- **Debugging controller inputs:** Use `mappingAndTesting/unlimitedOutputs.py` (edit Vendor/Product IDs as needed) to inspect raw HID data.
