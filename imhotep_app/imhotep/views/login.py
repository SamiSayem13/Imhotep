from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout,
    QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QCursor
from ..db.auth import AuthHandler

class LoginView(QWidget):
    goto_forgot = pyqtSignal()
    goto_selection = pyqtSignal()
    goto_register = pyqtSignal()
    goto_doctor = pyqtSignal()          # <-- added so handle_login can emit this
    login_success = pyqtSignal(str)     # emit User_ID

    def __init__(self):
        super().__init__()
        self.current_role = None        # <-- added to remember selected role

        self.setWindowTitle("Imhotep Login")
        self.resize(480, 520)
        self.setStyleSheet("background-color: #f4f5f7;")
        self.setMinimumSize(400, 450)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.card = QFrame(self)
        self.card.setStyleSheet("QFrame { background-color: white; border-radius: 18px; }")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25); shadow.setOffset(0, 5); shadow.setColor(QColor(0, 0, 0, 60))
        self.card.setGraphicsEffect(shadow)

        self.back_btn = QPushButton("← Back", self)
        self.back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.back_btn.setStyleSheet("""
            QPushButton { background-color: #DC3545; color: white; border: none; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #E94B5A; }
        """)
        self.back_btn.clicked.connect(self.goto_selection.emit)

        self.setup_ui()
        self.adjust_positions()

    # <-- added setter so Router can pass the role (doctor/patient/pharmacist)
    def set_role(self, role: str):
        self.current_role = role
        print("Role set to:", role)

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
        title.setFont(QFont("Segoe UI", 18, QFont.Bold)); title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Log in to your account")
        subtitle.setFont(QFont("Segoe UI", 10)); subtitle.setStyleSheet("color: #555;"); subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.unique_code = QLineEdit()
        self.unique_code.setPlaceholderText("Unique Code")
        self.unique_code.setFixedHeight(38); self.unique_code.setStyleSheet(self._line_style())
        self.unique_code.textChanged.connect(lambda _: self._remove_spaces_in_lineedit(self.unique_code))
        layout.addWidget(self.unique_code)

        pwd_row = QHBoxLayout(); pwd_row.setSpacing(8)
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password"); self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(38); self.password.setStyleSheet(self._line_style())
        pwd_row.addWidget(self.password)

        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedWidth(40); self.show_password_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_password_btn.clicked.connect(lambda: self._toggle_echo(self.password, self.show_password_btn))
        self.show_password_btn.setStyleSheet(self._small_icon_button_style())
        pwd_row.addWidget(self.show_password_btn)
        layout.addLayout(pwd_row)

        forgot = QLabel("<a href='#' style='color:#007BFF;text-decoration:none;'>Forgot Password?</a>")
        forgot.setFont(QFont("Segoe UI", 9)); forgot.setAlignment(Qt.AlignLeft)
        forgot.setTextInteractionFlags(Qt.TextBrowserInteraction)
        forgot.linkActivated.connect(self.goto_forgot.emit)
        layout.addWidget(forgot)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color:red;"); self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        row = QHBoxLayout(); row.setSpacing(12)
        self.login_btn = self.create_button("Log In", "#2475FF", "#3B8BFF")
        self.login_btn.clicked.connect(self.handle_login); row.addWidget(self.login_btn)

        self.register_btn = self.create_button("Register", "#1EBE64", "#2ED97A")
        self.register_btn.clicked.connect(self.goto_register.emit)
        row.addWidget(self.register_btn)
        layout.addLayout(row)

    def _line_style(self):
        return """                QLineEdit { border: 1px solid #ddd; border-radius: 8px; padding-left: 10px; font-size: 11pt; background-color: #fff; }
            QLineEdit:focus { border: 2px solid #1EBE64; }
        """

    def _small_icon_button_style(self):
        return """                QPushButton { background-color: transparent; border: 1px solid #ddd; border-radius: 6px; font-size: 12pt; }
            QPushButton:hover { background-color: #f0f0f0; }
        """

    def _toggle_echo(self, line_edit, btn):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal); btn.setText("🙈")
        else:
            line_edit.setEchoMode(QLineEdit.Password); btn.setText("👁")

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
        btn = QPushButton(text); btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; border-radius: 8px; font-weight: bold; font-size: 10pt; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """)
        return btn

    def handle_login(self):
        user = self.unique_code.text().strip()
        pwd = self.password.text().strip()
        self.error_label.setText("")
        if " " in user:
            self.error_label.setText("Unique ID cannot contain spaces."); return
        if not user or not pwd:
            self.error_label.setText("Please enter both Unique Code and Password."); return

        result = AuthHandler.verify_user_credentials(user, pwd)

        if result == "Login Success":
            self.error_label.setStyleSheet("color:green;")
            self.error_label.setText("Login Successful")
            # keep emitting user_id for generic success
            self.login_success.emit(user)
            # role-specific route (doctor/patient/pharmacist)
            if self.current_role == "doctor":
                self.goto_doctor.emit()
        elif "Error" in result:
            self.error_label.setStyleSheet("color:red;"); self.error_label.setText(result)
        else:
            self.error_label.setStyleSheet("color:red;"); self.error_label.setText("Incorrect Unique ID or Password.")
