import hid

def detect_controllers():
    connected_devices = hid.enumerate()
    keywords = ['gamepad', 'joystick', 'controller', 'snes', 'retrolink']
    
    found_controllers = []
    
    for device in connected_devices:
        product_name = device.get('product_string', '')
        if product_name is None:
            continue
            
        product_name = product_name.lower()
        
        # Se achar a palavra-chave, salva o PATH (Caminho Físico)
        if any(word in product_name for word in keywords):
            usb_path = device['path']
            real_name = device.get('product_string', 'Uknown Controller')
            
            # Evita adicionar o mesmo controle duas vezes (as vezes o Mac lista interfaces duplicadas)
            if usb_path not in [c['path'] for c in found_controllers]:
                found_controllers.append({
                    'path': usb_path,
                    'name': real_name
                })
            
    print(f"{len(found_controllers)} controller found!\n")
    return found_controllers
