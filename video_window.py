import os
import sys
from decouple import config

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLineEdit
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

import requests as rq
import random as rnd


class YTVideoWindow(QMainWindow):
    video_list = []
    video_index = 0
    max_videos = 20
    YT_API_KEY = config("YT_API_KEY")

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Funny videos")
        self.setGeometry(400, 400, 1280, 720)
        self.widget = QWidget(self)

        self.load_video_list()

        # Widget para el navegador
        self.webview = QWebEngineView()
        self.webview.load(self.create_video_url(self.get_video_id()))

        self.next_button = QPushButton("Load next video")
        self.next_button.clicked.connect(self.next_video)

        self.previous_button = QPushButton("Load previous video")
        self.previous_button.clicked.connect(self.previous_video)

        self.toplayout = QHBoxLayout()
        self.toplayout.addWidget(self.previous_button)
        self.toplayout.addWidget(self.next_button)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.toplayout)
        self.layout.addWidget(self.webview)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def load_video_list(self):
        response = rq.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": self.YT_API_KEY,
                "part": "snippet",
                "maxResults": self.max_videos,
                "q": "funny animals",
                "type": "video",
                "order": "viewCount",
                "videoEmbeddable": "true",
                "videoSyndicated": "true",
            },
        )
        self.video_list = response.json()["items"]

        # Shuffle the list
        rnd.shuffle(self.video_list)

    # Get videoId from current video index
    def get_video_id(self):
        return self.video_list[self.video_index]["id"]["videoId"]

    # Create video URL
    def create_video_url(self, video_id):
        q_url = QUrl(f"http://localhost:3004/?video={video_id}")

        return q_url

    # Load next video
    def next_video(self):
        self.video_index += 1
        if self.video_index >= len(self.video_list):
            self.video_index = 0

        url = self.create_video_url(self.get_video_id())
        print(url)
        self.webview.load(url)

    # Load previous video
    def previous_video(self):
        self.video_index -= 1
        if self.video_index < 0:
            self.video_index = len(self.video_list) - 1

        url = self.create_video_url(self.get_video_id())
        print(url)
        self.webview.load(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YTVideoWindow()
    window.show()
    sys.exit(app.exec())
