# -*- coding: utf-8 -*-
import pygame
from camera import Camera
from weather import WeatherThread

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
        self.current_scene = "scene1"

        self.camera = Camera()
        self.camera.daemon = True
        self.camera.start()

        self.weather_thread = WeatherThread(self)
        self.weather_thread.start()

    def start(self):
        while not self.done:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event == pygame.QUIT:
                    self.done = True

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_ESCAPE]:
                self.done = True

            # command for testing
            if pressed[pygame.K_1]:
                self.current_scene = "scene1"
            if pressed[pygame.K_2]:
                self.current_scene = "scene2"

            # retrieve gesture command from camera module
            command = self.camera.command
            if command:
                if command == "right" and self.current_scene == "scene1":
                    self.current_scene = "scene2"
                elif command == "left" and self.current_scene == "scene2":
                    self.current_scene = "scene1"

            self.scenes[self.current_scene].render(self.screen)

            pygame.display.flip()


# basic scene class
class Scene:
    def __init__(self):
        self.next = self

    def render(self, screen):
        pass

    def update(self):
        pass

    def process_input(self, events):
        pass


class Scene1(Scene):
    def __init__(self, parent):
        Scene.__init__(self)

        self.parent = parent
        self.last_update = 0

        self.font1 = pygame.font.SysFont("segoe-ui-symbol", 20)

    def render(self, screen):
        screen.fill((0, 0, 0))

        if self.parent.weather:
            self.display_weather(screen)

    def display_weather(self, screen):
        weather_info = self.parent.weather

        # check whether the weather info has been updated
        if weather_info['time'] == self.last_update:
            return

        city = weather_info['city']
        temp = weather_info['temperature']
        weather_text = self.font1.render(city + ": " + str(temp) + "℃", True, (255, 255, 255))

        screen.blit(weather_text, (20, 20))


class Scene2(Scene):
    def __init__(self, parent):
        Scene.__init__(self)

        self.parent = parent

    def render(self, screen):
        screen.fill((255, 0, 0))


app = Interface()
app.start()
