from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QApplication, QMainWindow,
    QWidget, QSpacerItem, QSizePolicy
)
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

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Adicionar o Banner:
        banner_path = os.path.join('icones', 'global_hitss_banner.png')  # caminho do banner
        try:
            banner_pixmap = QPixmap(resource_path(banner_path))
            banner_label = QLabel()
            banner_label.setPixmap(banner_pixmap.scaledToWidth(500))
            banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(banner_label)
        except Exception as e:
            print(f"Erro ao carregar banner: {e}")

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
            # "Scripts": os.path.join('icones', 'scripts.png'),
            # "Treinamentos": os.path.join('icones', 'treinamentos.png'),
            "Telefonia": os.path.join('icones', 'telefonia.png'),
            "Troubleshooting": os.path.join('icones', 'troubleshooting.png')
        }

        buttons = {
            "CPE/GAT": self.open_cpe_gat,
            # "Scripts": self.open_scripts,
            # "Treinamentos": self.open_treinamentos,
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

        # Create a horizontal layout for the "About" button and the labels
        bottom_layout = QHBoxLayout()

        # About Button (positioned at the bottom left)
        self.about_button = QPushButton("Sobre")
        self.about_button.clicked.connect(self.show_about_dialog)
        self.about_button.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                color: white;
                background-color: gray;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 70px;
                max-width: 70px;
            }
            QPushButton:hover {
                background-color: darkgray;
            }
            QPushButton:pressed {
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
        for label in [dev_label, version_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: black;
                }
            """)
            labels_layout.addWidget(label)

        # Add the vertical layout to the bottom layout
        bottom_layout.addLayout(labels_layout)

        # Add the bottom layout to the main layout
        layout.addLayout(bottom_layout)


    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()  # Use exec() for modal dialogs

    def open_navigation_window(self, window_type: str):
        try:
            self.nav_window = NavigationWindow(window_type)
            self.nav_window.show()
            self.close()
        except Exception as e:
            print(f"Erro ao abrir janela de navegação: {e}")

    def open_cpe_gat(self):
        self.open_navigation_window("cpe_gat")

    # def open_treinamentos(self):
    # self.open_navigation_window("treinamentos")

    # def open_scripts(self):
    # self.open_navigation_window("scripts")

    def open_telefonia(self):
        self.open_navigation_window("telefonia")

    def open_troubleshooting(self):
        self.open_navigation_window("troubleshooting")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())