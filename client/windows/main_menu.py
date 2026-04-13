from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt


class MainMenu(QWidget):
    def __init__(self, user, api, app):
        super().__init__()

        self.user = user
        self.api = api
        self.app = app

        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    # 🎨 UI
    def init_ui(self):
        role_name = self.get_role_name(self.user["role"])

        title = QLabel(
            f"🔥 Добро пожаловать\n\n{role_name}\n{self.user['full_name']}"
        )
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px;
            color: #ff3b30;
            font-weight: bold;
        """)

        self.layout.addWidget(title)
        self.layout.addSpacing(30)

        self.setup_buttons()

        self.layout.addStretch()

    # 🎯 Кнопки
    def setup_buttons(self):
        role = self.user["role"]

        # 👤 Диспетчер
        if role == "dispatcher":
            self.add_button("➕ Заполнить КУЛП", self.open_create_fire)

        # 🔍 Инспектор
        elif role == "inspector":
            self.add_button("📄 Список КУЛП", self.open_fire_list)

        # 🛠 Админ
        elif role == "admin":
            self.add_button("📄 Все КУЛП", self.open_fire_list)
            self.add_button("👥 Управление пользователями", self.open_users)
            self.add_button("📊 Мониторинг", self.open_monitoring)

        # 📊 Руководитель
        elif role == "chief":
            self.add_button("📊 Мониторинг", self.open_monitoring)

    # 🧩 Кнопка
    def add_button(self, text, handler):
        btn = QPushButton(text)
        btn.clicked.connect(handler)
        self.layout.addWidget(btn)

    def get_role_name(self, role):
        roles = {
            "dispatcher": "Исполнитель-1 (Диспетчер)",
            "inspector": "Исполнитель-2 (Инспектор)",
            "admin": "Администратор",
            "chief": "Руководитель"
        }
        return roles.get(role, role)

    # 📂 Действия
    def open_users(self):
        self.app.go_to_users()

    def open_create_fire(self):
        self.app.go_to_fire_create(self.user)
        print("Создание КУЛП")

    def open_review(self):
        print("Проверка КУЛП")

    def open_all_fires(self):
        print("Все КУЛП")

    def open_edit(self):
        print("Редактирование")

    def open_monitoring(self):
        print("Мониторинг")

    def open_fire_list(self):
        self.app.go_to_fire_list(self.user)
    
    def open_fire(self, fire_id):
        self.app.go_to_fire_edit(self.user, fire_id)