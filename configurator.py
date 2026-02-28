import hid
import time
import json
from controllerGetter import detect_controllers

# Botões que queremos mapear
BUTTONS_TO_MAP = ['up', 'down', 'left', 'right', 'A', 'B', 'X', 'Y', 'L', 'R', 'select', 'start']

def start_multiplayer_calibration():
    print("=======================================")
    print("  Universal Multiplayer Calibration  ")
    print("=======================================\n")

    # 1. Encontra os controles conectados
    controllers = detect_controllers()
    if not controllers:
        print("No controllers found. Please connect them and try again.")
        return

    # Limita a 2 jogadores
    controllers_to_map = controllers[:2]
    all_profiles = []

    # 2. Loop para mapear cada jogador conectado
    for player_id, target_controller in enumerate(controllers_to_map):
        print(f"\n--- SETTING UP PLAYER {player_id + 1} ---")
        print(f"Device: {target_controller['name']}")
        
        try:
            gamepad = hid.device()
            gamepad.open_path(target_controller['path'])
            gamepad.set_nonblocking(True)
            
            print("Please DO NOT touch any buttons on this controller.")
            print("Reading idle state in 3 seconds...\n")
            time.sleep(3)

            # Lê o estado de descanso
            idle_state = []
            for _ in range(10):
                data = gamepad.read(64)
                if data:
                    idle_state = data
                time.sleep(0.05)
                
            if not idle_state:
                print(f"Failed to read data for Player {player_id + 1}. Skipping.")
                continue

            print(f"Player {player_id + 1} Idle state captured!\n")
            
            player_profile = {}

            # Loop de Calibragem para este jogador
            for button in BUTTONS_TO_MAP:
                print(f"[PLAYER {player_id + 1}] PRESS AND HOLD: [{button.upper()}]")
                
                button_data = None
                
                # Espera o botão ser pressionado
                while True:
                    current_data = gamepad.read(64)
                    if current_data and current_data != idle_state:
                        for index in range(len(idle_state)):
                            if current_data[index] != idle_state[index]:
                                # Matemática mágica (XOR)
                                changed_mask = current_data[index] ^ idle_state[index]
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

                print(f"[{button.upper()}] mapped successfully!")
                print(f"RELEASE the button and wait...")
                
                # Espera o botão ser solto
                while True:
                    current_data = gamepad.read(64)
                    if current_data == idle_state:
                        time.sleep(0.5)
                        break
                    time.sleep(0.01)
                    
                print("-" * 30)

            # Adiciona o perfil deste jogador à lista principal
            all_profiles.append(player_profile)

        except Exception as e:
            print(f"Error setting up Player {player_id + 1}: {e}")
        finally:
            if 'gamepad' in locals():
                gamepad.close()

    # 3. Salva TODOS os perfis em um único arquivo de lista
    with open('profiles.json', 'w') as json_file:
        json.dump(all_profiles, json_file, indent=4)
        
    print("\nAll connected controllers calibrated!")
    print("Profiles saved as 'profiles.json'. You can now run translator.py.")

if __name__ == "__main__":
    start_multiplayer_calibration()