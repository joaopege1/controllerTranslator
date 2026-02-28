import hid
import time
from pynput.keyboard import Controller, Key
from controllerGetter import detectar_controle_automaticamente

# ---------------------------------------------------------
# 1. SETUP: Criação do teclado virtual e Mapa de Teclas
# ---------------------------------------------------------
keyboard_controller = Controller()

KEY_MAP = {
    'up': 'w',
    'down': 's',
    'left': 'a',
    'right': 'd',
    'A': 'l',
    'B': 'k',
    'X': 'i',
    'Y': 'j',
    'L': 'q',
    'R': 'e',
    'start': Key.enter,
    'select': Key.space
}

# ---------------------------------------------------------
# 2. MEMÓRIA: Guarda o que está apertado e o que não está
# ---------------------------------------------------------
current_state = {button: False for button in KEY_MAP}
previous_state = {button: False for button in KEY_MAP}

def process_inputs(report):
    if not report:
        return

    # A. Lê as Setinhas
    current_state['left']  = (report[3] == 0)
    current_state['right'] = (report[3] == 255)
    current_state['up']    = (report[4] == 0)
    current_state['down']  = (report[4] == 255)

    # B. Lê os Botões de Ação
    current_state['X'] = bool(report[5] & 16)
    current_state['A'] = bool(report[5] & 32)
    current_state['B'] = bool(report[5] & 64)
    current_state['Y'] = bool(report[5] & 128)

    # C. Lê os Botões Menu e Ombro
    current_state['L'] = bool(report[6] & 1)
    current_state['R'] = bool(report[6] & 2)
    current_state['select'] = bool(report[6] & 16)
    current_state['start'] = bool(report[6] & 32)

    # D. A Mágica de Pressionar e Soltar Teclas (COM HOLD FORÇADO)
    for button, is_pressed in current_state.items():
        virtual_key = KEY_MAP[button]

        # SE O BOTÃO ESTIVER APERTADO
        if is_pressed:
            keyboard_controller.press(virtual_key)
            if not previous_state[button]:
                print(f"[{button}] Pressed -> Key '{virtual_key}'")
        
        # Se eu soltei agora
        elif not is_pressed and previous_state[button]:
            keyboard_controller.release(virtual_key)
            print(f"[{button}] Released")
        
        # Atualiza a memória
        previous_state[button] = is_pressed

# ---------------------------------------------------------
# 3. O LOOP PRINCIPAL
# ---------------------------------------------------------
print("Starting Controller Translator...")

try:
    # 1. Busca os IDs usando o SEU arquivo externo!
    VENDOR_ID, PRODUCT_ID = detect_controllers()
    
    # Se não achou, encerra o programa graciosamente
    if VENDOR_ID is None or PRODUCT_ID is None:
        print("Finishing the program. Try connecting the controller and try again.")
        exit()

    # 2. Conecta usando os IDs dinâmicos
    gamepad = hid.device()
    gamepad.open(VENDOR_ID, PRODUCT_ID)
    gamepad.set_nonblocking(True)
    
    print("Success! Your controller is now a keyboard.")

    # 3. Inicia a escuta do controle
    while True:
        data = gamepad.read(64)
        if data:
            process_inputs(data)
        time.sleep(0.005)

except IOError as ex:
    print(f"Error: Controller not found. {ex}")
except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    if 'gamepad' in locals():
        gamepad.close()