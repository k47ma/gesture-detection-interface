import requests
import json
import threading
import time

# module for looking up weather and location


class WeatherThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)

        self.parent = parent

    def run(self):
        while True:
            # get the current ip address and city
            response = requests.get("https://ipfind.co/me?auth=81f6b6dd-9a71-40c9-afd3-df87942266e9")
            content = json.loads(str(response.content, 'utf-8'))

            ip_address = content['ip_address']
            city = content['city']
            country = content['country_code']

            # get the current weather information
            response = requests.get("http://api.apixu.com/v1/current.json?key=e6b55e0ed58e42c2abf00045172909&q=" +
                                    ip_address)
            content = json.loads(str(response.content, 'utf-8'))
            temperature = content['current']['temp_c']
            condition = content['current']['condition']['text']
            icon_url = "http:" + content['current']['condition']['icon']

            # get weather forecast information
            params = {'q': city + country, 'units': "metric", 'appid': "508b76be5129c25115e5e60848b4c20c"}
            response = requests.get("http://api.openweathermap.org/data/2.5/forecast", params=params)
            content = json.loads(str(response.content, 'utf-8'))
            forecasts = content.list[:7]

            high_c = self.get_highest(forecasts)
            low_c = self.get_lowest(forecasts)

            formatted_forecasts = [(forecast['dy_text'], forecast['main']['temp']) for forecast in forecasts]

            information = {"city": city, "condition": condition, "icon_url": icon_url, "temperature": temperature,
                           "high_c": high_c, "low_c": low_c, "forecasts": formatted_forecasts, "time": int(time.time())}
            self.parent.weather = information

            # update every half an hour
            time.sleep(1800)

    def get_highest(self, forecasts):
        max_temp = max([forecast['main']['temp_max'] for forecast in forecasts])
        return max_temp

    def get_lowest(self, forecasts):
        min_temp = min([forecast['main']['temp_min'] for forecast in forecasts])
        return min_temp
