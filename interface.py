# -*- coding: utf-8 -*-
import pygame
from camera import Camera
from weather import WeatherThread
import time
from urllib.request import urlopen
import io

# module for user interface

WIDTH = 1920
HEIGHT = 1080


class Interface(object):
    def __init__(self):
        object.__init__(self)

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.done = False

        self.weather = {}

        self.scene1 = Scene1(self)
        self.scene2 = Scene2(self)
        self.scenes = {"scene1": self.scene1, "scene2": self.scene2}
        self.current_scene_name = "scene1"

        self.camera = Camera()
        self.camera.start()

        self.weather_thread = WeatherThread(self)
        self.weather_thread.daemon = True
        self.weather_thread.start()

    def start(self):
        while not self.done:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.switch_scene()

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_ESCAPE]:
                self.terminate()
            if pressed[pygame.K_LALT] and pressed[pygame.K_F4]:
                self.terminate()

            # retrieve gesture command from camera module
            command = self.camera.command
            if command:
                self.switch_scene(command)
                self.camera.command = ""

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
        self.camera.done = True


# basic scene class
class Scene:
    def __init__(self, parent):
        self.parent = parent
        self.next = self

        self.font1 = pygame.font.SysFont("segoe-ui-symbol", 30)
        self.font2 = pygame.font.SysFont("Calibri", 23, bold=True)
        self.font3 = pygame.font.SysFont("segoe-ui-symbol", 25)

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

        screen.blit(time_text, (500, 5))


class Scene1(Scene):
    def __init__(self, parent):
        Scene.__init__(self, parent)

        self.last_update = 0

        self.icons = {}

    def refresh(self, screen):
        screen.fill((0, 0, 0))

    def render(self, screen):
        if self.parent.weather:
            self.display_weather(screen, (800, 30))
        self.display_greeting(screen, (100, 30))

    def display_weather(self, screen, coords):
        x, y = coords
        weather_info = self.parent.weather

        # check whether the weather info has been updated
        if weather_info['time'] == self.last_update:
            return

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

        temp_text = self.font1.render(temp + "℃", True, self.WHITE)
        temp_range_text = self.font1.render(low + " - " + high + "℃", True, self.WHITE)
        screen.blit(temp_text, (x+60, y+90))
        screen.blit(temp_range_text, (x, y+135))

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

        if self.parent.camera.present:
            user = " Kai"
        else:
            user = ""

        greeting_text = self.font1.render("Hi" + user + ",", True, self.WHITE)
        greeting_text2 = self.font1.render("Good " + d + "!", True, self.WHITE)
        screen.blit(greeting_text, (x, y))
        screen.blit(greeting_text2, (x, y+45))

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


app = Interface()
app.start()
