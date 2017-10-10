import requests
import json
import threading
import time

# module for news information section


class NewsThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)

        self.parent = parent

    def run(self):
        pass
