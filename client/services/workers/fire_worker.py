from PySide6.QtCore import QObject, Signal


class FireListWorker(QObject):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, fire_service, status):
        super().__init__()
        self.fire_service = fire_service
        self.status = status

    def run(self):
        try:
            fires = self.fire_service.get_fires(self.status)
            self.finished.emit(fires)
        except Exception as e:
            self.error.emit(str(e))