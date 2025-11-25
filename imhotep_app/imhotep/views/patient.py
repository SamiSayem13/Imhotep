import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGridLayout, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import pymysql
from pymysql.err import MySQLError


class PatientPortal(QWidget):
    """
    Patient portal view.
    - Maintains its own DB connection settings (no external get_conn).
    - Emits goto_login when the back button is clicked.
    """
    goto_login = pyqtSignal()

    # Local DB config (edit if needed)
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "imhotep",
        "charset": "utf8mb4",
        "autocommit": True,  # ensure reads/writes don't require manual commit
        "cursorclass": pymysql.cursors.DictCursor,
    }

    logger = logging.getLogger("ImhotepPatientPortal")
    if not logger.handlers:
        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    # --------------------------
    # Small UI helpers
    # --------------------------
    class StyledCard(QFrame):
        def __init__(self, title: str = "", content: str = "", border_color: str = "#e0e0e0"):
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
            self.content_label.setStyleSheet("color: #444;")
            self.scroll_area.setWidget(self.content_label)
            layout.addWidget(self.scroll_area)
            layout.addStretch()

        def set_content(self, text: str):
            self.content_label.setText(text)

    class PrescriptionCard(QFrame):
        def __init__(self, prescription_text: str = "—", doctor_text: str = "—"):
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
    # Lifecycle
    # --------------------------
    def __init__(self, patient_id: Union[int, str, None] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.patient_id: Optional[int] = self._coerce_patient_id(patient_id)

        self.setWindowTitle("Imhotep - Patient's Portal")
        self.resize(900, 650)
        self.setMinimumSize(760, 580)
        self.setStyleSheet("background-color: #eef2f5;")

        self._build_ui()
        self._load_data()

    def set_user(self, user_id: Union[int, str]):
        """Called by the router after successful login."""
        self.patient_id = self._coerce_patient_id(user_id)
        self._load_data()

    # --------------------------
    # Build UI
    # --------------------------
    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(12)

        # Header
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
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

        # Patient info and back
        top_row = QHBoxLayout()
        self.patient_info = QLabel("Patient: —\nUID: —")
        self.patient_info.setFont(QFont("Segoe UI", 10))
        top_row.addWidget(self.patient_info)
        top_row.addStretch()

        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedSize(90, 34)
        self.back_btn.setStyleSheet("""
            QPushButton { background-color: #ef5350; color: white; border-radius: 6px; }
            QPushButton:hover { background-color: #e53935; }
        """)
        self.back_btn.clicked.connect(self.goto_login.emit)
        top_row.addWidget(self.back_btn)
        self.main_layout.addLayout(top_row)

        # Cards grid
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)

        self.suggestion_card = PatientPortal.StyledCard("Doctor's Suggestions", "—", "#64B5F6")
        self.grid.addWidget(self.suggestion_card, 0, 0, 2, 1)

        self.prescription_card = PatientPortal.PrescriptionCard()
        self.grid.addWidget(self.prescription_card, 0, 1, 1, 1)

        self.past_card = PatientPortal.StyledCard("Past Prescriptions", "—", "#E0E0E0")
        self.grid.addWidget(self.past_card, 1, 1, 1, 1)

        self.main_layout.addLayout(self.grid)

    # --------------------------
    # DB helpers (self-contained, PyMySQL)
    # --------------------------
    @classmethod
    def _get_conn(cls):
        """
        Return a fresh PyMySQL connection using only local DB_CONFIG.
        """
        conn = pymysql.connect(**cls.DB_CONFIG)
        try:
            conn.ping(reconnect=True)
            if hasattr(conn, "autocommit") and not conn.get_autocommit():
                conn.autocommit(True)
        except Exception:
            pass
        return conn

    @classmethod
    def _fetch_one(cls, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        try:
            with cls._get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                    return cur.fetchone()
        except MySQLError:
            cls.logger.exception("Error executing _fetch_one (query=%s, params=%s)", query, params)
            return None

    @classmethod
    def _fetch_all(cls, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        try:
            with cls._get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                    return cur.fetchall()
        except MySQLError:
            cls.logger.exception("Error executing _fetch_all (query=%s, params=%s)", query, params)
            return []

    # --------------------------
    # Data access
    # --------------------------
    @classmethod
    def _get_patient_info(cls, patient_id: int) -> Optional[Dict[str, Any]]:
        return cls._fetch_one(
            "SELECT * FROM prescription WHERE Patient_ID = %s",
            (patient_id,),
        )

    @classmethod
    def _get_prescriptions(cls, patient_id: int) -> List[Dict[str, Any]]:
        # Using all relevant columns from Prescription table
        return cls._fetch_all(
            """
            SELECT Pr_ID, Patient_ID, Doctor_Sugg, Prescription, Visit_Date, Dispense
            FROM Prescription
            WHERE Patient_ID = %s
            ORDER BY COALESCE(Visit_Date, '1900-01-01') DESC, Pr_ID DESC
            LIMIT 20
            """,
            (patient_id,),
        )
    @classmethod
    def _get_user_name(cls, user_id: int) -> Optional[str]:
        row = cls._fetch_one(
            "SELECT User_Name FROM user WHERE User_ID = %s",
            (user_id,),
        )
        return row["User_Name"] if row else None

    # --------------------------
    # Load and bind data to UI  
    # --------------------------
    def _load_data(self):
        if self.patient_id is None:
            self._show_empty_state()
            return

        patient = self._get_patient_info(self.patient_id)
        prescriptions = self._get_prescriptions(self.patient_id)

        if not patient:
            self._show_empty_state()
            return

        name = self._get_user_name(self.patient_id) or "—"
        uid = patient.get("Patient_ID", self.patient_id)
        self.patient_info.setText(f"Patient: {name}\nUID: {uid}")

        if prescriptions:
            # latest prescription (ordered by Visit_Date DESC, Pr_ID DESC)
            current = prescriptions[0]

            # Suggestion and details from Prescription table
            sugg = current.get("Doctor_Sugg") or "No suggestions available."
            self.suggestion_card.set_content(sugg)

            pres_text = current.get("Prescription") or "Medication"
            doc_text = current.get("Doctor_Sugg") or "—"
            visit_date = current.get("Visit_Date") or ""
            dispense = current.get("Dispense")

            status = "Active" if dispense else "Dispensed"

            self.prescription_card.prescription_label.setText(
                f"{pres_text}\n(Visit Date: {visit_date}, Status: {status})"
            )
            self.prescription_card.doc_info.setText(f"Provided by: {doc_text}")

            # past prescriptions (skip the first)
            past_items: List[str] = []
            for p in prescriptions[1:]:
                txt = p.get("Prescription") or ""
                dt = p.get("Visit_Date") or ""
                if txt:
                    line = f"{txt} - {dt}".strip(" -")
                    past_items.append(line)

            self.past_card.set_content(
                "\n".join(past_items) if past_items else "No older prescriptions."
            )
        else:
            # no prescriptions at all
            self.suggestion_card.set_content("No suggestions available.")
            self.prescription_card.prescription_label.setText("No active prescription")
            self.prescription_card.doc_info.setText("Provided by: —")
            self.past_card.set_content("No prescription history.")

    def _show_empty_state(self):
        if self.patient_id is None:
            self.patient_info.setText("Patient: —\nUID: —")
        else:
            patient = self._get_patient_info(self.patient_id)
            name = self._get_user_name(self.patient_id) or "—"
            uid = self.patient_id

            self.patient_info.setText(f"Patient: {name}\nUID: {uid}")

        self.prescription_card.prescription_label.setText("No active prescription")
        self.prescription_card.doc_info.setText("Provided by: —")
        self.suggestion_card.set_content("No suggestions available.")
        self.past_card.set_content("No prescription history.")


    # --------------------------
    # Utility
    # --------------------------
    @staticmethod
    def _coerce_patient_id(value: Union[int, str, None]) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        s = str(value).strip()
        return int(s) if s.isdigit() else None
