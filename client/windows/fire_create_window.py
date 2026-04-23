from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton,
    QHBoxLayout, QScrollArea, QFrame
)

from services.workers.reference_worker import ReferenceWorker
from services.fire_create_service import FireCreateService
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

        self.on_fire_type_changed(self.is_forest.currentText())
        self.on_right_of_way_index_changed(self.right_of_way.currentIndex())
        self.on_municipality_changed(self.municipality.currentIndex())

    # =========================
    # DATA
    # =========================
    def load_references(self):
        self.references = self.worker.load_all()

    def fill_data(self):
        self.fill_municipalities()
        self.fill_forestry()
        self.fill_land_types()

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
        self.right_of_way.currentIndexChanged.connect(self.on_right_of_way_index_changed)
        self.municipality.currentIndexChanged.connect(self.on_municipality_changed)

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

        self.is_forest = SafeComboBox()
        self.is_forest.addItems(["", "Сухая трава", "Лес"])

        self.land_type = SafeComboBox()
        self.area = QLineEdit()

        form.addRow("Дата", self.fire_date)
        form.addRow("Тип", self.is_forest)
        form.addRow("Состав земли", self.land_type)
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

        self.municipality = SafeComboBox()
        self.settlement = SafeComboBox()

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
        self.forestry = SafeComboBox()

        self.right_of_way = SafeComboBox()
        self.right_of_way.addItems(["Нет", "Да"])

        self.right_of_way_type = SafeComboBox()

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

        self.municipality.addItem("", None)
        for m in self.references["municipalities"]:
            self.municipality.addItem(m["name"], m["id"])

    def fill_land_types(self):
        self.land_type.clear()

        self.land_type.addItem("", None)
        for lt in self.references["land_types"]:
            self.land_type.addItem(lt["name"], lt["id"])

    def fill_forestry(self):
        self.forestry.clear()

        self.forestry.addItem("", None)
        for f in self.references["forestry"]:
            self.forestry.addItem(f["name"], f["id"])

    def fill_right_of_way_types(self):
        self.right_of_way_type.clear()

        self.right_of_way_type.addItem("")
        self.right_of_way_type.addItem(
            "Полоса отвода железнодорожных путей", "railway"
        )
        self.right_of_way_type.addItem(
            "Полоса отвода автомобильной дороги", "road"
        )
        self.right_of_way_type.addItem(
            "Полоса отвода линии электропередачи", "powerline"
        )


    # =========================
    # PARTICIPANTS
    # =========================
    def add_participant_row(self):
        row = QHBoxLayout()

        participant = SafeComboBox()
        tech_type = SafeComboBox()
        time = QLineEdit()
        time.setPlaceholderText("HH:MM")

        participant.addItem("", None)
        tech_type.addItem("", None)

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

    def on_right_of_way_index_changed(self, index):
        value = self.right_of_way.itemText(index)
        enabled = (value == "Да")

        self.right_of_way_type.setVisible(enabled)
        self.owner.setVisible(enabled)

        if enabled:
            self.fill_right_of_way_types()

        if not enabled:
            self.right_of_way_type.clear()
            self.owner.clear()

    def load_selsovets(self, municipality_id):
        selsovets = self.api.get_selsovets(municipality_id)

        self.settlement.clear()

        if not selsovets:
            self.settlement.setVisible(False)
            return

        self.settlement.setVisible(True)
        self.settlement.addItem("", None)

        for s in selsovets:
            self.settlement.addItem(s["name"], s["id"])

    def on_municipality_changed(self, index):
        municipality_id = self.municipality.currentData()

        if not municipality_id:
            self.settlement.clear()
            self.settlement.setVisible(False)
            return

        self.load_selsovets(municipality_id)

    # =========================
    # SAVE
    # =========================
    def save(self):
        dto = self.service.build_dto(self)
        self.api.create_fire(dto)
        self.app.go_to_main(self.user)