#!/usr/bin/env python

"""
OctoPiPanel v0.1

OctoPiPanel creates a simple interface on a small screen to control OctoPrint
OctoPiPanel requires Pygame to be installed. Pygame can be downloaded from http://pygame.org
OctoPiPanel is developed by Jonas Lorander (jonas@haksberg.net)
https://github.com/jonaslorander/OctoPiPanel


Simplified BSD-2 License:

Copyright 2014 Jonas Lorander.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Al Sweigart ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Al Sweigart OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Jonas Lorander.
"""
__author__ = "Jonas Lorander"
__license__ = "Simplified BSD 2-Clause License"

import os
import pygame
import pygbutton
import platform
import time
from threading import Thread

from config import OctoPiPanelConfig
from printer import Printer
from client import OctoPiClient

from views.dashboardview import DashboardView
from views.menuview import MenuView
from views.settingsview import SettingsView
from views.controlview import ControlView
from views.graphview import GraphView
from views.loadfileview import LoadfileView
from views.consoleview import ConsoleView

class OctoPiPanel():
    """
    @var done: anything can set to True to forcequit
    @var screen: points to: pygame.display.get_surface()        
    """

    def __init__(self, config):
        """
        .
        """
        self.color_bg = pygame.Color(41, 61, 70)
        
        self.config = config
        self.octopi_client = OctoPiClient(self.config.api_baseurl, self.config.apikey)
        self.printer = Printer()

        self.done = False

        self.background_image = pygame.transform.smoothscale(pygame.image.load(os.path.join(self.config.script_directory, 'assets/background.png')), (self.config.width, self.config.height - self.config.statusbarheight))
        self.menu_button_image = os.path.join(self.config.script_directory, 'assets/button-menu.png')
        self.temperature_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-temperature.png'))

        self.menu = MenuView(self.handle_viewchange, self.config)

        self.views = dict()
        self.views["dashboard"] = DashboardView(self.config, self.octopi_client, self.printer)
        self.views["graph"] = GraphView(self.config, self.printer)
        self.views["control"] = ControlView(self.config, self.octopi_client)
        self.views["settings"] = SettingsView(self.config)
        self.views["console"] = ConsoleView(self.config)
        self.views["loadfile"] = LoadfileView(self.config, self.octopi_client)

        self.firstframe = True

        self.active_view = self.views["dashboard"]

        self.menu_open = False

        # Status flags
        self.getstate_ticks = pygame.time.get_ticks()

        if platform.system() == 'Linux':
            # Init framebuffer/touchscreen environment variables
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.putenv('SDL_FBDEV'      , '/dev/fb1')
            os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
            os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

        # init pygame and set up screen
        pygame.init()
        # Display the mouse on Windows or MacOS
        if self.config.fullscreen and self.config.showmouse == False:
            print "[OCTOPIPANEL]: Grabbing event input"
            pygame.mouse.set_visible(self.config.showmouse)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(self.config.showmouse)
            pygame.event.set_grab(False)

        display_info = pygame.display.Info()
        if self.config.fullscreen:
            pygame.display.set_mode((display_info.current_w, display_info.current_h), self.config.window_flags)
            self.screen = pygame.Surface((self.config.width, self.config.height), self.config.window_flags)
        else:
            self.screen = pygame.display.set_mode((self.config.width, self.config.height), self.config.window_flags)
        pygame.display.set_caption(self.config.caption)


        # Set font
        self.fntRegText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 24)
        self.fntText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 12)
        self.fntTextSmall = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 10)
        self.percent_txt = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 30)

        # backlight on off status and control
        self.bglight_ticks = pygame.time.get_ticks()
        self.bglight_on = True

        self.clock = pygame.time.Clock()

        #self.btnMenu = pygbutton.PygButton((self.config.width-60,  0, 60, self.config.titlebarheight), "<MENU>" ) # normal=self.menu_button_image)
        self.btnMenu = pygbutton.PygButton((self.config.width-60,  0, 60, self.config.titlebarheight), normal=self.menu_button_image)

        # I couldnt seem to get at pin 252 for the backlight using the usual method, 
        # but this seems to work
        if platform.system() == 'Linux':
            os.system("echo 252 > /sys/class/gpio/export")
            os.system("echo 'out' > /sys/class/gpio/gpio252/direction")
            os.system("echo '1' > /sys/class/gpio/gpio252/value")

        # Init of class done
        print "OctoPiPanel initiated"

    def start(self):
        # OctoPiPanel started
        print "OctoPiPanel started!"
        print "---"

        self.thread = Thread(target=self.state_thread)
        self.thread.start()

        """ game loop: input, move, render"""
        while not self.done:
            # Handle events
            self.handle_events()

            # Is it time to turn of the backlight?
            if pygame.time.get_ticks() - self.bglight_ticks > self.config.backlightofftime and platform.system() == 'Linux':
                # disable the backlight
                os.system("echo '0' > /sys/class/gpio/gpio252/value")
                self.bglight_ticks = pygame.time.get_ticks()
                self.bglight_on = False

            # Draw everything
            self.draw()

        """ Clean up """
        # enable the backlight before quiting
        if platform.system() == 'Linux':
            os.system("echo '1' > /sys/class/gpio/gpio252/value")

        # OctoPiPanel is going down.
        print "OctoPiPanel is going down."

        """ Quit """
        pygame.quit()

    def handle_events(self):
        """handle all events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print "quit"
                self.done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print "Got escape key"
                    self.done = True

            # It should only be possible to click a button if you can see it
            #  e.g. the backlight is on
            if self.bglight_on:
                if self.config.fullscreen and ( event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN)) :
                    display_info = pygame.display.Info()			
                    if self.config.width != display_info.current_w and self.config.height != display_info.current_h :
                        scale_w = (float(self.config.width) / display_info.current_w)
                        scale_h = (float(self.config.height) / display_info.current_h)
                        scaled_pos = (int(event.pos[0] * scale_w), int(event.pos[1] * scale_h))                        
                        event.pos = scaled_pos
                            
                if self.menu_open:
                    self.menu.handle_event(event)
                else:
                    self.active_view.handle_event(event)

                if 'click' in self.btnMenu.handleEvent(event):
                    self.menu_open = not self.menu_open

            # Did the user click on the screen?
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Reset backlight counter
                self.bglight_ticks = pygame.time.get_ticks()

                if self.bglight_on == False and platform.system() == 'Linux':
                    # enable the backlight
                    os.system("echo '1' > /sys/class/gpio/gpio252/value")
                    self.bglight_on = True
                    print "Background light on."

    """
    Get status update from API, regarding temp etc.
    """
    def state_thread(self):
        while not self.done:
            self.octopi_client.get_printer_status(self.printer)
            self.octopi_client.get_job_status(self.printer)
            self.octopi_client.get_connection_status(self.printer)

            time.sleep(self.config.updatetime / 1000.0)

    def draw(self):
        self.clock.tick(30)

        #clear whole screen
        self.screen.fill(self.color_bg)
        self.screen.blit(self.background_image, (0, 0, self.config.width, self.config.height - self.config.statusbarheight))

        # render print progress background shade
        s = pygame.Surface((self.config.width*self.printer.Completion/100, self.config.statusbarheight), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, self.config.height - self.config.statusbarheight))

        # Render current view
        if self.menu_open:
            self.menu.draw(self.screen,self.firstframe)
            self.firstframe = True
        else:
            self.active_view.draw(self.screen, self.firstframe)
            if self.firstframe:
                self.firstframe = False

        # Render menu button
        self.btnMenu.draw(self.screen)

        # Draw status bar
        self.screen.blit(self.temperature_icon, (0, self.config.height-self.config.statusbarheight))
        hot_end_label = self.fntText.render(u'Hot end: {0}\N{DEGREE SIGN}C ({1}\N{DEGREE SIGN}C)'.format(self.printer.HotEndTemp, self.printer.HotEndTempTarget), 1, (255, 255, 255))
        self.screen.blit(hot_end_label, (40, self.config.height-self.config.statusbarheight + 5))
        bed_temp_label = self.fntText.render(u'Bed: {0}\N{DEGREE SIGN}C ({1}\N{DEGREE SIGN}C)'.format(self.printer.BedTemp, self.printer.BedTempTarget), 1, (255, 255, 255))
        self.screen.blit(bed_temp_label, (40, self.config.height-self.config.statusbarheight + 20))

        file_name_lbl = self.fntRegText.render(self.printer.FileName, 1, (255, 255, 255))
        xpos = (self.config.width - file_name_lbl.get_width()) / 2
        ypos = (self.config.statusbarheight - file_name_lbl.get_height()) / 2
        self.screen.blit(file_name_lbl, (xpos, self.config.height - self.config.statusbarheight + ypos ))

        completion_label = self.percent_txt.render("{0:.1f}%".format(self.printer.Completion), 1, (255, 255, 255))
        self.screen.blit(completion_label, (self.config.width-10- (completion_label.get_width()), self.config.height- self.config.statusbarheight + 5))

        # update screen
        if self.config.fullscreen:
            pygame.display.get_surface().blit(
                pygame.transform.smoothscale(self.screen,(pygame.display.Info().current_w, pygame.display.Info().current_h)), (0,0))
        pygame.display.update()

    def handle_viewchange(self, view_name):
        if view_name in self.views:
            self.active_view = self.views[view_name]
            self.menu_open = False


    # Reboot system
    def _reboot(self):
        if platform.system() == 'Linux':
            os.system("reboot")
        else:
            pygame.image.save(self.screen, "screenshot.jpg")

        self.done = True
        print "reboot"

        return

    # Shutdown system
    def _shutdown(self):
        if platform.system() == 'Linux':
            os.system("shutdown -h 0")

        self.done = True
        print "shutdown"

        return

if __name__ == '__main__':
    config = OctoPiPanelConfig.load_from_file()

    opp = OctoPiPanel(config)
    opp.start()
