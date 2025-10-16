import sys
import subprocess
import time
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar

class VerificadorThread(QThread):
    progresso = pyqtSignal(int)
    status = pyqtSignal(str)
    finalizado = pyqtSignal()

    def run(self):
        etapas = [
            ("Verificando FFmpeg...", self.verificar_ffmpeg),
            ("Verificando conexão...", self.verificar_internet),
            ("Verificando permissões...", self.verificar_permissoes),
        ]
        total = len(etapas)
        for i, (msg, func) in enumerate(etapas, 1):
            self.status.emit(msg)
            func()
            self.progresso.emit(int((i / total) * 100))
            time.sleep(0.8)
        self.finalizado.emit()

    def verificar_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[StreamCatch] FFmpeg detectado.")
        except FileNotFoundError:
            print("[StreamCatch] FFmpeg ausente.")

    def verificar_internet(self):
        import requests
        try:
            requests.head("https://www.youtube.com", timeout=5)
            print("[StreamCatch] Conexão OK")
        except Exception:
            print("[StreamCatch] Sem conexão com a internet")

    def verificar_permissoes(self):
        import os
        try:
            temp = os.path.join(os.getcwd(), "teste.tmp")
            with open(temp, "w") as f:
                f.write("ok")
            os.remove(temp)
            print("[StreamCatch] Permissões OK")
        except Exception:
            print("[StreamCatch] Sem permissão de escrita")


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 250)
        self.setStyleSheet("background-color: #1a1a1a; color: white; border-radius: 10px;")

        layout = QVBoxLayout()
        self.label = QLabel("Inicializando StreamCatch...", alignment=Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px;")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                background: #222;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #e50914;
            }
        """)
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addStretch()
        self.setLayout(layout)

        self.thread = VerificadorThread()
        self.thread.progresso.connect(self.progress.setValue)
        self.thread.status.connect(self.label.setText)
        self.thread.finalizado.connect(self.abrir_app)
        self.thread.start()

    def abrir_app(self):
        from streamcatch.app import StreamCatchApp
        self.close()
        self.janela = StreamCatchApp()
        self.janela.show()


def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
