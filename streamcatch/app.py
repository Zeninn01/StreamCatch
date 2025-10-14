import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QHBoxLayout, QProgressBar
)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt

class StreamCatch(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StreamCatch")
        self.setGeometry(300, 150, 600, 350)
        self.setWindowIcon(QIcon())  # depois podemos colocar o ícone oficial

        # Cores do tema
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))  # fundo preto
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        # Layout principal
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Título
        title = QLabel("🎧 StreamCatch")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E50914; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Campo de link
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Cole aqui o link do YouTube...")
        self.url_input.setStyleSheet("""
            background-color: #1E1E1E;
            color: white;
            border: 2px solid #E50914;
            border-radius: 8px;
            padding: 8px;
        """)
        layout.addWidget(self.url_input)

        # Botões
        button_layout = QHBoxLayout()
        self.download_video_btn = QPushButton("Baixar Vídeo")
        self.download_audio_btn = QPushButton("Baixar Áudio")

        for btn in [self.download_video_btn, self.download_audio_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E50914;
                    color: white;
                    border-radius: 8px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #B00610;
                }
            """)

        button_layout.addWidget(self.download_video_btn)
        button_layout.addWidget(self.download_audio_btn)
        layout.addLayout(button_layout)

        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #E50914;
                border-radius: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #E50914;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress)

        # Status
        self.status_label = QLabel("Aguardando link...")
        self.status_label.setStyleSheet("color: gray;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StreamCatch()
    window.show()
    sys.exit(app.exec_())
