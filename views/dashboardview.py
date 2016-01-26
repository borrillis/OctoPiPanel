import os
import datetime
import pygame
import pygbutton
from views.panelview import PanelView


class DashboardView(PanelView):
    def __init__(self, config, octopi_client, printer):
        PanelView.__init__(self, config, "Dashboard")

        self.printer = printer
        self.octopi_client = octopi_client

        self.fntText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 60)
        self.fntRegText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 12)

        # Start, stop and pause buttons
        self.start_button_image = os.path.join(self.config.script_directory, 'assets/button-start.png')
        self.pause_button_image = os.path.join(self.config.script_directory, 'assets/button-pause.png')
        self.stop_button_image = os.path.join(self.config.script_directory, 'assets/button-stop.png')
        spacing = self.config.width / 4
        self.btn_start_print = pygbutton.PygButton((spacing-30, 130, 60, 60), normal=self.start_button_image)
        self.btn_pause_print = pygbutton.PygButton((spacing * 2-30, 130, 60, 60), normal=self.pause_button_image)
        self.btn_abort_print = pygbutton.PygButton((spacing * 3-30, 130, 60, 60), normal=self.stop_button_image)

    def draw(self, screen, firstframe):
        PanelView.draw(self, screen, firstframe)

        time_remaining_lbl = self.fntText.render(str(datetime.timedelta(seconds=self.printer.PrintTimeLeft)), 1, (255, 255, 255))
        pos = (self.config.width - time_remaining_lbl.get_width()) / 2
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

