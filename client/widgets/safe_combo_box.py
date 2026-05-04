from PySide6.QtWidgets import QComboBox, QSizePolicy
from PySide6.QtCore import Qt

class SafeComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumContentsLength(12)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)

    def wheelEvent(self, event):
        if not self.view().isVisible():
            event.ignore()
            return

        if not self.hasFocus():
            event.ignore()
            return

        super().wheelEvent(event)
