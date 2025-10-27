import sys
from PyQt5.QtWidgets import QApplication
from launcher_ui import PurpleLauncher

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = PurpleLauncher()
    launcher.show()
    sys.exit(app.exec_())