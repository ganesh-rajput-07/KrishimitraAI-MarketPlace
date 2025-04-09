import sys
import os
import webbrowser
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krishimitra AI")
        self.setGeometry(100, 100, 800, 600)

        # Create button to open the web app
        self.button = QPushButton("Open Krishimitra AI", self)
        self.button.clicked.connect(self.open_django_app)

        layout = QVBoxLayout()
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set the correct working directory
        self.project_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.project_dir)

        print(f"Current Directory: {os.getcwd()}")
        print(f"Files: {os.listdir()}")

        # Start Django server
        self.start_django_server()

        try:
            self.django_process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
            stdout=open("django_stdout.log", "w"),
            stderr=open("django_stderr.log", "w"),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        except Exception as e:
            with open("error_log.txt", "w") as f:
                f.write(str(e))


    def open_django_app(self):
        """Opens the web app in the default browser"""
        webbrowser.open("http://127.0.0.1:8000")

    def closeEvent(self, event):
        """Stops the Django server when app closes"""
        if self.django_process:
            self.django_process.terminate()
            self.django_process.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
