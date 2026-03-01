import sys
import os
import threading
from pathlib import Path
import customtkinter as ctk

# Adiciona o diretório pai ao path para importar as engines
sys.path.insert(0, str(Path(__file__).parent.parent))

# Tenta importar as engines. Se falhar, cria mocks para a UI abrir e testar o visual.
try:
    from engines import configurator
    from engines import translator
    ENGINES_LOADED = True
    
    # A FONTE DA VERDADE: O frontend usa EXATAMENTE o mesmo caminho que o backend gerou
    PATH_JSON = configurator.PATH_JSON 
    
except ImportError:
    print("WARNING: Engines not found. Running UI test only mode.")
    ENGINES_LOADED = False
    PATH_JSON = "profiles.json" # Caminho falso para modo de teste
    
    class MockEngine:
        is_running = False
        def start_multiplayer_calibration(self): pass
        def start_translator(self): pass
    configurator = MockEngine()
    translator = MockEngine()

# -------------------------------------------------------------
# PALETA DE CORES RETRO & FONTES
# -------------------------------------------------------------
BG_COLOR = "#080808"       # Preto Fundo
PANEL_BG = "#141414"       # Cinza Painel
FG_GREEN = "#39ff14"       # Verde Neon
FG_RED = "#ff003c"         # Vermelho Neon
FG_CYAN = "#00f3ff"        # Ciano Neon
FG_YELLOW = "#ffe600"      # Amarelo Alerta
FG_GRAY = "#888888"        # Cinza Texto

try:
    FONT_FAMILY = "Courier New" 
except:
    FONT_FAMILY = "Courier"

# -------------------------------------------------------------
# PARSER DO TERMINAL (O Cérebro Visual)
# -------------------------------------------------------------
class RetroTerminalParser:
    """Intercepta os prints e decide onde mostrá-los na nova UI."""
    def __init__(self, app_gui):
        self.app_gui = app_gui
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self.process_line(line.strip())

    def flush(self):
        pass

    def process_line(self, line):
        if not line: return

        # 1. LOG GERAL
        self.app_gui.after(0, self.app_gui.add_to_system_log, line)

        # 2. CAPTURA DE ERROS (Libera a interface se der erro)
        if "not found!" in line or "Error:" in line:
            self.app_gui.is_busy = False
            self.app_gui.after(0, self.app_gui.show_action_screen, "FILE MISSING", FG_RED)
            
        elif "Please run 'Calibrate" in line:
            self.app_gui.is_busy = False
            self.app_gui.after(0, self.app_gui.show_action_screen, "MUST CALIBRATE", FG_YELLOW)

        # 3. AÇÃO IMEDIATA (Comandos normais)
        elif "PRESS AND HOLD" in line:
            button = line.split("[")[-1].replace("]", "")
            self.app_gui.after(0, self.app_gui.show_action_screen, f"HOLD: {button}", FG_YELLOW)
            
        elif "RELEASE the button" in line:
            self.app_gui.after(0, self.app_gui.show_action_screen, "RELEASE NOW", FG_CYAN)
            
        elif "Idle state captured" in line:
            self.app_gui.after(0, self.app_gui.show_action_screen, "IDLE OK", FG_GREEN)
            
        elif "All connected controllers calibrated" in line:
            self.app_gui.is_busy = False # Libera a interface ao terminar a calibração
            self.app_gui.after(0, self.app_gui.show_action_screen, "CALIBRATION DONE", FG_GREEN)

        elif "Starting Configuration" in line:
            self.app_gui.after(0, self.app_gui.update_sidebar_status, "CALIBRATING...", FG_CYAN)
            self.app_gui.after(0, self.app_gui.show_action_screen, "INITIALIZING...", FG_GRAY)

        elif "Starting Universal" in line:
             self.app_gui.after(0, self.app_gui.update_sidebar_status, "ACTIVE - RUNNING", FG_GREEN)
             self.app_gui.after(0, self.app_gui.show_action_screen, "AWAITING INPUT", FG_GRAY)

        elif "Pressed ->" in line:
            parts = line.split("Pressed")
            btn_info = parts[0].strip() 
            self.app_gui.after(0, self.app_gui.show_action_screen, f"{btn_info} INPUT", FG_GREEN)

        elif "stopped" in line.lower() and "calib" not in line.lower():
             self.app_gui.is_busy = False # Libera a interface ao apertar Stop
             self.app_gui.after(0, self.app_gui.show_action_screen, "SYSTEM HALTED", FG_RED)


# -------------------------------------------------------------
# FRONTEND CLASS
# -------------------------------------------------------------
class UniversalGamepadUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Variável exclusiva do Frontend para controlar se ele está ocupado ---
        self.is_busy = False 
        
        self.title("Universal Controller HUB")
        self.geometry("850x550") 
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        self.center_window()
        self.setup_layout()
        
        sys.stdout = RetroTerminalParser(self)
        
        print("--- SYSTEM BOOT SEQUENCE INITIATED ---")
        print(f"OS detected: {sys.platform}")
        print(f"Targeting profile path: {PATH_JSON}")
        
        # Inicia o Heartbeat (Monitoramento contínuo do arquivo)
        self.check_system_health()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=260) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # ================== SIDEBAR (ESQUERDA) ==================
        self.sidebar = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, border_width=2, border_color="#222222")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        title_lbl = ctk.CTkLabel(
            self.sidebar, 
            text="UNIVERSAL\nCONTROLLER\n[HUB v2.1]", 
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=FG_GREEN, justify="left"
        )
        title_lbl.pack(pady=(20, 15), padx=20, anchor="w")

        # Caixa de Status do Sistema
        self.status_box = ctk.CTkFrame(self.sidebar, fg_color="#0a0a0a", border_width=2, border_color=FG_GRAY, corner_radius=0)
        self.status_box.pack(fill="x", padx=15, pady=(0, 20))
        
        self.status_indicator = ctk.CTkLabel(
            self.status_box, text="STATUS: CHECKING...", 
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=FG_GRAY
        )
        self.status_indicator.pack(pady=10)

        btn_style = {
            "font": ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            "height": 45, 
            "corner_radius": 0,
            "border_width": 2,
            "fg_color": "transparent"
        }

        self.btn_calib = ctk.CTkButton(
            self.sidebar, text="[1] CALIBRATE INPUTS", 
            command=self.run_calibrator, 
            border_color=FG_CYAN, text_color=FG_CYAN, hover_color="#002222",
            **btn_style
        )
        self.btn_calib.pack(fill="x", padx=15, pady=(10, 15)) 

        self.btn_start = ctk.CTkButton(
            self.sidebar, text="[2] ENGAGE TRANSLATOR", 
            command=self.run_translator,
            border_color=FG_GREEN, text_color=FG_GREEN, hover_color="#002200",
             state="disabled", 
            **btn_style
        )
        self.btn_start.pack(fill="x", padx=15, pady=(0, 15))

        self.btn_halt = ctk.CTkButton(
            self.sidebar, text="/// EMERGENCY HALT ///", 
            command=self.emergency_stop,
            border_color=FG_RED, text_color=FG_RED, hover_color="#220000",
            **btn_style
        )
        self.btn_halt.pack(side="bottom", fill="x", padx=15, pady=20)

        # ================== MONITORES (DIREITA) ==================
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.right_panel.grid_rowconfigure(0, weight=4) 
        self.right_panel.grid_rowconfigure(1, weight=2)
        self.right_panel.grid_columnconfigure(0, weight=1) 

        self.log_frame = ctk.CTkFrame(self.right_panel, fg_color=PANEL_BG, border_width=2, border_color=FG_GRAY, corner_radius=0)
        self.log_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        log_title = ctk.CTkLabel(self.log_frame, text="> SYSTEM LOG FEED", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=FG_GRAY, anchor="w")
        log_title.pack(fill="x", padx=5, pady=2)

        self.log_box = ctk.CTkTextbox(
            self.log_frame, fg_color="#0a0a0a", text_color=FG_GREEN,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            corner_radius=0, activate_scrollbars=True
        )
        self.log_box.pack(fill="both", expand=True, padx=2, pady=2)
        self.log_box.configure(state="disabled") 

        self.action_frame = ctk.CTkFrame(self.right_panel, fg_color="#000000", border_width=3, border_color=FG_CYAN, corner_radius=0)
        self.action_frame.grid(row=1, column=0, sticky="nsew")
        self.action_frame.pack_propagate(False) 

        self.action_label = ctk.CTkLabel(
            self.action_frame, text="STANDBY MODE",
            font=ctk.CTkFont(family=FONT_FAMILY, size=28, weight="bold"), 
            text_color=FG_GRAY
        )
        self.action_label.place(relx=0.5, rely=0.5, anchor="center")

    # -------------------------------------------------------------
    # LÓGICA DE UPDATE DA UI (Heartbeat System 2.0)
    # -------------------------------------------------------------
    def check_system_health(self):
        """Monitora o arquivo baseando-se no estado exclusivo da UI."""
        # Se você clicou em algum botão e a interface assumiu que está ocupada, 
        # ela pausa a atualização visual para não piscar no meio do jogo.
        if not self.is_busy:
            if os.path.exists(PATH_JSON):
                self.update_sidebar_status("SYSTEM READY", FG_GREEN)
                self.status_box.configure(border_color=FG_GREEN)
                self.btn_start.configure(state="normal", fg_color="transparent", text_color=FG_GREEN, border_color=FG_GREEN)
                self.btn_calib.configure(fg_color="transparent", text_color=FG_CYAN, border_color=FG_CYAN)
            else:
                self.update_sidebar_status("CALIBRATION REQUIRED", FG_YELLOW)
                self.status_box.configure(border_color=FG_YELLOW)
                self.btn_start.configure(state="disabled", border_color=FG_GRAY, text_color=FG_GRAY)
                self.btn_calib.configure(fg_color="#222200", border_color=FG_YELLOW, text_color=FG_YELLOW)
        
        # Chama a si mesmo a cada 1 segundo indefinidamente
        self.after(1000, self.check_system_health)

    def update_sidebar_status(self, text, color):
        self.status_indicator.configure(text=f"STATUS: {text}", text_color=color)

    def add_to_system_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{text}\n")
        self.log_box.see("end") 
        self.log_box.configure(state="disabled")

    def show_action_screen(self, text, color):
        self.action_label.configure(text=text, text_color=color)

    # -------------------------------------------------------------
    # COMANDOS (THREADS)
    # -------------------------------------------------------------
    def run_calibrator(self):
        if not ENGINES_LOADED: return
        self.is_busy = True # Informa a UI que agora o usuário está fazendo algo
        print("\n>>> INITIALIZING CALIBRATION THREAD <<<")
        thread = threading.Thread(target=configurator.start_multiplayer_calibration, daemon=True)
        thread.start()

    def run_translator(self):
        if not ENGINES_LOADED: return
        
        if not os.path.exists(PATH_JSON):
            print("WARNING: Refusing to start. profiles.json is missing.")
            self.show_action_screen("MISSING DATA", FG_RED)
            return

        self.is_busy = True # Informa a UI que o jogo começou
        print("\n>>> INITIALIZING TRANSLATOR THREAD <<<")
        thread = threading.Thread(target=translator.start_translator, daemon=True)
        thread.start()

    def emergency_stop(self):
        print("\n!!! EMERGENCY STOP SIGNAL SENT !!!")
        self.is_busy = False # Libera a UI de volta para o modo ocioso
        if ENGINES_LOADED:
            # Envia o sinal para o seu backend parar os loops "while"
            configurator.is_running = False
            translator.is_running = False
        self.show_action_screen("STOPPING...", FG_RED)

if __name__ == "__main__":
    app = UniversalGamepadUI()
    app.mainloop()