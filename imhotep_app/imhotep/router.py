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

        # --- instantiate views ---
        self.selection = SelectionView()
        self.login = LoginView()
        self.forgot = ForgotPasswordView(parent=self.login)
        self.register = RegisterView()
        self.doctor = DoctorPortal()
        self.pharmacist = PharmacistPortal()
        self.patient = PatientPortal()              # <-- NEW

        # --- wire navigation from selection ---
        self.selection.goto_login.connect(self.show_login)
        self.selection.goto_register.connect(self.show_register)

        # --- wire navigation from login/forgot/register ---
        self.login.goto_forgot.connect(self.show_forgot)
        self.login.goto_selection.connect(self.show_selection)
        self.login.goto_register.connect(self.show_register)
        self.login.login_success.connect(self.on_login_success)

        self.forgot.goto_login.connect(self.show_login)

        self.register.goto_selection.connect(self.show_selection)
        self.register.register_success.connect(self.on_register_success)
        self.register.goto_login.connect(self.show_login)

        # --- portals back to login ---
        self.doctor.goto_login.connect(self.show_login)
        self.pharmacist.goto_login.connect(self.show_login)
        self.patient.goto_login.connect(self.show_login)      # <-- NEW

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
        """
        role = getattr(self.login, "current_role", None)

        if role == "doctor":
            if self.stack.indexOf(self.doctor) == -1:
                self.stack.addWidget(self.doctor)
            if hasattr(self.doctor, "set_user"):
                self.doctor.set_user(user_id)
            self.stack.setCurrentWidget(self.doctor)
            return

        if role == "pharmacist":
            if self.stack.indexOf(self.pharmacist) == -1:
                self.stack.addWidget(self.pharmacist)
            if hasattr(self.pharmacist, "set_user"):
                self.pharmacist.set_user(user_id)
            self.stack.setCurrentWidget(self.pharmacist)
            return

        if role == "patient":
            if self.stack.indexOf(self.patient) == -1:
                self.stack.addWidget(self.patient)
            # Pass the numeric patient id into the portal (it will coerce safely)
            if hasattr(self.patient, "set_user"):
                self.patient.set_user(user_id)
            self.stack.setCurrentWidget(self.patient)
            return

        # Unknown role → go back
        self.show_selection()

    def on_register_success(self, user_id: str):
        print(f"Registration successful for User_ID: {user_id}")
        QMessageBox.information(self, "Success", f"Registration successful for User_ID: {user_id}")
        self.show_selection()
