import sys
from PySide6.QtWidgets import QApplication

from services.api_client import ApiClient
from app import App


def main():
    app_qt = QApplication(sys.argv)

    # 🎨 Глобальный стиль приложения
    app_qt.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: white;
            font-family: Segoe UI;
        }

        QLineEdit {
            padding: 10px;
            border-radius: 8px;
            background-color: #2b2b2b;
            border: 1px solid #444;
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

    # 🔌 API
    api = ApiClient()

    # 🧠 Основное приложение
    window = App(api)
    window.setWindowTitle("🔥 NFMP - Учет пожаров")
    window.resize(500, 600)
    window.show()

    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()