# main.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QApplication, QMainWindow,
    QWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon, QPixmap
import sys
import os
from navigation import NavigationWindow


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre o LoogTools")
        self.setGeometry(200, 200, 400, 300)  # Ajuste o tamanho conforme necessário

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Readme
        readme_path = resource_path("LEIA-ME.txt")  # Directly use resource_path
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = f.read()
            except Exception as e:
                readme_content = f"Erro ao ler LEIA-ME.txt: {e}"
        else:
            readme_content = "Arquivo LEIA-ME.txt não encontrado."

        self.readme_text = QTextEdit()
        self.readme_text.setReadOnly(True)
        self.readme_text.setPlainText(readme_content)
        layout.addWidget(self.readme_text)

        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoogTools")
        self.setGeometry(100, 100, 550, 540)
        self.dark_mode = False  # Estado do modo noturno
        self.init_ui()

    def init_ui(self):
        # Definir o ícone da janela
        icon_path = os.path.join('icones', 'global_hitss_logo.png')
        try:
            self.setWindowIcon(QIcon(resource_path(icon_path)))
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.central_widget = central_widget

        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.main_layout = layout

        # Adicionar o Banner:
        self.banner_path_light = os.path.join('icones', 'global_hitss_banner.png')
        self.banner_path_dark = os.path.join('icones', 'global_hitss_banner_branco.png')
        self.banner_path = self.banner_path_light  # Inicializa com o banner claro

        try:
            banner_pixmap = QPixmap(resource_path(self.banner_path))
            banner_label = QLabel()
            banner_label.setPixmap(banner_pixmap.scaledToWidth(500))
            banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(banner_label)
        except Exception as e:
            print(f"Erro ao carregar banner: {e}")
        
        self.banner_label = banner_label  # Armazena a referência ao banner

        title_label = QLabel("Escolha uma Opção:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")  # Add object name for styling
        
        self.title_label = title_label  # Armazena a referência ao title_label

        layout.addWidget(title_label)

        # Icons for buttons
        button_icons = {
            "CPE/GAT": os.path.join('icones', 'cpe_gat.png'),
            #"Scripts": os.path.join('icones', 'scripts.png'),
            #"Treinamentos": os.path.join('icones', 'treinamentos.png'),
            "Telefonia": os.path.join('icones', 'telefonia.png'),
            "Troubleshooting": os.path.join('icones', 'troubleshooting.png')
        }

        buttons = {
            "CPE/GAT": self.open_cpe_gat,
            #"Scripts": self.open_scripts,
            #"Treinamentos": self.open_treinamentos,
            "Telefonia": self.open_telefonia,
            "Troubleshooting": self.open_troubleshooting
        }

        for text, callback in buttons.items():
            button = QPushButton(text)
            # Add icons to buttons
            icon_path = button_icons.get(text)
            if icon_path:
                try:
                    button.setIcon(QIcon(resource_path(icon_path)))
                    button.setIconSize(QPixmap(resource_path(icon_path)).size())  # Scale the icon
                except Exception as e:
                    print(f"Erro ao carregar ícone do botão: {e}")

            button.setObjectName(f"{text.replace('/', '_')}Button")
            button.setStyleSheet(f"""
                QPushButton#{text.replace('/', '_')}Button {{
                    font-size: 14pt;
                    color: white;
                    background-color: red;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 50px;
                }}
                QPushButton#{text.replace('/', '_')}Button:hover {{
                    background-color: darkred;
                }}
                QPushButton#{text.replace('/', '_')}Button:pressed {{
                    background-color: firebrick;
                }}
            """)
            button.clicked.connect(callback)
            layout.addWidget(button)

        # Create a horizontal layout for the "About" button and the labels
        bottom_layout = QHBoxLayout()

        # About Button (positioned at the bottom left)
        self.about_button = QPushButton("Sobre")
        self.about_button.clicked.connect(self.show_about_dialog)
        self.about_button.setObjectName("aboutButton")
        self.about_button.setStyleSheet("""
            QPushButton#aboutButton {
                font-size: 10pt;
                color: white;
                background-color: gray;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 70px;
                max-width: 70px;
            }
            QPushButton#aboutButton:hover {
                background-color: darkgray;
            }
            QPushButton#aboutButton:pressed {
                background-color: dimgray;
            }
        """)
        bottom_layout.addWidget(self.about_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        # Add a horizontal spacer item to push the labels to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bottom_layout.addItem(spacer)

        # Create a vertical layout for the labels
        labels_layout = QVBoxLayout()
        labels_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)  # Align labels to bottom-right

        # Labels
        dev_label = QLabel("Desenvolvido por Ryan Nishikawa")
        version_label = QLabel("VERSÃO DO SOFTWARE 1.1.3")
        dev_label.setObjectName("devLabel")
        version_label.setObjectName("versionLabel")

        self.dev_label = dev_label  # Armazena a referência para atualização
        self.version_label = version_label # Armazena a referência para atualização

        for label in [dev_label, version_label]:
            label.setStyleSheet("""
                QLabel#devLabel, QLabel#versionLabel {
                    font-size: 10pt;
                    color: black;
                }
            """)
            labels_layout.addWidget(label)

        # Add the vertical layout to the bottom layout
        bottom_layout.addLayout(labels_layout)

        # Add the bottom layout to the main layout
        layout.addLayout(bottom_layout)

        # Botão de alternância do modo noturno (adicionado aqui)
        self.toggle_dark_mode_button = QPushButton("🌙")  # Ícone inicial: Lua
        self.toggle_dark_mode_button.setCheckable(True) #Definir como checkable
        self.toggle_dark_mode_button.setChecked(False) #Estado inicial
        self.toggle_dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.toggle_dark_mode_button.setStyleSheet("""
            QPushButton {
                font-size: 16pt;
                border: none;
                background-color: transparent;
                color: black;
                padding: 0;
                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:checked {
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1); /* Pequeno realce ao passar o mouse */
            }
        """)
        bottom_layout.addWidget(self.toggle_dark_mode_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.apply_stylesheet() # Garante que o estilo seja aplicado após a criação dos widgets

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()  # Use exec() for modal dialogs

    def open_navigation_window(self, window_type: str):
        try:
            self.nav_window = NavigationWindow(window_type, self.dark_mode)
            self.nav_window.show()
            self.close()
        except Exception as e:
            print(f"Erro ao abrir janela de navegação: {e}")

    def open_cpe_gat(self):
        self.open_navigation_window("cpe_gat")

    #def open_treinamentos(self):
        #self.open_navigation_window("treinamentos")

    #def open_scripts(self):
       #self.open_navigation_window("scripts")

    def open_telefonia(self):
        self.open_navigation_window("telefonia")

    def open_troubleshooting(self):
        self.open_navigation_window("troubleshooting")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_stylesheet()
        # Atualize o texto do botão e o ícone
        if self.dark_mode:
            self.toggle_dark_mode_button.setText("☀️")  # Ícone: Sol
            self.toggle_dark_mode_button.setStyleSheet("""
                QPushButton {
                    font-size: 16pt;
                    border: none;
                    background-color: transparent;
                    color: white;
                    padding: 0;
                    min-width: 30px;
                    max-width: 30px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1); /* Pequeno realce ao passar o mouse */
                }
            """)
        else:
            self.toggle_dark_mode_button.setText("🌙")  # Ícone: Lua
            self.toggle_dark_mode_button.setStyleSheet("""
                QPushButton {
                    font-size: 16pt;
                    border: none;
                    background-color: transparent;
                    color: black;
                    padding: 0;
                    min-width: 30px;
                    max-width: 30px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.1); /* Pequeno realce ao passar o mouse */
                }
            """)


    def apply_stylesheet(self):
        if self.dark_mode:
            self.central_widget.setStyleSheet("""
                QWidget {
                    background-color: #222222;
                    color: #DDDDDD;
                }

                

                QPushButton#CPE_GATButton, QPushButton#TreinamentosButton,
                QPushButton#TelefoniaButton, QPushButton#TroubleshootingButton {
                    background-color: #29434e;
                }

                QPushButton#CPE_GATButton:hover, QPushButton#TreinamentosButton:hover,
                QPushButton#TelefoniaButton:hover, QPushButton#TroubleshootingButton:hover {
                    background-color: #39535e;
                }

                QPushButton#CPE_GATButton:pressed, QPushButton#TreinamentosButton:pressed,
                QPushButton#TelefoniaButton:pressed, QPushButton#TroubleshootingButton:pressed {
                    background-color: #19333e;
                }
                
            """)
            
            # Atualiza o estilo dos labels
            self.dev_label.setStyleSheet("""
                QLabel#devLabel, QLabel#versionLabel{
                    font-size: 10pt;
                    color: #DDDDDD;
                }
            """)
            self.version_label.setStyleSheet("""
                QLabel#devLabel, QLabel#versionLabel{
                    font-size: 10pt;
                    color: #DDDDDD;
                }
            """)
            
            self.title_label.setStyleSheet("""
                QLabel#titleLabel {
                    font-size: 18pt;
                    font-weight: bold;
                    color: #DDDDDD;
                    margin-bottom: 20px;
                }
            """)
            
            # Atualiza o banner
            self.banner_path = self.banner_path_dark
            banner_pixmap = QPixmap(resource_path(self.banner_path))
            self.banner_label.setPixmap(banner_pixmap.scaledToWidth(500))
            
            
        else:
            self.central_widget.setStyleSheet("")  # Reseta para o estilo padrão
            
            # Reseta os estilos dos labels
            self.dev_label.setStyleSheet("""
                QLabel#devLabel, QLabel#versionLabel{
                    font-size: 10pt;
                    color: black;
                }
            """)
            self.version_label.setStyleSheet("""
                QLabel#devLabel, QLabel#versionLabel{
                    font-size: 10pt;
                    color: black;
                }
            """)
            
            self.title_label.setStyleSheet("""
                QLabel#titleLabel {
                    font-size: 18pt;
                    font-weight: bold;
                    color: black;
                    margin-bottom: 20px;
                }
            """)
            
            self.banner_path = self.banner_path_light
            banner_pixmap = QPixmap(resource_path(self.banner_path))
            self.banner_label.setPixmap(banner_pixmap.scaledToWidth(500))
            
            
            
            about_button = self.findChild(QPushButton, "aboutButton")
            if about_button:
                about_button.setStyleSheet("""
                    QPushButton#aboutButton {
                        font-size: 10pt;
                        color: white;
                        background-color: gray;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 10px;
                        min-width: 70px;
                        max-width: 70px;
                    }
                    QPushButton#aboutButton:hover {
                        background-color: darkgray;
                    }
                    QPushButton#aboutButton:pressed {
                        background-color: dimgray;
                    }
                """)

            cpe_button = self.findChild(QPushButton, "CPE_GATButton")
            if cpe_button:
                cpe_button.setStyleSheet("""
                    QPushButton#CPE_GATButton {
                        font-size: 14pt;
                        color: white;
                        background-color: red;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 50px;
                    }
                    QPushButton#CPE_GATButton:hover {
                        background-color: darkred;
                    }
                    QPushButton#CPE_GATButton:pressed {
                        background-color: firebrick;
                    }
                """)
            treinamentos_button = self.findChild(QPushButton, "TreinamentosButton")
            if treinamentos_button:
                treinamentos_button.setStyleSheet("""
                    QPushButton#TreinamentosButton {
                        font-size: 14pt;
                        color: white;
                        background-color: red;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 50px;
                    }
                    QPushButton#TreinamentosButton:hover {
                        background-color: darkred;
                    }
                    QPushButton#TreinamentosButton:pressed {
                        background-color: firebrick;
                    }
                """)
            telefonia_button = self.findChild(QPushButton, "TelefoniaButton")
            if telefonia_button:
                telefonia_button.setStyleSheet("""
                    QPushButton#TelefoniaButton {
                        font-size: 14pt;
                        color: white;
                        background-color: red;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 50px;
                    }
                    QPushButton#TelefoniaButton:hover {
                        background-color: darkred;
                    }
                    QPushButton#TelefoniaButton:pressed {
                        background-color: firebrick;
                    }
                """)
            troubleshooting_button = self.findChild(QPushButton, "TroubleshootingButton")
            if troubleshooting_button:
                troubleshooting_button.setStyleSheet("""
                    QPushButton#TroubleshootingButton {
                        font-size: 14pt;
                        color: white;
                        background-color: red;
                        border: none;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 50px;
                    }
                    QPushButton#TroubleshootingButton:hover {
                        background-color: darkred;
                    }
                    QPushButton#TroubleshootingButton:pressed {
                        background-color: firebrick;
                    }
                """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())