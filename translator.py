import hid
import time
from pynput.keyboard import Controller, Key
from controllerGetter import detect_controllers

keyboard_controller = Controller()

# ---------------------------------------------------------
# 1. MAPAS DE TECLAS (Player 1 e Player 2)
# ---------------------------------------------------------
MAPS_PER_PLAYER = [
    { # PLAYER 1 (Exatamente como você já tinha)
        'up': 'w', 'down': 's', 'left': 'a', 'right': 'd',
        'A': 'l', 'B': 'k', 'X': 'i', 'Y': 'j',
        'L': 'q', 'R': 'e', 'start': Key.enter, 'select': Key.space
    },
    { # PLAYER 2 (Use as setinhas do teclado e outras letras)
        'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
        'A': 'v', 'B': 'c', 'X': 'f', 'Y': 'x',
        'L': '1', 'R': '2', 'start': '3', 'select': '4'
    }
]

# ---------------------------------------------------------
# 2. MEMÓRIA: Separada para cada jogador
# ---------------------------------------------------------
# Cria uma lista com duas "memórias" separadas
current_state = [{button: False for button in mapping} for mapping in MAPS_PER_PLAYER]
previous_state = [{button: False for button in mapping} for mapping in MAPS_PER_PLAYER]

def process_inputs(report, player_id):
    if not report:
        return

    # Pega o mapa e a memória específicos deste jogador
    player_current_state = current_state[player_id]
    player_previous_state = previous_state[player_id]
    key_map = MAPS_PER_PLAYER[player_id]

    # Lê os botões (A lógica matemática é igualzinha!)
    player_current_state['left']  = (report[3] == 0)
    player_current_state['right'] = (report[3] == 255)
    player_current_state['up']    = (report[4] == 0)
    player_current_state['down']  = (report[4] == 255)

    player_current_state['X'] = bool(report[5] & 16)
    player_current_state['A'] = bool(report[5] & 32)
    player_current_state['B'] = bool(report[5] & 64)
    player_current_state['Y'] = bool(report[5] & 128)

    player_current_state['L'] = bool(report[6] & 1)
    player_current_state['R'] = bool(report[6] & 2)
    player_current_state['select'] = bool(report[6] & 16)
    player_current_state['start'] = bool(report[6] & 32)

    # Executa os toques de teclado
    for button, is_pressed in player_current_state.items():
        virtual_key = key_map[button]

        if is_pressed:
            keyboard_controller.press(virtual_key)
            if not player_previous_state[button]:
                print(f"[P{player_id + 1}] {button} Pressed -> Key '{virtual_key}'")
        
        elif not is_pressed and player_previous_state[button]:
            keyboard_controller.release(virtual_key)
            print(f"[P{player_id + 1}] {button} Released")
        
        player_previous_state[button] = is_pressed

# ---------------------------------------------------------
# 3. O LOOP PRINCIPAL MULTIPLAYER
# ---------------------------------------------------------
print("Starting the program")

open_controllers = []

try:
    # 1. Busca todos os controles conectados
    controller_list = detect_controllers()
    
    if not controller_list:
        print("No controllers found.")
        exit()

    # 2. Abre a conexão com cada controle encontrado (Máximo de 2 para bater com nossos mapas)
    for index, controller_info in enumerate(controller_list[:2]):
        gamepad = hid.device()
        gamepad.open_path(controller_info['path']) # Abrindo pelo CAMINHO DA PORTA, não pelo ID!
        gamepad.set_nonblocking(True)
        open_controllers.append(gamepad)
        print(f"Player {index + 1} Connected: {controller_info['name']}")

    print("\nAll done! Lets go!!")

    # 3. O Loop Duplo
    while True:
        # Passa por cada controle aberto e lê os dados
        for player_id, gamepad in enumerate(open_controllers):
            data = gamepad.read(64)
            if data:
                process_inputs(data, player_id)
                
        time.sleep(0.005)

except IOError as ex:
    print(f"Connection error: {ex}")
except KeyboardInterrupt:
    print("\nProgram finished")
finally:
    # Fecha todos os controles com segurança
    for gamepad in open_controllers:
        gamepad.close()

        