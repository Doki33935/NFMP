from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt, QObject, Signal, QThread, QMetaObject


class LoginWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, api, username, password):
        super().__init__()
        self.api = api
        self.username = username
        self.password = password

    def run(self):
        try:
            user = self.api.login(self.username, self.password)
            self.finished.emit(user)
        except Exception as e:
            self.error.emit(str(e))

class LoginWindow(QWidget):
    def __init__(self, api, app):
        super().__init__()

        self.api = api
        self.app = app

        self.thread = None
        self.worker = None

        self.setMinimumSize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Система учета\nландшафтных пожаров")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ff3b30;
        """)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Логин")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Начать работу")
        self.login_btn.clicked.connect(self.handle_login)

        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")
        self.error.setAlignment(Qt.AlignCenter)

        self.password.returnPressed.connect(self.handle_login)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.error)
        layout.addStretch()

        self.setLayout(layout)

    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            self.error.setText("Введите логин и пароль")
            return

        self.error.setText("")
        self.set_loading(True)

        # 🔥 thread
        self.thread = QThread()
        self.worker = LoginWorker(self.api, username, password)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.thread.finished.connect(self.cleanup)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
    
    def on_success(self, user):
        self.set_loading(False)
        self.app.go_to_main(user)

    def on_error(self, message):
        self.set_loading(False)
        self.error.setText(message)

    def set_loading(self, state: bool):
        self.login_btn.setEnabled(not state)

        if state:
            self.login_btn.setText("Вход...")
        else:
            self.login_btn.setText("Начать работу")
        
    def cleanup(self):
        self.thread = None
        self.worker = None