import hid
import time
import json
import os
from pynput.keyboard import Controller, Key
from controllerGetter import detect_controllers

keyboard_controller = Controller()

# ---------------------------------------------------------
# 1. MAPAS DE TECLAS (Para o Teclado do Mac)
# ---------------------------------------------------------
PLAYER_KEY_MAPS = [
    { # PLAYER 1
        'up': 'w', 'down': 's', 'left': 'a', 'right': 'd',
        'A': 'l', 'B': 'k', 'X': 'i', 'Y': 'j',
        'L': 'q', 'R': 'e', 'start': Key.enter, 'select': Key.space
    },
    { # PLAYER 2
        'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
        'A': 'v', 'B': 'c', 'X': 'f', 'Y': 'x',
        'L': '1', 'R': '2', 'start': '3', 'select': '4'
    }
]

# ---------------------------------------------------------
# 2. CARREGA OS PERFIS UNIVERSAIS
# ---------------------------------------------------------
if not os.path.exists('profiles.json'):
    print("Error: 'profiles.json' not found!")
    print("Please run 'configurator.py' first to map your controllers.")
    exit()

with open('profiles.json', 'r') as file:
    loaded_profiles = json.load(file)

# Prepara as memórias (Listas de Dicionários) baseadas em quantos perfis existem
current_state = [{button: False for button in p.keys()} for p in loaded_profiles]
previous_state = [{button: False for button in p.keys()} for p in loaded_profiles]

def process_inputs(report, player_id):
    if not report:
        return

    # Pega os dados específicos deste jogador
    profile = loaded_profiles[player_id]
    state_atual = current_state[player_id]
    state_anterior = previous_state[player_id]
    key_map = PLAYER_KEY_MAPS[player_id]

    # 1. Matemática de tradução dinâmica
    for button_name, config in profile.items():
        idx = config['index']
        mask = config['mask']
        idle_val = config['idle_value']
        
        if len(report) <= idx:
            continue
            
        # XOR + AND bitwise magic
        is_pressed = ((report[idx] ^ idle_val) & mask) == mask
        state_atual[button_name] = is_pressed

    # 2. Executa os toques no teclado com Hold Forçado
    for button, is_pressed in state_atual.items():
        virtual_key = key_map.get(button)
        if not virtual_key:
            continue

        if is_pressed:
            keyboard_controller.press(virtual_key)
            if not state_anterior[button]:
                print(f"[P{player_id + 1}] {button} Pressed -> Key '{virtual_key}'")
        
        elif not is_pressed and state_anterior[button]:
            keyboard_controller.release(virtual_key)
            print(f"[P{player_id + 1}] {button} Released")
        
        state_anterior[button] = is_pressed

# ---------------------------------------------------------
# 3. O LOOP PRINCIPAL MULTIPLAYER
# ---------------------------------------------------------
print("Starting Universal Multiplayer Translator...")

open_gamepads = []

try:
    connected_controllers = detect_controllers()
    
    if not connected_controllers:
        print("No controllers found. Exiting.")
        exit()

    # Só tenta abrir controles até o número de perfis que temos calibrados (máx 2)
    limit = min(len(connected_controllers), len(loaded_profiles), 2)
    
    for player_id in range(limit):
        target = connected_controllers[player_id]
        gamepad = hid.device()
        gamepad.open_path(target['path'])
        gamepad.set_nonblocking(True)
        open_gamepads.append(gamepad)
        
        print(f"Player {player_id + 1} Ready: {target['name']}")

    print("\nRunning... (Press Ctrl+C to stop)")

    # O loop que escuta todo mundo
    while True:
        for player_id, gamepad in enumerate(open_gamepads):
            data = gamepad.read(64)
            if data:
                process_inputs(data, player_id)
        time.sleep(0.005)

except IOError as ex:
    print(f"Connection Error: {ex}")
except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    for gamepad in open_gamepads:
        gamepad.close()