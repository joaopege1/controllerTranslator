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
	
	print("Connected!")

	# Guarda o último estado do comando (começa vazio)
	last_report = None

	# Agora isso é uma LISTA de verdade (sem aspas!)
	static_report = [1, 128, 128, 127, 127, 15, 0, 0]

	while True:
		# Lê o pacote de dados do comando
		report = gamepad.read(64)
		
		# Se recebeu dados E esses dados forem diferentes dos últimos que vimos:
		if report and report != last_report:
			
			# Compara lista com lista!
			if report == static_report:
				print("(No Button Pressed)")
			else:
				print(f"(REPORT) Button Pressed: {report}")
			
			# Atualiza a nossa "memória" com o novo estado
			last_report = report
		
		# Uma pequena pausa para não fritar o processador do Mac
		time.sleep(0.01)
		
except IOError as ex:
    print(f"Error: Controller not found. {ex}")
except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    if 'gamepad' in locals():
        gamepad.close()
