import os
import pygame
import pygame.color
from views.panelview import PanelView


class MenuView(PanelView):
    def __init__(self, config, bus):
        PanelView.__init__(self, config, bus)

        self.fntRegText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 16)
        dashboard_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-dashboard.png'))
        graph_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-graph.png'))
        control_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-control.png'))
        setting_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-setting.png'))

        self.menu_items = [{"text": "Dashboard", "icon": dashboard_icon, "name": "dashboard"},
                           {"text": "Temperature Graph", "icon": graph_icon, "name": "graph"},
                           {"text": "Control", "icon": control_icon, "name": "control"},
                           {"text": "Settings", "icon": setting_icon, "name": "settings"}]
        self.items_per_page = 4
        self.page = 0

        self.background_color = pygame.color.Color("#EF3220")
        self.divider_color = pygame.color.Color("#CC302B")

    def handle_event(self, event):
        PanelView.handle_event(self, event)

        if event.type == pygame.MOUSEBUTTONUP:
            if 40 <= event.pos[1] < 200:
                item_pos = ((event.pos[1] - 40) / 40) + (self.page * self.items_per_page)
                if len(self.menu_items) > item_pos:
                    self.bus.publish("viewchange", self.menu_items[item_pos]["name"])

    def draw(self, screen):
        PanelView.draw(self, screen)

        s = pygame.Surface((320, 200))
        s.fill(self.background_color)
        screen.blit(s, (0, 0))

        pygame.draw.line(screen, self.divider_color, (0, 40), (320, 40))

        for index, item in enumerate(self.menu_items[self.page * self.items_per_page: self.page + 1 * self.items_per_page]):
            file_name_lbl = self.fntRegText.render(item["text"], 1, (255, 255, 255))

            ypos = 40 + (index * 40)
            screen.blit(file_name_lbl, (40, ypos + 12))
            pygame.draw.line(screen, self.divider_color, (0, ypos + 40), (320, ypos + 40))

            screen.blit(item["icon"], (0, ypos))