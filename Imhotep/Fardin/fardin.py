import sys
import re
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QCheckBox, QSpacerItem, QSizePolicy,
    QHBoxLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt


class GlowButton(QPushButton):
    def __init__(self, text="", glow_color="#701A1A", *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.glow_color = QColor(glow_color)
        self._shadow = None
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def enterEvent(self, event):
        if not self._shadow:
            self._shadow = QGraphicsDropShadowEffect(self)
            self._shadow.setBlurRadius(18)
            self._shadow.setColor(self.glow_color)
            self._shadow.setOffset(0, 0)
            self.setGraphicsEffect(self._shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._shadow:
            self.setGraphicsEffect(None)
            self._shadow = None
        super().leaveEvent(event)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Red Reserve")
        self.resize(420, 400)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        # ------------------------
        # BACK BUTTON (top-left)
        # ------------------------
        back_btn = GlowButton("←")
        back_btn.setFixedSize(40, 30)
        back_btn.setFont(QFont("Arial", 22))
        back_btn.setStyleSheet(
            "QPushButton { border:none; color:#701A1A; background:transparent; }"
        )
        back_btn.clicked.connect(self.close)

        back_bar = QHBoxLayout()
        back_bar.addWidget(back_btn)   # left
        back_bar.addStretch()          # push rest to the right

        # Pull this bar left so it’s near the window edge,
        # while keeping the main content margins at 80px.
        back_bar.setContentsMargins(-80, 5, 0, 5)

        # ------------------------
        # TITLE
        # ------------------------
        title = QLabel("LOGIN", self)
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #701A1A;")

        # ------------------------
        # USERNAME
        # ------------------------
        self.username = QLineEdit(self)
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(40)
        self.username.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.username.setStyleSheet("""
            QLineEdit {
                border: 2px solid black;
                border-radius: 6px;
                padding-left: 8px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 2px solid #701A1A;
            }
        """)

        # ------------------------
        # PASSWORD
        # ------------------------
        self.password = QLineEdit(self)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(40)
        self.password.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password.setStyleSheet("""
            QLineEdit {
                border: 2px solid black;
                border-radius: 6px;
                padding-left: 8px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 2px solid #701A1A;
            }
        """)

        # ------------------------
        # SHOW PASSWORD
        # ------------------------
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.setStyleSheet("color: #701A1A; font-size: 13px;")
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)

        # ------------------------
        # LOGIN BUTTON
        # ------------------------
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #701A1A;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B1E1E;
            }
        """)
        self.login_btn.clicked.connect(self.check_login)

        # ------------------------
        # CREATE ACCOUNT BUTTON
        # ------------------------
        self.create_btn = QPushButton("Create an account")
        self.create_btn.setMinimumHeight(38)
        self.create_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.create_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #701A1A;
                border-radius: 8px;
                color: #701A1A;
                background: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #701A1A;
                color: white;
            }
        """)
        self.create_btn.clicked.connect(self.create_account)

        # ------------------------
        # MAIN LAYOUT
        # ------------------------
        layout = QVBoxLayout()
        layout.addLayout(back_bar)  # back button row at the top
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(title)
        layout.addSpacing(25)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.show_password_cb)
        layout.addSpacing(15)
        layout.addWidget(self.login_btn)
        layout.addSpacing(10)
        layout.addWidget(self.create_btn)
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.setContentsMargins(50, 20, 50, 30)
        layout.setSpacing(12)
        self.setLayout(layout)

    def toggle_password_visibility(self):
        self.password.setEchoMode(
            QLineEdit.Normal if self.show_password_cb.isChecked() else QLineEdit.Password
        )

    def connect_db(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="fArdin787898",
                database="blood_bank"
            )
            return conn
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", str(err))
            return None

    def check_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Input Error", "Enter both username and password!")
            return

        conn = self.connect_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Username, Pass FROM user_login WHERE Username=%s", (user,))
            row = cursor.fetchone()
            conn.close()

            if row is None:
                QMessageBox.warning(self, "Login Failed", "User does not exist!")
                return

            db_user, db_pass = row
            if db_pass is None:
                db_pass = ""

            if pwd == db_pass:
                QMessageBox.information(self, "Success", "Successfully logged in!")
            else:
                QMessageBox.warning(self, "Login Failed", "Incorrect username or password!")

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"MySQL Error: {err}")

    def create_account(self):
        QMessageBox.information(self, "Info", "Create account clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
