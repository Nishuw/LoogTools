from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
import os

class CodigosSIPWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.codigos_sip = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.search_input = self.create_search_input(layout)
        self.table = self.create_table(layout)
        
        self.carregar_codigos_sip()

    def create_search_input(self, parent_layout: QVBoxLayout) -> QLineEdit:
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Digite para filtrar códigos SIP...")
        search_input.textChanged.connect(self.filtrar_tabela)
        search_layout.addWidget(search_input)
        parent_layout.addLayout(search_layout)
        return search_input

    def create_table(self, parent_layout: QVBoxLayout) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Código", "Descrição"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Impede edição da tabela
        parent_layout.addWidget(table)
        return table

    def carregar_codigos_sip(self):
        caminho_arquivo = os.path.join(os.path.dirname(__file__), "codigos_sip.txt")
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as file:
                for linha in file:
                    linha = linha.strip()
                    if ":" in linha:
                        codigo, descricao = linha.split(":", 1)
                        self.codigos_sip[codigo.strip()] = descricao.strip()
                    else:
                        print(f"Linha inválida ignorada: {linha}")

            self.preencher_tabela()
        except FileNotFoundError:
            QMessageBox.critical(self, "Erro", f"Arquivo '{caminho_arquivo}' não encontrado.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar códigos SIP: {e}")

    def preencher_tabela(self):
        self.table.setRowCount(len(self.codigos_sip))
        for idx, (codigo, descricao) in enumerate(sorted(self.codigos_sip.items())):
            self.table.setItem(idx, 0, QTableWidgetItem(codigo))
            self.table.setItem(idx, 1, QTableWidgetItem(descricao))

    def filtrar_tabela(self, texto: str):
        texto = texto.lower()
        for row in range(self.table.rowCount()):
            codigo = self.table.item(row, 0).text().lower()
            descricao = self.table.item(row, 1).text().lower()
            mostrar = texto in codigo or texto in descricao
            self.table.setRowHidden(row, not mostrar)