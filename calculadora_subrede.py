from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
import ipaddress

class CalculadoraSubredeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Radio buttons for IP version selection
        ip_version_layout = QHBoxLayout()
        self.ip_version_group = QButtonGroup()
        
        self.ipv4_radio = QRadioButton("IPv4")
        self.ipv6_radio = QRadioButton("IPv6")
        self.ipv4_radio.setChecked(True)
        
        self.ip_version_group.addButton(self.ipv4_radio)
        self.ip_version_group.addButton(self.ipv6_radio)
        
        ip_version_layout.addWidget(self.ipv4_radio)
        ip_version_layout.addWidget(self.ipv6_radio)
        layout.addLayout(ip_version_layout)

        # Example placeholder text changes based on IP version
        self.ipv4_radio.toggled.connect(self.update_placeholder)
        
        self.entry_ipv4 = self.create_input_field("Bloco de Rede em CIDR:", layout)
        self.update_placeholder()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button("Calcular", self.calcular_subrede))
        button_layout.addWidget(self.create_button("Limpar", self.limpar_subrede))
        button_layout.addWidget(self.create_button("Exportar para Arquivo", self.exportar_subrede))
        button_layout.addWidget(self.create_button("Copiar Resultado", self.copiar_resultado))
        layout.addLayout(button_layout)

        layout.addWidget(QLabel("Resultados do Cálculo:"))
        self.tree_calculo = QTreeWidget()
        self.tree_calculo.setHeaderLabels(["Propriedade", "Valor"])
        self.tree_calculo.setColumnWidth(0, 200)
        layout.addWidget(self.tree_calculo)

    def update_placeholder(self):
        if self.ipv4_radio.isChecked():
            self.entry_ipv4.setPlaceholderText("ex.: 192.168.1.0/24")
        else:
            self.entry_ipv4.setPlaceholderText("ex.: 2001:db8::/32")

    def create_input_field(self, label_text: str, parent_layout: QVBoxLayout) -> QLineEdit:
        parent_layout.addWidget(QLabel(label_text))
        input_field = QLineEdit()
        input_field.setStyleSheet("border: 2px solid gray; padding: 5px;")
        parent_layout.addWidget(input_field)
        return input_field

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

    def calcular_subrede(self):
        try:
            endereco = self.entry_ipv4.text().strip()
            if not endereco:
                raise ValueError("Insira um bloco de rede em CIDR")

            rede = ipaddress.ip_network(endereco, strict=False)
            
            # Verify if IP version matches selected radio button
            is_ipv4 = isinstance(rede, ipaddress.IPv4Network)
            if (is_ipv4 and not self.ipv4_radio.isChecked()) or (not is_ipv4 and not self.ipv6_radio.isChecked()):
                raise ValueError("Versão IP selecionada não corresponde ao endereço fornecido")

            wildcard = self.calculate_wildcard(rede.netmask) if is_ipv4 else "N/A para IPv6"
            lista_ips = list(rede.hosts())

            self.tree_calculo.clear()
            resultados = [
                ("Endereço de Rede", str(rede.network_address)),
                ("Máscara de Sub-rede", str(rede.netmask)),
                ("Wildcard Mask", wildcard),
                ("Broadcast Address", str(rede.broadcast_address) if is_ipv4 else "N/A para IPv6"),
                ("Número Total de Hosts", str(rede.num_addresses))
            ]

            if lista_ips:
                resultados.append(("Primeiro IP Disponível", str(lista_ips[0])))
                resultados.append(("Último IP Disponível", str(lista_ips[-1])))

            for prop, valor in resultados:
                self.tree_calculo.addTopLevelItem(QTreeWidgetItem([prop, valor]))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular: {str(e)}")

    def calculate_wildcard(self, netmask):
        return '.'.join(str(255 - int(octeto)) for octeto in str(netmask).split('.'))

    def limpar_subrede(self):
        self.entry_ipv4.clear()
        self.tree_calculo.clear()

    def exportar_subrede(self):
        try:
            if self.tree_calculo.topLevelItemCount() == 0:
                raise ValueError("Nenhum dado para exportar. Realize o cálculo primeiro!")

            arquivo, _ = QFileDialog.getSaveFileName(self, 'Salvar Arquivo', 'subnet_calculo_resultado.txt', 'Arquivos de Texto (*.txt)')

            if arquivo:
                with open(arquivo, "w") as f:
                    f.write("Resultados do Cálculo de Sub-rede\n")
                    f.write("=" * 50 + "\n")

                    for i in range(self.tree_calculo.topLevelItemCount()):
                        item = self.tree_calculo.topLevelItem(i)
                        f.write(f"{item.text(0)}: {item.text(1)}\n")

                    f.write("=" * 50 + "\n")

                QMessageBox.information(self, "Sucesso", f"Resultados exportados para: {arquivo}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")

    def copiar_resultado(self):
        try:
            if self.tree_calculo.topLevelItemCount() == 0:
                raise ValueError("Nenhum dado para copiar. Realize o cálculo primeiro!")

            texto = "Resultados do Cálculo de Sub-rede\n" + "=" * 50 + "\n"

            for i in range(self.tree_calculo.topLevelItemCount()):
                item = self.tree_calculo.topLevelItem(i)
                texto += f"{item.text(0)}: {item.text(1)}\n"

            texto += "=" * 50 + "\n"

            clipboard = QGuiApplication.clipboard()
            clipboard.setText(texto)

            QMessageBox.information(self, "Sucesso", "Resultados copiados para a área de transferência!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao copiar: {str(e)}")