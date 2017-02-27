import pygame
from views.panelview import PanelView


class ConsoleView(PanelView):

    def __init__(self, config):
        PanelView.__init__(self, config, "Console")
        self.background_color = pygame.color.Color("#EF3220")

    def draw(self, screen, firstframe):
        PanelView.draw(self, screen, firstframe)

        s = pygame.Surface((self.config.width, self.config.height - self.config.statusbarheight - self.config.titlebarheight))
        
        s.fill(self.background_color)

        pass