import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QComboBox,
    QFileDialog, QMessageBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from urllib.request import urlopen
from io import BytesIO
import yt_dlp

class DownloaderThread(QThread):
    progresso = pyqtSignal(int)
    mensagem = pyqtSignal(str)
    finalizado = pyqtSignal()

    def __init__(self, url, tipo, pasta, format_id=None):
        super().__init__()
        self.url = url
        self.tipo = tipo
        self.pasta = pasta
        self.format_id = format_id

    def run(self):
        try:
            self.mensagem.emit("Conectando ao YouTube...")
            ydl_opts = {
                "outtmpl": os.path.join(self.pasta, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progresso_hook],
                "quiet": True,
            }
            if self.format_id:
                ydl_opts["format"] = self.format_id

            if self.tipo == "Música (MP3)":
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.mensagem.emit("Download concluído!")
        except Exception as e:
            self.mensagem.emit(f"Erro: {e}")
        finally:
            self.finalizado.emit()

    def progresso_hook(self, d):
        if d.get("status") == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                self.progresso.emit(int(float(percent)))
            except:
                self.progresso.emit(0)

class StreamCatchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StreamCatch Beta")
        self.setGeometry(150, 150, 900, 600)
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: white; font-size: 14px; }
            QPushButton { background-color: #e50914; color: white; border-radius: 6px; padding: 10px; }
            QPushButton:hover { background-color: #f44336; }
            QLineEdit { background-color: #1e1e1e; padding: 8px; border-radius: 6px; border: 1px solid #333; color: white; }
            QComboBox { background-color: #1e1e1e; color: white; border-radius: 6px; padding: 5px; border: 1px solid #333; }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Título
        titulo = QLabel("🎬 StreamCatch", alignment=Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: #e50914;")
        layout.addWidget(titulo)

        # Campo URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Cole o link do vídeo do YouTube aqui...")
        self.url_input.textChanged.connect(self.atualizar_video_info)  # chama ao colar link
        layout.addWidget(self.url_input)

        # Miniatura
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(320, 180)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("border: 2px solid #e50914; border-radius: 6px; background: #000;")
        layout.addWidget(self.thumb_label, alignment=Qt.AlignCenter)

        # Pasta de download
        pasta_layout = QHBoxLayout()
        self.pasta_label = QLabel("Destino: Nenhuma pasta selecionada")
        self.botao_pasta = QPushButton("Escolher pasta")
        self.botao_pasta.clicked.connect(self.escolher_pasta)
        pasta_layout.addWidget(self.pasta_label)
        pasta_layout.addWidget(self.botao_pasta)
        layout.addLayout(pasta_layout)

        # Tipo de download
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Vídeo (MP4)", "Música (MP3)"])
        self.combo_tipo.currentTextChanged.connect(self.atualizar_video_info)
        layout.addWidget(self.combo_tipo)

        # Qualidade
        self.combo_qualidade = QComboBox()
        layout.addWidget(self.combo_qualidade)

        # Botão baixar
        self.botao_baixar = QPushButton("Baixar")
        self.botao_baixar.clicked.connect(self.iniciar_download)
        layout.addWidget(self.botao_baixar)

        # Barra de progresso
        self.progresso = QProgressBar()
        layout.addWidget(self.progresso)

        # Mensagem
        self.mensagem = QLabel("", alignment=Qt.AlignCenter)
        layout.addWidget(self.mensagem)

        # Marca d'água / Sobre
        self.marca = QLabel("StreamCatch Beta - Desenvolvido por Ailton Junior", alignment=Qt.AlignRight)
        self.marca.setStyleSheet("font-size: 10px; color: #888888; margin-top: 10px;")
        layout.addWidget(self.marca)

        self.setLayout(layout)
        self.pasta_saida = os.getcwd()
        self.video_info = None

    def escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Escolher pasta de destino")
        if pasta:
            self.pasta_saida = pasta
            self.pasta_label.setText(f"Destino: {pasta}")

    def atualizar_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            return
        try:
            ydl_opts = {"quiet": True, "skip_download": True, "no_warnings": True, "ignoreerrors": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_info = info
        except Exception as e:
            self.mensagem.setText(f"Erro ao obter info: {e}")
            return

        # Atualizar thumbnail
        try:
            if info.get("thumbnails"):
                thumb_url = info["thumbnails"][-1].get("url")
                if thumb_url:
                    data = urlopen(thumb_url).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    self.thumb_label.setPixmap(pixmap.scaled(self.thumb_label.width(), self.thumb_label.height(), Qt.KeepAspectRatio))
        except:
            pass

        # Popular combo de qualidade (limpando duplicatas)
        self.combo_qualidade.clear()
        tipo = self.combo_tipo.currentText()
        if tipo == "Vídeo (MP4)":
            video_formats = [f for f in info["formats"] if f.get("vcodec") != "none"]
            res_dict = {}
            for f in video_formats:
                h = f.get("height")
                if h:
                    if h not in res_dict or f.get("filesize", 0) > res_dict[h].get("filesize", 0):
                        res_dict[h] = f
            for h in sorted(res_dict.keys(), reverse=True):
                f = res_dict[h]
                label = f"{h}p"
                self.combo_qualidade.addItem(label, f.get("format_id"))
        else:  # Música
            audio_formats = [f for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            abr_dict = {}
            for f in audio_formats:
                abr = f.get("abr") or 128
                if abr not in abr_dict or f.get("filesize", 0) > abr_dict[abr].get("filesize", 0):
                    abr_dict[abr] = f
            for abr in sorted(abr_dict.keys(), reverse=True):
                f = abr_dict[abr]
                label = f"{abr} kbps"
                self.combo_qualidade.addItem(label, f.get("format_id"))

    def iniciar_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Atenção", "Por favor, insira um link válido.")
            return
        tipo = self.combo_tipo.currentText()
        format_id = self.combo_qualidade.currentData()
        self.thread = DownloaderThread(url, tipo, self.pasta_saida, format_id=format_id)
        self.thread.progresso.connect(self.progresso.setValue)
        self.thread.mensagem.connect(self.mensagem.setText)
        self.thread.finalizado.connect(lambda: QMessageBox.information(self, "Concluído", "Download finalizado!"))
        self.thread.start()

def iniciar_interface_principal():
    """Chamada pelo main.py"""
    janela = StreamCatchApp()
    janela.show()
