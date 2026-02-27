import hid
import time

# Estes são os IDs exatos tirados da UBS Device Tree em System Information. (USB GAMEPAD)
VENDOR_ID = 0x0810
PRODUCT_ID = 0x0001

print(f"Searching for the commands (VID: {hex(VENDOR_ID)}, PID: {hex(PRODUCT_ID)})...")

try:
    # Inicializa o dispositivo
    gamepad = hid.device()
    gamepad.open(VENDOR_ID, PRODUCT_ID)
    
    # Ativa o modo não-bloqueante para o loop correr suavemente
    gamepad.set_nonblocking(True)
    
    print("Connected!")

    # Guarda o último estado do comando (começa vazio)
    last_report = None

    while True:
        # Lê o pacote de dados do comando
        report = gamepad.read(64)
        
        # Se recebeu dados E esses dados forem diferentes dos últimos que vimos:
        if report and report != last_report:
            print(f"Estado alterado: {report}")
            
            # Atualiza a nossa "memória" com o novo estado
            last_report = report
        
        # Pausa para não sobrecarregar o processador
        time.sleep(0.01)

except IOError as ex:
    print(f"Erro ao ligar ao comando: {ex}")
    print("Verifique se o comando está ligado à porta USB.")
except KeyboardInterrupt:
    print("\nA encerrar o programa...")
finally:
    # Fecha a ligação de forma segura
    if 'gamepad' in locals():
        gamepad.close()