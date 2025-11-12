from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from .views.selection import SelectionView
from .views.login import LoginView
from .views.forgot import ForgotPasswordView
from .views.register import RegisterView
from .views.doctor import DoctorPortal

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
        self.doctor = DoctorPortal()  # doctor portal view

        # --- wire navigation from selection ---
        # If SelectionView.goto_login emits a role (e.g. "doctor"), our show_login(role=None) will receive it.
        # If it emits without an arg, it's also fine (role defaults to None).
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

        self.doctor.goto_login.connect(self.show_login)


        # --- add initial views to stack ---
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
        # If LoginView exposes set_role, use it; otherwise stash on the instance.
        if hasattr(self.login, "set_role") and callable(getattr(self.login, "set_role")):
            self.login.set_role(role)
        else:
            # Fallback if you didn't add set_role in LoginView
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
            # Make sure the doctor view is in the stack once
            if self.stack.indexOf(self.doctor) == -1:
                self.stack.addWidget(self.doctor)
            self.stack.setCurrentWidget(self.doctor)
            return

        # TODO: plug in patient/pharmacist dashboards when ready
        if role == "patient":
            QMessageBox.information(self, "Login", "Patient panel is not implemented yet.")
            self.show_selection()
            return

        if role == "pharmacist":
            QMessageBox.information(self, "Login", "Pharmacist panel is not implemented yet.")
            self.show_selection()
            return

        # If we don't know the role, go back to selection
        self.show_selection()

    def on_register_success(self, user_id: str):
        print(f"Registration successful for User_ID: {user_id}")
        QMessageBox.information(self, "Success", f"Registration successful for User_ID: {user_id}")
        # after registering, send the user to the selection screen to pick role and login
        self.show_selection()
