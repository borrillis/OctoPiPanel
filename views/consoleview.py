import pygame
import pygbutton
import os
import string
from views.panelview import PanelView


class ConsoleView(PanelView):

    def __init__(self, config):
        PanelView.__init__(self, config, "Console")

        self.background_color = pygame.color.Color("#000000")
        self.divider_color = pygame.color.Color("#CC302B")

        self.fntText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/DejaVuSans.ttf"), 24)

        btn_send_image = pygame.transform.smoothscale(pygame.image.load(os.path.join(self.config.script_directory, 'assets/button-start.png')), (30, 30))
        s = pygame.Surface((30, 30))
        s.blit(btn_send_image, (0, 0))
        self.btn_send = pygbutton.PygButton((self.config.width - 35, self.config.height - self.config.statusbarheight - 35, 30, 30), normal=btn_send_image)

        self.current_string = ["H","e","l","l","o"]

    def handle_event(self, event):
        PanelView.handle_event(self, event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.current_string = self.current_string[0:-1]
            elif event.key == pygame.K_RETURN:
                self.current_string.append("")
            elif event.key == pygame.K_MINUS:
                self.current_string.append("_")
            elif 97 <= event.key <= 122:
                print "[CONSOLE]: {0}".format(event.key)
                if (event.mod & 1 == 1) or (event.mod & 2 == 2) :
                    self.current_string.append(("{0}".format(chr(event.key))).upper())
                else :
                    self.current_string.append(chr(event.key))

    def draw(self, screen, firstframe):
        PanelView.draw(self, screen, firstframe)

        s = pygame.Surface((self.config.width, self.config.height - self.config.statusbarheight - self.config.titlebarheight))
        s.fill(self.background_color)
        screen.blit(s, (0, self.config.titlebarheight))

        pygame.draw.line(screen, self.divider_color, (0, self.config.titlebarheight), (self.config.width, self.config.titlebarheight))

        message = string.join(self.current_string, "")

        top = self.config.height - self.config.statusbarheight - 40

        pygame.draw.rect(screen, self.background_color, (0, top, self.config.width - 40, 40), 0)
        pygame.draw.rect(screen, self.divider_color, (0, top, self.config.width - 40, 40), 1)
        self.btn_send.draw(screen)

        if len(message) != 0:
            screen.blit(self.fntText.render(message, 1, (255,255,255)), (5, top + 5))
