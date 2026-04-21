from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QLabel, QPushButton,
    QHBoxLayout, QScrollArea, QFrame
)

from services.workers.reference_worker import ReferenceWorker
from services.fire_create_service import FireCreateService
from widgets.fire_date_widget import FireDateWidget


class FireCreateWindow(QWidget):
    def __init__(self, api, app, user):
        super().__init__()

        self.api = api
        self.app = app
        self.user = user

        self.service = FireCreateService(user)
        self.worker = ReferenceWorker(api)

        self.setMinimumSize(800, 600)

        self.references = {}
        self.participant_rows = []

        # =========================
        # LAYOUT ROOT
        # =========================
        self.main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        self.form_layout = QVBoxLayout(container)
        self.form_layout.setSpacing(20)

        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)

        # =========================
        # LOAD DATA
        # =========================
        self.load_references()

        # =========================
        # UI
        # =========================
        self.build_ui()
        self.fill_data()

    # =========================
    # DATA
    # =========================
    def load_references(self):
        self.references = self.worker.load_all()

    def fill_data(self):
        self.fill_municipalities()
        self.fill_forestry()

    # =========================
    # UI BUILD
    # =========================
    def build_ui(self):
        self.form_layout.addWidget(self.section_event())
        self.form_layout.addWidget(self.section_location())
        self.form_layout.addWidget(self.section_context())

        bottom = QHBoxLayout()

        back = QPushButton("Назад")
        save = QPushButton("Создать КУЛП")

        back.setObjectName("secondary")

        back.clicked.connect(self.app.go_back)
        save.clicked.connect(self.save)

        bottom.addStretch()
        bottom.addWidget(back)
        bottom.addWidget(save)
        bottom.addStretch()

        self.form_layout.addLayout(bottom)

        # signals
        self.is_forest.currentTextChanged.connect(self.on_fire_type_changed)
        self.right_of_way.currentTextChanged.connect(self.on_right_of_way_changed)

    # =========================
    # SECTION HELPERS
    # =========================
    def section(self, title):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #252525;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(frame)

        label = QLabel(title)
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff3b30;")

        layout.addWidget(label)
        return frame

    # =========================
    # SECTION 1
    # =========================
    def section_event(self):
        frame = self.section("🔥 Событие")

        form = QFormLayout()

        self.fire_date = FireDateWidget()

        self.is_forest = QComboBox()
        self.is_forest.addItems(["Сухая трава", "Лес"])

        self.land_type = QLineEdit()
        self.area = QLineEdit()

        form.addRow("Дата", self.fire_date)
        form.addRow("Тип", self.is_forest)
        form.addRow("Земли", self.land_type)
        form.addRow("Площадь", self.area)

        frame.layout().addLayout(form)
        return frame

    # =========================
    # SECTION 2
    # =========================
    def section_location(self):
        frame = self.section("📍 Локация")

        form = QFormLayout()

        self.address = QLineEdit()
        self.comment = QLineEdit()

        self.municipality = QComboBox()
        self.settlement = QLineEdit()

        self.coords = QLabel("📍 координаты (потом карта)")

        form.addRow("Адрес", self.address)
        form.addRow("Комментарий", self.comment)
        form.addRow("МО", self.municipality)
        form.addRow("Сельсовет", self.settlement)
        form.addRow("Координаты", self.coords)

        frame.layout().addLayout(form)
        return frame

    # =========================
    # SECTION 3
    # =========================
    def section_context(self):
        frame = self.section("🧭 Контекст")

        form = QFormLayout()

        # participants
        self.participants_container = QVBoxLayout()

        add_btn = QPushButton("➕ Добавить участника")
        add_btn.clicked.connect(self.add_participant_row)

        form.addRow(QLabel("Участники"))
        form.addRow(add_btn)
        form.addRow(self.wrap_layout(self.participants_container))

        # forestry + road
        self.forestry = QComboBox()

        self.right_of_way = QComboBox()
        self.right_of_way.addItems(["Нет", "Да"])

        self.right_of_way_type = QLineEdit()
        self.owner = QLineEdit()

        self.source = QLineEdit()
        self.extra = QLineEdit()

        form.addRow("Лесничество", self.forestry)
        form.addRow("Полоса отвода", self.right_of_way)
        form.addRow("Тип", self.right_of_way_type)
        form.addRow("Владелец", self.owner)
        form.addRow("Источник", self.source)
        form.addRow("Дополнительно", self.extra)

        frame.layout().addLayout(form)
        return frame

    def wrap_layout(self, layout):
        w = QWidget()
        w.setLayout(layout)
        return w

    # =========================
    # DATA FILL
    # =========================
    def fill_municipalities(self):
        self.municipality.clear()

        for m in self.references["municipalities"]:
            self.municipality.addItem(m["name"], m["id"])

    def fill_forestry(self):
        self.forestry.clear()

        for f in self.references["forestry"]:
            self.forestry.addItem(f["name"], f["id"])

    # =========================
    # PARTICIPANTS
    # =========================
    def add_participant_row(self):
        row = QHBoxLayout()

        participant = QComboBox()
        tech_type = QComboBox()
        time = QLineEdit()
        time.setPlaceholderText("HH:MM")

        for p in self.references["participants"]:
            participant.addItem(p["name"], p["id"])

        for t in self.references["tech_types"]:
            tech_type.addItem(t["name"], t["id"])

        remove_btn = QPushButton("❌")
        remove_btn.clicked.connect(lambda: self.remove_participant_row(row))

        row.addWidget(participant)
        row.addWidget(tech_type)
        row.addWidget(time)
        row.addWidget(remove_btn)

        self.participants_container.addLayout(row)

        self.participant_rows.append((row, participant, tech_type, time))

    def remove_participant_row(self, row):
        for i in reversed(range(row.count())):
            w = row.itemAt(i).widget()
            if w:
                w.deleteLater()

        self.participants_container.removeItem(row)

        self.participant_rows = [
            x for x in self.participant_rows if x[0] != row
        ]

    # =========================
    # LOGIC
    # =========================
    def on_fire_type_changed(self, value):
        is_forest = (value == "Лес")

        self.forestry.setVisible(is_forest)

        if not is_forest:
            self.forestry.setCurrentIndex(-1)

    def on_right_of_way_changed(self, value):
        enabled = (value == "Да")

        self.right_of_way_type.setVisible(enabled)
        self.owner.setVisible(enabled)

    # =========================
    # SAVE
    # =========================
    def save(self):
        data = self.service.build_payload(self)

        self.api.create_fire(data)
        self.app.go_to_main(self.user)