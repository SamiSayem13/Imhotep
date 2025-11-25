# router.py
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from .views.selection import SelectionView
from .views.login import LoginView
from .views.forgot import ForgotPasswordView
from .views.register import RegisterView
from .views.doctor import DoctorPortal
from .views.pharma import PharmacistPortal
from .views.patient import PatientPortal


class Router(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep")

        # --- central stack ---
        self.stack = QStackedWidget()
        lay = QVBoxLayout(self)
        lay.addWidget(self.stack)

        # --- instantiate main views ---
        self.selection = SelectionView()
        self.login = LoginView()
        self.forgot = ForgotPasswordView(parent=self.login)
        self.register = RegisterView()

        # portals: doctor created lazily, others created now
        self.doctor = None                      # will be created on first doctor login
        self.pharmacist = PharmacistPortal()
        self.patient = PatientPortal()

        # --- wire navigation from selection ---
        self.selection.goto_login.connect(self.show_login)
        self.selection.goto_register.connect(self.show_register)

        # login navigation
        self.login.goto_forgot.connect(self.show_forgot)
        self.login.goto_selection.connect(self.show_selection)
        self.login.goto_register.connect(self.show_register)
        self.login.login_success.connect(self.on_login_success)

        # forgot
        self.forgot.goto_login.connect(self.show_login)

        # register
        self.register.goto_selection.connect(self.show_selection)
        self.register.register_success.connect(self.on_register_success)
        self.register.goto_login.connect(self.show_login)

        # portals back to login
        # doctor: will be connected when we create it
        self.pharmacist.goto_login.connect(self.show_login)
        self.patient.goto_login.connect(self.show_login)

        # --- add initial views to stack (portals added lazily on first use) ---
        for w in (self.selection, self.login, self.forgot, self.register):
            self.stack.addWidget(w)

        self.resize(1000, 700)
        self.show_selection()

    # ---------- simple view switches ----------
    def show_selection(self):
        self.stack.setCurrentWidget(self.selection)

    def show_login(self, role=None):
        """
        Accepts optional role from SelectionView (e.g., 'doctor', 'patient', 'pharmacist').
        """
        if hasattr(self.login, "set_role") and callable(getattr(self.login, "set_role")):
            self.login.set_role(role)
        else:
            # fallback: just store it directly
            self.login.current_role = role
        self.stack.setCurrentWidget(self.login)

    def show_forgot(self):
        self.stack.setCurrentWidget(self.forgot)

    def show_register(self):
        self.stack.setCurrentWidget(self.register)

    # ---------- success handlers ----------
    def on_login_success(self, user_id: str):
        """
        Called when LoginView emits login_success.
        Routes based on the role set before login.
        user_id is the logged-in user's ID (e.g., doctor User_ID / Patient_ID).
        """
        role = getattr(self.login, "current_role", None)

        # ----- Doctor -----
        if role == "doctor":
            # create doctor portal on first use, pass doctor_id into ctor
            if self.doctor is None:
                self.doctor = DoctorPortal(doctor_id=user_id)
                self.doctor.goto_login.connect(self.show_login)
                self.stack.addWidget(self.doctor)
            else:
                # if DoctorPortal implements set_user, update its context
                if hasattr(self.doctor, "set_user"):
                    self.doctor.set_user(user_id)

            self.stack.setCurrentWidget(self.doctor)
            return

        # ----- Pharmacist -----
        if role == "pharmacist":
            if self.stack.indexOf(self.pharmacist) == -1:
                self.stack.addWidget(self.pharmacist)
            if hasattr(self.pharmacist, "set_user"):
                self.pharmacist.set_user(user_id)
            self.stack.setCurrentWidget(self.pharmacist)
            return

        # ----- Patient -----
        if role == "patient":
            if self.stack.indexOf(self.patient) == -1:
                self.stack.addWidget(self.patient)
            if hasattr(self.patient, "set_user"):
                self.patient.set_user(user_id)
            self.stack.setCurrentWidget(self.patient)
            return
        
        # inside on_login_success when role == "doctor":
        if role == "doctor":
            if self.doctor is None:
                self.doctor = DoctorPortal(doctor_id=user_id)  # name auto-fetched from DB
                self.doctor.goto_login.connect(self.show_login)
                self.stack.addWidget(self.doctor)
            else:
                if hasattr(self.doctor, "set_user"):
                    self.doctor.set_user(user_id)
            self.stack.setCurrentWidget(self.doctor)
            return


        # Unknown role → go back
        self.show_selection()

    def on_register_success(self, user_id: str):
        print(f"Registration successful for User_ID: {user_id}")
        QMessageBox.information(self, "Success", f"Registration successful for User_ID: {user_id}")
        self.show_selection()
