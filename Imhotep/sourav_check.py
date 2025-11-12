import sys
import logging
from typing import Any, Dict, List, Optional, Tuple
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGridLayout, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
 
# --------------------------
# Database configuration
# --------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "imhotep",
    "raise_on_warnings": True,
    "autocommit": True,
}
 
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("ImhotepApp")
 
# --------------------------
# Database helpers
# --------------------------
def fetch_one(query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        with conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
    except Error:
        logger.exception("Error in fetch_one")
        return None
 
def fetch_all(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        with conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
    except Error:
        logger.exception("Error in fetch_all")
        return []
 
# --------------------------
# Data Access
# --------------------------
def get_patient_info(patient_id: int) -> Optional[Dict[str, Any]]:
    return fetch_one("SELECT * FROM Patient_Portal WHERE Patient_ID=%s", (patient_id,))
 
def get_prescriptions(patient_id: int) -> List[Dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM Prescription WHERE Patient_ID=%s ORDER BY Visit_Date DESC LIMIT 20",
        (patient_id,)
    )
 
def get_patient_and_prescriptions(patient_id: int):
    patient = get_patient_info(patient_id)
    prescriptions = []
    if patient and patient.get("Patient_ID"):
        prescriptions = get_prescriptions(patient.get("Patient_ID"))
    return {"patient": patient, "prescriptions": prescriptions}
 
# --------------------------
# UI Components
# --------------------------
class StyledCard(QFrame):
    def __init__(self, title="", content="", border_color="#e0e0e0"):
        super().__init__()
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: white;
                border-radius: 12px;
                border: 2px solid {border_color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)
 
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setStyleSheet("color: #2b2b2b;")
        layout.addWidget(self.title_label)
 
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border:none;")
        self.content_label = QLabel(content)
        self.content_label.setFont(QFont("Segoe UI", 9))
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("color: #444444;")
        self.scroll_area.setWidget(self.content_label)
        layout.addWidget(self.scroll_area)
        layout.addStretch()
 
    def set_content(self, text):
        self.content_label.setText(text)
 
class PrescriptionCard(QFrame):
    def __init__(self, prescription_text="—", doctor_text="—"):
        super().__init__()
        self.setObjectName("prescriptionCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QFrame#prescriptionCard {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #81C784;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)
 
        self.prescription_label = QLabel(prescription_text)
        self.prescription_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.prescription_label.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            border-radius: 6px;
            padding: 6px 10px;
        """)
        layout.addWidget(self.prescription_label)
 
        self.doc_info = QLabel(f"Provided by: {doctor_text}")
        self.doc_info.setFont(QFont("Segoe UI", 9))
        self.doc_info.setStyleSheet("color: #555;")
        layout.addWidget(self.doc_info)
 
# --------------------------
# Main UI
# --------------------------
class PatientPortal(QWidget):
    def __init__(self, patient_id=None):
        super().__init__()
        self.patient_id = patient_id
        self.setWindowTitle("Imhotep - Patient's Portal")
        self.resize(900, 650)
        self.setMinimumSize(760, 580)
        self.setStyleSheet("background-color: #eef2f5;")
        self.setup_ui()
        self.load_data()
 
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(12)
 
        # Title
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_lbl = QLabel("Imhotep")
        title_lbl.setAlignment(Qt.AlignHCenter)
        title_lbl.setFont(QFont("Segoe UI Semibold", 32))
        subtitle_lbl = QLabel("Patient's Portal")
        subtitle_lbl.setAlignment(Qt.AlignHCenter)
        subtitle_lbl.setFont(QFont("Segoe UI", 11))
        subtitle_lbl.setStyleSheet("color: #7a7a7a;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(subtitle_lbl)
        self.main_layout.addWidget(title_widget)
 
        # Patient Info
        top_row = QHBoxLayout()
        self.patient_info = QLabel("Patient: —\nUID: —")
        self.patient_info.setFont(QFont("Segoe UI", 10))
        top_row.addWidget(self.patient_info)
        top_row.addStretch()
        self.main_layout.addLayout(top_row)
 
        # Grid for Cards
        self.grid = QGridLayout()
        self.prescription_card = PrescriptionCard()
        self.suggestion_card = StyledCard("Doctor's Suggestions", "—", "#64B5F6")
        self.past_card = StyledCard("Past Prescriptions", "—", "#E0E0E0")
 
        self.grid.addWidget(self.prescription_card, 0, 1)
        self.grid.addWidget(self.suggestion_card, 1, 0)
        self.grid.addWidget(self.past_card, 1, 1)
        self.main_layout.addLayout(self.grid)
 
        # Bottom Row
        bottom_row = QHBoxLayout()
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setFixedSize(110, 36)
        self.logout_btn.clicked.connect(self.close)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef5350;
                color: white;
                border-radius: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e53935; }
        """)
        bottom_row.addWidget(self.logout_btn)
        bottom_row.addStretch()
        self.main_layout.addLayout(bottom_row)
 
    # --------------------------
    # Load Data
    # --------------------------
    def load_data(self):
        data = get_patient_and_prescriptions(self.patient_id)
        patient = data.get("patient")
        prescriptions = data.get("prescriptions", [])
 
        if not patient:
            self.patient_info.setText("Patient: —\nUID: —")
            self.prescription_card.prescription_label.setText("No active prescription")
            self.prescription_card.doc_info.setText("Provided by: —")
            self.suggestion_card.set_content("No suggestions available.")
            self.past_card.set_content("No prescription history.")
            return
 
        self.patient_info.setText(f"Patient: {patient.get('User_Name','Unknown')}\nUID: {patient.get('Patient_ID','—')}")
 
        self.suggestion_card.set_content(patient.get("Doctor_sugg","No suggestions available."))
 
        if prescriptions:
            current = prescriptions[0]
            pres_text = current.get("Prescription") or "Medication"
            doc_text = current.get("Doctor_Sugg") or "—"
            self.prescription_card.prescription_label.setText(pres_text)
            self.prescription_card.doc_info.setText(f"Provided by: {doc_text}")
 
            past_list = [f"{p.get('Prescription','')} - {p.get('Visit_Date','')}" for p in prescriptions[1:]]
            self.past_card.set_content("\n".join(past_list) if past_list else "No older prescriptions.")
        else:
            self.prescription_card.prescription_label.setText("No active prescription")
            self.prescription_card.doc_info.setText("Provided by: —")
            self.past_card.set_content("No prescription history.")
 
# --------------------------
# Entry Point
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PatientPortal(patient_id=101)  # patient_id অনুযায়ী data load হবে
    win.show()
    sys.exit(app.exec_())