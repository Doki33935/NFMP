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
        self.user = None

        self.stack = QStackedWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.screens = {}

        self.go_to_login()

    # =========================
    # NAVIGATION
    # =========================

    def go_to_login(self):
        self._show("login", lambda: LoginWindow(self.api, self))

    def go_to_main(self, user):
        self.user = user
        self._reset_screens(except_keys={"login"})

        self._show("main", lambda: MainMenu(user, self))

    def go_to_users(self):
        self._show("users", lambda: UsersWindow(self.api, self))

    def go_to_fire_create(self):
        self._show(
            "fire_create",
            lambda: FireCreateWindow(self.api, self, self.user)
        )

    def go_to_fire_list(self):
        self._show(
            "fire_list",
            lambda: FireListWindow(self.api, self, self.user)
        )

    def go_to_fire_edit(self, fire_id):
        key = f"fire_edit_{fire_id}"

        self._show(
            key,
            lambda: FireEditWindow(self.api, self, self.user, fire_id)
        )

    # =========================
    # CORE NAV SYSTEM
    # =========================

    def _show(self, name, builder):
        if name not in self.screens:
            self.screens[name] = builder()
            self.stack.addWidget(self.screens[name])

        self.stack.setCurrentWidget(self.screens[name])

    def _reset_screens(self, except_keys=None):
        except_keys = set(except_keys or [])

        for key in list(self.screens.keys()):
            if key in except_keys:
                continue

            widget = self.screens.pop(key)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def go_back(self):
        if "main" in self.screens:
            self.stack.setCurrentWidget(self.screens["main"])