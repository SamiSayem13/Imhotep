import sys
from PyQt6.QtWidgets import QApplication

# --- FIX ---
# Create the QApplication instance *before* importing qtawesome.
# This allows qtawesome to correctly detect that you are using PyQt6
# and prevents the TypeError.
app = QApplication(sys.argv)

# Now import qtawesome
import qtawesome as qta

# Import the rest of your modules
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QSizePolicy)
from PyQt6.QtGui import QFont, QIcon, QFontDatabase
from PyQt6.QtCore import Qt, QSize

class ImhotepLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep - Role Selection")
        self.setGeometry(300, 200, 1200, 700)

        # Set a dark background for the main window so the white card is visible
        self.setStyleSheet("background-color: White;") 

        self.initUI()

    def initUI(self):
        # --- Central White Card ---
        card = QFrame(self)
        card.setFrameShape(QFrame.Shape.StyledPanel)
        
        # --- MODIFICATION ---
        # Increased the minimum size slightly for a better default
        card.setMinimumSize(500, 600) 
        
        # --- Layouts ---
        
        # Outer vertical layout to center vertically
        outer_v_layout = QVBoxLayout(self)
        outer_v_layout.addStretch(1) # Add stretch above the card

        # Horizontal layout to center horizontally
        center_h_layout = QHBoxLayout()
        center_h_layout.addStretch(1) # Add stretch to the left of the card
        
        # --- MODIFICATION ---
        # Added a stretch factor of 2 to the card.
        # This makes the card (2) take up twice as much proportional
        # space as the stretches (1) on either side.
        # (2 / (1+2+1)) = 50% of the horizontal space.
        center_h_layout.addWidget(card, 2) 
        
        center_h_layout.addStretch(1) # Add stretch to the right of the card
        
        # --- MODIFICATION ---
        # Added a stretch factor of 2 to the central layout.
        # This makes the card's layout (2) take up twice as much proportional
        # space as the stretches (1) above and below.
        # (2 / (1+2+1)) = 50% of the vertical space.
        outer_v_layout.addLayout(center_h_layout, 2)
        
        outer_v_layout.addStretch(1) # Add stretch below the card


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
        
        # --- MODIFICATION ---
        # Increased icon size
        button.setIconSize(QSize(28, 28))
        # Increased button minimum height
        button.setMinimumHeight(60) 
        return button

    def apply_styles(self, card, title, subtitle):
        """Applies all the QSS styling in one place."""
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
                /* --- MODIFICATION --- */
                font-size: 48px; 
                font-weight: bold;
                color: #333;
            }}
        """)
        
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-family: {font_family};
                /* --- MODIFICATION --- */
                font-size: 18px;
                color: #888;
            }}
        """)
        
        card.setStyleSheet(card.styleSheet() + f"""
            QPushButton {{
                font-family: {font_family};
                /* --- MODIFICATION --- */
                font-size: 18px;
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
    # 'app' is already created at the top of the script
    window = ImhotepLogin()
    window.show()
    sys.exit(app.exec())

