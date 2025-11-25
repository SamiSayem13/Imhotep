from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QFrame, QProgressBar, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QTimer
from pathlib import Path
from mysql.connector import Error
import traceback, pymysql
from PyQt5.QtWidgets import QMessageBox
import bcrypt

class RegisterView(QWidget):
    goto_selection = pyqtSignal()        # back/cancel
    register_success = pyqtSignal(str)   # emit User_ID if you want to auto-login/route
    goto_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep Registration")
        self.resize(1000, 700)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: #f5f5f5;")

        # Card
        self.card = QFrame(self)
        self.card.setStyleSheet("QFrame { background-color: white; border-radius: 20px; }")

        # Back
        self.back_btn = QPushButton("← Back", self)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton { background-color: #DC3545; color: white; border: none; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #E94B5A; }
        """)
        self.back_btn.setFixedSize(90, 35)
        self.back_btn.move(20, 20)
        self.back_btn.clicked.connect(lambda: self.goto_login.emit())

        # Title
        self.title = QLabel("Imhotep")
        self.title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("Register your account")
        self.subtitle.setFont(QFont("Segoe UI", 12))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: gray;")

        # Inputs
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full Name")

        self.pass_check = QLineEdit()
        self.pass_check.setPlaceholderText("Enter something that you'll never forget")

        self.unique_code = QLineEdit()
        self.unique_code.setPlaceholderText("Unique Code (digits only)")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Set Password (8-16 chars)")
        self.password.setEchoMode(QLineEdit.Password)

        for field in [self.full_name, self.pass_check, self.unique_code, self.password]:
            field.setFixedHeight(45)
            field.setStyleSheet("""
                QLineEdit { border: 2px solid #ddd; border-radius: 8px; padding-left: 10px; font-size: 15px; font-family: 'Segoe UI'; }
                QLineEdit:focus { border-color: #4CAF50; }
            """)

        # Eye toggle
        self.eye_button = QPushButton(self.password)
        self.eye_button.setText("👁️")
        self.eye_button.setCheckable(True)
        self.eye_button.setCursor(Qt.PointingHandCursor)
        self.eye_button.setToolTip("Show/Hide Password")
        self.eye_button.setFixedSize(24, 24)
        self.eye_button.setStyleSheet("""
            QPushButton { border: none; background-color: transparent; opacity: 0.6; }
            QPushButton:hover { background-color: rgba(0, 0, 0, 0.05); border-radius: 12px; opacity: 1.0; }
        """)
        self.eye_button.clicked.connect(self.toggle_password_visibility)
        self.password.textChanged.connect(self.adjust_eye_position)

        # Strength
        self.password_strength = QLabel("")
        self.password_strength.setAlignment(Qt.AlignLeft)
        self.password_strength.setStyleSheet("color: gray; font-size: 12px; padding-left: 5px; font-family: 'Segoe UI';")

        self.strength_bar = QProgressBar()
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setStyleSheet("""
            QProgressBar { background-color: #ddd; border-radius: 3px; }
            QProgressBar::chunk { border-radius: 3px; background-color: #f44336; }
        """)
        self.password.textChanged.connect(self.check_password_strength)

        # Info + notifications
        self.info = QLabel("Please have your NID or Birth Certificate ready for verification.")
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("color: gray; font-size: 12px; font-family: 'Segoe UI';")

        self.notification = QLabel("")
        self.notification.setAlignment(Qt.AlignCenter)
        self.notification.setStyleSheet("color: red; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';")

        # Buttons
        self.register_btn = QPushButton("Confirm")
        self.register_btn.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 8px; padding: 12px; font-weight: 600; font-size: 14px; font-family: 'Segoe UI'; }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.register_btn.clicked.connect(lambda: self.register_user())

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; border: none; border-radius: 8px; padding: 12px; font-weight: 600; font-size: 14px; font-family: 'Segoe UI'; }
            QPushButton:hover { background-color: #e53935; }
        """)
        self.cancel_btn.clicked.connect(self.goto_login.emit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.setSpacing(20)

        # Layout
        layout = QVBoxLayout(self.card)
        layout.addStretch(1)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addSpacing(20)

        layout.addWidget(self.full_name)
        layout.addWidget(self.pass_check)
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

    # ---------- NEW: auto-clear when shown ----------
    def clear_fields(self):
        """Reset all registration inputs and messages."""
        self.full_name.clear()
        self.pass_check.clear()
        self.unique_code.clear()
        self.password.clear()
        self.notification.clear()
        self.password_strength.clear()
        self.strength_bar.setValue(0)

    def showEvent(self, event):
        # every time this view becomes visible, wipe old data
        self.clear_fields()
        super().showEvent(event)

    # ----- layout helpers -----
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
        self.eye_button.move(
            self.password.width() - self.eye_button.width() - 10,
            (self.password.height() - self.eye_button.height()) // 2
        )

    def toggle_password_visibility(self):
        if self.eye_button.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
            self.eye_button.setText("🙈")
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.eye_button.setText("👁️")

    # ----- strength -----
    def check_password_strength(self):
        password = self.password.text()
        score = 0
        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isupper() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in "!@#$%^&*()-_=+[]{};:'\",.<>?/\\|" for c in password): score += 1

        if score <= 2:
            strength, color, bar_value = "Weak", "#f44336", 30
        elif 3 <= score <= 4:
            strength, color, bar_value = "Medium", "#ff9800", 65
        else:
            strength, color, bar_value = "Strong", "#4CAF50", 100

        self.password_strength.setText(f"Password strength: {strength}")
        self.password_strength.setStyleSheet(
            f"color: {color}; font-size: 12px; padding-left: 5px; font-family: 'Segoe UI';"
        )
        self.strength_bar.setValue(bar_value)
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: #ddd; border-radius: 3px; }}
            QProgressBar::chunk {{ border-radius: 3px; background-color: {color}; }}
        """)

    def show_notification(self, message, color="red"):
        self.notification.setText(message)
        self.notification.setStyleSheet(
            f"color: {color}; font-size: 13px; font-weight: bold; font-family: 'Segoe UI';"
        )

    # ----- DB: uses shared get_conn() -----
    def register_user(self, checked=False):
        conn = None
        cur = None

        try:
            # gather & validate inputs
            fullname = self.full_name.text().strip()
            unique_code = self.unique_code.text().strip()
            Match = self.pass_check.text().strip()
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

            # connect via PyMySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="imhotep",
                cursorclass=pymysql.cursors.Cursor
            )
            cur = conn.cursor()

            # duplicate check
            cur.execute("SELECT 1 FROM `user` WHERE `User_ID`=%s", (unique_code,))
            if cur.fetchone():
                self.show_notification("Unique Code already exists!")
                return

            # insert with hashed password + match
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_m = bcrypt.hashpw(Match.encode('utf-8'), bcrypt.gensalt())
            cur.execute(
                "INSERT INTO `user` (`User_ID`, `User_Name`, `Password`, `match`) VALUES (%s, %s, %s, %s)",
                (unique_code, fullname, hashed_pw.decode('utf-8'), hashed_m.decode('utf-8'))
            )
            conn.commit()

            self.show_notification("Registration Successful!", color="green")
            # optional: emit success
            self.register_success.emit(unique_code)

            # go back to login
            self.goto_login.emit()

            # local clear (even though showEvent will clear next time too)
            self.clear_fields()

        except Exception as e:
            traceback.print_exc()
            try:
                if conn:
                    conn.rollback()
            except:
                pass
            self.show_notification(f"Database error: {e}")
            QMessageBox.critical(self, "Database error", str(e))

        finally:
            try:
                if cur:
                    cur.close()
                if conn:
                    conn.close()
            except:
                pass
