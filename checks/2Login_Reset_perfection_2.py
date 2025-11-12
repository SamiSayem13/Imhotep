import sys
import re
import mysql.connector
from mysql.connector import errors as db_errors
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QMessageBox, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QCursor


# -------------------- Common Authentication Handler --------------------
class AuthHandler:
    @staticmethod
    def connect_db():
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="imhotep"
            )
            return conn
        except db_errors.Error as e:
            return None

    @staticmethod
    def verify_user_credentials(User_ID, Password):
        try: 
            conn = AuthHandler.connect_db()
            if not conn:
                return "Database connection failed"
            cur = conn.cursor()
            cur.execute("SELECT Password FROM user WHERE User_ID=%s", (User_ID,))
            result = cur.fetchone()
            cur.close()
            conn.close()
            if result and result[0] == Password:
                return "Login Success"
            else:
                return "Invalid Credentials"
        except db_errors.Error as e:
            return "Database Error: " + str(e)

    @staticmethod
    def reset_user_password(User_ID, Password):
        try:
            conn = AuthHandler.connect_db()
            if not conn:
                return "Database connection failed"
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE User_ID=%s", (User_ID))
            if cur.fetchone() is None:
                return "Unique Code not found"
            cur.execute("UPDATE user SET Password=%s WHERE User_ID=%s", (Password, User_ID))
            conn.commit()
            cur.close()
            conn.close()
            return "Password successfully updated"
        except db_errors.Error as e:
            return "Database Error: " + str(e)

# changes something

# -------------------- Forgot Password Window --------------------
class ForgotPasswordUI(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Reset Password - imhotep")
        self.resize(parent.width(), parent.height())
        self.setStyleSheet("background-color: #f4f5f7;")
        self.setMinimumSize(400, 450)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.card = QFrame(self)
        self.card.setStyleSheet("QFrame { background-color: white; border-radius: 18px; }")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.card.setGraphicsEffect(shadow)

        self.back_btn = QPushButton("← Back", self)
        self.back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E94B5A;
            }
        """)
        self.back_btn.clicked.connect(self.close_window)

        self.setup_ui()
        self.adjust_positions()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_positions()

    def adjust_positions(self):
        win_w, win_h = self.width(), self.height()
        card_w, card_h = int(win_w * 0.65), int(win_h * 0.7)
        card_x, card_y = (win_w - card_w) // 2, (win_h - card_h) // 2
        self.card.setGeometry(card_x, card_y, card_w, card_h)
        self.back_btn.setGeometry(20, 20, 80, 32)

    def setup_ui(self):
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        title = QLabel("Imhotep")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Reset your password")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #555;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.code = QLineEdit()
        self.code.setPlaceholderText("Unique Code")
        self.code.setFixedHeight(38)
        self.code.setStyleSheet(self._line_style())
        self.code.textChanged.connect(lambda txt: self._remove_spaces_in_lineedit(self.code))
        layout.addWidget(self.code)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)
        self.new_pwd = QLineEdit()
        self.new_pwd.setPlaceholderText("New Password")
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setFixedHeight(38)
        self.new_pwd.setStyleSheet(self._line_style())
        self.new_pwd.textChanged.connect(self.check_strength)
        pwd_row.addWidget(self.new_pwd)

        self.show_pwd_btn = QPushButton("👁")
        self.show_pwd_btn.setFixedWidth(40)
        self.show_pwd_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_pwd_btn.clicked.connect(lambda: self._toggle_echo(self.new_pwd, self.show_pwd_btn))
        self.show_pwd_btn.setStyleSheet(self._small_icon_button_style())
        pwd_row.addWidget(self.show_pwd_btn)
        layout.addLayout(pwd_row)

        self.strength_label = QLabel("")
        self.strength_label.setFont(QFont("Segoe UI", 8))
        self.strength_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.strength_label)

        conf_row = QHBoxLayout()
        conf_row.setSpacing(8)
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setPlaceholderText("Confirm Password")
        self.confirm_pwd.setEchoMode(QLineEdit.Password)
        self.confirm_pwd.setFixedHeight(38)
        self.confirm_pwd.setStyleSheet(self._line_style())
        conf_row.addWidget(self.confirm_pwd)

        self.show_conf_btn = QPushButton("👁")
        self.show_conf_btn.setFixedWidth(40)
        self.show_conf_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_conf_btn.clicked.connect(lambda: self._toggle_echo(self.confirm_pwd, self.show_conf_btn))
        self.show_conf_btn.setStyleSheet(self._small_icon_button_style())
        conf_row.addWidget(self.show_conf_btn)
        layout.addLayout(conf_row)

        info = QLabel("For verification, please have your NID or Birth Certificate ready.")
        info.setFont(QFont("Segoe UI", 8))
        info.setStyleSheet("color: #777;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        submit_btn = self.create_button("Submit", "#1EBE64", "#2ED97A")
        submit_btn.clicked.connect(self.reset_password)
        btn_row.addWidget(submit_btn)

        cancel_btn = self.create_button("Cancel", "#DC3545", "#E94B5A")
        cancel_btn.clicked.connect(self.close_window)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color:red;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

    def _line_style(self):
        return """
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 11pt;
                background-color: #fff;
            }
            QLineEdit:focus {
                border: 2px solid #1EBE64;
            }
        """

    def _small_icon_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """

    def _toggle_echo(self, line_edit: QLineEdit, btn: QPushButton):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            btn.setText("🙈")
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            btn.setText("👁")

    def _remove_spaces_in_lineedit(self, lineedit: QLineEdit):
        text = lineedit.text()
        if " " in text:
            cursor_pos = lineedit.cursorPosition()
            new_text = text.replace(" ", "")
            lineedit.blockSignals(True)
            lineedit.setText(new_text)
            lineedit.setCursorPosition(max(0, cursor_pos - (len(text) - len(new_text))))
            lineedit.blockSignals(False)

    def create_button(self, text, color, hover_color):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(36)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        return btn

    def check_strength(self):
        pwd = self.new_pwd.text()
        strength = self.get_password_strength(pwd)
        if strength == "Weak":
            self.strength_label.setText("Password Strength: Weak")
            self.strength_label.setStyleSheet("color: red;")
        elif strength == "Medium":
            self.strength_label.setText("Password Strength: Medium")
            self.strength_label.setStyleSheet("color: orange;")
        elif strength == "Strong":
            self.strength_label.setText("Password Strength: Strong")
            self.strength_label.setStyleSheet("color: green;")
        else:
            self.strength_label.setText("")

    def get_password_strength(self, password: str) -> str:
        if len(password) < 8 or len(password) > 16:
            return "Weak"
        lower = re.search(r"[a-z]", password)
        upper = re.search(r"[A-Z]", password)
        digit = re.search(r"\d", password)
        special = re.search(r"[^A-Za-z0-9\s]", password)
        if all([lower, upper, digit, special]):
            if len(password) >= 12:
                return "Strong"
            return "Medium"
        return "Weak"

    def reset_password(self):
        code = self.code.text().strip().replace(" ", "")
        new = self.new_pwd.text().strip()
        confirm = self.confirm_pwd.text().strip()
        self.error_label.setText("")
        if not code or not new or not confirm:
            self.error_label.setText("Please fill all fields.")
            return
        if new != confirm:
            self.error_label.setText("Passwords do not match.")
            return
        strength = self.get_password_strength(new)
        if strength == "Weak":
            self.error_label.setText("Password must be 8–16 chars with upper, lower, digit, special.")
            return

        result = AuthHandler.reset_user_password(code, new)
        if "successfully" in result:
            self.error_label.setStyleSheet("color:green;")
        else:
            self.error_label.setStyleSheet("color:red;")
        self.error_label.setText(result)

    def close_window(self):
        self.close()
        try:
            self.parent.show()
        except Exception:
            pass


# -------------------- Login Window --------------------
class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep Login")
        self.resize(480, 520)
        self.setStyleSheet("background-color: #f4f5f7;")
        self.setMinimumSize(400, 450)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.card = QFrame(self)
        self.card.setStyleSheet("QFrame { background-color: white; border-radius: 18px; }")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.card.setGraphicsEffect(shadow)

        self.back_btn = QPushButton("← Back", self)
        self.back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E94B5A;
            }
        """)
        self.back_btn.clicked.connect(self.close_window)

        self.setup_ui()
        self.adjust_positions()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_positions()

    def adjust_positions(self):
        win_w, win_h = self.width(), self.height()
        card_w, card_h = int(win_w * 0.65), int(win_h * 0.7)
        card_x, card_y = (win_w - card_w) // 2, (win_h - card_h) // 2
        self.card.setGeometry(card_x, card_y, card_w, card_h)
        self.back_btn.setGeometry(20, 20, 80, 32)

    def setup_ui(self):
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        title = QLabel("Imhotep")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Log in to your account")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #555;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.unique_code = QLineEdit()
        self.unique_code.setPlaceholderText("Unique Code")
        self.unique_code.setFixedHeight(38)
        self.unique_code.setStyleSheet(self._line_style())
        self.unique_code.textChanged.connect(lambda txt: self._remove_spaces_in_lineedit(self.unique_code))
        layout.addWidget(self.unique_code)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(38)
        self.password.setStyleSheet(self._line_style())
        pwd_row.addWidget(self.password)

        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedWidth(40)
        self.show_password_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_password_btn.clicked.connect(lambda: self._toggle_echo(self.password, self.show_password_btn))
        self.show_password_btn.setStyleSheet(self._small_icon_button_style())
        pwd_row.addWidget(self.show_password_btn)
        layout.addLayout(pwd_row)

        forgot = QLabel("<a href='#' style='color:#007BFF;text-decoration:none;'>Forgot Password?</a>")
        forgot.setFont(QFont("Segoe UI", 9))
        forgot.setAlignment(Qt.AlignLeft)
        forgot.setTextInteractionFlags(Qt.TextBrowserInteraction)
        forgot.linkActivated.connect(self.open_forgot_password)
        layout.addWidget(forgot)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color:red;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.login_btn = self.create_button("Log In", "#2475FF", "#3B8BFF")
        self.login_btn.clicked.connect(self.handle_login)
        row.addWidget(self.login_btn)

        self.register_btn = self.create_button("Register", "#1EBE64", "#2ED97A")
        self.register_btn.clicked.connect(lambda: self.error_label.setText("Register clicked!"))
        row.addWidget(self.register_btn)
        layout.addLayout(row)

    def _line_style(self):
        return """
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 11pt;
                background-color: #fff;
            }
            QLineEdit:focus {
                border: 2px solid #1EBE64;
            }
        """

    def _small_icon_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """

    def _toggle_echo(self, line_edit, btn):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            btn.setText("🙈")
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            btn.setText("👁")

    def _remove_spaces_in_lineedit(self, lineedit):
        text = lineedit.text()
        if " " in text:
            cursor_pos = lineedit.cursorPosition()
            new_text = text.replace(" ", "")
            lineedit.blockSignals(True)
            lineedit.setText(new_text)
            lineedit.setCursorPosition(max(0, cursor_pos - (len(text) - len(new_text))))
            lineedit.blockSignals(False)

    def create_button(self, text, color, hover_color):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        return btn

    def open_forgot_password(self):
        self.forgot_window = ForgotPasswordUI(self)
        self.forgot_window.resize(self.width(), self.height())
        self.forgot_window.show()
        self.hide()

    def handle_login(self):
        user = self.unique_code.text().strip()
        pwd = self.password.text().strip()
        self.error_label.setText("")
        if " " in user:
            self.error_label.setText("Unique ID cannot contain spaces.")
            return
        if not user or not pwd:
            self.error_label.setText("Please enter both Unique Code and Password.")
            return
        result = AuthHandler.verify_user_credentials(user, pwd)
        if result == "Login Success":
            self.error_label.setStyleSheet("color:green;")
            self.error_label.setText("Login Successful")
        elif "Error" in result:
            self.error_label.setStyleSheet("color:red;")
            self.error_label.setText(result)
        else:
            self.error_label.setStyleSheet("color:red;")
            self.error_label.setText("Incorrect Unique ID or Password.")

    def close_window(self):
        self.close()


# -------------------- Run App --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginUI()
    win.show()
    sys.exit(app.exec_())



