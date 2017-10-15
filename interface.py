# -*- coding: utf-8 -*-
import pygame
import time
import io
from urllib.request import urlopen
#from camera import Camera
from weather import WeatherThread
from news import NewsThread
from utility import *


# module for user interface

NAME = ""
WIDTH = 1920
HEIGHT = 1080
WHITE = (255, 255, 255)


class Interface(object):
    def __init__(self):
        object.__init__(self)

        pygame.init()
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.done = False

        self.weather = None
        self.news = None

        self.scene1 = Scene1(self)
        self.scene2 = Scene2(self)
        self.scenes = {"scene1": self.scene1, "scene2": self.scene2}
        self.current_scene_name = "scene1"
        
        #self.camera = Camera()
        #self.camera.start()

        self.weather_thread = WeatherThread(self)
        self.weather_thread.daemon = True
        self.weather_thread.start()

        self.news_thread = NewsThread(self)
        self.news_thread.daemon = True
        self.news_thread.start()

    def start(self):
        while not self.done:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.switch_scene()

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_ESCAPE]:
                self.terminate()
            if pressed[pygame.K_LALT] and pressed[pygame.K_F4]:
                self.terminate()

            # retrieve gesture command from camera module
            """
            command = self.camera.command
            if command:
                self.switch_scene(command)
                self.camera.command = ""
            """

            current_scene = self.scenes[self.current_scene_name]
            current_scene.refresh(self.screen)
            current_scene.render(self.screen)
            current_scene.display_general(self.screen)

            pygame.display.flip()

    def switch_scene(self, direction="right"):
        total = len(self.scenes)
        current_ind = int(self.current_scene_name[-1])

        if direction == "right":
            ind = current_ind + 1
        else:
            ind = current_ind - 1

        if ind > total:
            self.current_scene_name = "scene1"
        elif ind == 0:
            self.current_scene_name = "scene" + str(total)
        else:
            self.current_scene_name = "scene" + str(ind)

    def terminate(self):
        self.done = True
        #self.camera.done = True


# basic scene class
class Scene:
    def __init__(self, parent):
        self.parent = parent
        self.next = self

        self.font1 = pygame.font.SysFont("Arial Unicode MS", 35)
        self.font1_bold = pygame.font.SysFont("Arial", 35, bold=True)
        self.font2 = pygame.font.SysFont("Calibri", 28, bold=True)
        self.font3 = pygame.font.SysFont("Arial", 30)
        self.font4 = pygame.font.SysFont("Times New Roman", 18)
        self.font5 = pygame.font.SysFont("Arial", 55)
        self.font6 = pygame.font.SysFont("Arial", 15, bold=True)

        self.WHITE = (255, 255, 255)

    def render(self, screen):
        pass

    def refresh(self, screen):
        pass

    def process_input(self, events):
        pass

    def display_general(self, screen):
        current_time = time.localtime(time.time())

        year, month, day, hour, minute, second, week_day = current_time[:7]

        time_str = "%02d:%02d:%02d" % (hour, minute, second)
        time_text = self.font2.render(time_str, True, self.WHITE)

        screen.blit(time_text, (900, 10))


class Scene1(Scene):
    def __init__(self, parent):
        Scene.__init__(self, parent)

        self.icons = {}

        self.message1 = self.font1.render("Retrieving weather data...", True, self.WHITE)
        self.message2 = self.font1.render("Retrieving news data...", True, self.WHITE)

    def refresh(self, screen):
        screen.fill((0, 0, 0))

    def render(self, screen):
        self.display_greeting(screen, (100, 75))

        # display weather information
        if self.parent.weather:
            self.display_weather(screen, (1300, 150))
        else:
            screen.blit(self.message1, (1300, 150))

        # display news
        if self.parent.news:
            self.display_news(screen, (100, 250))
        else:
            screen.blit(self.message2, (100, 250))

    def display_greeting(self, screen, coords):
        x, y = coords
        current_time = time.localtime(time.time())
        year, month, day, hour, minute, second, week_day = current_time[:7]

        if 6 <= hour < 12:
            d = "morning"
        elif 12 <= hour <= 17:
            d = "afternoon"
        else:
            d = "evening"
        
        """
        if self.parent.camera.present:
            user = " Kai"
        else:
            user = ""
        """

        greeting_text = self.font5.render("Hi " + NAME + ",", True, self.WHITE)
        greeting_text2 = self.font5.render("Good " + d + "!", True, self.WHITE)
        screen.blit(greeting_text, (x, y))
        screen.blit(greeting_text2, (x, y+65))

    def display_weather(self, screen, coords):
        x, y = coords
        weather_info = self.parent.weather

        # display city and condition
        city = weather_info['city']
        condition = weather_info['condition']

        city_text = self.font1.render(city, True, self.WHITE)
        condition_text = self.font3.render(condition, True, self.WHITE)

        screen.blit(city_text, (x+20, y))
        screen.blit(condition_text, (x, y+45))

        # load image from web if the icon is not locally stored
        if condition not in self.icons:
            self.load_image(weather_info)
        icon = self.icons[condition]
        screen.blit(icon, (x-10, y+80))
        # display temperature
        temp = str(weather_info['temperature'])
        high = str(weather_info['high_c'])
        low = str(weather_info['low_c'])

        temp_text = self.font1_bold.render(temp + "°", True, self.WHITE)
        temp_range_text = self.font1.render("24h: " + low + " - " + high + "°", True, self.WHITE)
        screen.blit(temp_text, (x+60, y+100))
        screen.blit(temp_range_text, (x, y+155))

        fx = x
        fy = y + 220
        graph_width = 500
        graph_height = 300
        drawWeatherGraph(screen, (fx, fy), (fx+graph_width, fy+graph_height), weather_info['forecasts'], self.font6)

        # display last update time
        last_update = time.asctime(time.localtime(weather_info['time']))[11:16]
        last_update_text = self.font4.render("Last update: " + last_update, True, self.WHITE)
        screen.blit(last_update_text, (x, fy+graph_height+50))

    def display_news(self, screen, coords):
        x, y = coords
        news = self.parent.news

        default_text = self.font3.render("What's new today:", True, self.WHITE)
        screen.blit(default_text, (x, y))
        y += 50

        for article in news['articles']:
            article_text = self.font3.render(article['title'], True, self.WHITE)
            screen.blit(article_text, (x, y))
            y += 50

        # display last update time
        last_update = time.asctime(time.localtime(news['time']))[11:16]
        last_update_text = self.font4.render("Last update: " + last_update, True, self.WHITE)
        screen.blit(last_update_text, (x, y+10))

    def load_image(self, weather_info):
        condition = weather_info['condition']
        icon_url = weather_info['icon_url']

        # load image from url
        image = urlopen(icon_url).read()
        image_file = io.BytesIO(image)

        # add image object to dictionary
        icon = pygame.image.load(image_file)
        self.icons[condition] = icon


class Scene2(Scene):
    def __init__(self, parent):
        Scene.__init__(self, parent)

    def render(self, screen):
        screen.fill((255, 0, 0))


# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight < rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]


def drawWeatherGraph(surface, start, end, weather_info, font):
    x1, y1 = start
    x2, y2 = end

    max_temp = max([info[1] for info in weather_info])
    min_temp = min([info[1] for info in weather_info])
    points = []
    texts = []

    # calculate positions for each point
    for ind in range(len(weather_info)):
        info = weather_info[ind]
        weather_time = info[0][11:13]
        temp = info[1]
        texts.append((weather_time, temp))
        point_x = int(x1 + 0.1 * (x2 - x1) + 0.8 * (x2 - x1) / (len(weather_info) - 1) * ind)
        point_y = int(y2 - 0.2 * (y2 - y1) - 0.6 * (y2 - y1) / (max_temp - min_temp) * (temp - min_temp))
        points.append((point_x, point_y))

    p1 = (points[0][0], y2)
    p2 = (points[-1][0], y2)
    poly = [p1] + points + [p2]
    pygame.draw.polygon(surface, (50, 50, 50), poly)

    for ind in range(len(points)):
        point = points[ind]
        pygame.draw.circle(surface, WHITE, point, 4)
        drawDashedLine(surface, point, (point[0], y2), (3, 3), WHITE)

        if ind:
            pygame.draw.line(surface, WHITE, point, points[ind - 1])

        # add temperature and time information
        weather_time, temp = texts[ind]
        temp_text = font.render(str(int(temp)) + "°", True, WHITE)
        time_text = font.render(weather_time, True, WHITE)

        surface.blit(temp_text, (point[0] - 10, point[1] - 25))
        surface.blit(time_text, (point[0] - 10, y2 + 7))

    # draw x and y axis
    pygame.draw.line(surface, WHITE, start, (x1, y2))
    pygame.draw.line(surface, WHITE, (x1, y2), end)


app = Interface()
app.start()
