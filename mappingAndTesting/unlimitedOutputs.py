import hid
import time

# Estes são os IDs exatos da imagem que enviou
VENDOR_ID = 0x0810
PRODUCT_ID = 0x0001

print(f"Searching for the gamepad (VID: {hex(VENDOR_ID)}, PID: {hex(PRODUCT_ID)})...")

try:
    # Inicializa o dispositivo
    gamepad = hid.device()
    gamepad.open(VENDOR_ID, PRODUCT_ID)
    
    # Ativa o modo não-bloqueante para o loop correr suavemente
    gamepad.set_nonblocking(True)
    
    print("Success! Now your gamepad is a keyboard")

    while True:
        # Lê o pacote de dados do comando (geralmente entre 8 a 64 bytes)
        report = gamepad.read(64)
        
        if report:
            # Imprime no ecrã a lista de números recebida
            print(f"Data: {report}")
        
        # Uma pequena pausa de 10 milissegundos para não sobrecarregar o processador
        time.sleep(0.01)

except IOError as ex:
    print(f"Error: Controller not found. {ex}")
except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    if 'gamepad' in locals():
        gamepad.close()
        