import hid
import time
from pynput.keyboard import Controller, Key

# IDs do seu controle chinês
VENDOR_ID = 0x0810
PRODUCT_ID = 0x0001

# Cria o nosso teclado virtual
teclado = Controller()

# ---------------------------------------------------------
# 1. MAPA DE TECLAS: O que o controle vai simular no teclado?
# Mude as letras abaixo para as que você configurou no Delta.
# ---------------------------------------------------------
MAPA_TECLAS = {
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
estado_atual = {botao: False for botao in MAPA_TECLAS}
estado_anterior = {botao: False for botao in MAPA_TECLAS}

def processar_inputs(report):
    if not report:
        return

    # A. Lê as Setinhas (Índices 3 e 4)
    estado_atual['left']  = (report[3] == 0)
    estado_atual['right'] = (report[3] == 255)
    estado_atual['up']    = (report[4] == 0)
    estado_atual['down']  = (report[4] == 255)

    # B. Lê os Botões de Ação (Índice 5)
    # Usamos o operador "&" (Bitwise AND) para checar se o valor do botão está dentro do número misturado
    estado_atual['X'] = bool(report[5] & 16)
    estado_atual['A'] = bool(report[5] & 32)
    estado_atual['B'] = bool(report[5] & 64)
    estado_atual['Y'] = bool(report[5] & 128)

    # C. Lê os Botões Menu e Ombro (Índice 6)
    estado_atual['L'] = bool(report[6] & 1)
    estado_atual['R'] = bool(report[6] & 2)
    estado_atual['select'] = bool(report[6] & 16)
    estado_atual['start'] = bool(report[6] & 32)

    # D. A Mágica de Pressionar e Soltar Teclas!
    for botao, esta_pressionado in estado_atual.items():
        tecla_virtual = MAPA_TECLAS[botao]

        # Se eu apertei agora (está pressionado, mas não estava antes)
        if esta_pressionado and not estado_anterior[botao]:
            teclado.press(tecla_virtual)
            print(f"[{botao}] Pressionado -> Tecla '{tecla_virtual}'")
        
        # Se eu soltei agora (não está pressionado, mas estava antes)
        elif not esta_pressionado and estado_anterior[botao]:
            teclado.release(tecla_virtual)
            print(f"[{botao}] Solto")
        
        # Atualiza a memória para o próximo ciclo
        estado_anterior[botao] = esta_pressionado

# ---------------------------------------------------------
# 3. O LOOP PRINCIPAL
# ---------------------------------------------------------
print("Iniciando o Tradutor de Controle...")

try:
    gamepad = hid.device()
    gamepad.open(VENDOR_ID, PRODUCT_ID)
    gamepad.set_nonblocking(True)
    
    print("Sucesso! O seu controle agora é um teclado.")

    while True:
        dados = gamepad.read(64)
        if dados:
            processar_inputs(dados)
        time.sleep(0.005) # Loop bem rápido para não ter "lag" no jogo

except IOError as ex:
    print(f"Erro: Não encontrei o controle. {ex}")
except KeyboardInterrupt:
    print("\nPrograma encerrado.")
finally:
    if 'gamepad' in locals():
        gamepad.close()