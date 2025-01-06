from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
import sys
from navigation import NavigationWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoogTools")
        self.setGeometry(100, 100, 600, 450)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

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

        buttons = {
            "CPE/GAT": self.open_cpe_gat,
            "Telefonia": self.open_telefonia,
            "Troubleshooting": self.open_troubleshooting
        }

        for text, callback in buttons.items():
            button = QPushButton(text)
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
        version_label = QLabel("VERSÃO BETA 0.6.4")
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

    def open_telefonia(self):
        self.open_navigation_window("telefonia")

    def open_troubleshooting(self):
        self.open_navigation_window("troubleshooting")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
