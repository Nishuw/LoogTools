import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QSplitter, QScrollArea, QTextBrowser, QLabel,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut, QDesktopServices, QWheelEvent
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument


class SearchOverlay(QFrame):
    def __init__(self, content_viewer=None, dark_mode=False):
        super().__init__()
        self.content_viewer = content_viewer
        self.dark_mode = dark_mode
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar no texto...")
        self.search_input.setObjectName("searchTroubleshootingInput")  # Definindo nome para estilização
        self.search_input.setStyleSheet("""
            QLineEdit#searchTroubleshootingInput {
                background-color: white;
                border: 1px solid gray;
                border-radius: 4px;
                padding: 4px;
                max-width: 200px;
                color: black; /* Cor do texto */
            }
            QLineEdit#searchTroubleshootingInput::placeholder {
                color: #777777; /* Cor do placeholder (cinza mais escuro) */
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
        if self.content_viewer and self.content_viewer.content_type == "text":
            self.content_viewer.highlight_search(self.search_input.text())


class ContentViewer(QScrollArea):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.dark_mode = dark_mode
        self.setup_ui()
        self.content_type = None
        self.current_file_path = None
        self.base_path = None

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setObjectName("troubleshootingViewerContainer")  # Definindo nome para estilização

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout = layout

        self.search_overlay = SearchOverlay(content_viewer=self, dark_mode=self.dark_mode)
        self.search_overlay.hide()
        layout.addWidget(self.search_overlay, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.content_widget = QTextBrowser()
        self.content_widget.setOpenExternalLinks(False)
        # Configurar o QTextBrowser para lidar com recursos locais
        self.content_widget.setOpenLinks(False)
        self.content_widget.setObjectName("troubleshootingContentBrowser")  # Definindo nome para estilização

        self.pdf_view = QPdfView(self.container)
        self.pdf_view.setObjectName("troubleshootingPdfView")  # Definindo nome para estilização
        self.pdf_view.setVisible(False)
        self.pdf_document = QPdfDocument(self.container)

        layout.addWidget(self.content_widget)
        layout.addWidget(self.pdf_view)

        self.setWidget(self.container)
        self.original_html = ""

        # Ativar funcionalidade de zoom com Ctrl+roda do mouse
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.toggle_search)

    def toggle_search(self):
        if self.content_type == "text":
            if self.search_overlay.isVisible():
                self.search_overlay.clear_and_hide()
            else:
                self.search_overlay.show()
                self.search_overlay.search_input.setFocus()

    def clear_highlights(self):
        if self.content_type == "text":
            self.content_widget.setHtml(self.original_html)

    def highlight_search(self, search_text: str):
        if self.content_type == "text":
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

    def open_link(self, url):
        """Abrir link no navegador padrão."""
        QDesktopServices.openUrl(QUrl(url))

    def load_content(self, file_path: str):
        if not os.path.exists(file_path):
            self.content_widget.setText("Arquivo não encontrado")
            return

        self.current_file_path = file_path
        self.base_path = os.path.dirname(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.process_and_display(content)
        except Exception as e:
            self.content_widget.setText(f"Erro ao carregar arquivo: {str(e)}")

    def process_and_display(self, content: str):
        def replace_pdf(match):
            pdf_path = match.group(1)
            abs_path = os.path.join(self.base_path, pdf_path)
            if os.path.exists(abs_path) and abs_path.lower().endswith('.pdf'):
                self.load_pdf(abs_path)
                return ''
            else:
                return f'[PDF não encontrado: {pdf_path}]'

        content = re.sub(r'\[pdf:(.*?)\]', replace_pdf, content)

        if self.content_type == "pdf":
            return

        def replace_image(match):
            image_path = match.group(1)
            abs_path = os.path.join(self.base_path, image_path)
            if os.path.exists(abs_path):
                # Usar o caminho com file:/// para garantir que o QTextBrowser possa carregar
                return f'<img src="file:///{abs_path.replace(os.sep, "/")}" />'
            else:
                print(f"Imagem não encontrada: {abs_path}")
                return f'[Imagem não encontrada: {image_path}]'

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
                elif style == 'left':
                    css_styles.append('text-align: left')
                elif style == 'right':
                    css_styles.append('text-align: right')
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
        # Verificar se há links e transformar em tags <a>
        content = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', content)

        content = content.replace('\n', '<br>')

        self.original_html = content
        self.content_widget.setHtml(self.original_html)
        self.content_type = "text"
        self.content_widget.setVisible(True)
        self.pdf_view.setVisible(False)
        self.search_overlay.show()

    def load_pdf(self, file_path: str):
        self.content_widget.setVisible(False)
        self.pdf_view.setVisible(True)
        self.content_type = "pdf"
        self.search_overlay.hide()

        try:
            self.pdf_document.load(file_path)
            self.pdf_view.setDocument(self.pdf_document)
        except Exception as e:
            self.content_widget.setText(f"Erro ao carregar PDF: {str(e)}")
            self.content_widget.setVisible(True)
            self.pdf_view.setVisible(False)
            self.content_type = "text"

    def clear_content(self):
        self.pdf_view.setDocument(QPdfDocument(self))
        self.content_widget.clear()
        self.content_widget.setVisible(True)
        self.pdf_view.setVisible(False)
        self.content_type = "text"
        self.original_html = ""
        self.search_overlay.show()

    def set_base_path(self, base_path: str):
        """Sets the base path for resolving relative file paths."""
        self.base_path = base_path

    def zoom_in(self):
        """Zooms in the PDF view."""
        if self.content_type == "pdf":
            current_zoom = self.pdf_view.zoomFactor()
            self.pdf_view.setZoomFactor(current_zoom + 0.1)

    def zoom_out(self):
        """Zooms out the PDF view."""
        if self.content_type == "pdf":
            current_zoom = self.pdf_view.zoomFactor()
            self.pdf_view.setZoomFactor(current_zoom - 0.1)

    def wheelEvent(self, event: QWheelEvent):
        if self.content_type == "text" and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            font = self.content_widget.font()
            font_size = font.pointSize()

            if event.angleDelta().y() > 0:
                font_size += 1
            else:
                font_size -= 1

            if font_size > 0:
                font.setPointSize(font_size)
                self.content_widget.setFont(font)
        elif self.content_type == "pdf" and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)


class TroubleshootingWidget(QWidget):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.dark_mode = dark_mode
        self.processes = []
        self.setup_ui()
        self.load_processes()
        self.apply_stylesheet()  # Aplicar tema no construtor

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.main_layout = layout

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("troubleshootingSplitter")  # Nomeando para estilizar

        left_widget = QWidget()
        left_widget.setObjectName("troubleshootingLeftWidget")  # Nomeando para estilizar
        left_layout = QVBoxLayout(left_widget)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("troubleshootingSearchInput")  # Nomeando para estilizar
        self.search_input.setPlaceholderText("Digite para filtrar processos...")
        left_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setObjectName("troubleshootingTable")  # Nomeando para estilizar
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Processo", "Descrição"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.clicked.connect(self.show_process)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table)

        self.content_viewer = ContentViewer(dark_mode=self.dark_mode)
        self.content_viewer.setObjectName("troubleshootingContentViewer")  # Nomeando para estilizar

        splitter.addWidget(left_widget)
        splitter.addWidget(self.content_viewer)
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)  # Adicionar o splitter ao layout principal

    def load_processes(self):
        base_path = os.path.join(os.path.dirname(__file__), "processos", "Textos Processos")
        if not os.path.exists(base_path):
            print(f"Diretório não encontrado: {base_path}")  # Debug
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
                content = ''.join(lines[2:]) if len(lines) > 2 else ""

                # Configurar o caminho base para as imagens
                images_base_path = os.path.join(os.path.dirname(os.path.dirname(file_path)), "imagens")
                print(f"Caminho base das imagens: {images_base_path}")  # Debug

                self.content_viewer.set_base_path(images_base_path)  # Define o caminho base

                self.processes.append({
                    "name": process_name,
                    "description": description,
                    "file_path": file_path,
                    "content": content
                })
        except Exception as e:
            print(f"Erro ao processar arquivo {file_path}: {e}")  # Debug
            self.processes.append({
                "name": os.path.basename(file_path)[:-4],
                "description": "Erro ao carregar descrição",
                "file_path": file_path,
                "content": ""
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
            content = self.processes[row]["content"]
            self.content_viewer.clear_content()
            # self.content_viewer.set_base_path(os.path.dirname(file_path)) #Não precisa mais
            self.content_viewer.process_and_display(content)

    def apply_stylesheet(self):
        # Aplicar tema base
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #222222;
                    color: #DDDDDD;
                }
            """)

            self.search_input.setStyleSheet("""
                QLineEdit#troubleshootingSearchInput {
                    background-color: #333333;
                    color: #DDDDDD;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                    max-width: 200px;
                }
            """)

            self.table.setStyleSheet("""
                QTableWidget#troubleshootingTable {
                    background-color: #333333;
                    color: #DDDDDD;
                    border: 1px solid #555555;
                }

                QHeaderView::section {
                    background-color: #333333;
                    color: #DDDDDD;
                    border: none;
                }
            """)

            self.content_viewer.content_widget.setStyleSheet("""
                QTextBrowser#troubleshootingContentBrowser {
                    background-color: #333333;
                    padding: 10px;
                    white-space: pre-wrap;
                    color: #DDDDDD;
                }
            """)
        else:
            self.setStyleSheet("")  # Limpa o estilo para o modo normal

            self.search_input.setStyleSheet("""
                QLineEdit#troubleshootingSearchInput {
                    background-color: white;
                    border: 1px solid gray;
                    border-radius: 4px;
                    padding: 4px;
                    max-width: 200px;
                }
            """)

            self.table.setStyleSheet("")
            self.content_viewer.content_widget.setStyleSheet("""
                QTextBrowser#troubleshootingContentBrowser {
                    background-color: white;
                    padding: 10px;
                    white-space: pre-wrap;
                    color: black;
                }
            """)