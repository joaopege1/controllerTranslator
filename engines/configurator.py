import sys
import hid
import time
import json
from pathlib import Path
from .controllerGetter import detect_controllers

def get_path_profile() -> Path:
    if getattr(sys, 'frozen', False):
        # .app bundle: executable está em UniversalGamepad.app/Contents/MacOS/app/
        return Path(sys.executable).parents[3] / 'profiles.json'
    return Path(__file__).parent / 'profiles.json'

PATH_JSON = get_path_profile()

BUTTONS_TO_MAP = ['up', 'down', 'left', 'right', 'A', 'B', 'X', 'Y', 'L', 'R', 'select', 'start']
is_running = True

def start_multiplayer_calibration():
    global is_running
    is_running = True
    
    print("=======================================")
    print("  Universal Multiplayer Calibration  ")
    print("=======================================\n")

    controllers = detect_controllers()
    if not controllers:
        print("No controllers found. Please connect them and try again.")
        return

    controllers_to_map = controllers[:2]

    all_profiles = []
    if PATH_JSON.exists():
        try:
            with open(PATH_JSON) as f:
                all_profiles = json.load(f)
        except (json.JSONDecodeError, OSError):
            all_profiles = []

    for player_id, target_controller in enumerate(controllers_to_map):
        if not is_running: break

        if player_id < len(all_profiles) and all_profiles[player_id]:
            print(f"\n--- PLAYER {player_id + 1} already calibrated, skipping. ---")
            continue

        print(f"\n--- SETTING UP PLAYER {player_id + 1} ---")
        print(f"Device: {target_controller['name']}")
        
        gamepad = None
        try:
            gamepad = hid.device()
            gamepad.open_path(target_controller['path'])
            gamepad.set_nonblocking(True)
            
            print("Please DO NOT touch any buttons on this controller.")
            print("Reading idle state in 3 seconds...\n")
            time.sleep(3)

            idle_state = []
            for _ in range(10):
                data = gamepad.read(64)
                if data: idle_state = data
                time.sleep(0.05)
                
            if not idle_state:
                print(f"Failed to read data for Player {player_id + 1}. Skipping.")
                continue

            print(f"Player {player_id + 1} Idle state captured!\n")
            player_profile = {}

            for button in BUTTONS_TO_MAP:
                if not is_running: break
                
                print(f"[PLAYER {player_id + 1}] PRESS AND HOLD: [{button.upper()}]")
                button_data = None
                target_index = None # Guarda ONDE a mudança aconteceu
                
                # Espera o botão ser pressionado
                while is_running:
                    current_data = gamepad.read(64)
                    if current_data and current_data != idle_state:
                        for index, idle_val in enumerate(idle_state):
                            if current_data[index] != idle_val:
                                target_index = index
                                changed_mask = current_data[index] ^ idle_val
                                player_profile[button] = {
                                    "index": index,
                                    "idle_value": idle_state[index],
                                    "mask": changed_mask
                                }
                                button_data = current_data
                                break
                    if button_data:
                        break
                    time.sleep(0.01)

                if not is_running: break

                print(f"[{button.upper()}] mapped successfully!")
                print(f"RELEASE the button and wait...")
                
                # Espera o botão ser solto (Olhando APENAS para o índice mapeado)
                while is_running:
                    current_data = gamepad.read(64)
                    if current_data and len(current_data) > target_index:
                        # Se o índice exato voltou ao valor idle, consideramos solto!
                        if current_data[target_index] == idle_state[target_index]:
                            time.sleep(0.5) # Dá meio segundo pro usuário respirar
                            break
                    time.sleep(0.01)
                    
                print("-" * 30)

            while len(all_profiles) <= player_id:
                all_profiles.append({})
            all_profiles[player_id] = player_profile

        except Exception as e:
            print(f"Error setting up Player {player_id + 1}: {e}")
        finally:
            if gamepad is not None:
                gamepad.close()

    if is_running: # Só salva se a pessoa não apertou Stop no meio do caminho
        with open(PATH_JSON, 'w') as json_file:
            json.dump(all_profiles, json_file, indent=4)
        print(f"Path saved in {PATH_JSON}")
        print("\nAll connected controllers calibrated!")
        print("Profiles saved as 'profiles.json'. You can now press Start Translator")
    else:
        print("\nCalibration stopped by user.")