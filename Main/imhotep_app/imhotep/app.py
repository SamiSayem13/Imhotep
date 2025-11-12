import sys
from PyQt5.QtWidgets import QApplication
from .router import Router

def run_app():
    app = QApplication(sys.argv)
    router = Router()
    router.show_selection()  # start at role selection
    router.show()            # show main window
    sys.exit(app.exec_())
