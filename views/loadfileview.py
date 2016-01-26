import os
import pygame
import pygbutton
from datetime import datetime
from views.panelview import PanelView



class LoadfileView(PanelView):

    def __init__(self, config,  client):
        PanelView.__init__(self, config, "Files")
        self.config = config
        self.client = client
        self.maxlines = (config.height - config.statusbarheight - config.titlebarheight) / 40
        self.background_color = pygame.color.Color("#EF3220")
        self.background_color = pygame.Color(41, 61, 70)
        
        self.divider_color = pygame.color.Color("#CC302B")
        self.fntRegText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 16)
        
        
    def handle_event(self, event):
        PanelView.handle_event(self, event)

        if event.type == pygame.MOUSEBUTTONUP:
            if self.config.titlebarheight <= event.pos[1] < (self.config.height - self.config.statusbarheight):
                item_pos = ((event.pos[1] - 40) / 40)
                if len(self.files) > item_pos:
                    print (self.files[item_pos])

    def draw(self, screen, firstframe):
        PanelView.draw(self, screen, firstframe)
        if firstframe:
            self.files = self.client.get_files()
        s = pygame.Surface((self.config.width, self.config.height-self.config.statusbarheight-self.config.titlebarheight))
        
        s.fill(self.background_color)
        
        screen.blit(s, (0, self.config.titlebarheight))

        pygame.draw.line(screen, self.divider_color, (0, 40), (self.config.width, 40))
        index = 0
        for f in self.files:
        #   index, item in enumerate(self.menu_items[self.page * self.items_per_page: self.page + 1 * self.items_per_page]):
            dt = datetime.fromtimestamp(f['date'])
            size = f['size'] / 1000000.0
            shortname = f['name']
            if shortname[-6:] == ".gcode":
                shortname = shortname[:-6]
            rt = shortname + "  " + str(size) + "  " + str(dt)
            file_name_lbl = self.fntRegText.render(rt, 1, (255, 255, 255))

            ypos = 40 + (index * 40)
            screen.blit(file_name_lbl, (10, ypos + 12))
            pygame.draw.line(screen, self.divider_color, (0, ypos + 40), (self.config.width, ypos + 40))

            index += 1


