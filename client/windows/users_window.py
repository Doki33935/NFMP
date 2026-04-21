from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox
)


class UsersWindow(QWidget):
    def __init__(self, api, app):
        super().__init__()

        self.api = api
        self.app = app

        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        title = QLabel("👥 Создание пользователя")
        title.setStyleSheet("font-size: 18px; color: #ff3b30;")
        self.layout.addWidget(title)

        # Поля
        self.username = QLineEdit()
        self.username.setPlaceholderText("Логин")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("ФИО")

        self.role = QComboBox()
        self.role.addItems([
            "dispatcher",
            "inspector",
            "admin",
            "chief"
        ])

        # Кнопки
        create_btn = QPushButton("Создать пользователя")
        create_btn.clicked.connect(self.create_user)

        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.app.go_back)

        # Результат
        self.result = QLabel("")

        # Добавление
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.full_name)
        self.layout.addWidget(self.role)
        self.layout.addWidget(create_btn)
        self.layout.addWidget(back_btn)
        self.layout.addWidget(self.result)

    def create_user(self):
        try:
            self.api.create_user(
                self.username.text(),
                self.password.text(),
                self.full_name.text(),
                self.role.currentText()
            )

            # ✅ popup успеха
            msg = QMessageBox(self)
            msg.setWindowTitle("Успех")
            msg.setText("Пользователь успешно создан")
            msg.setIcon(QMessageBox.Information)
            msg.exec()

            # 👉 возврат в главное меню
            self.app.go_to_main(self.app.user)

        except Exception as e:
            print(e)

            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка")
            msg.setText("Не удалось создать пользователя")
            msg.setIcon(QMessageBox.Critical)
            msg.exec()