import os
import pygame
import pygame.color
from views.panelview import PanelView


class MenuView(PanelView):
    def __init__(self, viewchange, config):
        PanelView.__init__(self, config, "Menu")
        self.viewchange = viewchange # function to call when the view changes
        self.fntRegText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 16)
        dashboard_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-dashboard.png'))
        graph_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-graph.png'))
        control_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-control.png'))
        setting_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-setting.png'))

        self.menu_items = [{"text": "Dashboard", "icon": dashboard_icon, "name": "dashboard"},
                           {"text": "Temperature Graph", "icon": graph_icon, "name": "graph"},
                           {"text": "Control", "icon": control_icon, "name": "control"},
                           {"text": "Load file", "icon": setting_icon, "name": "loadfile"},
                           {"text": "Settings", "icon": setting_icon, "name": "settings"},
                           {"text": "Console", "icon": setting_icon, "name": "console"},]
        self.items_per_page = 6
        self.page = 0

        self.background_color = pygame.color.Color("#EF3220")
        self.divider_color = pygame.color.Color("#CC302B")

    def handle_event(self, event):
        PanelView.handle_event(self, event)

        if event.type == pygame.MOUSEBUTTONUP:
            if 40 <= event.pos[1] < 40 * (self.items_per_page + 1) :
                item_pos = ((event.pos[1] - 40) / 40) + (self.page * self.items_per_page)
                if len(self.menu_items) > item_pos:
                    self.viewchange(self.menu_items[item_pos]["name"])

    def draw(self, screen, firstframe):
        PanelView.draw(self, screen, firstframe)

        s = pygame.Surface((self.config.width, self.config.height-self.config.statusbarheight-self.config.titlebarheight))
        s.fill(self.background_color)
        screen.blit(s, (0, self.config.titlebarheight))

        pygame.draw.line(screen, self.divider_color, (0, 40), (self.config.width, 40))

        for index, item in enumerate(self.menu_items[self.page * self.items_per_page: self.page + 1 * self.items_per_page]):
            file_name_lbl = self.fntRegText.render(item["text"], 1, (255, 255, 255))

            ypos = 40 + (index * 40)
            screen.blit(file_name_lbl, (40, ypos + 12))
            pygame.draw.line(screen, self.divider_color, (0, ypos + 40), (self.config.width, ypos + 40))

            screen.blit(item["icon"], (0, ypos))