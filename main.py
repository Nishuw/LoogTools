from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoogTools")
        self.setGeometry(100, 100, 550, 540)
        self.init_ui()

    def init_ui(self):
        # Definir o ícone da janela
        icon_path = os.path.join('icones', 'global_hitss_logo.png')
        self.setWindowIcon(QIcon(resource_path(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Adicionar o Banner:
        banner_path = os.path.join('icones', 'global_hitss_banner.png')  # caminho do banner
        banner_pixmap = QPixmap(resource_path(banner_path))
        banner_label = QLabel()
        banner_label.setPixmap(banner_pixmap.scaledToWidth(500))
        banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(banner_label)

        title_label = QLabel("Escolha uma Opção:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: black;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)

        # Icons for buttons
        button_icons = {
            "CPE/GAT": os.path.join('icones', 'cpe_gat.png'),
            #"Scripts": os.path.join('icones', 'scripts.png'),
            "Treinamentos": os.path.join('icones', 'treinamentos.png'),
            "Telefonia": os.path.join('icones', 'telefonia.png'),
            "Troubleshooting": os.path.join('icones', 'troubleshooting.png')
        }

        buttons = {
            "CPE/GAT": self.open_cpe_gat,
            #"Scripts": self.open_scripts,
            "Treinamentos": self.open_treinamentos,
            "Telefonia": self.open_telefonia,
            "Troubleshooting": self.open_troubleshooting
        }

        for text, callback in buttons.items():
            button = QPushButton(text)
            # Add icons to buttons
            icon_path = button_icons.get(text)
            if icon_path:
                button.setIcon(QIcon(resource_path(icon_path)))
                button.setIconSize(QPixmap(resource_path(icon_path)).size())  # Scale the icon

            button.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    color: white;
                    background-color: red;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 50px;
                }
                QPushButton:hover {
                    background-color: darkred;
                }
                QPushButton:pressed {
                    background-color: firebrick;
                }
            """)
            button.clicked.connect(callback)
            layout.addWidget(button)

        layout.addStretch()

        dev_label = QLabel("Desenvolvido por Ryan Nishikawa")
        version_label = QLabel("VERSÃO DO SOFTWARE 1.1.2")
        for label in [dev_label, version_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: black;
                    margin-right: 10px;
                }
            """)
            layout.addWidget(label)

    def open_navigation_window(self, window_type: str):
        self.nav_window = NavigationWindow(window_type)
        self.nav_window.show()
        self.close()

    def open_cpe_gat(self):
        self.open_navigation_window("cpe_gat")

    def open_treinamentos(self):
        self.open_navigation_window("treinamentos")

   # def open_scripts(self):
       #self.open_navigation_window("scripts")

    def open_telefonia(self):
        self.open_navigation_window("telefonia")

    def open_troubleshooting(self):
        self.open_navigation_window("troubleshooting")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())