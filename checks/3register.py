import sys
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFrame, QProgressBar, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from pathlib import Path


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep Registration")
        self.resize(1000, 700)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: #f5f5f5;")

        # ---------------- CARD FRAME ----------------
        self.card = QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
            }
        """)

        # ---------------- BACK BUTTON ----------------
        self.back_btn = QPushButton("← Back", self)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4CAF50;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Segoe UI';
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.back_btn.setFixedSize(90, 35)
        self.back_btn.move(20, 20)
        self.back_btn.clicked.connect(self.go_back)

        # ---------------- TITLE & SUBTITLE ----------------
        self.title = QLabel("Imhotep")
        self.title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("Register your account")
        self.subtitle.setFont(QFont("Segoe UI", 12))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: gray;")

        # ---------------- INPUT FIELDS ----------------
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full Name")

        self.unique_code = QLineEdit()
        self.unique_code.setPlaceholderText("Unique Code (digits only)")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Set Password (8-16 chars)")
        self.password.setEchoMode(QLineEdit.Password)

        for field in [self.full_name, self.unique_code, self.password]:
            field.setFixedHeight(45)
            field.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    padding-left: 10px;
                    font-size: 15px;
                    font-family: 'Segoe UI';
                }
                QLineEdit:focus {
                    border-color: #4CAF50;
                }
            """)

        # ---------------- EYE BUTTON ----------------
        self.eye_button = QPushButton(self.password)
        BASE_DIR = Path(__file__).resolve().parent
        eye_off_path = BASE_DIR / "eye-off.png"
        eye_path = BASE_DIR / "eye.png"

        if eye_off_path.exists():
            self.eye_button.setIcon(QIcon(str(eye_off_path)))
        else:
            self.eye_button.setText("👁️")

        self.eye_button.setCheckable(True)
        self.eye_button.setCursor(Qt.PointingHandCursor)
        self.eye_button.setToolTip("Show/Hide Password")
        self.eye_button.setFixedSize(24, 24)
        self.eye_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                opacity: 0.6;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 12px;
                opacity: 1.0;
            }
        """)
        self.eye_button.clicked.connect(self.toggle_password_visibility)
        self.password.textChanged.connect(self.adjust_eye_position)

        # ---------------- PASSWORD STRENGTH ----------------
        self.password_strength = QLabel("")
        self.password_strength.setAlignment(Qt.AlignLeft)
        self.password_strength.setStyleSheet("color: gray; font-size: 12px; padding-left: 5px; font-family: 'Segoe UI';")

        self.strength_bar = QProgressBar()
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ddd;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #f44336;
            }
        """)

        self.password.textChanged.connect(self.check_password_strength)

        # ---------------- INFO & NOTIFICATION ----------------
        self.info = QLabel("Please have your NID or Birth Certificate ready for verification.")
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("color: gray; font-size: 12px; font-family: 'Segoe UI';")

        self.notification = QLabel("")
        self.notification.setAlignment(Qt.AlignCenter)
        self.notification.setStyleSheet("color: red; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';")

        # ---------------- BUTTONS ----------------
        self.register_btn = QPushButton("Register")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.register_btn.clicked.connect(self.register_user)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)

        # ---------------- BUTTON LAYOUT ----------------
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.setSpacing(20)

        # ---------------- MAIN CARD LAYOUT ----------------
        layout = QVBoxLayout(self.card)
        layout.addStretch(1)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.full_name)
        layout.addWidget(self.unique_code)
        layout.addWidget(self.password)
        layout.addWidget(self.password_strength)
        layout.addWidget(self.strength_bar)
        layout.addSpacing(10)
        layout.addWidget(self.info)
        layout.addWidget(self.notification)
        layout.addSpacing(15)
        layout.addLayout(btn_layout)
        layout.addStretch(1)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(12)

        self.update_card_layout()

    # ---------------- UI UPDATE METHODS ----------------
    def update_card_layout(self):
        card_width = int(self.width() * 0.55)
        card_height = int(self.height() * 0.8)
        self.card.resize(card_width, card_height)
        self.card.move((self.width() - card_width) // 2, (self.height() - card_height) // 2)
        self.adjust_eye_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_layout()

    def adjust_eye_position(self):
        """Keep eye button inside password field and center-aligned."""
        self.eye_button.move(
            self.password.width() - self.eye_button.width() - 10,
            (self.password.height() - self.eye_button.height()) // 2
        )

    def toggle_password_visibility(self):
        BASE_DIR = Path(__file__).resolve().parent
        eye_off_path = BASE_DIR / "eye-off.png"
        eye_path = BASE_DIR / "eye.png"

        if self.eye_button.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
            if eye_path.exists():
                self.eye_button.setIcon(QIcon(str(eye_path)))
            else:
                self.eye_button.setText("🙈")
        else:
            self.password.setEchoMode(QLineEdit.Password)
            if eye_off_path.exists():
                self.eye_button.setIcon(QIcon(str(eye_off_path)))
            else:
                self.eye_button.setText("👁️")

    # ---------------- PASSWORD STRENGTH CHECK ----------------
    def check_password_strength(self):
        password = self.password.text()
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()-_=+[]{};:'\",.<>?/\\|" for c in password):
            score += 1

        if score <= 2:
            strength = "Weak"
            color = "#f44336"
            bar_value = 30
        elif 3 <= score <= 4:
            strength = "Medium"
            color = "#ff9800"
            bar_value = 65
        else:
            strength = "Strong"
            color = "#4CAF50"
            bar_value = 100

        self.password_strength.setText(f"Password strength: {strength}")
        self.password_strength.setStyleSheet(f"color: {color}; font-size: 12px; padding-left: 5px; font-family: 'Segoe UI';")
        self.strength_bar.setValue(bar_value)
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #ddd;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
                background-color: {color};
            }}
        """)

    # ---------------- HELPER METHODS ----------------
    def show_notification(self, message, color="red"):
        self.notification.setText(message)
        self.notification.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';")

    def register_user(self):
        fullname = self.full_name.text().strip()
        unique_code = self.unique_code.text().strip()
        password = self.password.text().strip()
        self.notification.clear()

        if not fullname or not unique_code or not password:
            self.show_notification("Please fill in all fields.")
            return
        if " " in unique_code:
            self.show_notification("Unique Code cannot contain spaces!")
            return
        if not unique_code.isdigit():
            self.show_notification("Unique Code must contain digits only!")
            return
        if not (8 <= len(password) <= 16):
            self.show_notification("Password must be 8 to 16 characters long!")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="imhotep")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM user WHERE User_ID = %s", (unique_code,))
            if cursor.fetchone():
                self.show_notification("Unique Code already exists!")
                return

            cursor.execute(
                "INSERT INTO user (User_Name, User_ID, Password) VALUES (%s, %s, %s)",
                (fullname, unique_code, password)
            )
            conn.commit()

            self.show_notification("Registration Successful!", color="green")
            self.full_name.clear()
            self.unique_code.clear()
            self.password.clear()
            self.password_strength.clear()
            self.strength_bar.setValue(0)

        except Error as err:
            if "2003" in str(err):
                self.show_notification("MySQL server not running! Please start it.")
            elif "1049" in str(err):
                self.show_notification("Database 'imhotep' not found! Please create it first.")
            else:
                self.show_notification(f"Database Error: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def go_back(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())
