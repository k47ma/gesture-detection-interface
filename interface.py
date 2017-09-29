# -*- coding: utf-8 -*-
import pygame
from camera import Camera
from weather import WeatherThread
import time

# module for user interface


class Interface(object):
    def __init__(self):
        object.__init__(self)

        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        self.clock = pygame.time.Clock()
        self.done = False

        self.weather = {}

        self.scene1 = Scene1(self)
        self.scene2 = Scene2(self)
        self.scenes = {"scene1": self.scene1, "scene2": self.scene2}
        self.current_scene_name = "scene1"

        self.camera = Camera()
        self.camera.daemon = True
        self.camera.start()

        self.weather_thread = WeatherThread(self)
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
                self.done = True

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


# basic scene class
class Scene:
    def __init__(self):
        self.next = self

        self.font1 = pygame.font.SysFont("segoe-ui-symbol", 20)
        self.font2 = pygame.font.SysFont("Times New Roman", 15)

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
        screen.blit(time_text, (200, 10))


class Scene1(Scene):
    def __init__(self, parent):
        Scene.__init__(self)

        self.parent = parent
        self.last_update = 0

    def refresh(self, screen):
        screen.fill((0, 0, 0))

    def render(self, screen):
        if self.parent.weather:
            self.display_weather(screen)

    def display_weather(self, screen):
        weather_info = self.parent.weather

        # check whether the weather info has been updated
        if weather_info['time'] == self.last_update:
            return

        city = weather_info['city']
        temp = weather_info['temperature']
        weather_text = self.font1.render(city + ": " + str(temp) + "℃", True, self.WHITE)

        screen.blit(weather_text, (20, 20))


class Scene2(Scene):
    def __init__(self, parent):
        Scene.__init__(self)

        self.parent = parent

    def render(self, screen):
        screen.fill((255, 0, 0))


app = Interface()
app.start()
