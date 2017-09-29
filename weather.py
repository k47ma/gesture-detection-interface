import requests
import json
import threading
import time
import api_keys

# module for looking up weather and location


class WeatherThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)

        self.parent = parent

    def run(self):
        while True:
            # get the current ip address and city
            response = requests.get("https://ipfind.co/me?auth=" + api_keys.ip_key)
            content = json.loads(str(response.content, 'utf-8'))

            ip_address = content['ip_address']
            city = content['city']

            # get the current weather information
            response = requests.get("http://api.apixu.com/v1/current.json?key=" + api_keys.weather_key + "&q=" + ip_address)
            content = json.loads(str(response.content, 'utf-8'))
            condition = content['current']['condition']['text']
            icon_url = "http:" + content['current']['condition']['icon']

            # get the 24h weather information
            response = requests.get("https://api.uwaterloo.ca/v2/weather/current.json")
            content = json.loads(str(response.content, 'utf-8'))
            temperature = content['data']['temperature_current_c']
            high_c = content['data']['temperature_24hr_max_c']
            low_c = content['data']['temperature_24hr_min_c']

            information = {"city": city, "condition": condition, "icon_url": icon_url, "temperature": temperature,
                           "high_c": high_c, "low_c": low_c, "time": int(time.time())}
            self.parent.weather = information

            time.sleep(1800)
