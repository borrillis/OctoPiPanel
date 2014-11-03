import os
import pygame
from views.panelview import PanelView


class GraphView(PanelView):
    def __init__(self, config, bus, printer):
        PanelView.__init__(self, config, bus)

        self.printer = printer

        self.graph_area_left = 30
        self.graph_area_top = 40
        self.graph_area_width = 285
        self.graph_area_height = 160

        self.fntTextSmall = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 10)

    def draw(self, screen):
        # Temperature Graphing
        # Graph area
        pygame.draw.rect(screen, (255, 255, 255),
                         (self.graph_area_left, self.graph_area_top, self.graph_area_width, self.graph_area_height))

        # Graph axes
        # X, temp
        pygame.draw.line(screen, pygame.Color("white"), [self.graph_area_left, self.graph_area_top],
                         [self.graph_area_left, self.graph_area_top + self.graph_area_height], 2)

        # X-axis divisions
        pygame.draw.line(screen, pygame.Color("white"),
                         [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 5],
                         [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 5], 2)  # 0
        pygame.draw.line(screen, pygame.Color("white"),
                         [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 4],
                         [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 4], 2)  # 50
        pygame.draw.line(screen, pygame.Color("white"),
                         [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 3],
                         [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 3], 2)  # 100
        pygame.draw.line(screen, pygame.Color("white"),
                         [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 2],
                         [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 2], 2)  # 150
        pygame.draw.line(screen, pygame.Color("white"),
                         [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 1],
                         [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 1], 2)  # 200
        pygame.draw.line(screen, pygame.Color("white"),
                         [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 0],
                         [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 0], 2)  # 250

        # X-axis scale
        lbl0 = self.fntTextSmall.render("0", 1, pygame.Color("white"))
        screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 5))
        lbl0 = self.fntTextSmall.render("50", 1, pygame.Color("white"))
        screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 4))
        lbl0 = self.fntTextSmall.render("100", 1, pygame.Color("white"))
        screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 3))
        lbl0 = self.fntTextSmall.render("150", 1, pygame.Color("white"))
        screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 2))
        lbl0 = self.fntTextSmall.render("200", 1, pygame.Color("white"))
        screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 1))
        lbl0 = self.fntTextSmall.render("250", 1, pygame.Color("white"))
        screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 0))

        # X-axis divisions, grey lines
        pygame.draw.line(screen, (200, 200, 200),
                         [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 4],
                         [self.graph_area_left + self.graph_area_width - 2,
                          self.graph_area_top + (self.graph_area_height / 5) * 4], 1)  # 50
        pygame.draw.line(screen, (200, 200, 200),
                         [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 3],
                         [self.graph_area_left + self.graph_area_width - 2,
                          self.graph_area_top + (self.graph_area_height / 5) * 3], 1)  # 100
        pygame.draw.line(screen, (200, 200, 200),
                         [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 2],
                         [self.graph_area_left + self.graph_area_width - 2,
                          self.graph_area_top + (self.graph_area_height / 5) * 2], 1)  # 150
        pygame.draw.line(screen, (200, 200, 200),
                         [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 1],
                         [self.graph_area_left + self.graph_area_width - 2,
                          self.graph_area_top + (self.graph_area_height / 5) * 1], 1)  # 200

        # Y, time, 2 seconds per pixel
        pygame.draw.line(screen, (0, 0, 0), [self.graph_area_left, self.graph_area_top + self.graph_area_height],
                         [self.graph_area_left + self.graph_area_width, self.graph_area_top + self.graph_area_height],
                         2)

        # Scaling factor
        g_scale = self.graph_area_height / 250.0

        # Print temperatures for hot end
        i = 0
        for t in self.printer.HotEndTempList:
            x = self.graph_area_left + i
            y = self.graph_area_top + self.graph_area_height - int(t * g_scale)
            pygame.draw.line(screen, (220, 0, 0), [x, y], [x + 1, y], 2)
            i += 1

        # Print temperatures for bed
        i = 0
        for t in self.printer.BedTempList:
            x = self.graph_area_left + i
            y = self.graph_area_top + self.graph_area_height - int(t * g_scale)
            pygame.draw.line(screen, (0, 0, 220), [x, y], [x + 1, y], 2)
            i += 1

        # Draw target temperatures
        # Hot end
        pygame.draw.line(screen, (180, 40, 40), [self.graph_area_left,
                                                      self.graph_area_top + self.graph_area_height - (
                                                      self.printer.HotEndTempTarget * g_scale)],
                         [self.graph_area_left + self.graph_area_width,
                          self.graph_area_top + self.graph_area_height - (self.printer.HotEndTempTarget * g_scale)], 1)
        # Bed
        pygame.draw.line(screen, (40, 40, 180), [self.graph_area_left,
                                                      self.graph_area_top + self.graph_area_height - (
                                                      self.printer.BedTempTarget * g_scale)],
                         [self.graph_area_left + self.graph_area_width,
                          self.graph_area_top + self.graph_area_height - (self.printer.BedTempTarget * g_scale)], 1)

