from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QButtonGroup, QRadioButton, QMessageBox
)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt

class Fechamento(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.comentario = self.create_text_field("Comentário de Fechamento:", layout, 50)
        self.responsavel = self.create_text_field("Nome do Responsável:", layout, 50)

        self.equip_group = self.create_radio_group("Técnico possui equipamento JDSU ou Wise?", [
            "Sim", "Não", "Cliente não autorizou", "Atividade IPVPN ou Voz", "Projeto Visita única"
        ], layout)

        self.result_group = self.create_radio_group("Resultado do teste:", [
            "Sucesso JDSU", "Falha JDSU", "Sucesso Wise", "Falha Wise"
        ], layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button("Limpar", self.limpar_campos))
        button_layout.addWidget(self.create_button("Formatar", self.formatar_fechamento))
        button_layout.addWidget(self.create_button("Formatar & Copiar", self.formatar_e_copiar))
        layout.addLayout(button_layout)

        self.resultado = self.create_output_field(layout)

        self.setup_tab_navigation([
            self.comentario, self.responsavel, self.resultado
        ])

    def create_text_field(self, label_text: str, parent_layout: QVBoxLayout, height: int) -> QTextEdit:
        parent_layout.addWidget(QLabel(label_text))
        text_field = QTextEdit()
        text_field.setMaximumHeight(height)
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

    def create_radio_group(self, label_text: str, options: list[str], parent_layout: QVBoxLayout) -> QButtonGroup:
        parent_layout.addWidget(QLabel(label_text))
        group = QButtonGroup()
        layout = QHBoxLayout()

        for i, text in enumerate(options):
            radio = QRadioButton(text)
            radio.setStyleSheet("""
                QRadioButton {
                    color: black;
                }
            """)
            group.addButton(radio, i)
            layout.addWidget(radio)

        parent_layout.addLayout(layout)
        return group

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
        parent_layout.addWidget(QLabel("Resultado:"))
        output = QTextEdit()
        output.setReadOnly(True)
        output.setMinimumHeight(150)
        output.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid gray;
                padding: 2px;
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
        for field in [self.comentario, self.responsavel, self.resultado]:
            field.clear()

        for group in [self.equip_group, self.result_group]:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)

    def formatar_fechamento(self):
        comentario = self.comentario.toPlainText().strip()
        responsavel = self.responsavel.toPlainText().strip()
        equip_status = self.get_radio_selection(self.equip_group)
        result_status = self.get_radio_selection(self.result_group)

        formatted_text = ""

        if comentario:
            formatted_text += "===== Comentário de Fechamento =====\n\n"
            formatted_text += f"{comentario}\n\n"

            if equip_status == "Sim":
                formatted_text += "Técnico possui JDSU ou Wise? Sim\n\n"
                formatted_text += f"Resultado do teste: {result_status}\n\n"
            elif equip_status == "Não":
                formatted_text += "Técnico possui JDSU ou Wise? Não\n\n"
            elif equip_status == "Cliente não autorizou":
                formatted_text += "Situação: Cliente não autorizou\n\n"
            elif equip_status == "Atividade IPVPN ou Voz":
                formatted_text += "Atividade IPVPN ou Voz\n\n"
            elif equip_status == "Projeto Visita única":
                formatted_text += "Situação: Projeto Visita Única\n\n"

            if responsavel:
                formatted_text += "===== Responsável pela validação =====\n\n"
            formatted_text += f"{responsavel}\n\n"

        self.resultado.setPlainText(formatted_text)
        return formatted_text

    def formatar_e_copiar(self):
        formatted_text = self.formatar_fechamento()
        if formatted_text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(formatted_text)
            QMessageBox.information(self, "Sucesso", "Texto copiado para a área de transferência!")

    def get_radio_selection(self, group: QButtonGroup) -> str:
        selected = group.checkedButton()
        return selected.text() if selected else "Não informado"