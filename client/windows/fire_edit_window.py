from datetime import datetime, time, timedelta

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QScrollArea, QFrame, QPlainTextEdit,
)

from models.fire_update import FireUpdateDTO
from services.workers.reference_worker import ReferenceWorker
from widgets.safe_combo_box import SafeComboBox


class DateStepWidget(QWidget):
    def __init__(self, initial_date):
        super().__init__()
        self.current_date = QDate(initial_date.year, initial_date.month, initial_date.day)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.prev_btn = QPushButton("<")
        self.prev_btn.clicked.connect(self.prev_day)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("fieldTitle")
        self.label.setMinimumWidth(150)

        self.next_btn = QPushButton(">")
        self.next_btn.clicked.connect(self.next_day)

        layout.addWidget(self.prev_btn)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.next_btn)
        self.update_label()

    def prev_day(self):
        self.current_date = self.current_date.addDays(-1)
        self.update_label()

    def next_day(self):
        today = QDate.currentDate()
        if self.current_date >= today:
            return

        self.current_date = self.current_date.addDays(1)
        self.update_label()

    def update_label(self):
        self.label.setText(self.current_date.toString("dd.MM.yyyy"))
        self.next_btn.setEnabled(self.current_date < QDate.currentDate())

    def value(self):
        return self.current_date.toPython()


class HourStepWidget(QWidget):
    def __init__(self, initial_hour=1):
        super().__init__()
        self.hour = min(max(initial_hour or 1, 1), 24)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.prev_btn = QPushButton("<")
        self.prev_btn.clicked.connect(self.prev_hour)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("fieldTitle")
        self.label.setMinimumWidth(150)

        self.next_btn = QPushButton(">")
        self.next_btn.clicked.connect(self.next_hour)

        layout.addWidget(self.prev_btn)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.next_btn)
        self.update_label()

    def prev_hour(self):
        if self.hour > 1:
            self.hour -= 1
            self.update_label()

    def next_hour(self):
        if self.hour < 24:
            self.hour += 1
            self.update_label()

    def update_label(self):
        self.label.setText(f"{self.hour:02d}:00")
        self.prev_btn.setEnabled(self.hour > 1)
        self.next_btn.setEnabled(self.hour < 24)

    def value(self):
        return self.hour


class FireEditWindow(QWidget):
    def __init__(self, api, app, user, fire_id):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user
        self.fire_id = fire_id
        self.references = {}

        self.setWindowTitle(f"КУЛП #{fire_id}")
        self.setMinimumSize(860, 720)

        self.load_data()
        self.build_ui()

    def load_data(self):
        self.fire = self.api.get_fire(self.fire_id)
        if self.fire.status == "OPEN":
            self.fire = self.api.take_fire(self.fire_id)
        self.references = ReferenceWorker(self.api).load_all()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        title = QLabel(f"Редактирование КУЛП #{self.fire_id}")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Данные карточки, результат проверки и сведения о ликвидации")
        subtitle.setObjectName("muted")
        root.addWidget(title)
        root.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        content = QVBoxLayout(container)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(14)
        content.addWidget(self.section_event())
        content.addWidget(self.section_location())
        content.addWidget(self.section_context())
        content.addWidget(self.section_completion())
        content.addWidget(self.section_service())
        content.addStretch()

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

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
        root.addLayout(buttons)

    def section(self, title, hint=None):
        frame = QFrame()
        frame.setObjectName("section")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        label = QLabel(title)
        label.setObjectName("sectionTitle")
        layout.addWidget(label)

        if hint:
            hint_label = QLabel(hint)
            hint_label.setObjectName("muted")
            hint_label.setWordWrap(True)
            layout.addWidget(hint_label)

        return frame

    def section_event(self):
        frame = self.section("Событие")
        form = self.form()

        self.date = DateStepWidget(self.fire.fire_date)

        self.fire_type = SafeComboBox()
        self.fire_type.addItem("Сухая трава", False)
        self.fire_type.addItem("Лес", True)
        self.fire_type.setCurrentIndex(1 if self.fire.is_forest else 0)
        self.fire_type.currentIndexChanged.connect(self.on_fire_type_changed)

        self.area = QLineEdit("" if self.fire.area is None else str(self.fire.area))

        self.land_type = SafeComboBox()
        self.reason = SafeComboBox()
        self.fill_combo(self.land_type, self.references.get("land_types", []), self.fire.land_type_id)
        self.fill_combo(self.reason, self.references.get("reasons", []), self.fire.reason_id)

        form.addRow("Дата пожара", self.date)
        form.addRow("Вид пожара", self.fire_type)
        form.addRow("Площадь (га)", self.area)
        form.addRow("Земли", self.land_type)
        form.addRow("Причина пожара", self.reason)

        frame.layout().addLayout(form)
        return frame

    def section_location(self):
        frame = self.section("Место пожара")
        form = self.form()

        self.address = QLineEdit(self.fire.address or "")

        self.municipality = SafeComboBox()
        self.settlement = SafeComboBox()
        self.fill_combo(self.municipality, self.references.get("municipalities", []), self.fire.municipality_id)
        self.municipality.currentIndexChanged.connect(self.on_municipality_changed)
        self.on_municipality_changed()

        self.latitude = QLineEdit("" if self.fire.latitude is None else str(self.fire.latitude))
        self.longitude = QLineEdit("" if self.fire.longitude is None else str(self.fire.longitude))

        form.addRow("Адрес", self.address)
        form.addRow("МО", self.municipality)
        form.addRow("Сельсовет", self.settlement)
        form.addRow("Широта", self.latitude)
        form.addRow("Долгота", self.longitude)

        frame.layout().addLayout(form)
        return frame

    def section_context(self):
        frame = self.section("Контекст")
        form = self.form()

        self.forestry = SafeComboBox()
        self.fill_combo(self.forestry, self.references.get("forestry", []), self.fire.forestry_id)

        self.right_of_way = SafeComboBox()
        self.right_of_way.addItem("Нет", False)
        self.right_of_way.addItem("Да", True)
        self.right_of_way.setCurrentIndex(1 if self.fire.right_of_way else 0)
        self.right_of_way.currentIndexChanged.connect(self.on_right_of_way_changed)

        self.right_of_way_type = SafeComboBox()
        self.fill_right_of_way_types()
        index = self.right_of_way_type.findData(self.fire.right_of_way_type)
        self.right_of_way_type.setCurrentIndex(index if index >= 0 else 0)

        self.owner = SafeComboBox()
        self.fill_combo(self.owner, self.references.get("owner_types", []))
        owner_index = self.owner.findData(self.fire.owner)
        if self.fire.owner and owner_index < 0:
            self.owner.addItem(f"{self.fire.owner} (старое значение)", self.fire.owner)
            owner_index = self.owner.count() - 1
        self.owner.setCurrentIndex(owner_index if owner_index >= 0 else 0)
        self.source = QLineEdit(self.fire.source or "")

        self.extra = QPlainTextEdit()
        self.extra.setPlainText(self.fire.extra or "")
        self.extra.setFixedHeight(92)

        form.addRow("Лесничество", self.forestry)
        form.addRow("Наличие ЗОУИТ", self.right_of_way)
        form.addRow("Тип ЗОУИТ", self.right_of_way_type)
        form.addRow("Собственник", self.owner)
        form.addRow("Детальная информация о собственнике", self.source)
        form.addRow("Дополнительно", self.extra)

        frame.layout().addLayout(form)
        self.on_fire_type_changed()
        self.on_right_of_way_changed()
        return frame

    def section_completion(self):
        frame = self.section(
            "Ликвидация пожара",
            "Укажите дату и час ликвидации перед закрытием КУЛП.",
        )
        form = self.form()

        end_dt = self.fire.end_time or datetime.combine(self.fire.fire_date, time(1, 0))
        end_hour = 24 if end_dt.hour == 0 and self.fire.end_time else max(end_dt.hour, 1)

        self.end_date = DateStepWidget(end_dt.date())
        self.end_hour = HourStepWidget(end_hour)

        form.addRow("Дата ликвидации", self.end_date)
        form.addRow("Час ликвидации", self.end_hour)

        frame.layout().addLayout(form)
        return frame

    def section_service(self):
        frame = self.section("Служебная информация")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        self.add_info_line(layout, "Карточку создал", self.fire.creator_name or f"ID {self.fire.creator_id}")
        self.add_info_line(layout, "Время оформления", self.format_datetime(self.fire.time_msg))
        self.add_info_line(layout, "Статус", self.fire.status)
        if self.fire.reviewer_name:
            self.add_info_line(layout, "Дознаватель", self.fire.reviewer_name)

        frame.layout().addLayout(layout)
        return frame

    def add_info_line(self, layout, label, value):
        row = QHBoxLayout()
        name = QLabel(f"{label}:")
        name.setObjectName("muted")
        text = QLabel(str(value or ""))
        text.setObjectName("fieldTitle")
        text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row.addWidget(name)
        row.addWidget(text, 1)
        layout.addLayout(row)

    def form(self):
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFormAlignment(Qt.AlignTop)
        layout.setHorizontalSpacing(16)
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

    def fill_right_of_way_types(self):
        self.fill_combo(self.right_of_way_type, self.references.get("zouit_types", []))

    def on_municipality_changed(self, *args):
        municipality_id = self.municipality.currentData()
        self.settlement.clear()
        self.settlement.addItem("", None)

        if not municipality_id:
            self.settlement.setVisible(False)
            return

        for item in self.api.get_selsovets(municipality_id):
            self.settlement.addItem(item["name"], item["id"])

        index = self.settlement.findData(self.fire.selsovet_id)
        self.settlement.setCurrentIndex(index if index >= 0 else 0)
        self.settlement.setVisible(True)

    def on_fire_type_changed(self, *args):
        is_forest = self.fire_type.currentData() is True
        self.forestry.setVisible(is_forest)

        if not is_forest:
            self.forestry.setCurrentIndex(0)

    def on_right_of_way_changed(self, *args):
        enabled = self.right_of_way.currentData() is True
        self.right_of_way_type.setVisible(enabled)

        if not enabled:
            self.right_of_way_type.setCurrentIndex(0)

    def build_dto(self):
        end_date = self.end_date.value()
        end_hour = self.end_hour.value()

        if end_hour == 24:
            end_time = datetime.combine(end_date + timedelta(days=1), time(0, 0))
        else:
            end_time = datetime.combine(end_date, time(end_hour, 0))

        return FireUpdateDTO(
            fire_date=self.date.value(),
            end_time=end_time,
            is_forest=self.fire_type.currentData() is True,
            land_type_id=self.land_type.currentData(),
            reason_id=self.reason.currentData(),
            area=self.parse_float(self.area.text(), "Площадь"),
            address=self.address.text(),
            municipality_id=self.municipality.currentData(),
            selsovet_id=self.settlement.currentData(),
            latitude=self.parse_float(self.latitude.text(), "Широта"),
            longitude=self.parse_float(self.longitude.text(), "Долгота"),
            forestry_id=self.forestry.currentData(),
            right_of_way=self.right_of_way.currentData() is True,
            right_of_way_type=self.right_of_way_type.currentData() or None,
            owner=self.owner.currentData() or None,
            source=self.source.text() or None,
            extra=self.extra.toPlainText() or None,
        )

    def validate_form(self):
        errors = []

        if self.land_type.currentData() is None:
            errors.append("Выберите земли")

        if not self.address.text().strip():
            errors.append("Укажите адрес")

        if self.municipality.currentData() is None:
            errors.append("Выберите МО")

        if self.fire_type.currentData() is True and self.forestry.currentData() is None:
            errors.append("Для лесного пожара выберите лесничество")

        if self.right_of_way.currentData() is True and self.right_of_way_type.currentData() is None:
            errors.append("Для территории ЗОУИТ выберите тип ЗОУИТ")

        if errors:
            raise ValueError("\n".join(errors))

    def parse_float(self, value, label):
        value = (value or "").strip().replace(",", ".")
        if not value:
            return None

        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"{label}: укажите число") from exc

    def save(self, show_message=True):
        try:
            self.validate_form()
            self.api.update_fire(self.fire_id, self.build_dto())
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return False

        if show_message:
            QMessageBox.information(self, "Готово", "КУЛП сохранен")
        return True

    def close_fire(self):
        if not self.save(show_message=False):
            return

        try:
            self.api.close_fire(self.fire_id)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return

        QMessageBox.information(self, "Готово", "КУЛП закрыт")
        self.app.go_back()

    def format_datetime(self, value):
        if not value:
            return ""

        return value.strftime("%d.%m.%Y %H:%M")
