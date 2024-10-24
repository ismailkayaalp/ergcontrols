import sys
from PyQt5.QtWidgets import QApplication
from simple_apps import SimpleApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleApp()
    sys.exit(app.exec_())