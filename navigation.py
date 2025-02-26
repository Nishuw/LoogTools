# navigation.py
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
from treinamentos import TreinamentosWidget
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
    def __init__(self, window_type: str, dark_mode: bool):
        super().__init__()
        self.setWindowTitle("LoogTools")
        self.setGeometry(100, 100, 800, 600)
        self.dark_mode = dark_mode  # Recebe o estado do modo noturno
        self.banner_path_light = os.path.join('icones', 'global_hitss_banner.png')
        self.banner_path_dark = os.path.join('icones', 'global_hitss_banner_branco.png')
        self.banner_path = self.banner_path_light
        self.init_ui(window_type)

    def init_ui(self, window_type: str):
        # Definir o ícone da janela
        icon_path = os.path.join('icones', 'global_hitss_logo.png')
        self.setWindowIcon(QIcon(resource_path(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.central_widget = central_widget  # Add this line

        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.main_layout = layout

        # Adicionar o Banner:
        self.banner_label = QLabel()
        self.update_banner()  # Carrega o banner inicial
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.banner_label)

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
        self.back_button = back_button  # Armazena o botão de voltar

        self.load_tabs(window_type)
        self.apply_stylesheet()  # Aplica o tema inicial

    def load_tabs(self, window_type: str):
        tab_loaders = {
            "cpe_gat": self.load_cpe_gat_tabs,
            "treinamentos": self.load_treinamentos_tabs,
            # "scripts": self.load_scripts_tabs,
            "telefonia": self.load_telefonia_tabs,
            "troubleshooting": self.load_troubleshooting_tabs
        }

        loader = tab_loaders.get(window_type)
        if loader:
            loader()
        else:
            raise ValueError(f"Tipo de janela desconhecido: {window_type}")

    def load_cpe_gat_tabs(self):
        self.observacao_widget = ObservacaoWidget(dark_mode=self.dark_mode)
        self.fechamento_widget = Fechamento(dark_mode=self.dark_mode)
        self.add_tab(self.observacao_widget, "Observação")
        self.add_tab(self.fechamento_widget, "Fechamento")
        self.add_tab(CertidaoWidget(), "Teste de Certidão")
        self.add_tab(CalculadoraSubredeWidget(), "Calculadora de Sub-rede")
        self.add_tab(CodigosSIPWidget(), "Códigos SIP")

    # def load_scripts_tabs(self):
    # self.add_tab(ScriptWidget(), "Scripts")  # Nova função para carregar a aba de scripts

    def load_treinamentos_tabs(self):
        self.add_tab(TreinamentosWidget(dark_mode=self.dark_mode), "Treinamentos")

    def load_telefonia_tabs(self):
        self.add_tab(TelefoniaWidget(), "Telefonia")
        self.add_tab(ColetaDeLogsWidget(), "Coleta de Logs")
        self.add_tab(CodigosSIPWidget(), "Códigos SIP")

    def load_troubleshooting_tabs(self):
        self.add_tab(TroubleshootingWidget(dark_mode=self.dark_mode), "Troubleshooting")

    def add_tab(self, widget: QWidget, title: str):
        scroll_area = create_scrollable_area(widget)
        self.tab_widget.addTab(scroll_area, title)
        scroll_area.setObjectName(title.replace(' ', '') + "ScrollArea")

    def go_back(self):
        from main import MainWindow
        self.main_window = MainWindow()
        self.main_window.dark_mode = self.dark_mode  # Passa o estado do modo noturno de volta
        self.main_window.apply_stylesheet()  # Reaplicar o tema
        self.main_window.show()
        self.close()

    def apply_stylesheet(self):
        if self.dark_mode:
            stylesheet = """
                QWidget {
                    background-color: #222222;
                    color: #DDDDDD;
                }
                QTextEdit {
                    background-color: #333333;
                    color: #DDDDDD;
                }
                QLineEdit {
                    background-color: #333333;
                    color: #DDDDDD;
                }
                QTreeWidget {
                    background-color: #333333;
                    color: #DDDDDD;
                }
                QTableWidget {
                    background-color: #333333;
                    color: #DDDDDD;
                }
                QPushButton {
                    background-color: #29434e;
                    color: #DDDDDD;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #39535e;
                }
                QPushButton:pressed {
                    background-color: #19333e;
                }
                QRadioButton {
                    color: #DDDDDD;
                }
                QLabel {
                    color: #DDDDDD;
                }
                QComboBox {
                    background-color: #333333;
                    color: #DDDDDD;
                    border: 1px solid #555555; /* Cor da borda para melhor visibilidade */
                }

                QComboBox QAbstractItemView {
                    background-color: #333333;
                    color: #DDDDDD;
                    border: none;
                    outline: 0px;
                }

                QComboBox QAbstractItemView::item {
                    border: none;
                    outline: 0px;
                }
            """
        else:
            stylesheet = ""  # Limpa o estilo para o modo normal

        self.central_widget.setStyleSheet(stylesheet)
        self.update_banner()

        # Chamar update_theme nos widgets ObservacaoWidget e Fechamento
        if hasattr(self, 'observacao_widget') and self.observacao_widget:
            self.observacao_widget.dark_mode = self.dark_mode  # Atualizar o valor de dark_mode
            self.observacao_widget.update_theme()

        if hasattr(self, 'fechamento_widget') and self.fechamento_widget:
            self.fechamento_widget.dark_mode = self.dark_mode  # Atualizar o valor de dark_mode
            self.fechamento_widget.update_theme()

    def update_banner(self):
        if self.dark_mode:
            self.banner_path = self.banner_path_dark
        else:
            self.banner_path = self.banner_path_light
        banner_pixmap = QPixmap(resource_path(self.banner_path))
        self.banner_label.setPixmap(banner_pixmap.scaledToWidth(250))