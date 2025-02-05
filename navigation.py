from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, QScrollArea, QLabel
from PyQt6.QtCore import Qt
from utils import create_scrollable_area
from observacao import ObservacaoWidget
from fechamento import Fechamento
from calculadora_subrede import CalculadoraSubredeWidget
from codigos_sip import CodigosSIPWidget
from telefonia import TelefoniaWidget
from coleta_logs_telefonia import ColetaDeLogsWidget
from troubleshooting import TroubleshootingWidget
#from scripts import ScriptWidget
#from treinamentos import TreinamentosWidget
from PyQt6.QtGui import QPixmap, QIcon  # Import QIcon
from certidao import CertidaoWidget 

import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class NavigationWindow(QMainWindow):
    def __init__(self, window_type: str):
        super().__init__()
        self.setWindowTitle("LoogTools")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui(window_type)

    def init_ui(self, window_type: str):
        # Definir o ícone da janela
        icon_path = os.path.join('icones', 'global_hitss_logo.png')
        self.setWindowIcon(QIcon(resource_path(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Adicionar o Banner:
        banner_path = os.path.join('icones', 'global_hitss_banner.png')  # Ajustado para 'icones'
        banner_pixmap = QPixmap(resource_path(banner_path))
        banner_label = QLabel()
        banner_label.setPixmap(banner_pixmap.scaledToWidth(250))
        banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(banner_label)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        button_style = """
            QPushButton {
                color: white;
                background-color: red;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
            QPushButton:pressed {
                background-color: firebrick;
            }
        """

        back_button = QPushButton("Voltar ao Menu")
        back_button.setStyleSheet(button_style)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.load_tabs(window_type)

    def load_tabs(self, window_type: str):
        tab_loaders = {
            "cpe_gat": self.load_cpe_gat_tabs,
            #"treinamentos": self.load_treinamentos_tabs,
            #"scripts": self.load_scripts_tabs,
            "telefonia": self.load_telefonia_tabs,
            "troubleshooting": self.load_troubleshooting_tabs
        }

        loader = tab_loaders.get(window_type)
        if loader:
            loader()
        else:
            raise ValueError(f"Tipo de janela desconhecido: {window_type}")

    def load_cpe_gat_tabs(self):
        self.add_tab(ObservacaoWidget(), "Observação")
        self.add_tab(Fechamento(), "Fechamento")
        self.add_tab(CertidaoWidget(), "Teste de Certidão")
        self.add_tab(CalculadoraSubredeWidget(), "Calculadora de Sub-rede")
        self.add_tab(CodigosSIPWidget(), "Códigos SIP")  
    #def load_scripts_tabs(self):
       # self.add_tab(ScriptWidget(), "Scripts")  # Nova função para carregar a aba de scripts

    #def load_treinamentos_tabs(self):
        #self.add_tab(TreinamentosWidget(), "Treinamentos")

    def load_telefonia_tabs(self):
        self.add_tab(TelefoniaWidget(), "Telefonia")
        self.add_tab(ColetaDeLogsWidget(), "Coleta de Logs")
        self.add_tab(CodigosSIPWidget(), "Códigos SIP")
        

    def load_troubleshooting_tabs(self):
        self.add_tab(TroubleshootingWidget(), "Troubleshooting")

    def add_tab(self, widget: QWidget, title: str):
        scroll_area = create_scrollable_area(widget)
        self.tab_widget.addTab(scroll_area, title)

    def go_back(self):
        from main import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()