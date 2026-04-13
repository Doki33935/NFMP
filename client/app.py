from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout

from windows.login_window import LoginWindow
from windows.main_menu import MainMenu
from windows.fire_create_window import FireCreateWindow
from windows.users_window import UsersWindow
from windows.fire_list_window import FireListWindow
from windows.fire_edit_window import FireEditWindow

class App(QWidget):
    def __init__(self, api):
        super().__init__()

        self.api = api

        self.stack = QStackedWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # кеш экранов (lazy cache)
        self.screens = {}

        self.go_to_login()

    def show_screen(self, name, builder):
        if name not in self.screens:
            self.screens[name] = builder()
            self.stack.addWidget(self.screens[name])

        self.stack.setCurrentWidget(self.screens[name])

    # 🔐 LOGIN
    def go_to_login(self):
        self.show_screen("login", lambda: LoginWindow(self.api, self))

    # 🏠 MAIN MENU
    def go_to_main(self, user):
        self.user = user
        self.show_screen("main", lambda: MainMenu(user, self.api, self))

    # 👥 USERS
    def go_to_users(self):
        self.show_screen(
            "users",
            lambda: UsersWindow(self.api, self)
        )

    # 🔥 CREATE FIRE
    def go_to_fire_create(self, user):
        self.show_screen(
            "fire_create",
            lambda: FireCreateWindow(self.api, self, user)
        )

    # 🔙 назад (к главному меню)
    def go_back(self):
        self.stack.setCurrentWidget(self.screens["main"])

    def go_to_fire_list(self, user):
        self.show_screen(
            "fire_list",
            lambda: FireListWindow(self.api, self, user)
        )


    def go_to_fire_edit(self, user, fire_id):
        self.show_screen(
            "fire_edit",
            lambda: FireEditWindow(self.api, self, user, fire_id)
        )