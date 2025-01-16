from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QSplitter, QScrollArea, QTextBrowser, QLabel, QFrame, QComboBox,
    QFormLayout, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
import re
import os


class ScriptWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.current_script_index = None
        self.init_ui()
        self.load_scripts()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Criando o splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Parte esquerda - Lista de scripts e pesquisa
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Campo de pesquisa
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar scripts...")
        self.search_input.textChanged.connect(self.filter_table)
        left_layout.addWidget(self.search_input)

        # Tabela de scripts
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Script", "Descrição"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.handle_table_click)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table)

        # Parte direita - Visualização e edição do script
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Form para edição dos parâmetros
        self.dynamic_form_widget = QWidget()
        self.dynamic_form_layout = QFormLayout(self.dynamic_form_widget)
        right_layout.addWidget(self.dynamic_form_widget)

        # Botões
        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copiar Script")
        copy_button.clicked.connect(self.copy_script)
        button_layout.addWidget(copy_button)

        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_button)
        right_layout.addLayout(button_layout)

        # Visualização do script
        self.script_view = QTextBrowser()
        self.script_view.setPlainText("")
        right_layout.addWidget(self.script_view)

        # Adicionar widgets ao splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])

    def load_scripts(self):
        base_path = os.path.join(os.path.dirname(__file__), "scriptss")
        if not os.path.exists(base_path):
            return

        for filename in os.listdir(base_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(base_path, filename)
                self.add_script(file_path)

        self.populate_table()

    def add_script(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                script_name = lines[0].strip() if len(lines) >= 1 else os.path.basename(file_path)[:-4]
                description = lines[1].strip() if len(lines) >= 2 else "Sem descrição disponível"
                content = ''.join(lines[2:]) if len(lines) > 2 else ""
                self.scripts.append({
                    "name": script_name,
                    "description": description,
                    "content": content,
                    "file_path": file_path
                })
        except Exception as e:
            print(f"Erro ao carregar script {file_path}: {str(e)}")

    def populate_table(self):
        self.table.setRowCount(len(self.scripts))
        for row, script in enumerate(self.scripts):
            self.table.setItem(row, 0, QTableWidgetItem(script["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(script["description"]))

    def filter_table(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            script = self.table.item(row, 0).text().lower()
            description = self.table.item(row, 1).text().lower()
            self.table.setRowHidden(row, text not in script and text not in description)

    def handle_table_click(self, row, column):
        if 0 <= row < len(self.scripts):
            self.current_script_index = row
            self.show_script(row)

    def show_script(self, row):
        script_content = self.scripts[row]["content"]

        # Buscar o tipo de script usando regex com flag DOTALL
        script_type_match = re.search(r"\(tipo de scrip(?:t)?\)(.*?)\(/tipo de scrip(?:t)?\)", script_content, re.DOTALL)

        if script_type_match:
            script_type = script_type_match.group(1).strip()

            # Configurar interface baseado no tipo de script
            if script_type == "BLD CISCO PE":
                self.configure_cisco_pe()
            elif script_type == "BLD NOKIA PE":
                self.configure_nokia_pe()
            else:
                print(f"Tipo de script não reconhecido: {script_type}")
        else:
            print("Tipo de script não encontrado no conteúdo")

        self.update_script_view(script_content)

    def clear_dynamic_form(self):
        while self.dynamic_form_layout.count():
            child = self.dynamic_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Limpa referências para widgets dinâmicos
        self.interface_input = None
        self.ip_input = None
        self.ipv6_input = None
        self.status_combo = None
        self.ipv4_pe_input = None
        self.ipv4_cpe_input = None
        self.ipv6_cpe_input = None
        self.interface_pe_input = None
        self.qos_id_input = None

    def configure_cisco_pe(self):
        self.clear_dynamic_form()

        self.status_combo = QComboBox()
        self.status_combo.addItems(["ENCONTRADAS", "APLICADAS", "FINAIS"])
        self.status_combo.currentTextChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("Status:", self.status_combo)

        self.interface_input = QLineEdit()
        self.interface_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("Interface PE (opção 1):", self.interface_input)

        self.ip_input = QLineEdit()
        self.ip_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("IP CPE (opção 2):", self.ip_input)

        self.ipv6_input = QLineEdit()
        self.ipv6_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("IPv6 CPE (opção 3):", self.ipv6_input)

    def configure_nokia_pe(self):
        self.clear_dynamic_form()

        self.status_combo = QComboBox()
        self.status_combo.addItems(["INICIAIS", "APLICADAS", "FINAIS"])
        self.status_combo.currentTextChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("Tipo de LOGS:", self.status_combo)

        self.ipv4_pe_input = QLineEdit()
        self.ipv4_pe_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("End. IPv4 PE (opção 1):", self.ipv4_pe_input)

        self.ipv4_cpe_input = QLineEdit()
        self.ipv4_cpe_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("End. IPv4 CPE (opção 2):", self.ipv4_cpe_input)

        self.ipv6_cpe_input = QLineEdit()
        self.ipv6_cpe_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("End. IPv6 CPE (opção 3):", self.ipv6_cpe_input)

        self.interface_pe_input = QLineEdit()
        self.interface_pe_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("Interface - PE (1º comando, opção 4):", self.interface_pe_input)

        self.qos_id_input = QLineEdit()
        self.qos_id_input.textChanged.connect(self.update_script)
        self.dynamic_form_layout.addRow("ID QoS - PE (2º comando, opção 5):", self.qos_id_input)

    def extract_script_requirements(self, block_content):
        """
        Extract all required options from a script block.
        Returns a set of required options (e.g., {'opção 1', 'opção 2'}).
        """
        return set(re.findall(r'\b(opção \d+)\b', block_content))

    def process_script_blocks(self, content):
        """
        Process script blocks in the content and handle conditional visibility.
        """
        # Remove o tipo de script da visualização
        content = re.sub(r'\(tipo de scrip(?:t)?\).*?\(/tipo de scrip(?:t)?\)', '', content, flags=re.DOTALL)
        
        # Remove blocos relacionados ao (script2)
        content = re.sub(r'\(script2\).*?\(/script2\)', '', content, flags=re.DOTALL)

        # Create dictionary of filled options
        filled_options = {}

        # Adicionar valores preenchidos pelos campos dinâmicos
        if hasattr(self, 'status_combo') and self.status_combo:
            filled_options['status'] = self.status_combo.currentText()

        if hasattr(self, 'interface_input') and self.interface_input is not None:
            if self.interface_input.text().strip():
                filled_options['opção 1'] = self.interface_input.text()
            if self.ip_input and self.ip_input.text().strip():
                filled_options['opção 2'] = self.ip_input.text()
            if self.ipv6_input and self.ipv6_input.text().strip():
                filled_options['opção 3'] = self.ipv6_input.text()

        if hasattr(self, 'ipv4_pe_input') and self.ipv4_pe_input is not None:
            if self.ipv4_pe_input.text().strip():
                filled_options['opção 1'] = self.ipv4_pe_input.text()
            if self.ipv4_cpe_input and self.ipv4_cpe_input.text().strip():
                filled_options['opção 2'] = self.ipv4_cpe_input.text()
            if self.ipv6_cpe_input and self.ipv6_cpe_input.text().strip():
                filled_options['opção 3'] = self.ipv6_cpe_input.text()
            if self.interface_pe_input and self.interface_pe_input.text().strip():
                filled_options['opção 4'] = self.interface_pe_input.text()
            if self.qos_id_input and self.qos_id_input.text().strip():
                filled_options['opção 5'] = self.qos_id_input.text()

        # Substituir o bloco de status
        if 'status' in filled_options:
            content = re.sub(
                r'!######### CONFIGURACOES \(.*?\) \(/.*?\) ##########',
                f'!######### CONFIGURACOES {filled_options["status"]} ##########',
                content,
                flags=re.DOTALL
            )
            content = re.sub(
                r'########### CONFIGURAÇÕES \(.*?\) \(/.*?\) ##########',
                f'########### CONFIGURAÇÕES {filled_options["status"]} ##########',
                content,
                flags=re.DOTALL
            )

        # Processar linhas com opções
        lines = content.split('\n')
        processed_lines = []
        skip_cisco_block = False
        block_buffer = []  # Temporário para armazenar o bloco condicional

        for line in lines:
            if line.startswith('################################'):
                # Início do bloco especial
                block_buffer = [line]  # Inicializa o buffer do bloco
                skip_cisco_block = True
                continue

            if skip_cisco_block:
                # Adiciona linhas ao buffer do bloco especial
                block_buffer.append(line)
                if line.strip() == "1500":
                    # Final do bloco especial
                    skip_cisco_block = False
                    # Condicionalmente adiciona o bloco ao resultado
                    if 'opção 3' in filled_options:
                        processed_lines.extend(block_buffer)
                    block_buffer = []  # Reseta o buffer
                    continue

            if 'opção 3' in line:
                # Adicionar a linha apenas se "opção 3" estiver preenchida
                if 'opção 3' in filled_options:
                    for opt, value in filled_options.items():
                        line = line.replace(opt, value)
                    processed_lines.append(line)
                else:
                    # Ignorar a linha se "opção 3" não estiver preenchida
                    continue
            elif 'opção' in line:
                # Verifica se todas as outras opções na linha estão preenchidas
                options_in_line = re.findall(r'opção \d+', line)
                if all(opt in filled_options for opt in options_in_line):
                    for opt, value in filled_options.items():
                        line = line.replace(opt, value)
                    processed_lines.append(line)
                else:
                    # Remove apenas as partes com "opção (número)"
                    for opt in options_in_line:
                        line = line.replace(opt, "")
                    processed_lines.append(line.strip())
            else:
                processed_lines.append(line)

        # Juntar as linhas processadas
        processed_content = '\n'.join(processed_lines)

        return processed_content.strip()

    def update_script(self):
        if self.current_script_index is None:
            return

        try:
            script = self.scripts[self.current_script_index]
            original_content = script["content"]
            processed_content = self.process_script_blocks(original_content)
            self.script_view.setPlainText(processed_content)
        except Exception as e:
            print(f"Erro ao atualizar script: {str(e)}")
            self.script_view.setPlainText(original_content)

    def update_script_view(self, content: str):
        try:
            processed_content = self.process_script_blocks(content)
            self.script_view.setPlainText(processed_content)
        except Exception as e:
            print(f"Erro ao atualizar visualização do script: {str(e)}")
            self.script_view.setPlainText(content)

    def copy_script(self):
        script_content = self.script_view.toPlainText()
        if script_content:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(script_content)
            QMessageBox.information(self, "Sucesso", "Script copiado para a área de transferência!")

    def clear_fields(self):
        """
        Limpa todos os campos e atualiza a visualização
        """
        self.clear_dynamic_form()
        if self.current_script_index is not None:
            self.show_script(self.current_script_index)