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
        while True:
            # retrieve news data
            params = {'source': "cnn", 'sortBy': "top", 'apiKey': "d094eb3adb9c4548b22946efdc417e17"}
            response = requests.get("https://newsapi.org/v1/articles", params=params)
            content = json.loads(str(response.content, 'utf-8'))

            articles = content['articles']
            self.parent.news = {'articles': articles, 'time': int(time.time())}

            # update every 15 min
            time.sleep(900)
