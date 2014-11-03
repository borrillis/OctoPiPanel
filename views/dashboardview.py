import os
import datetime
import pygame
import pygbutton
from views.panelview import PanelView


class DashboardView(PanelView):
    def __init__(self, config, bus, octopi_client, printer):
        PanelView.__init__(self, config, bus)

        self.printer = printer
        self.octopi_client = octopi_client

        self.fntText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 60)
        self.fntRegText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 12)

        # Start, stop and pause buttons
        self.start_button_image = os.path.join(self.config.script_directory, 'assets/button-start.png')
        self.pause_button_image = os.path.join(self.config.script_directory, 'assets/button-pause.png')
        self.stop_button_image = os.path.join(self.config.script_directory, 'assets/button-stop.png')
        self.btn_start_print = pygbutton.PygButton((35, 130, 60, 60), normal=self.start_button_image)
        self.btn_pause_print = pygbutton.PygButton((130, 130, 60, 60), normal=self.pause_button_image)
        self.btn_abort_print = pygbutton.PygButton((225, 130, 60, 60), normal=self.stop_button_image)

    def draw(self, screen):
        PanelView.draw(self, screen)

        time_remaining_lbl = self.fntText.render(str(datetime.timedelta(seconds=self.printer.PrintTimeLeft)), 1, (255, 255, 255))
        pos = (320 - time_remaining_lbl.get_width()) / 2
        screen.blit(time_remaining_lbl, (pos, 40))

        file_name_lbl = self.fntRegText.render(self.printer.FileName, 1, (255, 255, 255))
        screen.blit(file_name_lbl, (pos, 100))

        self.btn_start_print.draw(screen)
        self.btn_pause_print.draw(screen)
        self.btn_abort_print.draw(screen)
        pass

    def handle_event(self, event):
        PanelView.handle_event(self, event)

        if 'click' in self.btn_start_print.handleEvent(event):
            self.octopi_client.start_print()

        if 'click' in self.btn_pause_print.handleEvent(event):
            self.octopi_client.abort_print()

        if 'click' in self.btn_abort_print.handleEvent(event):
            self.octopi_client.pause_print()

