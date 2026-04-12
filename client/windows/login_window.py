from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self, api, app):
        super().__init__()

        self.api = api
        self.app = app

        self.setMinimumSize(400, 500)

        self.init_ui()

    # 🎨 UI
    def init_ui(self):
        layout = QVBoxLayout()

        # 🔥 Заголовок
        title = QLabel("🔥 Система учета\nландшафтных пожаров")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ff3b30;
        """)

        # 👤 Логин
        self.username = QLineEdit()
        self.username.setPlaceholderText("Логин")

        # 🔒 Пароль
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.Password)

        # ▶ Кнопка
        login_btn = QPushButton("Начать работу")
        login_btn.clicked.connect(self.handle_login)

        # ❌ Ошибка
        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")
        self.error.setAlignment(Qt.AlignCenter)

        # 🔥 UX — Enter для входа
        self.password.returnPressed.connect(self.handle_login)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(self.error)
        layout.addStretch()

        self.setLayout(layout)

    # 🔐 Логика входа
    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            self.error.setText("Введите логин и пароль")
            return

        try:
            user = self.api.login(username, password)

            # 👉 переход через stack
            self.app.go_to_main(user)

        except Exception as e:
            print(e)
            self.error.setText("Неверный логин или пароль")