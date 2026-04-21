from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QDate


class FireDateWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.current_date = QDate.currentDate()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # ←
        self.btn_prev = QPushButton("◀")
        self.btn_prev.clicked.connect(self.prev_day)

        # дата
        self.label = QLabel()
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.label.setMinimumWidth(150)

        # →
        self.btn_next = QPushButton("▶")
        self.btn_next.clicked.connect(self.next_day)

        self.layout.addWidget(self.btn_prev)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn_next)

        self.update_label()
        self.update_limits()

    # =========================
    # ЛОГИКА
    # =========================
    def prev_day(self):
        self.current_date = self.current_date.addDays(-1)
        self.update_label()
        self.update_limits()

    def next_day(self):
        today = QDate.currentDate()

        # ❌ запрещаем будущее
        if self.current_date >= today:
            return

        self.current_date = self.current_date.addDays(1)
        self.update_label()
        self.update_limits()

    # =========================
    # UI
    # =========================
    def update_label(self):
        self.label.setText(self.current_date.toString("dd.MM.yyyy"))

    def update_limits(self):
        today = QDate.currentDate()

        # кнопка вперёд блокируется на "сегодня"
        self.btn_next.setEnabled(self.current_date < today)

    # =========================
    # API
    # =========================
    def value(self):
        return self.current_date.toPython()