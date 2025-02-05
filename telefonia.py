from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, 
    QButtonGroup, QRadioButton, QMessageBox
)
from PyQt6.QtGui import QGuiApplication
from tab_navigation import setup_tab_navigation

class TelefoniaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.validada_group = self.create_radio_group("1) Atividade validada?", ["Sim", "Não"], layout)
        self.pt_oe_group = self.create_radio_group("2) PT/OE:", ["PT", "OE"], layout)
        self.fechada_group = self.create_radio_group("PT/OE fechada?", ["Sim", "Não"], layout)

        self.justificativa = self.create_text_field("Justifique caso não fechada:", layout, 50)
        self.port_group = self.create_radio_group("3) É portabilidade?", ["Sim", "Não"], layout)
        self.bilhetes_group = self.create_radio_group("Bilhetes encerrados?", ["Sim", "Não possui bilhetes"], layout)
        self.migrou_group = self.create_radio_group("4) Migrou (TG ou CENTRAL)?", ["Sim", "Não"], layout)
        self.broadsoft_group = self.create_radio_group("5) É migração para Broadsoft?", ["Sim", "Não"], layout)

        layout.addWidget(QLabel("Ticket suporte IMS (Se SIM, abrir ticket Suporte IMS)"))
        self.ticket_ims = self.create_text_field("", layout, 50)

        self.responsavel = self.create_text_field("6) Responsável pela validação:", layout, 50)

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
        button_layout.addWidget(self.create_button("Limpar", self.limpar_campos, button_style))
        button_layout.addWidget(self.create_button("Formatar & Copiar", self.formatar_e_copiar, button_style))
        layout.addLayout(button_layout)

        self.resultado = self.create_output_field(layout)

        setup_tab_navigation([
            self.justificativa, self.ticket_ims, self.responsavel
        ])

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

    def create_text_field(self, label_text: str, parent_layout: QVBoxLayout, height: int) -> QTextEdit:
        if label_text:
            parent_layout.addWidget(QLabel(label_text))
        text_field = QTextEdit()
        text_field.setMaximumHeight(height)
        parent_layout.addWidget(text_field)
        return text_field

    def create_button(self, text: str, callback, style: str) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setStyleSheet(style)
        return button

    def create_output_field(self, parent_layout: QVBoxLayout) -> QTextEdit:
        output = QTextEdit()
        output.setReadOnly(True)
        output.setMinimumHeight(150)
        parent_layout.addWidget(output)
        return output

    def show_warning_popup(self, message: str):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Atenção!")
        msg.exec()

    def check_conditions(self):
        # Verifica condição para opção 4
        if self.get_radio_value(self.migrou_group) == "Sim":
            self.show_warning_popup(
                "Migração de Central: Enviar e-mail para CCIPSOE@."
            )
        
        # Verifica condição para opção 5
        if self.get_radio_value(self.broadsoft_group) == "Sim":
            self.show_warning_popup("Antes de finalizar a Ordem de Serviço (OS), é imprescindível acionar o "
                "Suporte N2 para realizar a inclusão da numeração do cliente no servidor "
                "IMS-ENUM, exceto em casos de Pré-Teste de Portabilidade.")

    def limpar_campos(self):
        for field in [self.justificativa, self.ticket_ims, self.responsavel, self.resultado]:
            field.clear()

        for group in [
            self.validada_group, self.pt_oe_group, self.fechada_group,
            self.port_group, self.bilhetes_group, self.migrou_group,
            self.broadsoft_group
        ]:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)

    def formatar_fechamento(self):
        formatted_text = (
            f"Atividade validada: {self.get_radio_value(self.validada_group)}\n"
            f"PT/OE: {self.get_radio_value(self.pt_oe_group)}\n"
            f"PT/OE fechada: {self.get_radio_value(self.fechada_group)}\n"
        )

        if self.get_radio_value(self.fechada_group) == "Não":
            formatted_text += f"Justificativa: {self.justificativa.toPlainText().strip()}\n"

        formatted_text += (
            f"É portabilidade: {self.get_radio_value(self.port_group)}\n"
            f"Bilhetes encerrados: {self.get_radio_value(self.bilhetes_group)}\n"
            f"Migrou (TG ou CENTRAL): {self.get_radio_value(self.migrou_group)}\n"
            f"É migração para Broadsoft: {self.get_radio_value(self.broadsoft_group)}\n"
        )

        if self.get_radio_value(self.broadsoft_group) == "Sim":
            formatted_text += f"Ticket suporte IMS: {self.ticket_ims.toPlainText().strip()}\n"

        formatted_text += f"Responsável: {self.responsavel.toPlainText().strip()}"

        self.resultado.setPlainText(formatted_text)
        return formatted_text

    def formatar_e_copiar(self):
        formatted_text = self.formatar_fechamento()
        if formatted_text:
            self.check_conditions()  # Chama a verificação das condições
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(formatted_text)

    def get_radio_value(self, group: QButtonGroup) -> str:
        selected = group.checkedButton()
        return selected.text() if selected else "Não informado"