from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self, api):
        super().__init__()

        self.api = api

        self.setWindowTitle("NFMP - Система учета пожаров")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout()

        # 🔥 Заголовок
        title = QLabel("🔥 Система учета\nландшафтных пожаров")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
        """)

        # Логин
        self.username = QLineEdit()
        self.username.setPlaceholderText("Логин")

        # Пароль
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.Password)

        # Кнопка
        login_btn = QPushButton("Начать работу")
        login_btn.clicked.connect(self.handle_login)

        # Ошибка
        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(self.error)
        layout.addStretch()

        self.setLayout(layout)

        # 🎨 стиль
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                padding: 12px;
                border-radius: 10px;
                background-color: #ff3b30;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5c50;
            }
        """)

    def handle_login(self):
        username = self.username.text()
        password = self.password.text()

        try:
            self.api.login(username, password)
            self.error.setText("Успешный вход 🚀")

            # 👉 дальше откроем главное меню
        except Exception as e:
            self.error.setText("Ошибка входа")