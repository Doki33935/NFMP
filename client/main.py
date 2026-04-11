import sys
from PySide6.QtWidgets import QApplication

from services.api_client import ApiClient
from windows.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)

    api = ApiClient()

    window = LoginWindow(api)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()