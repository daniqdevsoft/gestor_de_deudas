import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLineEdit, QPushButton, QLabel,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from vista.interfaz import ventana_principal

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(400, 250)
        self.setWindowIcon(QIcon("data/favicon.ico"))

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Título
        titulo = QLabel("Gestor de Deudas - Login")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(titulo)

        # Usuario
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setFixedHeight(45)  # más alto
        self.user_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        layout.addWidget(self.user_input)

        # Contraseña
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedHeight(45)  # más alto
        self.pass_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        layout.addWidget(self.pass_input)

        # Botón login
        self.login_btn = QPushButton("Ingresar")
        self.login_btn.setFixedHeight(60)  # botón más grande
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 6px;
                padding: 10px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.login_btn.clicked.connect(self.check_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def check_login(self):
        usuario = self.user_input.text()
        clave = self.pass_input.text()

        # Aquí defines tus credenciales válidas
        if usuario == "keli" and clave == "gus123456":
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("data/favicon.png"))

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = ventana_principal()
        window.setWindowIcon(QIcon("data/favicon.ico"))
        window.show()
        sys.exit(app.exec_())