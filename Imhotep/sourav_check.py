import sys
import logging
import pymysql
import pymysql.cursors
from typing import Any, Dict, List, Optional
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QFont

# --------------------------
# Logging
# --------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("ImhotepApp")

# --------------------------
# Bootstrap: ensure tables exist
# (Kept global as it's a one-time setup)
# --------------------------
DDL_PATIENT_PORTAL = """
CREATE TABLE IF NOT EXISTS `Patient_Portal` (
  `Patient_ID` INT PRIMARY KEY,
  `User_ID` INT,
  `User_Name` VARCHAR(100),
  `Doctor_sugg` TEXT,
  `Pr_ID` INT
) ENGINE=InnoDB;
"""

DDL_PRESCRIPTION = """
CREATE TABLE IF NOT EXISTS `prescription` (
  `Prescription_ID` INT AUTO_INCREMENT PRIMARY KEY,
  `Patient_ID` INT,
  `Medication_Name` VARCHAR(255),
  `Doctor_Name` VARCHAR(255),
  `Doctor_UID` VARCHAR(100),
  `Date_Issued` DATE,
  KEY `idx_patient_id` (`Patient_ID`)
) ENGINE=InnoDB;
"""

def init_db():
    """Creates both tables if they don't exist."""
    try:
        with pymysql.connect(
            host="localhost", user="root", password="", database="imhotep"
        ) as conn:
            with conn.cursor() as cur:
                logger.info("Initializing Patient_Portal table...")
                cur.execute(DDL_PATIENT_PORTAL)
                logger.info("Initializing prescription table...")
                cur.execute(DDL_PRESCRIPTION)
                conn.commit()
                logger.info("Database initialized successfully.")
    except Exception as e:
        logger.exception(f"DB init error: {e}")


# --------------------------
# UI components (Unchanged)
# (These are separate classes, which is correct)
# --------------------------
class StyledCard(QFrame):
    def __init__(self, title="", content="", border_color="#e0e0e0"):
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: white;
                border-radius: 12px;
                border: 2px solid {border_color};
            }}
            QLabel {{ background: transparent; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setStyleSheet("color: #2b2b2b;")
        layout.addWidget(self.title_label)

        self.content_label = QLabel(content)
        self.content_label.setFont(QFont("Segoe UI", 9))
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("color: #444;")
        layout.addWidget(self.content_label)
        layout.addStretch()

    def set_content(self, text: str):
        self.content_label.setText(text)


class PrescriptionCard(QFrame):
    def __init__(self, med_text="—", doctor_text="—", doctor_uid="—"):
        super().__init__()
        self.setObjectName("prescriptionCard")
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

        self.med_label = QLabel(med_text)
        self.med_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.med_label.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            border-radius: 6px;
            padding: 6px 10px;
        """)
        layout.addWidget(self.med_label)

        self.doc_info = QLabel(f"Provided by: {doctor_text}\nDoctor UID: {doctor_uid}")
        self.doc_info.setFont(QFont("Segoe UI", 9))
        self.doc_info.setStyleSheet("color: #555;")
        layout.addWidget(self.doc_info)

        self.view_btn = QPushButton("View Details")
        self.view_btn.setFixedWidth(110)
        self.view_btn.setCursor(Qt.PointingHandCursor)
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: 600;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {{ background-color: #1976D2; }}
        """)
        layout.addWidget(self.view_btn, alignment=Qt.AlignLeft)


# --------------------------
# Main UI
# --------------------------
class PatientPortal(QWidget):
    def __init__(self, uid="123"):
        super().__init__()
        self.uid = uid
        self.setWindowTitle("Imhotep - Patient Portal")
        self.resize(900, 650)
        self.setMinimumSize(760, 580)
        self.setStyleSheet("background-color: #eef2f5;")
        self.setup_ui()
        
        # Call the "all-in-one" function directly
        self.load_data_and_update_ui()

    def setup_ui(self):
        # (This function is unchanged)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        title = QLabel("Imhotep")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI Semibold", 26))
        layout.addWidget(title)

        self.info = QLabel("Patient: Unknown\nUID: Unknown")
        layout.addWidget(self.info)

        grid = QGridLayout()
        self.prescription_card = PrescriptionCard()
        self.suggestion_card = StyledCard("Doctor's Suggestions", "Unknown", "#64B5F6")
        self.past_card = StyledCard("Past Prescriptions", "Unknown", "#E0E0E0")

        grid.addWidget(self.prescription_card, 0, 0)
        grid.addWidget(self.suggestion_card, 0, 1)
        grid.addWidget(self.past_card, 1, 0, 1, 2)
        layout.addLayout(grid)

        logout_row = QHBoxLayout()
        logout_row.addStretch()
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setFixedSize(100, 36)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E94B5A; }
        """)
        self.logout_btn.clicked.connect(self.close)
        logout_row.addWidget(self.logout_btn)
        layout.addLayout(logout_row)

    # ----------------------------------------------------
    # --- All logic is now inside the PatientPortal class ---
    # ----------------------------------------------------

    def get_conn(self):
        """Create and return a database connection to local 'imhotep'."""
        return pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="imhotep"
        )

    def as_text(self, value) -> str:
        """Return a clean string or 'Unknown' if the DB value is None/empty."""
        if value is None:
            return "Unknown"
        s = str(value).strip()
        return s if s else "Unknown"

    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetches a single row safely."""
        try:
            with self.get_conn() as conn: 
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    cur.execute(query, params or ())
                    row = cur.fetchone()
                    return row
        except Exception as e:
            logger.exception(f"fetch_one error: {e}")
            return None

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetches all rows safely."""
        try:
            with self.get_conn() as conn: 
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    cur.execute(query, params or ())
                    rows = cur.fetchall()
                    return rows
        except Exception as e:
            logger.exception(f"fetch_all error: {e}")
            return []

    def get_patient_info(self, uid: str) -> Optional[Dict[str, Any]]:
        """If uid is numeric -> match by User_ID. Otherwise -> match by User_Name."""
        if uid.isdigit():
            q = ("SELECT Patient_ID, User_ID, User_Name, Doctor_sugg, Pr_ID "
                 "FROM Patient_Portal WHERE User_ID = %s")
            return self.fetch_one(q, (int(uid),)) 
        else:
            q = ("SELECT Patient_ID, User_ID, User_Name, Doctor_sugg, Pr_ID "
                 "FROM Patient_Portal WHERE User_Name = %s")
            return self.fetch_one(q, (uid,)) 

    def get_prescriptions(self, patient_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Optional: tries to read past prescriptions."""
        q = """
            SELECT Medication_Name, Doctor_Name, Doctor_UID, Date_Issued
            FROM prescription
            WHERE Patient_ID = %s
            ORDER BY Date_Issued DESC
            LIMIT %s
        """
        return self.fetch_all(q, (patient_id, limit)) 

    def get_patient_data(self, uid: str, limit: int = 10):
        """Gathers all data (this is a simple, blocking function)."""
        patient = self.get_patient_info(uid) 
        prescriptions = []
        if patient and patient.get("Patient_ID") is not None:
            prescriptions = self.get_prescriptions(patient["Patient_ID"], limit) 
        return {"patient": patient, "prescriptions": prescriptions}

    def load_data_and_update_ui(self):
        """
        This is the "all-in-one" function.
        It runs on the main thread and will freeze the UI.
        """
        try:
            data = self.get_patient_data(self.uid, 10) 
            self.update_ui(data)
        except Exception as e:
            self.db_error(f"A critical error occurred: {e}")

    def update_ui(self, data: dict):
        """This function displays the data."""
        patient = data.get("patient")
        prescriptions = data.get("prescriptions", [])

        if not patient:
            self.info.setText("Patient: Unknown\nUID: Unknown")
            self.suggestion_card.set_content("Unknown")
            self.prescription_card.med_label.setText("Unknown")
            self.prescription_card.doc_info.setText("Provided by: Unknown\nDoctor UID: Unknown")
            self.past_card.set_content("Unknown")
            return

        name = self.as_text(patient.get("User_Name")) 
        uid_display = self.as_text(patient.get("User_ID")) 
        self.info.setText(f"Patient: {name}\nUID: {uid_display}")

        self.suggestion_card.set_content(self.as_text(patient.get("Doctor_sugg"))) 

        if prescriptions:
            current = prescriptions[0]
            med = self.as_text(current.get("Medication_Name"))
            doc = self.as_text(current.get("Doctor_Name"))
            doc_uid = self.as_text(current.get("Doctor_UID"))
            self.prescription_card.med_label.setText(med)
            self.prescription_card.doc_info.setText(f"Provided by: {doc}\nDoctor UID: {doc_uid}")

            if len(prescriptions) > 1:
                past_list = []
                for p in prescriptions[1:6]:
                    med_i = self.as_text(p.get("Medication_Name"))
                    date_i = self.as_text(p.get("Date_Issued"))
                    past_list.append(f"{med_i} - {date_i}")
                self.past_card.set_content("\n".join(past_list))
            else:
                self.past_card.set_content("Unknown")
        else:
            self.prescription_card.med_label.setText("Unknown")
            self.prescription_card.doc_info.setText("Provided by: Unknown\nDoctor UID: Unknown")
            self.past_card.set_content("Unknown")

    def db_error(self, msg):
        """This function handles error popups."""
        logger.error(msg)
        QMessageBox.warning(self, "Database Error", f"Could not load data.\nError: {msg}")


# --------------------------
# Entry point
# --------------------------
if __name__ == "__main__":
    init_db()  # This will safely create the tables if they don't exist
    app = QApplication(sys.argv)
    
    # --- MODIFIED ---
    # The application will now load data for the patient with User_ID '1234567'
    win = PatientPortal(uid="1234567")
    # --- END MODIFIED ---
    
    win.show()
    sys.exit(app.exec_())