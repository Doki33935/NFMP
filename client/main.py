import sys
from PySide6.QtWidgets import QApplication

from services.api_client import ApiClient
from app import App


def main():
    app_qt = QApplication(sys.argv)

    # Глобальный стиль приложения
    app_qt.setStyleSheet("""
        QWidget {
            background-color: #181a1f;
            color: #f4f7fb;
            font-family: Segoe UI;
            font-size: 14px;
        }

        /* ===== INPUTS ===== */
        QLineEdit, QComboBox, QPlainTextEdit {
            padding: 8px;
            border-radius: 6px;
            background-color: #23262d;
            color: #f4f7fb;
            border: 1px solid #3a3f49;
            selection-background-color: #dc2626;
            selection-color: #ffffff;
            min-height: 30px;
        }

        QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
            border-color: #ef4444;
        }

        QLineEdit:disabled, QComboBox:disabled, QPlainTextEdit:disabled {
            color: #8d96a6;
            background-color: #1f2229;
        }

        QComboBox QAbstractItemView {
            background-color: #23262d;
            color: #f4f7fb;
            selection-background-color: #ef4444;
            selection-color: #ffffff;
            outline: 0;
        }

        QComboBox::drop-down {
            border: none;
            width: 28px;
        }

        /* ===== BUTTONS ===== */
        QPushButton {
            padding: 9px 14px;
            border-radius: 6px;
            background-color: #dc2626;
            color: white;
            font-weight: bold;
            min-width: 140px;
            min-height: 36px;
        }

        QPushButton:hover {
            background-color: #ef4444;
        }

        /* вторичная кнопка (назад) */
        QPushButton#secondary {
            background-color: #343944;
        }

        QPushButton#secondary:hover {
            background-color: #444b58;
        }

        QPushButton#iconButton {
            min-width: 0;
            max-width: 36px;
            padding: 8px;
            background-color: #343944;
        }

        /* ===== TABS ===== */
        QTabWidget::pane {
            border: 1px solid #333;
            border-radius: 8px;
            padding: 10px;
            background: #20232a;
        }

        QTabBar::tab {
            background: #23262d;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 4px;
        }

        QTabBar::tab:selected {
            background: #dc2626;
        }

        /* ===== LABELS ===== */
        QLabel {
            color: #eef2f8;
            font-size: 13px;
            background: transparent;
        }

        QLabel#pageTitle {
            color: #ffffff;
            font-size: 22px;
            font-weight: 700;
            padding: 4px 0 8px 0;
        }

        QLabel#sectionTitle {
            color: #f87171;
            font-size: 16px;
            font-weight: 700;
        }

        QLabel#muted {
            color: #aab1bf;
        }

        QLabel#fieldTitle {
            color: #d8dee9;
            font-size: 14px;
            font-weight: 700;
        }

        QFrame#section {
            background: #20232a;
            border: 1px solid #303641;
            border-radius: 8px;
        }

        QFrame#participantRow {
            background: #23262d;
            border: 1px solid #353b46;
            border-radius: 6px;
        }
    """)

    # API
    api = ApiClient()

    # Основное приложение
    window = App(api)
    window.setWindowTitle("NFMP - учет ландшафтных пожаров")
    window.resize(980, 720)
    window.show()

    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()
