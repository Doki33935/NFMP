from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

from services.role_service import RoleService


class MainMenu(QWidget):
    def __init__(self, user, app):
        super().__init__()

        self.user = user
        self.app = app

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        role_name = RoleService.get_role_name(self.user.role)

        title = QLabel(
            f"🔥 Добро пожаловать\n\n{role_name}\n{self.user.full_name}"
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

    def setup_buttons(self):
        actions = RoleService.get_actions(self.user.role)

        for action in actions:
            self.add_action_button(action)

    def add_action_button(self, action):
        mapping = {
            "create_fire": ("➕ Заполнить КУЛП", self.open_create_fire),
            "fire_list": ("📄 Список КУЛП", self.open_fire_list),
            "users": ("👥 Управление пользователями", self.open_users),
            "monitoring": ("📊 Мониторинг", self.open_monitoring),
        }

        text, handler = mapping[action]

        btn = QPushButton(text)
        btn.clicked.connect(handler)

        self.layout.addWidget(btn)

    def open_users(self):
        self.app.go_to_users()

    def open_create_fire(self):
        self.app.go_to_fire_create()

    def open_monitoring(self):
        print("Мониторинг")

    def open_fire_list(self):
        self.app.go_to_fire_list()