# router.py
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from .views.selection import SelectionView
from .views.login import LoginView
from .views.forgot import ForgotPasswordView
from .views.register import RegisterView
from .views.doctor import DoctorPortal
from .views.pharma import PharmacistPortal  # ensure this path matches your file


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
        self.pharmacist = PharmacistPortal()  # pharmacist portal view

        # --- wire navigation from selection ---
        # SelectionView.goto_login may emit a role (e.g., "doctor", "patient", "pharmacist")
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

        # --- add initial views to stack (portals are added lazily on first use) ---
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
        Makes LoginView aware of which role is being logged in, so we can route correctly after success.
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
        We route based on the role that was set when coming from the SelectionView.
        """
        role = getattr(self.login, "current_role", None)

        if role == "doctor":
            if self.stack.indexOf(self.doctor) == -1:
                self.stack.addWidget(self.doctor)
            # Optional: pass user context to doctor portal if it exposes a setter
            if hasattr(self.doctor, "set_user") and callable(getattr(self.doctor, "set_user")):
                self.doctor.set_user(user_id)
            self.stack.setCurrentWidget(self.doctor)
            return

        if role == "pharmacist":
            if self.stack.indexOf(self.pharmacist) == -1:
                self.stack.addWidget(self.pharmacist)
            # Optional: pass user context to pharmacist portal if it exposes a setter
            if hasattr(self.pharmacist, "set_user") and callable(getattr(self.pharmacist, "set_user")):
                # If LoginView can provide a display name, you can pass it as a second arg.
                # e.g., self.pharmacist.set_user(user_id, self.login.get_user_name())
                self.pharmacist.set_user(user_id)
            self.stack.setCurrentWidget(self.pharmacist)
            return

        if role == "patient":
            QMessageBox.information(self, "Login", "Patient panel is not implemented yet.")
            self.show_selection()
            return

        # If we don't know the role, go back to selection
        self.show_selection()

    def on_register_success(self, user_id: str):
        print(f"Registration successful for User_ID: {user_id}")
        QMessageBox.information(self, "Success", f"Registration successful for User_ID: {user_id}")
        # after registering, send the user to the selection screen to pick role and login
        self.show_selection()
