import hid

def detect_controllers():
    print("Scanning Mac USB ports...")
    
    # Lista todos os dispositivos HID conectados
    connected_devices = hid.enumerate()
    
    # Palavras comuns que os fabricantes chineses usam
    keywords = ['gamepad', 'joystick', 'controller', 'snes', 'retrolink']
    
    for device in connected_devices:
        # Pega o nome do produto e converte para minúsculas para facilitar a busca
        product_name = device.get('product_string', '')
        if product_name is None:
            continue
            
        product_name = product_name.lower()
        
        # Se alguma palavra-chave estiver no nome do produto, achamos!
        if any(keyword in product_name for keyword in keywords):
            vid = device['vendor_id']
            pid = device['product_id']
            actual_name = device.get('product_string', 'Unknown Controller')
            
            print(f"Controller detected: {actual_name}")
            print(f"   -> VID: {hex(vid)} | PID: {hex(pid)}\n")
            
            return vid, pid
            
    # Se o loop terminar e não achar nada
    print("No controller found.")
    print("Check if the cable is properly connected.")
    return None, None