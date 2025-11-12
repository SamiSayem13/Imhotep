# imhotep/views/pharmacist.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGroupBox, QSizePolicy, QSpacerItem, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import pymysql
from pymysql import err as pymysql_err


# ---------------- Database config + local connector ----------------
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="",
    database="imhotep",
    charset="utf8mb4",
)

def get_connection():
    """
    Return a fresh PyMySQL connection using the local DB_CONFIG.
    Kept local to this file (no external imports).
    """
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG.get("charset", "utf8mb4"),
        autocommit=False,                       # explicit commits where needed
        cursorclass=pymysql.cursors.Cursor,     # fetches tuples like (..,..)
    )


class PharmacistPortal(QWidget):
    """
    Router-compatible Pharmacist portal.

    Emits:
      - goto_login: when user clicks Back or Log Out

    Exposes:
      - set_user(user_id: str, user_name: str | None): optional context setter after login
    """
    goto_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._current_user_id = None
        self._current_user_name = None

        self.setWindowTitle("Imhotep — Pharmacist's Portal")
        self.setGeometry(100, 50, 1000, 750)
        self._build_ui()

    # ---------------- Public API ----------------
    def set_user(self, user_id: str, user_name: str = None):
        self._current_user_id = user_id
        self._current_user_name = user_name or "—"

    # ---------------- UI ----------------
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(12)

        # top row
        top_row = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.setFixedSize(90, 36)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: 1px solid #e74c3c;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #c93f3b; }
            QPushButton:pressed { background-color: #c93f3b; }
        """)
        self.btn_back.clicked.connect(self.goto_login.emit)
        top_row.addWidget(self.btn_back, alignment=Qt.AlignLeft)
        top_row.addStretch(1)
        outer.addLayout(top_row)

        # titles
        self.title = QLabel("Imhotep")
        self.title.setFont(QFont("Segoe UI", 38, QFont.Bold))
        self.subtitle = QLabel("Pharmacist's Portal")
        self.subtitle.setFont(QFont("Segoe UI", 13))
        self.subtitle.setStyleSheet("color: #777;")
        outer.addWidget(self.title, alignment=Qt.AlignHCenter)
        outer.addWidget(self.subtitle, alignment=Qt.AlignHCenter)
        outer.addSpacing(22)

        # card
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setMinimumWidth(860)
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card.setStyleSheet("""
            QFrame#card {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,1), stop:1 rgba(250,250,250,1));
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.08);
            }
        """)
        self.card_layout = QHBoxLayout(self.card)
        self.card_layout.setContentsMargins(48, 48, 48, 48)
        self.card_layout.setSpacing(36)

        # left column
        self.left_col = QVBoxLayout()
        self.left_col.setSpacing(22)

        # Find Patient group
        find_group = QGroupBox()
        find_group.setFlat(True)
        find_group.setStyleSheet("QGroupBox { border: none; }")
        fg_layout = QVBoxLayout()
        lbl_find = QLabel("Find Patient")
        lbl_find.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.input_uid = QLineEdit()
        self.input_uid.setPlaceholderText("Enter Patient ID (or leave blank for all)")
        self.input_uid.setFixedHeight(36)
        self.input_uid.setStyleSheet("""
            QLineEdit {
                padding: 6px; border: 1px solid #ddd; border-radius: 6px; background: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #7fb3ff; background: #fff;
            }
        """)
        btn_load = QPushButton("Load Prescription(s)")
        btn_load.setFixedHeight(44)
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setStyleSheet("""
            QPushButton {
                background-color: #2e86de; color: white; border-radius: 6px;
                font-weight: 600; padding: 6px 14px;
            }
            QPushButton:hover { background-color: #2574c8; }
            QPushButton:pressed { background-color: #1f5fa8; }
        """)
        btn_load.clicked.connect(self._on_load)
        fg_layout.addWidget(lbl_find)
        fg_layout.addWidget(self.input_uid)
        fg_layout.addWidget(btn_load)
        find_group.setLayout(fg_layout)

        # patient details
        details_group = QGroupBox("Patient Details")
        details_group.setFont(QFont("Segoe UI", 13))
        d_layout = QVBoxLayout()
        self.lbl_name = QLabel("Name: —")
        self.lbl_uid = QLabel("UID: —")
        d_layout.addWidget(self.lbl_name)
        d_layout.addWidget(self.lbl_uid)
        d_layout.addStretch(1)
        details_group.setLayout(d_layout)

        # logout
        btn_logout = QPushButton("Log Out")
        btn_logout.setFixedHeight(40)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton { background-color: #d9534f; color: white; border-radius: 6px;
                          font-weight: 600; padding: 8px 12px; }
            QPushButton:hover { background-color: #c93f3b; }
        """)
        btn_logout.clicked.connect(self.goto_login.emit)

        self.left_col.addWidget(find_group)
        self.left_col.addWidget(details_group)
        self.left_col.addStretch(1)
        self.left_col.addWidget(btn_logout, alignment=Qt.AlignLeft)

        # right column with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        self.right_col = QVBoxLayout(scroll_content)
        self.right_col.setSpacing(12)

        pr_label = QLabel("Pending Prescriptions")
        pr_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.right_col.addWidget(pr_label)
        self.right_col.addStretch(1)

        scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setWidget(scroll_content)

        # compose
        self.card_layout.addLayout(self.left_col, 2)
        self.card_layout.addWidget(scroll_area, 3)

        outer.addWidget(self.card, alignment=Qt.AlignHCenter)
        outer.addSpacerItem(QSpacerItem(0, 16, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # ---------------- Responsive font/spacing ----------------
    def resizeEvent(self, event):
        width = self.width()
        scale = width / 1000
        self.title.setFont(QFont("Segoe UI", int(36 * scale), QFont.Bold))
        self.subtitle.setFont(QFont("Segoe UI", int(12 * scale)))
        self.card_layout.setContentsMargins(int(36 * scale), int(36 * scale),
                                            int(36 * scale), int(36 * scale))
        self.left_col.setSpacing(int(22 * scale))
        self.right_col.setSpacing(int(16 * scale))
        return super().resizeEvent(event)

    # ---------------- Data access ----------------
    def _query_prescriptions_all(self):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT p.Doctor_Sugg, p.Prescription, p.Visit_Date, p.Dispense,
                                pt.User_Name, pt.Patient_ID
                FROM prescription p
                JOIN patient_portal pt ON p.Patient_ID = pt.Patient_ID
                ORDER BY p.Visit_Date DESC
            """)
            return cur.fetchall()
        finally:
            try:
                cur.close()
            except Exception:
                pass
            conn.close()

    def _query_prescriptions_by_id(self, patient_id):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT p.Doctor_Sugg, p.Prescription, p.Visit_Date, p.Dispense,
                                pt.User_Name, pt.Patient_ID
                FROM prescription p
                JOIN patient_portal pt ON p.Patient_ID = pt.Patient_ID
                WHERE p.Patient_ID = %s
                ORDER BY p.Visit_Date DESC
            """, (patient_id,))
            return cur.fetchall()
        finally:
            try:
                cur.close()
            except Exception:
                pass
            conn.close()

    # ---------------- UI helpers ----------------
    def _clear_prescriptions_area(self):
        while self.right_col.count() > 2:
            item = self.right_col.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _create_prescription_card(self, info_text, med_text, patient_id):
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        card.setStyleSheet("""
            QFrame { border: 1px solid rgba(0,0,0,0.08); border-radius: 10px; background-color: #FFFFFF; }
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 12, 12, 12)

        med_label = QLabel(f"<b>Medication:</b> {med_text}")
        med_label.setFont(QFont("Segoe UI", 10))
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #555;")

        btn_dispense = QPushButton("Dispense")
        btn_dispense.setCursor(Qt.PointingHandCursor)
        btn_dispense.setStyleSheet("""
            QPushButton {
                background-color: #28a745; color: white; border-radius: 8px;
                font-weight: 600; padding: 4px 10px;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
        """)
        btn_dispense.clicked.connect(lambda _, pid=patient_id, w=card: self._on_dispense(pid, w))

        lay.addWidget(med_label)
        lay.addWidget(info_label)
        lay.addWidget(btn_dispense, alignment=Qt.AlignRight)
        return card

    def _load_prescriptions(self, rows):
        self._clear_prescriptions_area()
        if not rows:
            empty_lbl = QLabel("No prescriptions found.")
            empty_lbl.setStyleSheet("color: #777; font-style: italic;")
            self.right_col.insertWidget(1, empty_lbl)
            return

        for doctor_sugg, prescription_text, visit_date, dispense, patient_name, patient_id in rows:
            info_text = (
                f"Patient: {patient_name} (ID: {patient_id})\n"
                f"Doctor Suggestion: {doctor_sugg}\n"
                f"Dispense Status: {'Active' if dispense else 'Dispensed'}\n"
                f"Visit Date: {visit_date}"
            )
            card = self._create_prescription_card(info_text, prescription_text, patient_id)
            self.right_col.insertWidget(1, card)

    # ---------------- Handlers ----------------
    def _on_load(self):
        uid = self.input_uid.text().strip()
        try:
            if uid:
                rows = self._query_prescriptions_by_id(uid)
                if rows:
                    name = rows[0][4]
                    self.lbl_name.setText(f"Name: {name}")
                    self.lbl_uid.setText(f"UID: {uid}")
                    self._load_prescriptions(rows)
                else:
                    self.lbl_name.setText("Name: —")
                    self.lbl_uid.setText("UID: —")
                    QMessageBox.information(self, "No Results",
                                            f"No prescriptions found for Patient ID {uid}.")
            else:
                rows = self._query_prescriptions_all()
                self.lbl_name.setText("Name: All Patients")
                self.lbl_uid.setText("UID: —")
                self._load_prescriptions(rows)
        except pymysql_err.MySQLError as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def _on_dispense(self, patient_id, card_widget):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE prescription SET Dispense=0 WHERE Patient_ID=%s", (patient_id,))
            conn.commit()
            QMessageBox.information(self, "Dispensed",
                                    f"Prescription for Patient ID {patient_id} has been dispensed.")
            card_widget.deleteLater()
        except pymysql_err.MySQLError as e:
            # Attempt rollback if the UPDATE failed mid-transaction
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
            QMessageBox.critical(self, "Error", f"Database error: {e}")
        finally:
            try:
                if cur:
                    cur.close()
            except Exception:
                pass
            if conn:
                conn.close()
