import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFontMetrics
import yt_dlp


class FetchQualitiesThread(QThread):
    qualities_found = pyqtSignal(list, str, str)  # qualidades, título, thumbnail
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            ydl_opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            title = info.get("title", "Título não disponível")
            thumbnail_url = info.get("thumbnail", "")

            # Filtra somente resoluções de vídeo válidas
            formats = info.get("formats", [])
            qualities = sorted(
                {f.get("height") for f in formats if f.get("height")},
                reverse=True
            )
            qualities = [f"{q}p" for q in qualities] if qualities else ["Qualidade não disponível"]

            self.qualities_found.emit(qualities, title, thumbnail_url)
        except Exception as e:
            self.error.emit(f"Erro ao processar vídeo: {e}")


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, save_path, quality, mode):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.quality = quality
        self.mode = mode

    def run(self):
        try:
            out_template = os.path.join(self.save_path, "%(title)s.%(ext)s")
            ydl_opts = {
                "outtmpl": out_template,
                "progress_hooks": [self.hook],
                "quiet": True,
            }

            if self.mode == "Música (MP3)":
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }]
                })
            else:  # Vídeo MP4
                # Converte o valor "1080p" para número
                height = self.quality.rstrip("p")
                ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.finished.emit(f"✅ Download concluído!\nSalvo em: {self.save_path}")
        except Exception as e:
            self.finished.emit(f"❌ Erro ao baixar: {e}")

    def hook(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                percent = int(downloaded / total * 100)
                self.progress.emit(percent)
        elif d.get("status") == "finished":
            self.progress.emit(100)


class StreamCatch(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("StreamCatch")
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #f0f0f0; font-family: 'Segoe UI'; font-size: 14px; }
            QPushButton { background-color: #e50914; color: white; border: none; padding: 10px; border-radius: 6px; }
            QPushButton:hover { background-color: #b20710; }
            QLineEdit, QComboBox { background-color: #1e1e1e; border: 1px solid #333; border-radius: 4px; padding: 6px; color: #f0f0f0; }
        """)

        layout = QVBoxLayout()

        # URL
        self.url_label = QLabel("URL do vídeo/música:")
        self.url_input = QLineEdit()
        self.url_input.textChanged.connect(self.on_url_changed)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Miniatura + título
        self.title_thumb_layout = QHBoxLayout()
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(80, 45)
        self.thumbnail_label.setStyleSheet("border: 2px solid #e50914; border-radius: 6px;")
        self.title_label = QLabel("")
        self.title_label.setWordWrap(False)
        self.title_label.setStyleSheet("color: #f0f0f0;")
        self.title_thumb_layout.addWidget(self.thumbnail_label)
        self.title_thumb_layout.addWidget(self.title_label)
        layout.addLayout(self.title_thumb_layout)

        # Tipo
        self.mode_label = QLabel("Tipo de download:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Vídeo (MP4)", "Música (MP3)"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_combo)

        # Qualidade
        self.quality_label = QLabel("Qualidade do vídeo:")
        self.quality_combo = QComboBox()
        self.quality_combo.setEnabled(False)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)

        # Pasta de destino
        self.path_button = QPushButton("Escolher pasta de destino")
        self.path_button.clicked.connect(self.select_path)
        layout.addWidget(self.path_button)
        self.path_display = QLabel("Pasta de destino: (não selecionada)")
        layout.addWidget(self.path_display)

        # Botão de download
        self.download_button = QPushButton("Iniciar download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.save_path = ""

    def elide_text(self, text, max_width, label):
        metrics = QFontMetrics(label.font())
        return metrics.elidedText(text, Qt.ElideRight, max_width)

    def on_url_changed(self):
        url = self.url_input.text().strip()
        if "youtube.com" in url or "youtu.be" in url:
            self.quality_combo.clear()
            self.quality_combo.addItem("Carregando qualidades...")
            self.quality_combo.setEnabled(False)
            self.title_label.setText("Carregando título...")
            self.thumbnail_label.clear()

            self.thread_qualities = FetchQualitiesThread(url)
            self.thread_qualities.qualities_found.connect(self.update_qualities)
            self.thread_qualities.error.connect(self.show_error)
            self.thread_qualities.start()

    def update_qualities(self, qualities, title, thumbnail_url):
        self.quality_combo.clear()
        self.quality_combo.addItems(qualities)
        self.quality_combo.setEnabled(True)
        self.title_label.setText(self.elide_text(title, 300, self.title_label))

        try:
            response = requests.get(thumbnail_url)
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.thumbnail_label.setPixmap(pixmap.scaled(80, 45, Qt.KeepAspectRatio))
        except:
            self.thumbnail_label.clear()

    def show_error(self, error_msg):
        self.quality_combo.clear()
        self.quality_combo.addItem("Erro ao obter qualidades")
        self.quality_combo.setEnabled(False)
        self.title_label.setText("")
        self.thumbnail_label.clear()
        QMessageBox.warning(self, "Erro", error_msg)

    def on_mode_changed(self):
        mode = self.mode_combo.currentText()
        if mode == "Música (MP3)":
            self.quality_combo.setEnabled(False)
            self.quality_combo.clear()
            self.quality_combo.addItem("Não aplicável (áudio apenas)")
        else:
            self.on_url_changed()

    def select_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Escolher pasta para salvar")
        if folder:
            self.save_path = folder
            self.path_display.setText(f"Pasta de destino: {folder}")

    def start_download(self):
        url = self.url_input.text().strip()
        mode = self.mode_combo.currentText()
        quality = self.quality_combo.currentText()

        if not url:
            QMessageBox.warning(self, "Erro", "Informe a URL do vídeo ou música!")
            return
        if not self.save_path:
            QMessageBox.warning(self, "Erro", "Escolha uma pasta de destino!")
            return

        self.download_button.setEnabled(False)
        self.progress.setValue(0)

        self.thread = DownloadThread(url, self.save_path, quality, mode)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.download_finished)
        self.thread.start()

    def download_finished(self, message):
        QMessageBox.information(self, "StreamCatch", message)
        self.download_button.setEnabled(True)
        self.progress.setValue(100)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StreamCatch()
    window.resize(460, 450)
    window.show()
    sys.exit(app.exec_())
