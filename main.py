import sys
import threading
from pathlib import Path
import customtkinter as ctk
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines import configurator
from engines import translator

# -------------------------------------------------------------
# Classe que Redireciona os 'prints' do terminal para a UI
# -------------------------------------------------------------
class ConsoleRedirector:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        # Insere o texto na caixa e rola para baixo automaticamente
        self.textbox.insert(ctk.END, text)
        self.textbox.see(ctk.END)

    def flush(self):
        pass # Necessário para o sys.stdout funcionar

# -------------------------------------------------------------
# FUNÇÕES DE SEGUNDO PLANO (THREADS)
# -------------------------------------------------------------
# Estas funções impedem que o aplicativo trave quando o loop começa!
def start_configurator_thread():
    print("Starting Configuration...")
    # Executa a função do seu backend num processo paralelo
    # IMPORTANTE: Altere 'start_multiplayer_calibration' para o nome exato da função principal do seu configurator.py
    thread = threading.Thread(target=configurator.start_multiplayer_calibration, daemon=True)
    thread.start()

def start_translator_thread():
    print("Starting Translation Engine (Play!)...")
    # IMPORTANTE: Altere para a função que inicia o loop no seu translator.py
    thread = threading.Thread(target=translator.start_translator, daemon=True) 
    thread.start()

# -------------------------------------------------------------
# A INTERFACE GRÁFICA (FRONTEND)
# -------------------------------------------------------------
# Configuração do visual moderno
ctk.set_appearance_mode("System")  # Segue o modo claro/escuro do macOS
ctk.set_default_color_theme("blue")

# Cria a Janela Principal
app = ctk.CTk()
app.title("Universal Controller Translator")
app.geometry("800x450")
app.resizable(False, False)
# Center the window
app.eval('tk::PlaceWindow . center')

# Título
title_label = ctk.CTkLabel(app, text="Universal Gamepad", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=(20, 5))

subtitle_label = ctk.CTkLabel(app, text="Connect your generic controller and play on Mac", text_color="gray")
subtitle_label.pack(pady=(0, 20))

# Frame dos Botões
button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=10)

def stop_processes():
    print("Stop everything")
    # Muda a variável global nos dois arquivos para encerrar os loops
    configurator.is_running = False
    translator.is_running = False

# Botão de Configurar (Calibrar)
btn_config = ctk.CTkButton(
    button_frame, 
    text="Calibrate Controllers", 
    width=200, 
    height=40,
    command=start_configurator_thread
)
btn_config.grid(row=0, column=0, padx=10)

# Botão de Rodar (Jogar)
btn_run = ctk.CTkButton(
    button_frame, 
    text="Start Translator", 
    width=200, 
    height=40,
    fg_color="#28a745", # Cor verde
    hover_color="#218838",
    command=start_translator_thread
)
btn_run.grid(row=0, column=1, padx=10)

# Botão para Parar
btn_stop = ctk.CTkButton(
    button_frame, 
    text="Stop", 
    width=130, 
    height=40,
    fg_color="#dc3545", # Vermelho
    hover_color="#c82333",
    command=stop_processes
)
btn_stop.grid(row=0, column=2, padx=10)

# A Caixa de "Console" para ver o que os motores estão fazendo
console_label = ctk.CTkLabel(app, text="System Console:")
console_label.pack(anchor="w", padx=20, pady=(20, 0))

console_box = ctk.CTkTextbox(app, width=560, height=150, corner_radius=8, state="normal")
console_box.pack(padx=20, pady=5)
console_box.configure(font=ctk.CTkFont(family="Courier", size=12))

# Ativa o redirecionamento dos prints para a caixa de texto!
sys.stdout = ConsoleRedirector(console_box)

# Inicia o loop da interface gráfica
if __name__ == "__main__":
    print("System ready. Choose an option above.")
    app.mainloop()