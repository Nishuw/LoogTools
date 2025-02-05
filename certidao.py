from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QTextEdit, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QGuiApplication


class CertidaoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Status do Teste
        self.status_group = self.create_radio_group("Status do teste:", ["PASSED", "FAILED"], layout)

        # ID do Teste
        self.id_input = self.create_input_field("Insira o ID do TESTE:", "ID do Teste", layout)

        # Nome do Arquivo Anexado
        self.arquivo_input = self.create_input_field("ANEXADO NO TICKET (NOME DO ARQUIVO):", "Ex:(SUCESSO_SPO_IP_73596.pdf)", layout)

        # Botões
        button_layout = QHBoxLayout()
        button_style = """
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
        """
        button_layout.addWidget(self.create_button("Formatar & Copiar", self.formatar_e_copiar, button_style))
        button_layout.addWidget(self.create_button("Limpar", self.limpar_campos, button_style))
        layout.addLayout(button_layout)

        # Caixa de Texto Formatado
        self.resultado = self.create_output_field("Resultado da Formatação:", layout)

    def create_radio_group(self, label_text: str, options: list[str], parent_layout: QVBoxLayout) -> QButtonGroup:
        parent_layout.addWidget(QLabel(label_text))
        group = QButtonGroup()
        layout = QHBoxLayout()

        for i, text in enumerate(options):
            radio = QRadioButton(text)
            group.addButton(radio, i)
            layout.addWidget(radio)

        parent_layout.addLayout(layout)
        return group

    def create_input_field(self, label_text: str, placeholder: str, parent_layout: QVBoxLayout) -> QLineEdit:
        parent_layout.addWidget(QLabel(label_text))
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        parent_layout.addWidget(input_field)
        return input_field

    def create_button(self, text: str, callback, style: str) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setStyleSheet(style)
        return button

    def create_output_field(self, label_text: str, parent_layout: QVBoxLayout) -> QTextEdit:
        parent_layout.addWidget(QLabel(label_text))
        output = QTextEdit()
        output.setReadOnly(True)
        output.setMinimumHeight(150)
        parent_layout.addWidget(output)
        return output

    def formatar_e_copiar(self):
        status = self.get_radio_value(self.status_group)
        id_teste = self.id_input.text().strip()
        arquivo = self.arquivo_input.text().strip()

        if not status:
            QMessageBox.warning(self, "Aviso", "Selecione o status do teste.")
            return

        if not id_teste:
            QMessageBox.warning(self, "Aviso", "Insira o ID do teste.")
            return

        formatted_text = "TESTE DE CERTIDÃO REALIZADO E SALVO.\n\n"
        formatted_text += f"STATUS {status}\n\n"
        formatted_text += f"ID: {id_teste}\n"

        if arquivo:
            formatted_text += f"\nANEXADO NO TICKET: {arquivo}\n"

        self.resultado.setPlainText(formatted_text)

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(formatted_text)
        QMessageBox.information(self, "Sucesso", "Texto copiado para a área de transferência!")

    def limpar_campos(self):
        self.id_input.clear()
        self.arquivo_input.clear()
        self.resultado.clear()
        self.status_group.setExclusive(False)
        for button in self.status_group.buttons():
            button.setChecked(False)
        self.status_group.setExclusive(True)

    def get_radio_value(self, group: QButtonGroup) -> str:
        selected = group.checkedButton()
        return selected.text() if selected else ""