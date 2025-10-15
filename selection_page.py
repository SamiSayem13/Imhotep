import sys
import qtawesome as qta
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtGui import QFont, QIcon, QFontDatabase
from PyQt6.QtCore import Qt, QSize

class ImhotepLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep - Role Selection")
        self.setGeometry(300, 200, 1200, 700)

        # Set a dark background for the main window
        self.setStyleSheet("background-color: white;")

        self.initUI()

    def initUI(self):
        # --- Central White Card ---
        card = QFrame(self)
        card.setFrameShape(QFrame.Shape.StyledPanel)
        # Set max size to control the width and height
        card.setMaximumSize(450, 550)
        
        # --- Layouts ---
        # Main layout to center the card horizontally and vertically
        main_layout = QHBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(card)
        main_layout.addStretch()

        # Vertical layout inside the card for the content
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(90, 90, 90, 90) # Add padding
        card_layout.setSpacing(20) # Spacing between widgets

        # --- Widgets ---
        # Title Label
        title_label = QLabel("Imhotep")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
       
        # Subtitle Label
        subtitle_label = QLabel("Please select your role to continue")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spacer to push buttons down
        card_layout.addStretch(1)
        
        # Add widgets to card layout
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        
        card_layout.addSpacing(20) # Add extra space before buttons

        # --- Role Buttons ---
        # We create a helper function to avoid repeating code
        doctor_button = self.create_role_button(" Doctor", "fa5s.stethoscope")
        patient_button = self.create_role_button(" Patient", "fa5s.user")
        pharmacist_button = self.create_role_button(" Pharmacist", "fa5s.mortar-pestle")

        doctor_button.clicked.connect(self.doctor_button_clicked)
        patient_button.clicked.connect(self.patient_button_clicked)
        pharmacist_button.clicked.connect(self.pharmacist_button_clicked) 

        card_layout.addWidget(doctor_button)
        card_layout.addWidget(patient_button)
        card_layout.addWidget(pharmacist_button)

        card_layout.addStretch(1)
        
        # --- Apply Stylesheets (like CSS) ---
        self.apply_styles(card, title_label, subtitle_label)

    def create_role_button(self, text, icon_name):
        """Helper function to create and style a role button."""
        button = QPushButton(text)
        button.setIcon(qta.icon(icon_name, color='#28a745')) # Green icon
        button.setIconSize(QSize(24, 24))
        button.setMinimumHeight(50) # Make buttons taller
        return button

    def apply_styles(self, card, title, subtitle):
        """Applies all the QSS styling in one place."""
        # Use a modern font if available, otherwise fallback
        QFontDatabase.addApplicationFont(":/fonts/Montserrat-Regular.ttf") # Example
        
        font_family = "Segoe UI" # A good default font

        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)

        title.setStyleSheet(f"""
            QLabel {{
                font-family: {font_family};
                font-size: 42px;
                font-weight: bold;
                color: #333;
            }}
        """)
        
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-family: {font_family};
                font-size: 14px;
                color: #888;
            }}
        """)
        
        # Apply style to all PushButtons within the card
        card.setStyleSheet(card.styleSheet() + f"""
            QPushButton {{
                font-family: {font_family};
                font-size: 16px;
                font-weight: 500;
                color: #28a745;
                background-color: transparent;
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 10px;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background-color: #f0fff0; /* Light green on hover */
            }}
        """)

    def doctor_button_clicked(self):
        print("Doctor button clicked!")

    def patient_button_clicked(self):
        print("Patient button clicked!")

    def pharmacist_button_clicked(self):
        print("Pharmacist button clicked!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImhotepLogin()
    window.show()
    sys.exit(app.exec())