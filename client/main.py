import sys
from PySide6.QtWidgets import QApplication

from services.api_client import ApiClient
from app import App


def main():
    app_qt = QApplication(sys.argv)

    # Глобальный стиль приложения
    app_qt.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: white;
            font-family: Segoe UI;
            font-size: 14px;
        }

        /* ===== INPUTS ===== */
        QLineEdit, QComboBox {
            padding: 8px;
            border-radius: 8px;
            background-color: #2b2b2b;
            border: 1px solid #444;
            min-height: 30px;
        }

        QComboBox QAbstractItemView {
            background-color: #2b2b2b;
            selection-background-color: #ff3b30;
        }

        /* ===== BUTTONS ===== */
        QPushButton {
            padding: 10px;
            border-radius: 8px;
            background-color: #ff3b30;
            color: white;
            font-weight: bold;
            min-width: 140px;
            min-height: 36px;
        }

        QPushButton:hover {
            background-color: #ff5c50;
        }

        /* вторичная кнопка (назад) */
        QPushButton#secondary {
            background-color: #444;
        }

        QPushButton#secondary:hover {
            background-color: #555;
        }

        /* ===== TABS ===== */
        QTabWidget::pane {
            border: 1px solid #333;
            border-radius: 10px;
            padding: 10px;
            background: #252525;
        }

        QTabBar::tab {
            background: #2b2b2b;
            padding: 8px 16px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 4px;
        }

        QTabBar::tab:selected {
            background: #ff3b30;
        }

        /* ===== LABELS ===== */
        QLabel {
            font-size: 13px;
        }
    """)

    # API
    api = ApiClient()

    # Основное приложение
    window = App(api)
    window.setWindowTitle("NFMP - Учет ландшафтных пожаров")
    window.resize(500, 600)
    window.show()

    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()