from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QMessageBox, QFrame)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt

class ObservacaoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.status_anterior = self.create_text_field("1) Status Anterior:", layout)
        self.foi_feito = self.create_text_field("2) O que foi feito:", layout)
        self.proximos_passos = self.create_text_field("3) Próximos passos:", layout)

        self.setup_tab_navigation([
            self.status_anterior, self.foi_feito, self.proximos_passos
        ])

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button("Limpar", self.limpar_campos))
        button_layout.addWidget(self.create_button("Formatar", self.formatar_observacao))
        button_layout.addWidget(self.create_button("Formatar & Copiar", self.formatar_e_copiar))
        layout.addLayout(button_layout)

        self.output = self.create_output_field(layout)

    def create_text_field(self, label_text: str, parent_layout: QVBoxLayout) -> QTextEdit:
        parent_layout.addWidget(QLabel(label_text))
        text_field = QTextEdit()
        text_field.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        text_field.setMinimumHeight(100)
        text_field.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid gray;
                padding: 5px;
            }
        """)
        parent_layout.addWidget(text_field)
        return text_field

    def create_button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                color: white;
                background-color: red;
                border: none;
                border-radius: 10px;
                padding: 2px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
            QPushButton:pressed {
                background-color: firebrick;
            }
        """)
        return button

    def create_output_field(self, parent_layout: QVBoxLayout) -> QTextEdit:
        output = QTextEdit()
        output.setReadOnly(True)
        output.setMinimumHeight(200)
        output.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid gray;
                padding: 5px;
            }
        """)
        parent_layout.addWidget(output)
        return output

    def setup_tab_navigation(self, fields: list[QTextEdit]):
        for i, field in enumerate(fields):
            next_field = fields[(i + 1) % len(fields)]
            field.keyPressEvent = self.create_tab_handler(field, next_field)

    def create_tab_handler(self, current_field, next_field):
        original_handler = current_field.keyPressEvent

        def handler(event):
            if event.key() == Qt.Key.Key_Tab:
                next_field.setFocus()
            else:
                original_handler(event)

        return handler

    def limpar_campos(self):
        for field in [self.status_anterior, self.foi_feito, self.proximos_passos, self.output]:
            field.clear()

    def formatar_observacao(self):
        status = self.status_anterior.toPlainText().strip()
        feito = self.foi_feito.toPlainText().strip()
        proximos = self.proximos_passos.toPlainText().strip()

        if not any([status, feito, proximos]):
            QMessageBox.warning(self, "Aviso", "Por favor, preencha ao menos um campo!")
            return

        formatted_text = (
            f"====== STATUS ANTERIOR ======\n{status}\n\n"
            f"====== O QUE FOI FEITO ======\n{feito}\n\n"
            f"====== PRÓXIMOS PASSOS ======\n{proximos}"
        )

        self.output.setPlainText(formatted_text)
        return formatted_text

    def formatar_e_copiar(self):
        formatted_text = self.formatar_observacao()
        if formatted_text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(formatted_text)
            QMessageBox.information(self, "Sucesso", "Texto copiado para a área de transferência!")
