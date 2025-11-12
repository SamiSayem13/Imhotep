import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QCursor
from ..db.auth import AuthHandler

class ForgotPasswordView(QWidget):
    goto_login = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Reset Password - imhotep")
        self.resize(600, 500)
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
        self.back_btn.clicked.connect(self.goto_login.emit)

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
        layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(12)

        title = QLabel("Imhotep"); title.setFont(QFont("Segoe UI", 18, QFont.Bold)); title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Reset your password")
        subtitle.setFont(QFont("Segoe UI", 10)); subtitle.setStyleSheet("color: #555;"); subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.code = QLineEdit(); self.code.setPlaceholderText("Unique Code"); self.code.setFixedHeight(38); self.code.setStyleSheet(self._line_style())
        self.code.textChanged.connect(lambda _: self._remove_spaces_in_lineedit(self.code)); layout.addWidget(self.code)

        pwd_row = QHBoxLayout(); pwd_row.setSpacing(8)
        self.new_pwd = QLineEdit(); self.new_pwd.setPlaceholderText("New Password"); self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setFixedHeight(38); self.new_pwd.setStyleSheet(self._line_style()); self.new_pwd.textChanged.connect(self.check_strength)
        pwd_row.addWidget(self.new_pwd)

        self.show_pwd_btn = QPushButton("👁"); self.show_pwd_btn.setFixedWidth(40); self.show_pwd_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_pwd_btn.clicked.connect(lambda: self._toggle_echo(self.new_pwd, self.show_pwd_btn))
        self.show_pwd_btn.setStyleSheet(self._small_icon_button_style()); pwd_row.addWidget(self.show_pwd_btn)
        layout.addLayout(pwd_row)

        self.strength_label = QLabel(""); self.strength_label.setFont(QFont("Segoe UI", 8)); self.strength_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.strength_label)

        conf_row = QHBoxLayout(); conf_row.setSpacing(8)
        self.confirm_pwd = QLineEdit(); self.confirm_pwd.setPlaceholderText("Confirm Password"); self.confirm_pwd.setEchoMode(QLineEdit.Password)
        self.confirm_pwd.setFixedHeight(38); self.confirm_pwd.setStyleSheet(self._line_style()); conf_row.addWidget(self.confirm_pwd)

        self.show_conf_btn = QPushButton("👁"); self.show_conf_btn.setFixedWidth(40); self.show_conf_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_conf_btn.clicked.connect(lambda: self._toggle_echo(self.confirm_pwd, self.show_conf_btn))
        self.show_conf_btn.setStyleSheet(self._small_icon_button_style()); conf_row.addWidget(self.show_conf_btn)
        layout.addLayout(conf_row)

        info = QLabel("For verification, please have your NID or Birth Certificate ready.")
        info.setFont(QFont("Segoe UI", 8)); info.setStyleSheet("color: #777;"); info.setAlignment(Qt.AlignCenter); layout.addWidget(info)

        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        submit_btn = self.create_button("Submit", "#1EBE64", "#2ED97A"); submit_btn.clicked.connect(self.reset_password); btn_row.addWidget(submit_btn)
        cancel_btn = self.create_button("Cancel", "#DC3545", "#E94B5A"); cancel_btn.clicked.connect(self.goto_login.emit); btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.error_label = QLabel(""); self.error_label.setStyleSheet("color:red;"); self.error_label.setAlignment(Qt.AlignCenter); layout.addWidget(self.error_label)

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
        btn = QPushButton(text); btn.setCursor(QCursor(Qt.PointingHandCursor)); btn.setFixedHeight(36)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; border-radius: 8px; font-weight: bold; font-size: 10pt; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """)
        return btn

    def check_strength(self):
        pwd = self.new_pwd.text()
        strength = self.get_password_strength(pwd)
        if strength == "Weak":
            self.strength_label.setText("Password Strength: Weak"); self.strength_label.setStyleSheet("color: red;")
        elif strength == "Medium":
            self.strength_label.setText("Password Strength: Medium"); self.strength_label.setStyleSheet("color: orange;")
        elif strength == "Strong":
            self.strength_label.setText("Password Strength: Strong"); self.strength_label.setStyleSheet("color: green;")
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
            return "Strong" if len(password) >= 12 else "Medium"
        return "Weak"

    def reset_password(self):
        code = self.code.text().strip()
        new = self.new_pwd.text().strip()
        confirm = self.confirm_pwd.text().strip()
        self.error_label.setText("")
        if not code or not new or not confirm:
            self.error_label.setText("Please fill all fields."); return
        if " " in code:
            self.error_label.setText("Unique Code cannot contain spaces."); return
        if new != confirm:
            self.error_label.setText("Passwords do not match."); return
        strength = self.get_password_strength(new)
        if strength == "Weak":
            self.error_label.setText("Password must be 8–16 chars with upper, lower, digit, special."); return

        result = AuthHandler.reset_user_password(code, new)
        if "successfully" in result:
            self.error_label.setStyleSheet("color:green;")
        else:
            self.error_label.setStyleSheet("color:red;")
        self.error_label.setText(result)
