from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import qtawesome as qta

class SelectionView(QWidget):
    goto_login = pyqtSignal(str)   # emits role name
    goto_register = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        outer = QVBoxLayout(self); outer.addStretch(1)
        center = QHBoxLayout(); outer.addLayout(center); outer.addStretch(1)

        card = QFrame()
        card.setStyleSheet("QFrame{background:white;border-radius:15px;}")
        center.addStretch(1); center.addWidget(card, 2); center.addStretch(1)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(90, 90, 90, 90)
        lay.setSpacing(20)

        title = QLabel("Imhotep"); title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("QLabel{font-family:'Segoe UI';font-size:48px;font-weight:bold;color:#333;}")
        subtitle = QLabel("Please select your role to continue"); subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("QLabel{font-family:'Segoe UI';font-size:18px;color:#888;}")

        lay.addStretch(1)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addSpacing(20)

        def role_btn(text, icon):
            b = QPushButton(text)
            b.setIcon(qta.icon(icon, color='#28a745'))
            b.setIconSize(QSize(28, 28))
            b.setMinimumHeight(60)
            b.setStyleSheet("""
                QPushButton{
                    font-family:'Segoe UI';font-size:18px;font-weight:500;
                    color:#28a745;background:transparent;border:2px solid #28a745;
                    border-radius:8px;padding:10px;text-align:left;padding-left:20px;
                }
                QPushButton:hover{background:#f0fff0;}
            """)
            return b

        doctor = role_btn(" Doctor", "fa5s.stethoscope")
        patient = role_btn(" Patient", "fa5s.user")
        pharmacist = role_btn(" Pharmacist", "fa5s.mortar-pestle")

        for role, b in (("doctor", doctor), ("patient", patient), ("pharmacist", pharmacist)):
            b.clicked.connect(lambda _, r=role: self.goto_login.emit(r))

        lay.addWidget(doctor)
        lay.addWidget(patient)
        lay.addWidget(pharmacist)
        lay.addStretch(1)
