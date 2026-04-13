from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class FireListWindow(QWidget):
    def __init__(self, api, app, user):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user

        self.setWindowTitle("Список КУЛП")
        self.setMinimumSize(700, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list = QListWidget()
        self.layout.addWidget(self.list)

        self.load_data()  # 👈 важно

        self.list.itemDoubleClicked.connect(self.open_fire)

    # 🔥 ВОТ ЭТО ТЫ СКОРЕЕ ВСЕГО ЗАБЫЛ
    def load_data(self):
        fires = self.api.get_fires(status="OPEN")  # 👈 ключевой момент

        self.list.clear()

        for f in fires:
            item = QListWidgetItem(
                f"#{f['id']} | {f['date']} | {f['address']} | {f['status']}"
            )

            item.setData(Qt.UserRole, f["id"])
            self.list.addItem(item)

    def open_fire(self, item):
        fire_id = item.data(Qt.UserRole)

        if fire_id is None:
            print("❌ fire_id is None")
            return

        self.app.go_to_fire_edit(self.user, fire_id)