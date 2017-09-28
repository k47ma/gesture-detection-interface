import pygame
from camera import Camera


class Interface(object):
    def __init__(self):
        object.__init__(self)

        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        self.clock = pygame.time.Clock()
        self.done = False

        self.scene1 = Scene1()
        self.scene2 = Scene2()
        self.scenes = {"scene1": self.scene1, "scene2": self.scene2}
        self.current_scene = "scene1"

        self.camera = Camera()
        self.camera.daemon = True
        self.camera.start()

        self.start()

    def start(self):
        while not self.done:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event == pygame.QUIT:
                    self.done = True

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_ESCAPE]:
                self.done = True

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
    def __init__(self):
        Scene.__init__(self)

    def render(self, screen):
        screen.fill((0, 255, 0))


class Scene2(Scene):
    def __init__(self):
        Scene.__init__(self)

    def render(self, screen):
        screen.fill((255, 0, 0))


app = Interface()
app.start()
