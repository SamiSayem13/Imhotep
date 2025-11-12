import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, 
                             QMessageBox, QScrollArea)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class PatientPortal(QWidget):
    def __init__(self):
        super().__init__()
        self.db = QSqlDatabase.addDatabase('QMYSQL')
        self.init_ui()
        
        if not self.connect_to_db():
            QMessageBox.critical(self, "Database Error", 
                                 f"Could not connect to the database. "
                                 f"Please check credentials in 'connect_to_db' function.\n\n"
                                 f"Driver: QMYSQL\n"
                                 f"Error: {self.db.lastError().text()}")
        
        # Load data for John Doe (Patient_ID 98765432)
        self.populate_ui(patient_id=98765432) 

    def init_ui(self):
        self.setWindowTitle('Imhotep - Patient\'s Portal')
        self.setGeometry(100, 100, 950, 700) # Made window slightly larger
        self.setMinimumSize(700, 550)
        self.setObjectName("patientPortalWindow") 
        
        self.main_card = QFrame(self)
        self.main_card.setObjectName("mainCard")
        self.main_card.setMaximumWidth(1100)
        self.main_card.setMinimumWidth(600)       
        
        main_window_layout = QHBoxLayout(self)
        main_window_layout.addStretch()
        main_window_layout.addWidget(self.main_card)
        main_window_layout.addStretch()

        card_layout = QGridLayout(self.main_card)
        card_layout.setContentsMargins(30, 20, 30, 30) 
        card_layout.setHorizontalSpacing(40) # Added more spacing

        title = QLabel("Imhotep")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Patient's Portal")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title, 0, 0, 1, 2)
        card_layout.addWidget(subtitle, 1, 0, 1, 2)
        
        left_column = self.create_left_column()
        card_layout.addLayout(left_column, 2, 0)

        right_column = self.create_right_column()
        card_layout.addLayout(right_column, 2, 1)
        
        card_layout.setColumnStretch(0, 1) 
        card_layout.setColumnStretch(1, 1)
        card_layout.setRowStretch(2, 1)

        self.apply_styles()

    def create_left_column(self):
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        self.patient_name_label = QLabel("Loading...")
        self.patient_name_label.setObjectName("patientName")
        
        self.patient_uid_label = QLabel("Loading...")
        self.patient_uid_label.setObjectName("patientUID")

        left_layout.addWidget(self.patient_name_label)
        left_layout.addWidget(self.patient_uid_label)
        
        suggestion_box = QFrame()
        suggestion_box.setObjectName("suggestionBox")
        suggestion_layout = QVBoxLayout(suggestion_box)
        suggestion_layout.setSpacing(10)

        suggestion_title = QLabel("Doctor's Suggestions")
        suggestion_title.setObjectName("boxTitle")
        
        self.suggestion_text_label = QLabel("Loading...")
        self.suggestion_text_label.setObjectName("boxText")
        self.suggestion_text_label.setWordWrap(True)

        suggestion_layout.addWidget(suggestion_title)
        suggestion_layout.addWidget(self.suggestion_text_label)
        
        left_layout.addWidget(suggestion_box)
        left_layout.addStretch(1) 
        
        self.logout_button = QPushButton("Log Out")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setFixedSize(120, 40)
        
        left_layout.addWidget(self.logout_button)
        
        return left_layout

    def create_right_column(self):
        """
        Creates the right column layout with
        PLACEHOLDER widgets that will be filled by the database.
        """
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        history_title = QLabel("Prescription History")
        history_title.setObjectName("historyTitle")
        right_layout.addWidget(history_title)

        # --- Current Prescription Box ---
        current_pr_box = QFrame()
        current_pr_box.setObjectName("currentPrescriptionBox")
        current_pr_layout = QVBoxLayout(current_pr_box)
        current_pr_layout.setSpacing(10)

        # --- These labels are now class members to be updated ---
        self.med_label = QLabel("Loading current prescription...")
        self.med_label.setObjectName("medLabel")
        self.med_label.setAlignment(Qt.AlignCenter)
        self.med_label.setFixedHeight(35)

        self.provider_label = QLabel("Provided by: ...")
        self.provider_label.setObjectName("providerLabel")
        
        self.doctor_uid_label = QLabel("Doctor UID: ...")
        self.doctor_uid_label.setObjectName("providerLabel")

        details_button = QPushButton("View Details")
        details_button.setObjectName("detailsButton")
        details_button.setFixedSize(150, 40)

        current_pr_layout.addWidget(self.med_label)
        current_pr_layout.addWidget(self.provider_label)
        current_pr_layout.addWidget(self.doctor_uid_label)
        current_pr_layout.addWidget(details_button)
        
        right_layout.addWidget(current_pr_box)

        # --- Past Prescriptions ---
        past_title = QLabel("Past Prescriptions")
        past_title.setObjectName("pastTitle")
        right_layout.addWidget(past_title)

        # --- This layout will be dynamically filled with buttons ---
        self.past_prescriptions_layout = QVBoxLayout()
        self.past_prescriptions_layout.setSpacing(10)

        # Add a placeholder
        self.past_placeholder = QLabel("Loading past prescriptions...")
        self.past_placeholder.setObjectName("providerLabel") # Use same faded style
        self.past_prescriptions_layout.addWidget(self.past_placeholder)
        
        # Add the dynamic layout to the main right layout
        right_layout.addLayout(self.past_prescriptions_layout)

        # 'View All History' is no longer needed if we list them all
        # view_all_link = QLabel("View All History")
        # view_all_link.setObjectName("viewAllLink")
        # view_all_link.setAlignment(Qt.AlignHCenter)
        # right_layout.addWidget(view_all_link)
        
        right_layout.addStretch(1)
        
        return right_layout

    def connect_to_db(self):
        """
        Establishes the database connection.
        !! YOU MUST UPDATE THESE DETAILS !!
        """
        # self.db is already created in __init__
        self.db.setHostName('localhost')     # <-- 99%
        self.db.setDatabaseName('imhotep')   # <-- From your screenshot
        self.db.setUserName('root')          # <-- Common default
        self.db.setPassword('') # <-- !! UPDATE THIS !!
        
        if not self.db.open():
            return False
        
        print("Database connected successfully.")
        return True

    def populate_ui(self, patient_id):
        """
        Queries ALL tables and populates the entire UI.
        !!! ALL COLUMN NAMES HERE ARE ASSUMPTIONS !!!
        """
        if not self.db.isOpen():
            self.patient_name_label.setText("DB Connection Error")
            self.patient_uid_label.setText(f"UID: {patient_id}")
            self.suggestion_text_label.setText("Could not connect to database.")
            self.med_label.setText("DB Connection Error")
            return

        # --- Query 1: Get Patient Info from patient_portal ---
        query = QSqlQuery()
        query.prepare("""
            SELECT User_Name, Doctor_sugg, Pr_ID 
            FROM patient_portal 
            WHERE Patient_ID = :id
        """)
        query.bindValue(":id", patient_id)
        
        current_pr_id = None
        if query.exec() and query.next():
            self.patient_name_label.setText(f"Patient: {query.value(0)}")
            self.patient_uid_label.setText(f"UID: {patient_id}")
            self.suggestion_text_label.setText(query.value(1))
            current_pr_id = query.value(2) # Get the ID for the *current* prescription
        else:
            self.patient_name_label.setText("Patient not found")
            self.patient_uid_label.setText(f"UID: {patient_id}")
            self.suggestion_text_label.setText("No suggestions found.")

        # --- Query 2: Get Current Prescription (if Pr_ID exists) ---
        if current_pr_id:
            pr_query = QSqlQuery()
            # --- ASSUMPTIONS: 'prescription' table columns ---
            pr_query.prepare("""
                SELECT Medication_Name, Dosage, Frequency, Doctor_ID 
                FROM prescription 
                WHERE Pr_ID = :pr_id
            """) # <-- ASSUMPTION on column names
            pr_query.bindValue(":pr_id", current_pr_id)
            
            current_doc_id = None
            if pr_query.exec() and pr_query.next():
                med_name = pr_query.value(0)
                dosage = pr_query.value(1)
                frequency = pr_query.value(2)
                current_doc_id = pr_query.value(3) # Get the Doctor_ID
                
                self.med_label.setText(f"{med_name}, {dosage} - {frequency}")
            else:
                self.med_label.setText("Prescription not found")

            # --- Query 3: Get Doctor Info (if Doctor_ID exists) ---
            if current_doc_id:
                doc_query = QSqlQuery()
                # --- ASSUMPTIONS: 'doctor_portal' table columns ---
                doc_query.prepare("""
                    SELECT Doctor_Name, Doctor_UID 
                    FROM doctor_portal 
                    WHERE Doctor_ID = :doc_id
                """) # <-- ASSUMPTION on column names
                doc_query.bindValue(":doc_id", current_doc_id)
                
                if doc_query.exec() and doc_query.next():
                    self.provider_label.setText(f"Provided by: Dr. {doc_query.value(0)}")
                    self.doctor_uid_label.setText(f"Doctor UID: {doc_query.value(1)}")
                else:
                    self.provider_label.setText("Doctor not found")
        else:
            self.med_label.setText("No current prescription")
            self.provider_label.setText("Provided by: N/A")
            self.doctor_uid_label.setText("Doctor UID: N/A")

        # --- Query 4: Get Past Prescriptions ---
        past_query = QSqlQuery()
        # --- ASSUMPTIONS: 'prescription' table columns ---
        past_query.prepare("""
            SELECT Medication_Name, Date_Issued 
            FROM prescription 
            WHERE Patient_ID = :id AND Status = 'Past'
        """) # <-- ASSUMPTION on column names 'Date_Issued', 'Status'
        past_query.bindValue(":id", patient_id)

        # Clear the placeholder
        self.clear_layout(self.past_prescriptions_layout)
        
        found_past = False
        if past_query.exec():
            while past_query.next():
                found_past = True
                med_name = past_query.value(0)
                date_str = past_query.value(1).toString("MMM yyyy") # Format date
                
                # Create a new button for each past prescription
                past_btn = QPushButton(f"{med_name} - {date_str}")
                past_btn.setProperty("class", "pastButton")
                self.past_prescriptions_layout.addWidget(past_btn)
        
        if not found_past:
            # If loop never ran, add the placeholder back
            self.past_placeholder = QLabel("No past prescriptions found.")
            self.past_placeholder.setObjectName("providerLabel")
            self.past_prescriptions_layout.addWidget(self.past_placeholder)

    def clear_layout(self, layout):
        """Removes all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def apply_styles(self):
        """Applies the full stylesheet to the application."""
        self.setStyleSheet("""
            /* --- Style for the main window background --- */
            #patientPortalWindow {
                background-color: #f0f2f5;
            }
        
            /* --- Main Card --- */
            #mainCard {
                background-color: white;
                border-radius: 16px;
            }
            
            /* --- Fonts & Titles --- */
            #title {
                font-family: Arial, sans-serif;
                font-size: 32px;
                font-weight: 600;
                color: #333;
                margin-bottom: 0px;
                padding: 0;
            }
            
            #subtitle {
                font-family: Arial, sans-serif;
                font-size: 16px;
                color: #777;
                margin-top: 0px;
                margin-bottom: 25px;
            }
            
            #historyTitle {
                font-family: Arial, sans-serif;
                font-size: 20px;
                font-weight: 600;
                color: #333;
                margin-bottom: 5px;
            }
            
            #pastTitle {
                font-family: Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                color: #333;
                margin-top: 10px;
            }
            
            /* --- Left Column --- */
            #patientName {
                font-family: Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
            }
            
            #patientUID {
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #555;
            }
            
            #suggestionBox {
                background-color: #e7f5ff; /* Light blue background */
                border: 1px solid #b3d9ff; /* Blue border */
                border-radius: 8px;
                padding: 15px;
            }
            
            #boxTitle {
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
            }
            
            #boxText {
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #333;
            }
            
            #logoutButton {
                background-color: #d9534f; /* Red */
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                padding: 10px;
                border: none;
            }
            #logoutButton:hover {
                background-color: #c9302c; /* Darker red */
            }

            /* --- Right Column --- */
            #currentPrescriptionBox {
                background-color: #f0fff4; /* Light green background */
                border: 1px solid #8fdfab; /* Green border */
                border-radius: 8px;
                padding: 15px;
            }
            
            #medLabel {
                background-color: #28a745; /* Green */
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                border-radius: 17px; /* Half of height for pill shape */
                padding: 5px 10px;
            }
            
            #providerLabel {
                font-family: Arial, sans-serif;
                font-size: 13px;
                color: #444;
            }
            
            #detailsButton {
                background-color: #007bff; /* Blue */
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                padding: 10px;
                border: none;
            }
            #detailsButton:hover {
                background-color: #0069d9; /* Darker blue */
            }
            
            /* --- Class selector (.) for past buttons --- */
            .pastButton {
                background-color: #e9ecef; /* Light gray */
                color: #333;
                font-family: Arial, sans-serif;
                font-size: 14px;
                border-radius: 8px;
                padding: 12px;
                border: none;
                text-align: left; /* Aligns text to the left */
            }
            .pastButton:hover {
                background-color: #dee2e6; /* Darker gray */
            }
            
            #viewAllLink {
                font-family: Arial, sans-serif;
                font-size: 13px;
                color: #007bff;
            }
        """)

# --- Main execution block ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    default_font = QFont("Arial", 10)
    app.setFont(default_font)
    
    window = PatientPortal()
    window.show()
    
    sys.exit(app.exec_())
