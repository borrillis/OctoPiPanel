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

import json
import os
import sys
import pygame
import pygbutton
import platform
import datetime
from pygame.locals import *
from cyrusbus import Bus

from config import OctoPiPanelConfig
from printer import Printer
from client import OctoPiClient
from views.dashboardview import DashboardView
from views.menuview import MenuView
from views.settingsview import SettingsView
from views.controlview import ControlView
from views.graphview import GraphView

class OctoPiPanel():
    """
    @var done: anything can set to True to forcequit
    @var screen: points to: pygame.display.get_surface()        
    """

    def __init__(self, config):
        """
        .
        """
        self.bus = Bus()
        self.bus.subscribe("viewchange", self.handle_viewchange)

        self.config = config
        self.octopi_client = OctoPiClient(self.config.api_baseurl, self.config.apikey)
        self.printer = Printer()

        self.done = False

        self.background_image = pygame.image.load(os.path.join(self.config.script_directory, 'assets/background.png'))
        self.menu_button_image = os.path.join(self.config.script_directory, 'assets/button-menu.png')
        self.temperature_icon = pygame.image.load(os.path.join(self.config.script_directory, 'assets/icon-temperature.png'))

        self.menu = MenuView(self.config, self.bus)

        self.views = dict()
        self.views["dashboard"] = DashboardView(self.config, self.bus, self.printer)
        self.views["graph"] = GraphView(self.config, self.bus)
        self.views["control"] = ControlView(self.config, self.bus)
        self.views["settings"] = SettingsView(self.config, self.bus)

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
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        pygame.display.set_caption(self.config.caption)

        # Set font
        self.fntText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 12)
        self.fntTextSmall = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 10)
        self.percent_txt = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 30)

        # backlight on off status and control
        self.bglight_ticks = pygame.time.get_ticks()
        self.bglight_on = True

        """
        # Home X/Y/Z buttons
        self.btnHomeXY        = pygbutton.PygButton((  5,   5, 100, self.buttonHeight), "Home X/Y")
        self.btnHomeZ         = pygbutton.PygButton((  5,  35, 100, self.buttonHeight), "Home Z")
        self.btnZUp           = pygbutton.PygButton((110,  35, 100, self.buttonHeight), "Z +25")

        # Heat buttons
        self.btnHeatBed       = pygbutton.PygButton((  5,  65, 100, self.buttonHeight), "Heat bed")
        self.btnHeatHotEnd    = pygbutton.PygButton((  5,  95, 100, self.buttonHeight), "Heat hot end")

        # Shutdown and reboot buttons
        self.btnReboot        = pygbutton.PygButton((215,   5, 100, self.buttonHeight), "Reboot")
        self.btnShutdown      = pygbutton.PygButton((215,  35, 100, self.buttonHeight), "Shutdown")
        """

        self.btnMenu      = pygbutton.PygButton((260,  0, 40, 40), normal=self.menu_button_image)

        # I couldnt seem to get at pin 252 for the backlight using the usual method, 
        # but this seems to work
        if platform.system() == 'Linux':
            os.system("echo 252 > /sys/class/gpio/export")
            os.system("echo 'out' > /sys/class/gpio/gpio252/direction")
            os.system("echo '1' > /sys/class/gpio/gpio252/value")

        # Init of class done
        print "OctoPiPanel initiated"

    def Start(self):
        # OctoPiPanel started
        print "OctoPiPanel started!"
        print "---"

        """ game loop: input, move, render"""
        while not self.done:
            # Handle events
            self.handle_events()

            # Update info from printer every other seconds
            if pygame.time.get_ticks() - self.getstate_ticks > self.config.updatetime:
                self.get_state()
                self.getstate_ticks = pygame.time.get_ticks()

            # Is it time to turn of the backlight?
            if pygame.time.get_ticks() - self.bglight_ticks > self.config.backlightofftime and platform.system() == 'Linux':
                # disable the backlight
                os.system("echo '0' > /sys/class/gpio/gpio252/value")
                self.bglight_ticks = pygame.time.get_ticks()
                self.bglight_on = False

            # Update buttons visibility, text, graphs etc
            self.update()

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

                if self.menu_open:
                    self.menu.handle_event(event)
                else:
                    self.active_view.handle_event(event)

                if 'click' in self.btnMenu.handleEvent(event):
                    self.menu_open = not self.menu_open

                """
                if 'click' in self.btnHomeXY.handleEvent(event):
                    self._home_xy()

                if 'click' in self.btnHomeZ.handleEvent(event):
                    self._home_z()

                if 'click' in self.btnZUp.handleEvent(event):
                    self._z_up()

                if 'click' in self.btnHeatBed.handleEvent(event):
                    self._heat_bed()

                if 'click' in self.btnHeatHotEnd.handleEvent(event):
                    self._heat_hotend()

                if 'click' in self.btnReboot.handleEvent(event):
                    self._reboot()

                if 'click' in self.btnShutdown.handleEvent(event):
                    self._shutdown()"""

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
    def get_state(self):
        """
        try:
            self.octopi_client.getprinterstatus()

            if req.status_code == 200:
                state = json.loads(req.text)

                # Set status flags
                self.HotEndTemp = state['temps']['tool0']['actual']
                self.BedTemp = state['temps']['bed']['actual']
                self.HotEndTempTarget = state['temps']['tool0']['target']
                self.BedTempTarget = state['temps']['bed']['target']

                if self.HotEndTempTarget == None:
                    self.HotEndTempTarget = 0.0

                if self.BedTempTarget == None:
                    self.BedTempTarget = 0.0

                if self.HotEndTempTarget > 0.0:
                    self.HotHotEnd = True
                else:
                    self.HotHotEnd = False

                if self.BedTempTarget > 0.0:
                    self.HotBed = True
                else:
                    self.HotBed = False

                #print self.apiurl_status

            # Get info about current job
            req = requests.get(self.apiurl_job + self.addkey)
            if req.status_code == 200:
                jobState = json.loads(req.text)

            req = requests.get(self.apiurl_connection + self.addkey)
            if req.status_code == 200:
                connState = json.loads(req.text)

                #print self.apiurl_job + self.addkey

                self.Completion = jobState['progress']['completion'] # In procent
                self.PrintTimeLeft = jobState['progress']['printTimeLeft']
                #self.Height = state['currentZ']
                self.FileName = jobState['job']['file']['name']
                self.JobLoaded = connState['current']['state'] == "Operational" and (jobState['job']['file']['name'] != "") or (jobState['job']['file']['name'] != None)

                # Save temperatures to lists
                self.HotEndTempList.popleft()
                self.HotEndTempList.append(self.HotEndTemp)
                self.BedTempList.popleft()
                self.BedTempList.append(self.BedTemp)

                #print self.HotEndTempList
                #print self.BedTempList

                self.Paused = connState['current']['state'] == "Paused"
                self.Printing = connState['current']['state'] == "Printing"


        except requests.exceptions.ConnectionError as e:
            print "Connection Error ({0}): {1}".format(e.errno, e.strerror)
"""
        return

    """
    Update buttons, text, graphs etc.
    """
    def update(self):
        # Set home buttons visibility
        """self.btnHomeXY.visible = not (self.printer.Printing or self.printer.Paused)
        self.btnHomeZ.visible = not (self.printer.Printing or self.printer.Paused)
        self.btnZUp.visible = not (self.printer.Printing or self.printer.Paused)

        # Set abort and pause buttons visibility
        #self.btnStartPrint.visible = not (self.printer.Printing or self.printer.Paused) and self.printer.JobLoaded
        #self.btnAbortPrint.visible = self.printer.Printing or self.printer.Paused
        #self.btnPausePrint.visible = self.printer.Printing or self.printer.Paused

        # Set texts on pause button
        #if self.printer.Paused:
            #self.btnPausePrint.caption = "Resume"
        #else:
            #self.btnPausePrint.caption = "Pause"

        # Set abort and pause buttons visibility
        self.btnHeatHotEnd.visible = not (self.printer.Printing or self.printer.Paused)
        self.btnHeatBed.visible = not (self.printer.Printing or self.printer.Paused)

        # Set texts on heat buttons
        if self.printer.HotHotEnd:
            self.btnHeatHotEnd.caption = "Turn off hot end"
        else:
            self.btnHeatHotEnd.caption = "Heat hot end"

        if self.printer.HotBed:
            self.btnHeatBed.caption = "Turn off bed"
        else:
            self.btnHeatBed.caption = "Heat bed"
        """

        return

    def draw(self):
        #clear whole screen
        self.screen.blit(self.background_image, (0, 0))

        # render print progress background shade
        s = pygame.Surface((320*self.printer.Completion/100, 240), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))

        # Render current view
        if self.menu_open:
            self.menu.draw(self.screen)
        else:
            self.active_view.draw(self.screen)

        # Render menu button
        self.btnMenu.draw(self.screen)

        # Draw status bar
        self.screen.blit(self.temperature_icon, (0, 200))
        hot_end_label = self.fntText.render(u'Hot end: {0}\N{DEGREE SIGN}C ({1}\N{DEGREE SIGN}C)'.format(self.printer.HotEndTemp, self.printer.HotEndTempTarget), 1, (255, 255, 255))
        self.screen.blit(hot_end_label, (40, 205))
        bed_temp_label = self.fntText.render(u'Bed: {0}\N{DEGREE SIGN}C ({1}\N{DEGREE SIGN}C)'.format(self.printer.BedTemp, self.printer.BedTempTarget), 1, (255, 255, 255))
        self.screen.blit(bed_temp_label, (40, 220))

        completion_label = self.percent_txt.render("{0:.1f}%".format(self.printer.Completion), 1, (255, 255, 255))
        self.screen.blit(completion_label, (310 - (completion_label.get_width()), 205))

        # update screen
        pygame.display.update()

    def handle_viewchange(self, eventkey, view_name):
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
    opp.Start()
