from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTabWidget, QFormLayout
)


class FireEditWindow(QWidget):
    def __init__(self, api, app, user, fire_id):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user
        self.fire_id = fire_id

        self.setWindowTitle(f"КУЛП #{fire_id}")
        self.setMinimumSize(900, 700)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_data()
        self.build_ui()

    # =========================
    # LOAD
    # =========================
    def load_data(self):
        self.fire = self.api.get_fire(self.fire_id)

    # =========================
    # UI ROOT
    # =========================
    def build_ui(self):
        self.title = QLabel(f"🔥 Редактирование КУЛП #{self.fire_id}")
        self.layout.addWidget(self.title)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab_location = self.build_tab_location()
        self.tab_fire = self.build_tab_fire()
        self.tab_extra = self.build_tab_extra()

        self.tabs.addTab(self.tab_location, "🧭 Локация")
        self.tabs.addTab(self.tab_fire, "🔥 Пожар")
        self.tabs.addTab(self.tab_extra, "🧾 Доп. данные")

        # кнопки
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save)

        self.close_btn = QPushButton("🔥 Закрыть КУЛП")
        self.close_btn.clicked.connect(self.close_fire)

        self.layout.addWidget(self.save_btn)
        self.layout.addWidget(self.close_btn)

    # =========================
    # TAB 1 - LOCATION
    # =========================
    def build_tab_location(self):
        w = QWidget()
        layout = QFormLayout()

        self.address = QLineEdit(self.fire.get("address", ""))
        self.comment = QLineEdit(self.fire.get("comment", ""))
        self.mo = QLineEdit(self.fire.get("municipality", ""))
        self.selsovet = QLineEdit(self.fire.get("settlement", ""))
        self.coords = QLineEdit(self.fire.get("coords", ""))

        layout.addRow("Адрес", self.address)
        layout.addRow("Комментарий", self.comment)
        layout.addRow("МО", self.mo)
        layout.addRow("Сельсовет", self.selsovet)
        layout.addRow("Координаты", self.coords)

        w.setLayout(layout)
        return w

    # =========================
    # TAB 2 - FIRE DATA
    # =========================
    def build_tab_fire(self):
        w = QWidget()
        layout = QFormLayout()

        self.date = QLineEdit(str(self.fire.get("date", "")))
        self.time_msg = QLineEdit(str(self.fire.get("time_msg", "")))
        self.fire_type = QLineEdit(self.fire.get("fire_type", ""))
        self.area = QLineEdit(str(self.fire.get("area", "")))
        self.land_type = QLineEdit(self.fire.get("land_type", ""))

        layout.addRow("Дата пожара", self.date)
        layout.addRow("Время сообщения", self.time_msg)
        layout.addRow("Вид пожара", self.fire_type)
        layout.addRow("Площадь (га)", self.area)
        layout.addRow("Земли", self.land_type)

        w.setLayout(layout)
        return w

    # =========================
    # TAB 3 - EXTRA
    # =========================
    def build_tab_extra(self):
        w = QWidget()
        layout = QFormLayout()

        self.source = QLineEdit(self.fire.get("source", ""))
        self.owner = QLineEdit(self.fire.get("owner", ""))
        self.forestry = QLineEdit(self.fire.get("forestry", ""))
        self.extra = QLineEdit(self.fire.get("extra", ""))

        layout.addRow("Источник", self.source)
        layout.addRow("Правообладатель", self.owner)
        layout.addRow("Лесничество", self.forestry)
        layout.addRow("Доп. инфо", self.extra)

        w.setLayout(layout)
        return w

    # =========================
    # SAVE
    # =========================
    def save(self):
        data = {
            "address": self.address.text(),
            "comment": self.comment.text(),
            "municipality": self.mo.text(),
            "settlement": self.selsovet.text(),
            "coords": self.coords.text(),

            "date": self.date.text(),
            "time_msg": self.time_msg.text(),
            "fire_type": self.fire_type.text(),
            "area": float(self.area.text() or 0),
            "land_type": self.land_type.text(),

            "source": self.source.text(),
            "owner": self.owner.text(),
            "forestry": self.forestry.text(),
            "extra": self.extra.text(),

            "inspector_fio": self.user["full_name"]
        }

        self.api.update_fire(self.fire_id, data)

        QMessageBox.information(self, "OK", "Сохранено")

    # =========================
    # CLOSE
    # =========================
    def close_fire(self):
        self.api.close_fire(self.fire_id)

        QMessageBox.information(self, "OK", "КУЛП закрыт")
        self.app.go_back()