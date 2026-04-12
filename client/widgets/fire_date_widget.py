from PySide6.QtWidgets import QDateEdit, QCalendarWidget
from PySide6.QtCore import QDate
from PySide6.QtGui import QColor, QTextCharFormat


class FireDateWidget(QDateEdit):
    def __init__(self):
        super().__init__()

        # 📅 базовые настройки
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())
        self.setDisplayFormat("dd.MM.yyyy")
        self.setMaximumDate(QDate.currentDate())

        # 📅 календарь (ВАЖНО: parent = self)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        # ❌ убираем номера недель
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        self.setCalendarWidget(self.calendar)

        # 🎨 стиль календаря
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #1e1e1e;
                color: white;
            }

            QCalendarWidget QToolButton {
                background-color: #2b2b2b;
                color: white;
                border-radius: 6px;
                padding: 5px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #ff3b30;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: #ff3b30;
                selection-color: white;
                background-color: #1e1e1e;
                gridline-color: #333;
            }

            QCalendarWidget QHeaderView::section {
                background-color: #2b2b2b;
                color: white;
                padding: 4px;
                border: none;
            }
        """)

        # 🎨 стиль input (ВАЖНО: убрали arrow hack)
        self.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border-radius: 8px;
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3a3a3a;
            }

            QDateEdit:hover {
                border: 1px solid #ff3b30;
            }

            QDateEdit::drop-down {
                width: 28px;
                border-left: 1px solid #3a3a3a;
                background: #2b2b2b;
            }

            QDateEdit::down-arrow {
                image: none;
            }
        """)

        # 🔥 стабильная подсветка (ТОЛЬКО текущий месяц)
        self.calendar.currentPageChanged.connect(self._highlight_weekends)
        self._highlight_weekends()

    # 🔥 стабильная логика выходных (без перебора 2 лет!)
    def _highlight_weekends(self):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#ff5c5c"))

        year = self.calendar.yearShown()
        month = self.calendar.monthShown()

        first = QDate(year, month, 1)

        for i in range(42):  # максимум клеток календаря
            d = first.addDays(i)

            if d.month() != month:
                continue

            if d.dayOfWeek() in (6, 7):
                self.calendar.setDateTextFormat(d, fmt)