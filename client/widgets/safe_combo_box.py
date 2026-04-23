from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt

class SafeComboBox(QComboBox):
    def wheelEvent(self, event):
        if not self.view().isVisible():
            event.ignore()
            return

        if not self.hasFocus():
            event.ignore()
            return

        super().wheelEvent(event)