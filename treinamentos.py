import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QSplitter, QScrollArea, QTextBrowser, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget


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
        # Player para vídeo
        self.video_player = QMediaPlayer()
        self.video_widget = None
        # Player para áudio
        self.audio_player = QMediaPlayer()
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.search_overlay = SearchOverlay(content_viewer=self)
        self.search_overlay.hide()
        self.layout.addWidget(self.search_overlay, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.content_widget = QTextBrowser()
        self.content_widget.setOpenExternalLinks(True)
        self.content_widget.setOpenLinks(False)
        self.content_widget.anchorClicked.connect(self._handle_link_click)
        
        self.content_widget.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.content_widget)
        self.setWidget(self.container)

        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.toggle_search)

        self.original_html = ""

    def _handle_link_click(self, url: QUrl):
        path = url.path()
        # No Windows, remover a primeira barra do caminho
        if os.name == 'nt' and path.startswith('/'):
            path = path[1:]
            
        if url.scheme() == "playvideo":
            # Mostrar o widget de vídeo
            if self.video_widget:
                self.video_widget.show()
            # Configurar e iniciar a reprodução do vídeo
            self.video_player.setSource(QUrl.fromLocalFile(path))
            self.video_player.play()
        
        elif url.scheme() == "playaudio":
            # Configurar e iniciar a reprodução do áudio
            self.audio_player.setSource(QUrl.fromLocalFile(path))
            self.audio_player.play()

    def create_video_player(self):
        if self.video_widget is None:
            self.video_widget = QVideoWidget()
            self.video_widget.setMinimumHeight(400)
            self.media_player.setVideoOutput(self.video_widget)
            self.layout.addWidget(self.video_widget)
            self.video_widget.hide()

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

    def load_content(self, file_name: str):
        # Criar o player de vídeo se ainda não existir
        self.create_video_player()
        
        base_path = os.path.join(os.path.dirname(__file__), "Treinamentos")
        text_folder = os.path.join(base_path, "Textos treinamentos")

        file_path = os.path.join(text_folder, file_name)
        if not os.path.exists(file_path):
            self.content_widget.setText("Arquivo não encontrado")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                process_content = ''.join(lines[2:]) if len(lines) > 2 else "Conteúdo do processo não disponível"
                processed_content = self.process_content(process_content, base_path)

                self.original_html = processed_content
                self.content_widget.setHtml(self.original_html)
                
        except Exception as e:
            self.content_widget.setText(f"Erro ao carregar arquivo: {str(e)}")

    def process_content(self, content: str, base_path: str) -> str:
        # Subpastas específicas
        image_folder = os.path.join(base_path, "Imagens treinamentos")
        audio_folder = os.path.join(base_path, "Audios treinamentos")
        video_folder = os.path.join(base_path, "Videos treinamentos")

        def replace_image(match):
            image_path = os.path.join(image_folder, match.group(1))
            return f'<img src="{image_path}" />' if os.path.exists(image_path) else f'[Imagem não encontrada: {match.group(1)}]'

        def replace_video(match):
            video_path = os.path.join(video_folder, match.group(1))
            if os.path.exists(video_path):
                # Criar um ID único para o vídeo
                video_id = f"video_{hash(video_path)}"
                # Criar um link que acionará o player de vídeo
                return f'<a href="playvideo:{video_path}" style="color: blue; text-decoration: underline;">Clique para reproduzir o vídeo: {match.group(1)}</a>'
            return f'[Vídeo não encontrado: {match.group(1)}]'

        def replace_audio(match):
            audio_path = os.path.join(audio_folder, match.group(1))
            if os.path.exists(audio_path):
                # Criar um link que acionará o player de áudio
                return f'<a href="playaudio:{audio_path}" style="color: blue; text-decoration: underline;">Clique para reproduzir o áudio: {match.group(1)}</a>'
            return f'[Áudio não encontrado: {match.group(1)}]'

        # Substituições no conteúdo
        content = re.sub(r'\[image:(.*?)\]', replace_image, content)
        content = re.sub(r'\[video:(.*?)\]', replace_video, content)
        content = re.sub(r'\[audio:(.*?)\]', replace_audio, content)
        return content.replace('\n', '<br>')


class TreinamentosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.treinamentos = []  # Lista de treinamentos
        self.setup_ui()
        self.load_treinamentos()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar treinamentos...")
        self.search_input.textChanged.connect(self.filter_table)
        left_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Treinamento", "Descrição"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.clicked.connect(self.show_treinamento)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Desabilita a edição da célula
        left_layout.addWidget(self.table)

        self.content_viewer = ContentViewer()
        splitter.addWidget(left_widget)
        splitter.addWidget(self.content_viewer)
        splitter.setSizes([300, 700])

    def load_treinamentos(self):
        base_path = os.path.join(os.path.dirname(__file__), "Treinamentos", "Textos treinamentos")
        if not os.path.exists(base_path):
            return

        for filename in os.listdir(base_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(base_path, filename)
                self.add_treinamento(file_path)

        self.populate_table()

    def add_treinamento(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                treinamento_name = lines[0].strip() if len(lines) >= 1 else os.path.basename(file_path)[:-4]
                description = lines[1].strip() if len(lines) >= 2 else "Sem descrição disponível"
                self.treinamentos.append({
                    "name": treinamento_name,
                    "description": description,
                    "file_path": file_path
                })
        except Exception:
            self.treinamentos.append({
                "name": os.path.basename(file_path)[:-4],
                "description": "Erro ao carregar descrição",
                "file_path": file_path
            })

    def populate_table(self):
        self.table.setRowCount(len(self.treinamentos))
        for row, treinamento in enumerate(self.treinamentos):
            self.table.setItem(row, 0, QTableWidgetItem(treinamento["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(treinamento["description"]))

    def filter_table(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            treinamento = self.table.item(row, 0).text().lower()
            description = self.table.item(row, 1).text().lower()
            self.table.setRowHidden(row, text not in treinamento and text not in description)

    def show_treinamento(self, index):
        row = index.row()
        if 0 <= row < len(self.treinamentos):
            file_path = self.treinamentos[row]["file_path"]
            self.content_viewer.load_content(file_path)
