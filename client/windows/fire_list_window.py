from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton
from PySide6.QtCore import Qt, QThread

from services.workers.fire_worker import FireListWorker


class FireListWindow(QWidget):
    def __init__(self, fire_service, app, user):
        super().__init__()

        self.fire_service = fire_service
        self.app = app
        self.user = user
        
        self.thread = None
        self.worker = None

        self.setMinimumSize(700, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Кнопки
        self.btn_open = QPushButton("Открытые")
        self.btn_review = QPushButton("На проверке")
        self.btn_completed = QPushButton("Завершённые")

        self.layout.addWidget(self.btn_completed)
        self.layout.addWidget(self.btn_open)
        self.layout.addWidget(self.btn_review)

        self.list = QListWidget()
        self.layout.addWidget(self.list)

        self.btn_open.clicked.connect(lambda: self.load_data("OPEN"))
        self.btn_review.clicked.connect(lambda: self.load_data("IN_REVIEW"))
        self.btn_completed.clicked.connect(lambda: self.load_data("COMPLETED"))
        self.list.itemDoubleClicked.connect(self.open_fire)

        self.load_data("OPEN")


    def load_data(self, status):
        self.list.clear()
        self.list.addItem("Загрузка...")

        self.thread = QThread()
        self.worker = FireListWorker(self.fire_service, status)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_loaded)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_loaded(self, fires):
        self.list.clear()

        for f in fires:
            item = QListWidgetItem(
                f"#{f['id']} | {f['fire_date']} | {f['address']} | {f['status']}"
            )

            item.setData(Qt.UserRole, f["id"])
            self.list.addItem(item)

    def on_error(self, message):
        self.list.clear()
        self.list.addItem(f"Ошибка: {message}")


    def open_fire(self, item):
        fire_id = item.data(Qt.UserRole)
        self.app.go_to_fire_edit(fire_id)