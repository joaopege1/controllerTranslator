import hid
import time
from pynput.keyboard import Controller, Key

# IDs do seu controle chinês
VENDOR_ID = 0x0810
PRODUCT_ID = 0x0001

# Cria o nosso teclado virtual
keyboard_controller = Controller()

# ---------------------------------------------------------
# 1. MAPA DE TECLAS: O que o controle vai simular no teclado?
# Mude as letras abaixo para as que você configurou no Delta.
# ---------------------------------------------------------
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
    'start': Key.enter,   # Teclas especiais usam o "Key."
    'select': Key.space
}

# ---------------------------------------------------------
# 2. MEMÓRIA: Guarda o que está apertado e o que não está
# ---------------------------------------------------------
# Começamos assumindo que nenhum botão está apertado
current_state = {button: False for button in KEY_MAP}
previous_state = {button: False for button in KEY_MAP}

def process_inputs(report):
    if not report:
        return

    # A. Lê as Setinhas (Índices 3 e 4)
    current_state['left']  = (report[3] == 0)
    current_state['right'] = (report[3] == 255)
    current_state['up']    = (report[4] == 0)
    current_state['down']  = (report[4] == 255)

    # B. Lê os Botões de Ação (Índice 5)
    # Usamos o operador "&" (Bitwise AND) para checar se o valor do botão está dentro do número misturado
    current_state['X'] = bool(report[5] & 16)
    current_state['A'] = bool(report[5] & 32)
    current_state['B'] = bool(report[5] & 64)
    current_state['Y'] = bool(report[5] & 128)

    # C. Lê os Botões Menu e Ombro (Índice 6)
    current_state['L'] = bool(report[6] & 1)
    current_state['R'] = bool(report[6] & 2)
    current_state['select'] = bool(report[6] & 16)
    current_state['start'] = bool(report[6] & 32)

    # D. A Mágica de Pressionar e Soltar Teclas (COM HOLD FORÇADO)
    for button, is_pressed in current_state.items():
        virtual_key = KEY_MAP[button]

        # SE O BOTÃO ESTIVER APERTADO (Não importa se foi agora ou antes)
        if is_pressed:
            # Continua enviando o sinal de "pressionado" repetidas vezes
            keyboard_controller.press(virtual_key)
            
            # Imprime no console apenas na primeira vez para não fludar a tela
            if not previous_state[button]:
                print(f"[{button}] Pressed -> Key '{virtual_key}'")
        
        # Se eu soltei agora (não está pressionado, mas estava antes)
        elif not is_pressed and previous_state[button]:
            keyboard_controller.release(virtual_key)
            print(f"[{button}] Released")
        
        # Atualiza a memória para o próximo ciclo
        previous_state[button] = is_pressed

# ---------------------------------------------------------
# 3. O LOOP PRINCIPAL
# ---------------------------------------------------------
print("Starting Controller Translator...")

try:
    gamepad = hid.device()
    gamepad.open(VENDOR_ID, PRODUCT_ID)
    gamepad.set_nonblocking(True)
    
    print("Success! Your controller is now a keyboard.")

    while True:
        data = gamepad.read(64)
        if data:
            process_inputs(data)
        time.sleep(0.005) # Loop bem rápido para não ter "lag" no jogo

except IOError as ex:
    print(f"Error: Controller not found. {ex}")
except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    if 'gamepad' in locals():
        gamepad.close()
