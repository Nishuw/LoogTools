import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QSplitter, QScrollArea, QTextBrowser, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut, QTextCharFormat, QColor


class SearchOverlay(QFrame):
    def __init__(self, content_viewer=None):
        super().__init__()
        self.content_viewer = content_viewer
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar no texto...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid gray;
                border-radius: 4px;
                padding: 4px;
                max-width: 200px;
            }
        """)
        layout.addWidget(self.search_input)

        self.search_input.textChanged.connect(self.handle_search)
        self.search_input.keyPressEvent = self.handle_key_press

        self.setFixedHeight(40)
        self.setMaximumWidth(220)

    def handle_key_press(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clear_and_hide()
        else:
            QLineEdit.keyPressEvent(self.search_input, event)

    def clear_and_hide(self):
        self.search_input.clear()
        self.hide()
        if self.content_viewer:
            self.content_viewer.clear_highlights()

    def handle_search(self):
        if self.content_viewer:
            self.content_viewer.highlight_search(self.search_input.text())


class ContentViewer(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_overlay = SearchOverlay(content_viewer=self)
        self.search_overlay.hide()
        layout.addWidget(self.search_overlay, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.content_widget = QTextBrowser()
        self.content_widget.setOpenExternalLinks(False)
        self.content_widget.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                padding: 10px;
            }
        """)
        layout.addWidget(self.content_widget)
        self.setWidget(self.container)

        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.toggle_search)

        self.original_html = ""

    def toggle_search(self):
        if self.search_overlay.isVisible():
            self.search_overlay.clear_and_hide()
        else:
            self.search_overlay.show()
            self.search_overlay.search_input.setFocus()

    def clear_highlights(self):
        self.content_widget.setHtml(self.original_html)

    def highlight_search(self, search_text: str):
        self.clear_highlights()

        if not search_text:
            return

        highlighted_html = re.sub(
            f"({re.escape(search_text)})",
            r'<span style="background-color: yellow;">\1</span>',
            self.original_html,
            flags=re.IGNORECASE
        )

        self.content_widget.setHtml(highlighted_html)

    def load_content(self, file_path: str):
        if not os.path.exists(file_path):
            self.content_widget.setText("Arquivo não encontrado")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                process_content = ''.join(lines[2:]) if len(lines) > 2 else "Conteúdo do processo não disponível"
                processed_content = self.process_content(process_content, os.path.dirname(file_path))

                self.original_html = processed_content
                self.content_widget.setHtml(self.original_html)
        except Exception as e:
            self.content_widget.setText(f"Erro ao carregar arquivo: {str(e)}")

    def process_content(self, content: str, base_path: str) -> str:
        def replace_image(match):
            image_path = match.group(1)
            abs_path = os.path.join(base_path, image_path)
            return f'<img src="{abs_path}" />' if os.path.exists(abs_path) else f'[Imagem não encontrada: {image_path}]'

        def replace_styles(match):
            styles = match.group(1).split(':')
            text = match.group(2)
            css_styles = []
            is_block = False
            for style in styles:
                if style == 'bold':
                    css_styles.append('font-weight: bold')
                elif style == 'center':
                    css_styles.append('text-align: center')
                    is_block = True
                elif style == 'left':
                    css_styles.append('text-align: left')
                    is_block = True
                elif style == 'right':
                    css_styles.append('text-align: right')
                    is_block = True
                elif style == 'red':
                    css_styles.append('color: red')
                elif style == 'yellow':
                    css_styles.append('color: yellow')
                elif style == 'blue':
                    css_styles.append('color: blue')    
                elif style == 'cipher':
                    css_styles.append('text-decoration: line-through')
                elif style.startswith('font:'):
                    font_name = style.split(':')[1]
                    css_styles.append(f'font-family: {font_name}')
            css_style_string = "; ".join(css_styles)
            tag = "div" if is_block else "span"
            return f'<{tag} style="{css_style_string}">{text}</{tag}>'

        content = re.sub(r'\[style:(.*?)\](.*?)\[\/style\]', replace_styles, content, flags=re.DOTALL)
        content = re.sub(r'\[image:(.*?)\]', replace_image, content)
        return content.replace('\n', '<br>')


class TroubleshootingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.processes = []
        self.setup_ui()
        self.load_processes()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar processos...")
        self.search_input.textChanged.connect(self.filter_table)
        left_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Processo", "Descrição"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.clicked.connect(self.show_process)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # desabilita a edição da cedula
        left_layout.addWidget(self.table)

        self.content_viewer = ContentViewer()

        splitter.addWidget(left_widget)
        splitter.addWidget(self.content_viewer)
        splitter.setSizes([300, 700])

    def load_processes(self):
        base_path = os.path.join(os.path.dirname(__file__), "processos")
        if not os.path.exists(base_path):
            return

        for filename in os.listdir(base_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(base_path, filename)
                self.add_process(file_path)

        self.populate_table()

    def add_process(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                process_name = lines[0].strip() if len(lines) >= 1 else os.path.basename(file_path)[:-4]
                description = lines[1].strip() if len(lines) >= 2 else "Sem descrição disponível"
                self.processes.append({
                    "name": process_name,
                    "description": description,
                    "file_path": file_path
                })
        except Exception:
            self.processes.append({
                "name": os.path.basename(file_path)[:-4],
                "description": "Erro ao carregar descrição",
                "file_path": file_path
            })

    def populate_table(self):
        self.table.setRowCount(len(self.processes))
        for row, process in enumerate(self.processes):
            self.table.setItem(row, 0, QTableWidgetItem(process["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(process["description"]))

    def filter_table(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            process = self.table.item(row, 0).text().lower()
            description = self.table.item(row, 1).text().lower()
            self.table.setRowHidden(row, text not in process and text not in description)

    def show_process(self, index):
        row = index.row()
        if 0 <= row < len(self.processes):
            file_path = self.processes[row]["file_path"]
            self.content_viewer.load_content(file_path)