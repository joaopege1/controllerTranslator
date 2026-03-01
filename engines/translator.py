import sys
import hid
import time
import json
import os
from pynput.keyboard import Controller, Key
from engines.controllerGetter import detect_controllers

def get_path_profile():
    if getattr(sys, 'frozen', False):
        # Se estiver a correr como um .app (PyInstaller no Mac)
        # O executável fica escondido em "UniversalGamepad.app/Contents/MacOS/app"
        # Precisamos de recuar 3 pastas para ficar ao lado do ícone da aplicação
        path_app = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
        return os.path.join(path_app, 'profiles.json')
    else:
        # Se estiver a correr normalmente no terminal (.py)
        path_script = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path_script, 'profiles.json')

# Guardamos o caminho correto nesta variável para usar no resto do código
PATH_JSON = get_path_profile()

keyboard_controller = Controller()

PLAYER_KEY_MAPS = [
    { # PLAYER 1
        'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
        'A': 'v', 'B': 'c', 'X': 'f', 'Y': 'x',
        'L': '1', 'R': '2', 'start': '3', 'select': '4'
    },
    { # PLAYER 2
        'up': 'w', 'down': 's', 'left': 'a', 'right': 'd',
        'A': 'l', 'B': 'k', 'X': 'i', 'Y': 'j',
        'L': 'q', 'R': 'e', 'start': Key.enter, 'select': Key.space
    }
]

is_running = True

def start_translator():
    global is_running
    is_running = True
    print("Starting Universal Multiplayer Translator...")

    # CARREGA OS PERFIS FRESQUINHOS DO DISCO TODA VEZ QUE CLICA START!
    if not os.path.exists(PATH_JSON):
        print(f"Error: {PATH_JSON} not found!")
        print("Please run 'Calibrate Controllers' first.")
        return

    with open(PATH_JSON, 'r') as file:
        loaded_profiles = json.load(file)

    current_state = [{button: False for button in p.keys()} for p in loaded_profiles]
    previous_state = [{button: False for button in p.keys()} for p in loaded_profiles]

    # Função interna para usar as variáveis frescas
    def process_inputs(report, player_id):
        profile = loaded_profiles[player_id]
        state_atual = current_state[player_id]
        state_anterior = previous_state[player_id]
        key_map = PLAYER_KEY_MAPS[player_id]

        for button_name, config in profile.items():
            idx = config['index']
            mask = config['mask']
            idle_val = config['idle_value']
            
            if len(report) <= idx: continue
                
            is_pressed = ((report[idx] ^ idle_val) & mask) == mask
            state_atual[button_name] = is_pressed

        for button, is_pressed in state_atual.items():
            virtual_key = key_map.get(button)
            if not virtual_key: continue

            if is_pressed:
                keyboard_controller.press(virtual_key)
                if not state_anterior[button]:
                    print(f"[P{player_id + 1}] {button} Pressed -> Key '{virtual_key}'")
            elif not is_pressed and state_anterior[button]:
                keyboard_controller.release(virtual_key)
                print(f"[P{player_id + 1}] {button} Released")
            
            state_anterior[button] = is_pressed

    open_gamepads = []

    try:
        connected_controllers = detect_controllers()
        
        if not connected_controllers:
            print("No controllers found. Exiting.")
            return

        limit = min(len(connected_controllers), len(loaded_profiles), 2)
        
        for player_id in range(limit):
            target = connected_controllers[player_id]
            gamepad = hid.device()
            gamepad.open_path(target['path'])
            gamepad.set_nonblocking(True)
            open_gamepads.append(gamepad)
            
            print(f"Player {player_id + 1} Ready: {target['name']}")

        print("\nRunning... (Press Stop to halt)")
        
        while is_running:
            for player_id, gamepad in enumerate(open_gamepads):
                data = gamepad.read(64)
                if data:
                    process_inputs(data, player_id)
            time.sleep(0.005)

    except IOError as ex:
        print(f"Connection Error: {ex}")
    finally:
        for gamepad in open_gamepads:
            gamepad.close()
        print("Translator stopped.")