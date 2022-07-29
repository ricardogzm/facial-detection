from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QMainWindow,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Signal, Slot, Qt, QThread, QTimer, QMutex
import requests as rq

# Disable IPV6 for all requests
rq.packages.urllib3.util.connection.HAS_IPV6 = False


class JokeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Joke Window")
        self.setFixedSize(500, 400)
        # self.setStyleSheet("background-color: black;")

        self.joke_label = QLabel("Joke")
        self.joke_label.setStyleSheet("font-size: 20px;")
        self.joke_label.setWordWrap(True)
        self.joke_label.setAlignment(Qt.AlignCenter)

        self.get_joke_button = QPushButton("Get joke")
        self.get_joke_button.clicked.connect(self.update_joke)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.joke_label)
        layout.addWidget(self.get_joke_button)
        layout.addWidget(self.close_button)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.update_joke()

    def update_joke(self):
        response = rq.get(
            "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
        )
        data = response.json()
        self.joke_label.setText(data["joke"])


if __name__ == "__main__":
    app = QApplication([])
    window = JokeWindow()
    window.show()
    app.exec_()
