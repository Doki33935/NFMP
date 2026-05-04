from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy,
    QMessageBox, QPlainTextEdit,
)

from services.fire_create_service import FireCreateService
from services.workers.reference_worker import ReferenceWorker
from widgets.fire_date_widget import FireDateWidget
from widgets.safe_combo_box import SafeComboBox


class FireCreateWindow(QWidget):
    def __init__(self, api, app, user):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user
        self.service = FireCreateService(user)
        self.worker = ReferenceWorker(api)

        self.references = {}
        self.participant_rows = []

        self.setMinimumSize(860, 720)
        self.load_references()
        self.build_ui()
        self.fill_data()

        self.on_fire_type_changed()
        self.on_right_of_way_changed()
        self.on_municipality_changed()

    def load_references(self):
        self.references = self.worker.load_all()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        title = QLabel("Создание карточки пожара")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Основные сведения, место, причина и участники реагирования")
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
        content.addWidget(self.section_participants())
        content.addStretch()

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        footer = QHBoxLayout()
        footer.addStretch()

        back = QPushButton("Назад")
        back.setObjectName("secondary")
        back.clicked.connect(self.app.go_back)

        save = QPushButton("Создать КУЛП")
        save.clicked.connect(self.save)

        footer.addWidget(back)
        footer.addWidget(save)
        root.addLayout(footer)

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

        self.fire_date = FireDateWidget()

        self.is_forest = SafeComboBox()
        self.is_forest.addItem("", None)
        self.is_forest.addItem("Сухая трава", False)
        self.is_forest.addItem("Лес", True)
        self.is_forest.currentIndexChanged.connect(self.on_fire_type_changed)

        self.land_type = SafeComboBox()
        self.reason = SafeComboBox()

        self.area = QLineEdit()
        self.area.setPlaceholderText("га")

        form.addRow("Дата пожара", self.fire_date)
        form.addRow("Вид пожара", self.is_forest)
        form.addRow("Состав земли", self.land_type)
        form.addRow("Причина", self.reason)
        form.addRow("Площадь", self.area)

        frame.layout().addLayout(form)
        return frame

    def section_location(self):
        frame = self.section("Место пожара")
        form = self.form()

        self.address = QLineEdit()
        self.address.setPlaceholderText("Адрес или ориентир")

        self.comment = QLineEdit()
        self.comment.setPlaceholderText("Комментарий к адресу")

        self.municipality = SafeComboBox()
        self.municipality.currentIndexChanged.connect(self.on_municipality_changed)
        self.settlement = SafeComboBox()

        coords = QLabel("Координаты будут подключены отдельным модулем карты")
        coords.setObjectName("muted")

        form.addRow("Адрес", self.address)
        form.addRow("Комментарий", self.comment)
        form.addRow("МО", self.municipality)
        form.addRow("Сельсовет", self.settlement)
        form.addRow("Координаты", coords)

        frame.layout().addLayout(form)
        return frame

    def section_context(self):
        frame = self.section("Контекст")
        form = self.form()

        self.forestry = SafeComboBox()

        self.right_of_way = SafeComboBox()
        self.right_of_way.addItem("Нет", False)
        self.right_of_way.addItem("Да", True)
        self.right_of_way.currentIndexChanged.connect(self.on_right_of_way_changed)

        self.right_of_way_type = SafeComboBox()
        self.owner = QLineEdit()
        self.owner.setPlaceholderText("Правообладатель")

        self.source = QLineEdit()
        self.source.setPlaceholderText("Источник сообщения")

        self.extra = QPlainTextEdit()
        self.extra.setPlaceholderText("Дополнительные сведения")
        self.extra.setFixedHeight(92)

        form.addRow("Лесничество", self.forestry)
        form.addRow("Полоса отвода", self.right_of_way)
        form.addRow("Тип полосы", self.right_of_way_type)
        form.addRow("Владелец", self.owner)
        form.addRow("Источник", self.source)
        form.addRow("Дополнительно", self.extra)

        frame.layout().addLayout(form)
        return frame

    def section_participants(self):
        frame = self.section(
            "Участники пожара",
            "Добавляйте организации и технику отдельными карточками.",
        )

        controls = QHBoxLayout()
        add_btn = QPushButton("Добавить участника")
        add_btn.setObjectName("secondary")
        add_btn.clicked.connect(self.add_participant_row)
        controls.addStretch()
        controls.addWidget(add_btn)
        frame.layout().addLayout(controls)

        self.participants_container = QVBoxLayout()
        self.participants_container.setSpacing(10)

        holder = QWidget()
        holder.setLayout(self.participants_container)
        holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        frame.layout().addWidget(holder)

        return frame

    def form(self):
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        return form

    def fill_data(self):
        self.fill_combo(self.municipality, self.references.get("municipalities", []))
        self.fill_combo(self.land_type, self.references.get("land_types", []))
        self.fill_combo(self.forestry, self.references.get("forestry", []))
        self.fill_combo(self.reason, self.references.get("reasons", []))

    def fill_combo(self, combo, items):
        combo.clear()
        combo.addItem("", None)

        for item in items:
            combo.addItem(item["name"], item["id"])

    def fill_right_of_way_types(self):
        self.right_of_way_type.clear()
        self.right_of_way_type.addItem("", None)
        self.right_of_way_type.addItem("Полоса отвода железнодорожных путей", "railway")
        self.right_of_way_type.addItem("Полоса отвода автомобильной дороги", "road")
        self.right_of_way_type.addItem("Полоса отвода линии электропередачи", "powerline")

    def add_participant_row(self):
        row_frame = QFrame()
        row_frame.setObjectName("participantRow")
        row_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        layout = QVBoxLayout(row_frame)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel(f"Участник #{len(self.participant_rows) + 1}")
        title.setObjectName("fieldTitle")

        remove_btn = QPushButton("x")
        remove_btn.setObjectName("iconButton")
        remove_btn.setFixedWidth(34)
        remove_btn.clicked.connect(lambda: self.remove_participant_row(row_frame))

        header.addWidget(title)
        header.addStretch()
        header.addWidget(remove_btn)

        participant = SafeComboBox()
        tech_type = SafeComboBox()
        arrival = QLineEdit()
        arrival.setPlaceholderText("HH:MM")
        arrival.setMaximumWidth(150)

        self.fill_combo(participant, self.references.get("participants", []))
        self.fill_combo(tech_type, self.references.get("tech_types", []))

        fields = QFormLayout()
        fields.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        fields.setHorizontalSpacing(12)
        fields.setVerticalSpacing(8)
        fields.addRow("Организация", participant)
        fields.addRow("Техника", tech_type)
        fields.addRow("Прибытие", arrival)

        layout.addLayout(header)
        layout.addLayout(fields)

        self.participants_container.addWidget(row_frame)
        self.participant_rows.append((row_frame, participant, tech_type, arrival))

    def remove_participant_row(self, row_frame):
        row_frame.deleteLater()
        self.participant_rows = [
            row for row in self.participant_rows if row[0] != row_frame
        ]

    def on_fire_type_changed(self, *args):
        is_forest = self.is_forest.currentData() is True
        self.forestry.setVisible(is_forest)

        if not is_forest:
            self.forestry.setCurrentIndex(0)

    def on_right_of_way_changed(self, *args):
        enabled = self.right_of_way.currentData() is True
        self.right_of_way_type.setVisible(enabled)
        self.owner.setVisible(enabled)

        if enabled:
            self.fill_right_of_way_types()
        else:
            self.right_of_way_type.clear()
            self.owner.clear()

    def on_municipality_changed(self, *args):
        municipality_id = self.municipality.currentData()

        self.settlement.clear()
        self.settlement.addItem("", None)

        if not municipality_id:
            self.settlement.setVisible(False)
            return

        for item in self.api.get_selsovets(municipality_id):
            self.settlement.addItem(item["name"], item["id"])

        self.settlement.setVisible(True)

    def save(self):
        try:
            self.validate_form()
            dto = self.service.build_dto(self)
            self.api.create_fire(dto)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return

        QMessageBox.information(self, "Готово", "КУЛП составлена успешно")
        self.app.go_to_main(self.user)

    def validate_form(self):
        errors = []

        if self.is_forest.currentData() is None:
            errors.append("Выберите вид пожара")

        if self.land_type.currentData() is None:
            errors.append("Выберите состав земли")

        if not self.address.text().strip():
            errors.append("Укажите адрес или ориентир")

        if self.municipality.currentData() is None:
            errors.append("Выберите МО")

        if self.is_forest.currentData() is True and self.forestry.currentData() is None:
            errors.append("Для лесного пожара выберите лесничество")

        if self.right_of_way.currentData() is True and self.right_of_way_type.currentData() is None:
            errors.append("Для полосы отвода выберите тип полосы")

        if errors:
            raise ValueError("\n".join(errors))
