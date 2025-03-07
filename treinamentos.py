# treinamentos.py
import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QSplitter, QScrollArea, QTextBrowser, QLabel,
    QFrame, QPushButton, QHBoxLayout, QSlider, QApplication
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QKeySequence, QShortcut, QPixmap

# Imports adicionais para lidar com PDFs
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument
from utils import zoom_in, zoom_out  # Importe as funções zoom_in e zoom_out


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
        self.setup_ui()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_position)

        self.current_file_path = None  # Armazena o caminho do arquivo atualmente carregado
        self.content_type = None  # Tipo de conteúdo exibido (text ou pdf)

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setObjectName("treinamentosViewerContainer")  # Definindo nome para estilização

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout = layout
        self.container_layout = layout #Definir container

        self.search_overlay = SearchOverlay(content_viewer=self)
        self.search_overlay.hide()
        layout.addWidget(self.search_overlay, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Text Browser para conteúdos de texto
        self.content_widget = QTextBrowser()
        self.content_widget.setOpenExternalLinks(True)
        self.content_widget.setOpenLinks(False)
        self.content_widget.setObjectName("treinamentosContentBrowser")  # Definindo nome para estilização
        self.content_widget.setStyleSheet("""
            QTextBrowser#treinamentosContentBrowser {
                background-color: white;
                padding: 10px;
                white-space: pre-wrap; /* Importante para exibir quebras de linha */
                color: black;
            }
        """)

        # PDF View para conteúdos PDF
        self.pdf_view = QPdfView(self.container)
        self.pdf_view.setObjectName("treinamentosPdfView")  # Definindo nome para estilização
        self.pdf_view.setVisible(False)
        self.pdf_document = QPdfDocument(self.container)

        # Adiciona os widgets ao layout
        layout.addWidget(self.content_widget)
        layout.addWidget(self.pdf_view)

        self.setWidget(self.container)

        # Ativar funcionalidade de zoom com Ctrl+roda do mouse
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Garante que o widget receba foco
        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.toggle_search)
        self.original_html = ""

        # Esconder inicialmente os elementos de vídeo
        self.video_container = QWidget()
        self.video_container.hide()
        layout.addWidget(self.video_container)

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
            self.controls_widget.setObjectName("videoControls")  # Adiciona um nome para estilização
            self.controls_layout = QHBoxLayout(self.controls_widget)
            self.controls_layout.setContentsMargins(5, 5, 5, 5)

            # Adicionar controles
            self.play_button = QPushButton("►")
            self.play_button.setObjectName("playButton")  # Adiciona um nome para estilização
            self.controls_layout.addWidget(self.play_button)
            self.play_button.clicked.connect(self.play_pause)

            self.position_slider = QSlider(Qt.Orientation.Horizontal)
            self.position_slider.setObjectName("positionSlider")  # Adiciona um nome para estilização
            self.position_slider.sliderMoved.connect(self.set_position)
            self.controls_layout.addWidget(self.position_slider)

            self.volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.volume_slider.setObjectName("volumeSlider")  # Adiciona um nome para estilização
            self.volume_slider.setMaximum(100)
            self.volume_slider.setValue(50)
            self.volume_slider.setMaximumWidth(100)
            self.volume_slider.valueChanged.connect(self.set_volume)
            self.controls_layout.addWidget(self.volume_slider)

            self.fullscreen_button = QPushButton("⛶")
            self.fullscreen_button.setObjectName("fullscreenButton")  # Adiciona um nome para estilização
            self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
            self.controls_layout.addWidget(self.fullscreen_button)

            video_layout.addWidget(self.controls_widget)

            self.container_layout.addWidget(self.video_container)

            # Conectar sinais
            self.video_player.playbackStateChanged.connect(self.update_play_button)
            self.video_player.durationChanged.connect(self.update_duration)
            self.audio_output.setVolume(0.5)
            self.video_container.hide()

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

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
        if self.content_type == "text":  # Aplica filtro apenas em conteúdo de texto
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
        # Se um arquivo já estava carregado, parar qualquer reprodução em andamento
        if self.current_file_path:
            self.stop_media()
            self.video_container.hide()  # Esconde o container de vídeo
            self.video_widget.hide()

        self.create_video_player()

        base_path = os.path.join(os.path.dirname(__file__), "Treinamentos")
        text_folder = os.path.join(base_path, "Textos treinamentos")
        video_folder = os.path.join(base_path, "Videos treinamentos")
        pdf_folder = os.path.join(base_path, "PDFs treinamentos")  # Caminho da pasta PDF

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
            # Verificar se há tag de PDF
            pdf_match = re.search(r'\[pdf:(.*?)\]', content)
            if pdf_match:
                pdf_filename = pdf_match.group(1)
                pdf_path = os.path.join(pdf_folder, pdf_filename)  # Caminho completo do PDF

                if os.path.exists(pdf_path):
                    self.load_pdf(pdf_path)
                    return  # Impede o carregamento de conteúdo de texto
                else:
                    content = f"[PDF não encontrado: {pdf_filename}]"  # Exibe mensagem de erro

            processed_content = self.process_content(content, base_path)

            self.load_text_content(processed_content)  # Carrega o conteúdo de texto

        except Exception as e:
            self.content_widget.setText(f"Erro ao carregar arquivo: {str(e)}")

        self.current_file_path = file_path  # Atualiza o caminho do arquivo

    def stop_media(self):
        """Para a reprodução de vídeo e/ou áudio."""
        if self.video_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.video_player.stop()
        if self.audio_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.audio_player.stop()
        self.timer.stop()  # Para o timer de atualização da posição do vídeo

    def process_content(self, content: str, base_path: str) -> str:
        """Processa o conteúdo, substituindo tags de imagem com HTML apropriado."""
        image_folder = os.path.join(base_path, "Imagens treinamentos")

        def replace_image(match):
            image_path = os.path.join(image_folder, match.group(1))
            return f'<img src="{image_path}" />' if os.path.exists(image_path) else f'[Imagem não encontrada: {match.group(1)}]'

        # Substituições no conteúdo
        content = re.sub(r'\[image:(.*?)\]', replace_image, content)
        content = re.sub(r'\[pdf:(.*?)\]', self.replace_pdf, content)  # Substituição da tag PDF
        return content.replace('\n', '<br>')

    def replace_pdf(self, match):
        """Substitui a tag [pdf] com uma chamada para exibir o PDF."""
        pdf_path = match.group(1)  # Obtém o caminho do PDF
        # Se necessário, você pode aqui verificar se o arquivo existe
        return f'<pdf_src>{pdf_path}</pdf_src>'  # Use uma tag personalizada para indicar o PDF

    def load_text_content(self, content: str):
        """Carrega conteúdo de texto no QTextBrowser e aplica as substituições."""
        self.content_widget.setVisible(True)
        self.pdf_view.setVisible(False)
        self.content_type = "text"
        self.search_overlay.show()
        self.original_html = content
        self.content_widget.setHtml(self.original_html)

    def load_pdf(self, file_path: str):
        """Carrega um arquivo PDF no QPdfView."""
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

    def wheelEvent(self, event):
        if self.content_type == "text" and event.modifiers() == Qt.KeyboardModifier.ControlModifier:  # Adicionada condição para o tipo texto
            font = self.content_widget.font()
            font_size = font.pointSize()

            if event.angleDelta().y() > 0:
                font_size += 1
            else:
                font_size -= 1

            if font_size > 0:  # Garante que o tamanho da fonte não seja negativo
                font.setPointSize(font_size)
                self.content_widget.setFont(font)
        elif self.content_type == "pdf" and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                zoom_in(self.pdf_view)
            else:
                zoom_out(self.pdf_view)
            event.accept()
        else:
            super().wheelEvent(event)


class TreinamentosWidget(QWidget):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.treinamentos = []  # Lista de treinamentos
        self.dark_mode = dark_mode  # Estado do modo noturno
        self.setup_ui()
        self.load_treinamentos()
        self.apply_stylesheet()  # Aplicar tema no construtor

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.main_layout = layout

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("treinamentosSplitter")  # Definindo nome para estilização
        layout.addWidget(splitter)

        left_widget = QWidget()
        left_widget.setObjectName("treinamentosLeftWidget")  # Definindo nome para estilização
        left_layout = QVBoxLayout(left_widget)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("treinamentosSearchInput")  # Definindo nome para estilização
        self.search_input.setPlaceholderText("Digite para filtrar treinamentos...")
        left_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setObjectName("treinamentosTable")  # Definindo nome para estilização
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Treinamento", "Descrição"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.clicked.connect(self.show_treinamento)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Desabilita a edição da célula
        left_layout.addWidget(self.table)

        self.content_viewer = ContentViewer()
        self.content_viewer.setObjectName("treinamentosContentViewer")  # Definindo nome para estilização

        splitter.addWidget(left_widget)
        splitter.addWidget(self.content_viewer)
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)  # Adicionando o splitter ao layout

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
            self.content_viewer.load_content(os.path.basename(file_path))  # Passa apenas o nome do arquivo

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
                QLineEdit#treinamentosSearchInput {
                    background-color: #333333;
                    color: #DDDDDD;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                    max-width: 200px;
                }
            """)

            self.table.setStyleSheet("""
                QTableWidget#treinamentosTable {
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
        else:
            self.setStyleSheet("")  # Limpa o estilo para o modo normal

            self.search_input.setStyleSheet("""
                QLineEdit#treinamentosSearchInput {
                    background-color: white;
                    border: 1px solid gray;
                    border-radius: 4px;
                    padding: 4px;
                    max-width: 200px;
                }
            """)

            self.table.setStyleSheet("")