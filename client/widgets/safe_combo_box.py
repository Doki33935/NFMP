from PySide6.QtWidgets import QComboBox, QCompleter, QSizePolicy
from PySide6.QtCore import Qt

class SafeComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumContentsLength(12)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMaxVisibleItems(12)

        completer = QCompleter(self.model(), self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(completer)

    def wheelEvent(self, event):
        if not self.view().isVisible():
            event.ignore()
            return

        if not self.hasFocus():
            event.ignore()
            return

        super().wheelEvent(event)
