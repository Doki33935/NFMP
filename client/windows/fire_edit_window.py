from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QTabWidget, QFormLayout, QHBoxLayout,
)

from models.fire_update import FireUpdateDTO
from services.workers.reference_worker import ReferenceWorker
from widgets.safe_combo_box import SafeComboBox


class FireEditWindow(QWidget):
    def __init__(self, api, app, user, fire_id):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user
        self.fire_id = fire_id
        self.references = {}

        self.setWindowTitle(f"КУЛП #{fire_id}")
        self.setMinimumSize(900, 700)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 18, 18, 18)
        self.layout.setSpacing(12)

        self.load_data()
        self.build_ui()

    def load_data(self):
        self.fire = self.api.get_fire(self.fire_id)
        self.references = ReferenceWorker(self.api).load_all()

    def build_ui(self):
        title = QLabel(f"Редактирование КУЛП #{self.fire_id}")
        title.setObjectName("pageTitle")
        self.layout.addWidget(title)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tabs.addTab(self.build_tab_location(), "Локация")
        self.tabs.addTab(self.build_tab_fire(), "Пожар")
        self.tabs.addTab(self.build_tab_extra(), "Доп. данные")

        buttons = QHBoxLayout()
        buttons.addStretch()

        self.back_btn = QPushButton("Назад")
        self.back_btn.setObjectName("secondary")
        self.back_btn.clicked.connect(self.app.go_back)

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save)

        self.close_btn = QPushButton("Закрыть КУЛП")
        self.close_btn.clicked.connect(self.close_fire)

        buttons.addWidget(self.back_btn)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.close_btn)
        self.layout.addLayout(buttons)

    def build_tab_location(self):
        widget = QWidget()
        layout = self.form()

        self.address = QLineEdit(self.fire.address or "")
        self.comment = QLineEdit(self.fire.address_comment or "")

        self.municipality = SafeComboBox()
        self.settlement = SafeComboBox()
        self.fill_combo(self.municipality, self.references.get("municipalities", []), self.fire.municipality_id)
        self.municipality.currentIndexChanged.connect(self.on_municipality_changed)
        self.on_municipality_changed(self.municipality.currentIndex())

        self.latitude = QLineEdit("" if self.fire.latitude is None else str(self.fire.latitude))
        self.longitude = QLineEdit("" if self.fire.longitude is None else str(self.fire.longitude))

        layout.addRow("Адрес", self.address)
        layout.addRow("Комментарий", self.comment)
        layout.addRow("МО", self.municipality)
        layout.addRow("Сельсовет", self.settlement)
        layout.addRow("Широта", self.latitude)
        layout.addRow("Долгота", self.longitude)

        widget.setLayout(layout)
        return widget

    def build_tab_fire(self):
        widget = QWidget()
        layout = self.form()

        self.date = QLineEdit(self.fire.fire_date.date().isoformat())

        self.fire_type = SafeComboBox()
        self.fire_type.addItems(["Сухая трава", "Лес"])
        self.fire_type.setCurrentText("Лес" if self.fire.is_forest else "Сухая трава")

        self.area = QLineEdit("" if self.fire.area is None else str(self.fire.area))

        self.land_type = SafeComboBox()
        self.reason = SafeComboBox()
        self.fill_combo(self.land_type, self.references.get("land_types", []), self.fire.land_type_id)
        self.fill_combo(self.reason, self.references.get("reasons", []), self.fire.reason_id)

        layout.addRow("Дата пожара", self.date)
        layout.addRow("Вид пожара", self.fire_type)
        layout.addRow("Площадь (га)", self.area)
        layout.addRow("Земли", self.land_type)
        layout.addRow("Причина пожара", self.reason)

        widget.setLayout(layout)
        return widget

    def build_tab_extra(self):
        widget = QWidget()
        layout = self.form()

        self.source = QLineEdit(self.fire.source or "")
        self.owner = QLineEdit(self.fire.owner or "")

        self.forestry = SafeComboBox()
        self.fill_combo(self.forestry, self.references.get("forestry", []), self.fire.forestry_id)

        self.extra = QLineEdit(self.fire.extra or "")

        layout.addRow("Источник", self.source)
        layout.addRow("Правообладатель", self.owner)
        layout.addRow("Лесничество", self.forestry)
        layout.addRow("Доп. инфо", self.extra)

        widget.setLayout(layout)
        return widget

    def form(self):
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(10)
        return layout

    def fill_combo(self, combo, items, selected_id=None):
        combo.clear()
        combo.addItem("", None)

        for item in items:
            combo.addItem(item["name"], item["id"])

        if selected_id is None:
            combo.setCurrentIndex(0)
            return

        index = combo.findData(selected_id)
        combo.setCurrentIndex(index if index >= 0 else 0)

    def on_municipality_changed(self, index):
        municipality_id = self.municipality.currentData()
        self.settlement.clear()
        self.settlement.addItem("", None)

        if not municipality_id:
            return

        for item in self.api.get_selsovets(municipality_id):
            self.settlement.addItem(item["name"], item["id"])

        selected = self.fire.selsovet_id
        index = self.settlement.findData(selected)
        if index >= 0:
            self.settlement.setCurrentIndex(index)

    def save(self):
        try:
            dto = FireUpdateDTO(
                fire_date=datetime.fromisoformat(self.date.text()),
                is_forest=self.fire_type.currentText() == "Лес",
                land_type_id=self.land_type.currentData(),
                reason_id=self.reason.currentData(),
                area=float(self.area.text()) if self.area.text() else None,
                address=self.address.text(),
                address_comment=self.comment.text() or None,
                municipality_id=self.municipality.currentData(),
                selsovet_id=self.settlement.currentData(),
                latitude=float(self.latitude.text()) if self.latitude.text() else None,
                longitude=float(self.longitude.text()) if self.longitude.text() else None,
                forestry_id=self.forestry.currentData(),
                owner=self.owner.text() or None,
                source=self.source.text() or None,
                extra=self.extra.text() or None,
                inspector_id=self.user.id,
            )
            self.api.update_fire(self.fire_id, dto)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return

        QMessageBox.information(self, "OK", "Сохранено")

    def close_fire(self):
        try:
            self.api.close_fire(self.fire_id)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return

        QMessageBox.information(self, "OK", "КУЛП закрыт")
        self.app.go_back()
