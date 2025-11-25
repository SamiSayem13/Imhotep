from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import pymysql
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QScrollArea, QTextEdit


class DoctorPortal(QWidget):
    goto_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep — Doctor's Portal")
        self.setMinimumSize(980, 700)
        self.setStyleSheet("background-color:#eef1f4;")

        # State Variables
        self.current_patient_id = None
        self.registered_doctor_name = None
        self.last_condition = ""
        self.last_prescription = ""
        self.current_edit_prescription_id = None

        self.init_ui()

    # --- small helper you were calling but didn’t have defined ---
    def show_notification(self, text, color="#888"):
        # ensure label exists before use; create one lazily if needed
        if not hasattr(self, "notification_label") or self.notification_label is None:
            self.notification_label = QLabel("")
        self.notification_label.setText(text)
        self.notification_label.setStyleSheet(f"color: {color}; font-size: 11px;")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 20, 28, 18)
        main_layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        title_container = QHBoxLayout()
        title_container.addStretch(1)
        title_label = QLabel("Imhotep")
        title_label.setFont(QFont("Helvetica", 40, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setContentsMargins(100, 0, 0, 0)
        title_container.addWidget(title_label)
        title_container.addStretch(1)
        top_row.addLayout(title_container)

        top_row.addSpacing(100)
        main_layout.addLayout(top_row)

        subtitle = QLabel("Doctor's Portal")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px;")
        main_layout.addWidget(subtitle)

        container = QFrame()
        container.setStyleSheet("background-color:white; border-radius:12px;")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(26, 22, 26, 22)
        container_layout.setSpacing(12)

        body_h = QHBoxLayout()
        body_h.setSpacing(18)

        # LEFT PANEL
        left_card = QFrame()
        left_card.setStyleSheet("background: #fbfbfb; border-radius: 10px;")

        left_v = QVBoxLayout(left_card)
        left_v.setContentsMargins(18, 16, 18, 16)
        left_v.setSpacing(12)
        left_v.addWidget(QLabel("Find Patient", font=QFont("Helvetica", 12, QFont.Bold)))

        self.uid_input = QLineEdit()
        # This is now Patient_ID, not UID
        self.uid_input.setPlaceholderText("Enter Patient ID")
        self.uid_input.setFixedHeight(36)
        self.uid_input.setStyleSheet("border:1px solid #e1e1e1; border-radius:6px; padding-left:8px;")
        left_v.addWidget(self.uid_input)

        self.notification_label = QLabel("")
        self.notification_label.setStyleSheet("color: #888; font-size: 11px;")
        left_v.addWidget(self.notification_label)

        self.load_btn = QPushButton("Load Patient")
        self.load_btn.setFixedHeight(40)
        self.load_btn.setStyleSheet("""
            QPushButton { background-color: #2475FF; color: white; border: none; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #2475FF; }
        """)
        self.load_btn.clicked.connect(self.on_load_patient)
        left_v.addWidget(self.load_btn)

        left_v.addWidget(QLabel("Patient History", font=QFont("Helvetica", 12, QFont.Bold)))
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setStyleSheet("border:1px solid #e9e9e9; border-radius:8px; background:#fff;")
        self.history_scroll.setFixedHeight(300)
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setContentsMargins(10, 10, 10, 10)
        self.history_layout.setSpacing(10)
        self.history_scroll.setWidget(self.history_content)
        left_v.addWidget(self.history_scroll)
        left_v.addStretch(5)

        # RIGHT PANEL
        right_card = QFrame()
        right_card.setStyleSheet("background: #fbfbfb; border-radius: 10px;")
        right_v = QVBoxLayout(right_card)
        right_v.setContentsMargins(18, 16, 18, 16)
        right_v.setSpacing(12)
        right_v.addWidget(QLabel("Current Condition & Prescription", font=QFont("Helvetica", 12, QFont.Bold)))

        bordered_frame = QFrame()
        bordered_frame.setStyleSheet("border: 1px solid #ccc; border-radius: 8px; background: #fff;")
        bordered_layout = QVBoxLayout(bordered_frame)
        bordered_layout.setContentsMargins(10, 10, 10, 10)
        bordered_layout.setSpacing(8)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Doctor's notes & patient condition...")
        self.notes_edit.setFixedHeight(120)
        bordered_layout.addWidget(self.notes_edit)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #ccc; margin-top:6px; margin-bottom:6px;")
        bordered_layout.addWidget(divider)

        self.prescription_edit = QTextEdit()
        self.prescription_edit.setPlaceholderText("Prescription details...")
        self.prescription_edit.setFixedHeight(100)
        bordered_layout.addWidget(self.prescription_edit)

        right_v.addWidget(bordered_frame)

        self.save_btn = QPushButton("Generate Prescription  Save")
        self.save_btn.setFixedHeight(44)
        self.save_btn.setStyleSheet("""
            QPushButton { background-color: #1EBE64; color: white; border: none; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #1EBE64; }
        """)
        self.save_btn.clicked.connect(self.on_save_prescription)
        right_v.addWidget(self.save_btn)

        logout_row = QHBoxLayout()
        logout_row.addStretch()
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setFixedSize(100, 36)
        self.logout_btn.setStyleSheet("""
            QPushButton { background-color: #DC3545; color: white; border: none; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #E94B5A; }
        """)
        self.logout_btn.clicked.connect(self.goto_login.emit)
        logout_row.addWidget(self.logout_btn)
        right_v.addLayout(logout_row)

        body_h.addWidget(left_card)
        body_h.addWidget(right_card)
        container_layout.addLayout(body_h)
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _create_history_card(self, rec):
        card = QFrame()
        card.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; background: #fff;")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(6)

        pid = rec.get("Pr_ID", "")
        note = rec.get("Doctor_Sugg") or ""
        presc_full = rec.get("Prescription") or ""
        info = QLabel(f"<b>ID:</b> {pid}<br><b>Notes:</b> {note[:120]}<br><b>Prescription:</b> {presc_full[:120]}")
        info.setWordWrap(True)
        vbox.addWidget(info)

        edit_btn = QPushButton("✏ Edit")
        edit_btn.setFixedWidth(72)
        edit_btn.setStyleSheet("""
            QPushButton { background-color: #DC3545; color: white; border: none; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #E94B5A; }
        """)
        edit_btn.clicked.connect(lambda _, r=rec: self._on_edit_history_record(r))
        vbox.addWidget(edit_btn, alignment=Qt.AlignRight)
        return card

    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def populate_history(self, records):
        self._clear_layout(self.history_layout)
        if not records:
            no_data = QLabel("No patient data found.")
            no_data.setStyleSheet("color:#888;")
            self.history_layout.addWidget(no_data)
            self.history_layout.addStretch()
            return
        for rec in records:
            self.history_layout.addWidget(self._create_history_card(rec))
        self.history_layout.addStretch()

    def _on_edit_history_record(self, rec):
        self.current_edit_prescription_id = rec.get("Pr_ID")
        # we now store Patient_ID in the line edit
        self.uid_input.setText(str(rec.get("Patient_ID") or ""))
        self.notes_edit.setPlainText(rec.get("Doctor_Sugg") or "")
        self.prescription_edit.setPlainText(rec.get("Prescription") or "")
        self.show_notification(f"Loaded record ID {self.current_edit_prescription_id} for editing.", "#20b54b")

    def on_load_patient(self):
        self.current_edit_prescription_id = None
        patient_id = self.uid_input.text().strip()
        if not patient_id:
            self.show_notification("Please enter Patient ID.", "#e05a4f")
            return

        conn = None
        cur = None
        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="imhotep",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            cur = conn.cursor()
            # Use Patient_ID directly, no join, no Patient_UID
            cur.execute("""
                SELECT *
                FROM prescription
                WHERE Patient_ID = %s
                ORDER BY Pr_ID ASC;
            """, (patient_id,))
            records = cur.fetchall()
            self.populate_history(records)
            if records:
                latest = records[0]
                self.notes_edit.setPlainText(latest.get("Doctor_Sugg") or "")
                self.prescription_edit.setPlainText(latest.get("Prescription") or "")
                self.show_notification("Loaded latest record.", "#666")
            else:
                self.notes_edit.clear()
                self.prescription_edit.clear()
                self.show_notification("No patient data found.", "#666")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Error loading patient data:\n{e}")
            print(f"Error loading patient: {e}")
        finally:
            try:
                if cur:
                    cur.close()
            finally:
                if conn:
                    conn.close()

    def on_save_prescription(self):
        patient_id = self.uid_input.text().strip()
        notes = self.notes_edit.toPlainText().strip()
        presc = self.prescription_edit.toPlainText().strip()

        if not patient_id:
            self.show_notification("Please enter Patient ID.", "#e05a4f")
            return
        if not notes and not presc:
            self.show_notification("Notes or prescription must not be empty.", "#e05a4f")
            return

        conn = None
        cur = None
        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="imhotep",
                cursorclass=pymysql.cursors.Cursor,  # tuple rows are fine here
                autocommit=False
            )
            cur = conn.cursor()

            # UPDATE existing prescription
            if self.current_edit_prescription_id:
                cur.execute("""
                    UPDATE prescription
                    SET Doctor_Sugg = %s, Prescription = %s
                    WHERE Pr_ID = %s
                """, (notes, presc, self.current_edit_prescription_id))
                conn.commit()
                self.show_notification("Prescription updated successfully.", "#20b54b")
                self.current_edit_prescription_id = None
                self.on_load_patient()
                return

            # INSERT new prescription
            # No Patient_UID lookup anymore – we trust the entered Patient_ID
            cur.execute("""
                INSERT INTO prescription (Patient_ID, Doctor_Sugg, Prescription)
                VALUES (%s, %s, %s)
            """, (patient_id, notes, presc))
            conn.commit()
            self.show_notification("Prescription saved successfully.", "#20b54b")
            self.on_load_patient()

        except Exception as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Save Error", f"Error saving prescription:\n{e}")
            print(f"Error saving prescription: {e}")
        finally:
            try:
                if cur:
                    cur.close()
            finally:
                if conn:
                    conn.close()
