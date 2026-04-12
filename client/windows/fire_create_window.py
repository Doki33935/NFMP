from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QTimeEdit, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from widgets.fire_date_widget import FireDateWidget


class FireCreateWindow(QWidget):
    def __init__(self, api, app, user):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.init_ui()

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    # 🎨 UI ENTRY
    def init_ui(self):

        # 🔥 БЛОК 1 — Событие (ВАЖНЕЙШИЙ)
        self.tabs.addTab(self.tab_fire_event(), "🔥 Пожар")

        # 🧭 БЛОК 2 — Локация
        self.tabs.addTab(self.tab_location(), "🧭 Локация")

        # 🧑‍🚒 БЛОК 3 — Контекст
        self.tabs.addTab(self.tab_context(), "🧑‍🚒 Контекст")

        # ⚙ БЛОК 4 — Система
        self.tabs.addTab(self.tab_system(), "⚙ Система")

        save_btn = QPushButton("💾 Сохранить КУЛП")
        save_btn.clicked.connect(self.save)

        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.app.go_back)

        self.layout.addWidget(save_btn)
        self.layout.addWidget(back_btn)

    # 🔥 БЛОК 1 — Событие пожара
    def tab_fire_event(self):
        w = QWidget()
        f = QFormLayout()

        self.date = FireDateWidget()
        self.time_msg = QTimeEdit()

        self.land_type = QComboBox()
        self.land_type.addItems(["лес", "сухая трава"])

        self.fire_type = QComboBox()
        self.fire_type.addItems(["низовой", "верховой", "торфяной"])

        self.area = QLineEdit()

        f.addRow("Дата пожара", self.date)
        f.addRow("Время сообщения", self.time_msg)
        f.addRow("Состав земель", self.land_type)
        f.addRow("Вид пожара", self.fire_type)
        f.addRow("Площадь", self.area)

        w.setLayout(f)
        return w

    # 🧭 БЛОК 2 — Локация
    def tab_location(self):
        w = QWidget()
        f = QFormLayout()

        self.address = QLineEdit()
        self.comment = QLineEdit()
        self.mo = QComboBox()
        self.selsovet = QComboBox()
        self.coords = QLabel("📍 координаты (карта позже)")

        f.addRow("Адрес", self.address)
        f.addRow("Комментарий", self.comment)
        f.addRow("Муниципальное образование", self.mo)
        f.addRow("Сельсовет", self.selsovet)
        f.addRow("Координаты", self.coords)

        w.setLayout(f)
        return w

    # 🧑‍🚒 БЛОК 3 — Контекст
    def tab_context(self):
        w = QWidget()
        f = QFormLayout()

        self.forestry = QComboBox()
        self.right_of_way = QComboBox()
        self.owner = QLineEdit()
        self.source = QLineEdit()
        self.extra = QLineEdit()

        self.forestry.addItems(["нет", "есть"])
        self.right_of_way.addItems(["нет", "жд", "авто", "лэп"])

        f.addRow("Лесничество", self.forestry)
        f.addRow("Полосы отвода", self.right_of_way)
        f.addRow("Правообладатель", self.owner)
        f.addRow("Источник", self.source)
        f.addRow("Доп. инфо", self.extra)

        w.setLayout(f)
        return w

    # ⚙ БЛОК 4 — Система
    def tab_system(self):
        w = QWidget()
        f = QFormLayout()

        self.fio_dispatcher = QLabel(self.user["full_name"])
        self.fio_inspector = QLabel("—")

        self.status = QLabel("DRAFT")
        self.service_time = QLabel("auto")

        f.addRow("Диспетчер", self.fio_dispatcher)
        f.addRow("Инспектор", self.fio_inspector)
        f.addRow("Статус", self.status)
        f.addRow("Обслуживание", self.service_time)

        w.setLayout(f)
        return w

    # 💾 SAVE
    def save(self):
        data = {
            "date": self.date.date().toString(),
            "time_msg": self.time_msg.time().toString(),
            "land_type": self.land_type.currentText(),
            "fire_type": self.fire_type.currentText(),
            "area": self.area.text(),

            "address": self.address.text(),
            "comment": self.comment.text(),
            "mo": self.mo.currentText(),
            "selsovet": self.selsovet.currentText(),

            "forestry": self.forestry.currentText(),
            "right_of_way": self.right_of_way.currentText(),
            "owner": self.owner.text(),
            "source": self.source.text(),
            "extra": self.extra.text(),

            "dispatcher_fio": self.user["full_name"],
        }

        self.api.create_fire(data)
        print("КУЛП сохранён")