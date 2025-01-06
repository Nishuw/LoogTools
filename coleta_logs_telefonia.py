from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QButtonGroup, QRadioButton, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QGuiApplication

class ColetaDeLogsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.group = self.create_radio_group("Selecione a Gerência:", ["MAE", "LMT"], layout)
        self.tg_input = self.create_input_field("Insira o Número do TG:", "Número do TG", layout)

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
        input_field.setMaximumWidth(200)
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
        output.setMinimumHeight(200)
        parent_layout.addWidget(output)
        return output

    def formatar_e_copiar(self):
        if not (self.group.checkedButton()):
            self.resultado.setPlainText("Por favor, selecione MAE ou LMT antes de formatar.")
            return

        tg = self.tg_input.text().strip()
        if not tg:
            QMessageBox.warning(self, "Aviso", "Insira o Número do TG antes de formatar!")
            return

        gerencia = self.group.checkedButton().text()
        formatacoes = self.gerar_comandos(gerencia, tg)

        resultado_formatado = "\n".join(formatacoes)
        self.resultado.setPlainText(resultado_formatado)

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(resultado_formatado)
        QMessageBox.information(self, "Sucesso", "Texto copiado para a área de transferência!")

    def gerar_comandos(self, gerencia: str, tg: str) -> list[str]:
        base_comandos = [
            f"LST TG:TG={tg},SSR=YES,SRT=YES,SOF=YES,SL=YES,SC=YES,SS=YES,SOT=YES,CLRDSP=YES,STGAP=YES,SCAC=YES,DIFF=YES,DCMI=YES;",
            f"LST SIPTG:TG={tg},SSR=YES,SRT=YES,SOF=YES,SOT=YES,CLRDSP=YES,SAP=YES,SCMC=YES;",
            f"LST RT: R={tg}, SSR=YES;",
            f"LST SRT: SRC={tg}, ST=YES;",
            f"LST TGLDIDX:TG={tg};",
            f"LST RTANA:MOD=MIX,RSC={tg},SPFX=YES;",
            f"LST TKDNSEG:TGNO={tg};",
            f"LST TGDSG: TG={tg};",
            f"LST TKC: TG={tg};",
            f"DSP OFTK:LT=TG,TG={tg},DT=AT;",
            f"LST SIPIPPAIR:TG={tg};",
            f"DSP SIPTG:TG={tg};",
            f"MOD BTG:TG={tg},BLS=UBL;"
        ]

        if gerencia == "LMT":
            base_comandos.extend([
                f"LST SIPTG:TG={tg},SSR=YES,SRTLST=YES,SOF=YES,SOT=YES,CLRDSP=YES,SAP=YES,SCMC=YES;",
                f"LST RTANA:LST=MIX, RSC={tg}, SPFX=YES;"
            ])

        return base_comandos

    def limpar_campos(self):
        self.tg_input.clear()
        self.resultado.clear()
        self.group.setExclusive(False)
        for button in self.group.buttons():
            button.setChecked(False)
        self.group.setExclusive(True)