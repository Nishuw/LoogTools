import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QSplitter, QScrollArea, QTextBrowser, QLabel, QFrame, QPushButton, QHBoxLayout, QSlider
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


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

class CustomVideoWidget(QVideoWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)  # Permite janela independente
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.exitFullScreen()
        else:
            super().keyPressEvent(event)
            
    def exitFullScreen(self):
        self.setFullScreen(False)
        if hasattr(self, 'original_parent'):
            self.setParent(self.original_parent)
            self.original_layout.insertWidget(0, self)
            self.controls_widget.setParent(self.original_parent)
            self.original_layout.addWidget(self.controls_widget)
            self.show()
            self.controls_widget.show()

class ContentViewer(QScrollArea):
    def __init__(self):
        super().__init__()
        self.video_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.video_player.setAudioOutput(self.audio_output)
        self.video_widget = None
        self.audio_player = QMediaPlayer()
        self.is_fullscreen = False
        self.is_theater_mode = False  # Adicionado
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_position)

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
            self.video_container = QWidget()
            video_layout = QVBoxLayout(self.video_container)
            video_layout.setContentsMargins(0, 0, 0, 0)
            
            # Usando o CustomVideoWidget
            self.video_widget = CustomVideoWidget()
            self.video_widget.setMinimumHeight(400)
            self.video_player.setVideoOutput(self.video_widget)
            video_layout.addWidget(self.video_widget)
            
            # Controles em um widget separado
            self.controls_widget = QWidget()
            self.controls_layout = QHBoxLayout(self.controls_widget)
            self.controls_layout.setContentsMargins(5, 5, 5, 5)
            
            # Estilo para os controles
            self.controls_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 0.7);
                }
                QPushButton {
                    color: white;
                    border: none;
                    padding: 5px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QSlider::handle {
                    background: white;
                    border: 1px solid #5c5c5c;
                }
            """)
            
            # Adicionar controles
            self.play_button = QPushButton("►")
            self.controls_layout.addWidget(self.play_button)
            self.play_button.clicked.connect(self.play_pause)
            
            self.position_slider = QSlider(Qt.Orientation.Horizontal)
            self.position_slider.sliderMoved.connect(self.set_position)
            self.controls_layout.addWidget(self.position_slider)
            
            self.volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.volume_slider.setMaximum(100)
            self.volume_slider.setValue(50)
            self.volume_slider.setMaximumWidth(100)
            self.volume_slider.valueChanged.connect(self.set_volume)
            self.controls_layout.addWidget(self.volume_slider)
            
            self.theater_button = QPushButton("🎭")
            self.theater_button.clicked.connect(self.toggle_theater_mode)
            self.controls_layout.addWidget(self.theater_button)
            
            self.fullscreen_button = QPushButton("⛶")
            self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
            self.controls_layout.addWidget(self.fullscreen_button)
            
            video_layout.addWidget(self.controls_widget)
            
            self.layout.addWidget(self.video_container)
            
            # Conectar sinais
            self.video_player.playbackStateChanged.connect(self.update_play_button)
            self.video_player.durationChanged.connect(self.update_duration)
            self.audio_output.setVolume(0.5)

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            # Guardar o estado normal
            self.normal_parent = self.video_widget.parent()
            self.normal_layout = self.video_widget.parent().layout()
            
            # Criar container temporário para tela cheia
            self.fullscreen_container = QWidget()
            fs_layout = QVBoxLayout(self.fullscreen_container)
            fs_layout.setContentsMargins(0, 0, 0, 0)
            
            # Mover widgets para o container de tela cheia
            self.video_widget.setParent(self.fullscreen_container)
            self.controls_widget.setParent(self.fullscreen_container)
            fs_layout.addWidget(self.video_widget)
            fs_layout.addWidget(self.controls_widget)
            
            self.fullscreen_container.showFullScreen()
            self.is_fullscreen = True
            self.fullscreen_button.setText("⊠")
        else:
            # Restaurar ao estado normal
            self.video_widget.setParent(self.normal_parent)
            self.controls_widget.setParent(self.normal_parent)
            self.normal_layout.addWidget(self.video_widget)
            self.normal_layout.addWidget(self.controls_widget)
            
            self.fullscreen_container.close()
            self.fullscreen_container = None
            
            self.is_fullscreen = False
            self.fullscreen_button.setText("⛶")

    def toggle_theater_mode(self):
        if not self.is_theater_mode:
            self.normal_height = self.video_widget.height()
            self.video_widget.setMinimumHeight(600)
            self.is_theater_mode = True
            self.theater_button.setText("🎭↙")
        else:
            self.video_widget.setMinimumHeight(400)
            self.is_theater_mode = False
            self.theater_button.setText("🎭")

    def update_position(self):
        try:
            if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.position_slider.setValue(self.video_player.position())
        except RuntimeError:
            # Lidar silenciosamente com erros de widget deletado
            pass        

    def play_pause(self):
        if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.video_player.pause()
        else:
            self.video_player.play()
            self.timer.start()

    def update_play_button(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("⏸")
        else:
            self.play_button.setText("►")

    def set_volume(self, value):
        volume = value / 100
        self.audio_output.setVolume(volume)

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.video_player.setPosition(position)


    def update_position(self):
        if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.position_slider.setValue(self.video_player.position())    

    def _handle_link_click(self, url: QUrl):
        path = url.path()
        if os.name == 'nt' and path.startswith('/'):
            path = path[1:]
            
        if url.scheme() == "playvideo":
            self.video_container.show()  # Mostra o container imediatamente
            self.video_widget.show()     # Garante que o widget de vídeo está visível
            self.video_player.setSource(QUrl.fromLocalFile(path))
            # Não inicia o vídeo automaticamente
            self.timer.start()    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

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
        video_folder = os.path.join(base_path, "Videos treinamentos")

        file_path = os.path.join(text_folder, file_name)
        if not os.path.exists(file_path):
            self.content_widget.setText("Arquivo não encontrado")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                content = ''.join(lines[2:]) if len(lines) > 2 else "Conteúdo não disponível"
                
                # Procurar por tags de vídeo no conteúdo
                video_match = re.search(r'\[video:(.*?)\]', content)
                if video_match:
                    video_filename = video_match.group(1)
                    video_path = os.path.join(video_folder, video_filename)
                    if os.path.exists(video_path):
                        # Mostrar o vídeo diretamente
                        self.video_container.show()
                        self.video_widget.show()
                        self.video_player.setSource(QUrl.fromLocalFile(video_path))
                        
                        # Remover a tag de vídeo do conteúdo
                        content = re.sub(r'\[video:.*?\]', '', content)
                
                processed_content = self.process_content(content, base_path)
                self.original_html = processed_content
                self.content_widget.setHtml(self.original_html)
                
        except Exception as e:
            self.content_widget.setText(f"Erro ao carregar arquivo: {str(e)}")

    def process_content(self, content: str, base_path: str) -> str:
        # Subpastas específicas
        image_folder = os.path.join(base_path, "Imagens treinamentos")
        audio_folder = os.path.join(base_path, "Audios treinamentos")
        

        def replace_image(match):
            image_path = os.path.join(image_folder, match.group(1))
            return f'<img src="{image_path}" />' if os.path.exists(image_path) else f'[Imagem não encontrada: {match.group(1)}]'

        def replace_audio(match):
            audio_path = os.path.join(audio_folder, match.group(1))
            if os.path.exists(audio_path):
                # Criar um link que acionará o player de áudio
                return f'<a href="playaudio:{audio_path}" style="color: blue; text-decoration: underline;">Clique para reproduzir o áudio: {match.group(1)}</a>'
            return f'[Áudio não encontrado: {match.group(1)}]'

        # Substituições no conteúdo
        content = re.sub(r'\[image:(.*?)\]', replace_image, content)
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
