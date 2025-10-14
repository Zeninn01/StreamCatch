# Interface criada com Qt Designer (ou manual)

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        MainWindow.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #f0f0f0;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #c0392b;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #c0392b;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QProgressBar {
                border: 1px solid #c0392b;
                border-radius: 8px;
                text-align: center;
                color: #ffffff;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #c0392b;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #c0392b;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px;
            }
        """)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        # Campo de link
        self.url_input = QtWidgets.QLineEdit(self.centralwidget)
        self.url_input.setPlaceholderText("Cole o link do YouTube aqui...")
        self.verticalLayout.addWidget(self.url_input)

        # Botões
        self.button_layout = QtWidgets.QHBoxLayout()
        self.btn_video = QtWidgets.QPushButton("🎬 Baixar Vídeo")
        self.btn_audio = QtWidgets.QPushButton("🎵 Baixar Música")
        self.button_layout.addWidget(self.btn_video)
        self.button_layout.addWidget(self.btn_audio)
        self.verticalLayout.addLayout(self.button_layout)

        # Barra de progresso
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setValue(0)
        self.verticalLayout.addWidget(self.progress_bar)

        # Log
        self.log_area = QtWidgets.QTextEdit(self.centralwidget)
        self.log_area.setReadOnly(True)
        self.verticalLayout.addWidget(self.log_area)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "StreamCatch"))
