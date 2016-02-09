#!/usr/bin/env python

__author__ = "Jonas Lorander"
__license__ = "Simplified BSD 2-Clause License"

import json
import os
import platform
import subprocess
from collections import deque
from ConfigParser import RawConfigParser
import datetime

import pygame
import requests

import pygbutton


class OctoPiPanel:

    # Read settings from OctoPiPanel.cfg settings file
    cfg = RawConfigParser()
    scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    settingsFilePath = os.path.join(scriptDirectory, "OctoPiPanel.cfg")
    cfg.readfp(open(settingsFilePath,"r"))

    api_baseurl = cfg.get('settings', 'baseurl')
    apikey = cfg.get('settings', 'apikey')
    updatetime = cfg.getint('settings', 'updatetime')

    if cfg.has_option('settings', 'window_width'):
        win_width = cfg.getint('settings', 'window_width')
    else:
        win_width = 320

    if cfg.has_option('settings', 'window_height'):
        win_height = cfg.getint('settings', 'window_height')
    else:
        win_height = 240

    if cfg.has_option('settings', 'enable_graph'):
        enable_graph = cfg.getboolean('settings', 'enable_graph')
    else:
        enable_graph = True

    if cfg.has_option('settings', 'hotend_temp'):
        hotend_temp = cfg.getint('settings', 'hotend_temp')
    else:
        hotend_temp = 190

    if cfg.has_option('settings', 'hotbed_temp'):
        hotbed_temp = cfg.getint('settings', 'hotbed_temp')
    else:
        hotbed_temp = 50

    if cfg.has_option('settings', 'z_up_value'):
        z_up_value = cfg.getint('settings', 'z_up_value')
    else:
        z_up_value = 25

    addkey = '?apikey={0}'.format(apikey)
    apiurl_printhead = '{0}/api/printer/printhead'.format(api_baseurl)
    apiurl_tool = '{0}/api/printer/tool'.format(api_baseurl)
    apiurl_bed = '{0}/api/printer/bed'.format(api_baseurl)
    apiurl_command = '{0}/api/printer/command'.format(api_baseurl)
    apiurl_job = '{0}/api/job'.format(api_baseurl)
    apiurl_status = '{0}/api/printer?apikey={1}'.format(api_baseurl, apikey)
    apiurl_connection = '{0}/api/connection'.format(api_baseurl)

    # print apiurl_job + addkey

    graph_area_left   = 30 # 6
    graph_area_top    = (win_height / 3) * 2
    graph_area_width  = win_width - graph_area_left - 5
    graph_area_height = win_height - graph_area_top - 5

    def __init__(self, caption="OctoPiPanel"):
        """
        .
        """
        self.done = False
        self.color_bg = pygame.Color(41, 61, 70)

        # Button settings
        self.leftPadding = 5
        self.buttonSpace = 10 if (self.win_width > 320) else 5
        self.buttonWidth = (self.win_width - self.leftPadding * 2 - self.buttonSpace * 2) / 3
        all_buttons_space = self.win_height - 5 if not self.enable_graph else ((self.win_height - 5) / 3) * 2
        self.buttonHeight = all_buttons_space / 4 - 5

        # Status flags
        self.connected = False
        self.hotend_temp = 0.0
        self.bed_temp = 0.0
        self.hotend_temp_target = 0.0
        self.bed_temp_target = 0.0
        self.HotHotEnd = False
        self.HotBed = False
        self.Paused = False
        self.Printing = False
        self.JobLoaded = False
        self.FanSpinning = False
        self.Completion = 0 # In procent
        self.PrintTimeLeft = 0
        self.Height = 0.0
        self.FileName = "Nothing"
        self.getstate_ticks = pygame.time.get_ticks()

        # Lists for temperature data
        self.HotEndTempList = deque([0] * self.graph_area_width)
        self.BedTempList = deque([0] * self.graph_area_width)

        if platform.system() == 'Linux':
            if subprocess.Popen(["pidof", "X"], stdout=subprocess.PIPE).communicate()[0].strip() == "":
                # Init framebuffer/touchscreen environment variables
                os.putenv('SDL_VIDEODRIVER', 'fbcon')
                os.putenv('SDL_FBDEV', '/dev/fb1')
                os.putenv('SDL_MOUSEDRV', 'TSLIB')
                os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

        # init pygame and set up screen
        pygame.init()
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        self.screen = pygame.display.set_mode( (self.win_width, self.win_height) )
        # modes = pygame.display.list_modes(16)
        # self.screen = pygame.display.set_mode(modes[0], FULLSCREEN, 16)
        pygame.display.set_caption( caption )

        # Set font
        font_size = 14 if self.enable_graph else 16
        self.fntText = pygame.font.Font(os.path.join(self.scriptDirectory, "DejaVuSans.ttf"), font_size)
        self.fntText.set_bold(True)
        self.fntTextSmall = pygame.font.Font(os.path.join(self.scriptDirectory, "DejaVuSans.ttf"), 10)
        self.fntTextSmall.set_bold(True)

        # Home X/Y, start/abort print & reboot buttons
        btn_gap = 5
        self.btnHomeXY        = pygbutton.PygButton((self.leftPadding, btn_gap, self.buttonWidth, self.buttonHeight), "Home X/Y")
        self.btnStartPrint    = pygbutton.PygButton((self.leftPadding + self.buttonWidth + self.buttonSpace, btn_gap, self.buttonWidth, self.buttonHeight), "Start print")
        self.btnAbortPrint    = pygbutton.PygButton((self.leftPadding + self.buttonWidth + self.buttonSpace, btn_gap, self.buttonWidth, self.buttonHeight), "Abort print", (200, 0, 0))
        self.btnConnect        = pygbutton.PygButton((self.leftPadding + self.buttonWidth * 2 + self.buttonSpace * 2, btn_gap, self.buttonWidth, self.buttonHeight), "Connect")

        # Home Z, Z up/pause & Shutdown buttons
        btn_gap += 5
        self.btnHomeZ         = pygbutton.PygButton((self.leftPadding, self.buttonHeight + btn_gap, self.buttonWidth, self.buttonHeight), "Home Z")
        self.btnZUp           = pygbutton.PygButton((self.leftPadding + self.buttonWidth + self.buttonSpace, self.buttonHeight + btn_gap, self.buttonWidth, self.buttonHeight), "Z +" + str(self.z_up_value))
        self.btnPausePrint    = pygbutton.PygButton((self.leftPadding + self.buttonWidth + self.buttonSpace,  self.buttonHeight + btn_gap, self.buttonWidth, self.buttonHeight), "Pause print")
        self.btnReboot      = pygbutton.PygButton((self.leftPadding + self.buttonWidth * 2 + self.buttonSpace * 2, self.buttonHeight + btn_gap, self.buttonWidth, self.buttonHeight), "Reboot");

        # Heat buttons
        btn_gap += 5
        self.btnHeatBed       = pygbutton.PygButton((self.leftPadding, self.buttonHeight * 2 + btn_gap, self.buttonWidth, self.buttonHeight), "Heat bed")
        self.btnFan           = pygbutton.PygButton((self.leftPadding + self.buttonWidth * 2 + self.buttonSpace * 2, self.buttonHeight * 2 + btn_gap, self.buttonWidth, self.buttonHeight), "Turn fan on")

        btn_gap += 5
        self.btnHeatHotEnd    = pygbutton.PygButton((self.leftPadding,  self.buttonHeight * 3 + btn_gap, self.buttonWidth, self.buttonHeight), "Heat hot end")

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
            if pygame.time.get_ticks() - self.getstate_ticks > self.updatetime:
                self.get_state()
                self.getstate_ticks = pygame.time.get_ticks()

            # Update buttons visibility, text, graphs etc
            self.update()

            # Draw everything
            self.draw()
            
        # OctoPiPanel is going down.
        print "OctoPiPanel is going down."

        """ Quit """
        pygame.quit()
       
    def handle_events(self):
        """handle all events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print "Quit"
                self.done = True

            # It should only be possible to click a button if you can see it
            #  e.g. the backlight is on
            if self.connected:
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

                if 'click' in self.btnStartPrint.handleEvent(event):
                    self._start_print()

                if 'click' in self.btnAbortPrint.handleEvent(event):
                    self._abort_print()

                if 'click' in self.btnPausePrint.handleEvent(event):
                    self._pause_print()

                if 'click' in self.btnReboot.handleEvent(event):
                    self._reboot()

                if 'click' in self.btnFan.handleEvent(event):
                    self._fan()

            if 'click' in self.btnConnect.handleEvent(event):
                self._connect()

    """
    Get status update from API, regarding temp etc.
    """
    def get_state(self):
        if self.connected:
            try:
                req = requests.get(self.apiurl_status)

                if req.status_code == 200:
                    state = json.loads(req.text)

                    # Set status flags
                    temp_key = 'temps' if 'temps' in state else 'temperature'
                    self.hotend_temp = state[temp_key]['tool0']['actual']
                    self.bed_temp = state[temp_key]['bed']['actual']
                    self.hotend_temp_target = state[temp_key]['tool0']['target']
                    self.bed_temp_target = state[temp_key]['bed']['target']

                    if self.hotend_temp_target is None:
                        self.hotend_temp_target = 0.0

                    if self.bed_temp_target is None:
                        self.bed_temp_target = 0.0

                    if self.hotend_temp_target > 0.0:
                        self.HotHotEnd = True
                    else:
                        self.HotHotEnd = False

                    if self.bed_temp_target > 0.0:
                        self.HotBed = True
                    else:
                        self.HotBed = False

                        # print self.apiurl_status
                elif req.status_code == 401:
                    print "Error: {0}".format(req.text)

                # Get info about current job
                req = requests.get(self.apiurl_job + self.addkey)
                job_state = None
                if req.status_code == 200:
                    job_state = json.loads(req.text)

                req = requests.get(self.apiurl_connection + self.addkey)
                if req.status_code == 200:
                    conn_state = json.loads(req.text)

                    # print self.apiurl_job + self.addkey

                    self.Completion = job_state['progress']['completion']  # In procent
                    self.PrintTimeLeft = job_state['progress']['printTimeLeft']
                    # self.Height = state['currentZ']
                    self.FileName = job_state['job']['file']['name']
                    self.JobLoaded = conn_state['current']['state'] == "Operational" and (job_state['job']['file']['name'] != "") or (job_state['job']['file']['name'] is not None)

                    # Save temperatures to lists
                    if self.enable_graph:
                        self.HotEndTempList.popleft()
                        self.HotEndTempList.append(self.hotend_temp)
                        self.BedTempList.popleft()
                        self.BedTempList.append(self.bed_temp)

                    self.Paused = conn_state['current']['state'] == "Paused"
                    self.Printing = conn_state['current']['state'] == "Printing"

            except requests.exceptions.ConnectionError as e:
                print "Connection Error ({0}): {1}".format(e.errno, e.strerror)

            return
        else:
            print "Not connected!"

    """
    Update buttons, text, graphs etc.
    """
    def update(self):
        # Set home buttons visibility
        self.btnHomeXY.visible = not (self.Printing or self.Paused)
        self.btnHomeZ.visible = not (self.Printing or self.Paused)
        self.btnZUp.visible = not (self.Printing or self.Paused)

        # Set abort and pause buttons visibility
        self.btnStartPrint.visible = not (self.Printing or self.Paused) and self.JobLoaded
        self.btnAbortPrint.visible = self.Printing or self.Paused
        self.btnPausePrint.visible = self.Printing or self.Paused

        # Set texts on pause button
        if self.Paused:
            self.btnPausePrint.caption = "Resume"
        else:
            self.btnPausePrint.caption = "Pause"
        
        # Set abort, pause, reboot and shutdown buttons visibility
        self.btnHeatHotEnd.visible = not (self.Printing or self.Paused)
        self.btnHeatBed.visible = not (self.Printing or self.Paused)
        self.btnConnect.visible = not (self.Printing or self.Paused)
        self.btnReboot.visible = not (self.Printing or self.Paused)
        self.btnFan.visible = not (self.Printing or self.Paused)

        # Set texts on heat buttons
        if self.HotHotEnd:
            self.btnHeatHotEnd.caption = "Turn off hot end"
        else:
            self.btnHeatHotEnd.caption = "Heat hot end"
        
        if self.HotBed:
            self.btnHeatBed.caption = "Turn off bed"
        else:
            self.btnHeatBed.caption = "Heat bed"

        if self.FanSpinning:
            self.btnFan.caption = "Turn fan off"
        else:
            self.btnFan.caption = "Turn fan on"

        if self.connected:
            self.btnConnect.caption = "Disconnect"
        else:
            self.btnConnect.caption = "Connect"

        return
               
    def draw(self):
        # clear whole screen
        self.screen.fill( self.color_bg )

        # Draw buttons
        self.btnHomeXY.draw(self.screen)
        self.btnHomeZ.draw(self.screen)
        self.btnZUp.draw(self.screen)
        self.btnHeatBed.draw(self.screen)
        self.btnHeatHotEnd.draw(self.screen)
        self.btnStartPrint.draw(self.screen)
        self.btnAbortPrint.draw(self.screen)
        self.btnPausePrint.draw(self.screen)
        self.btnConnect.draw(self.screen)
        self.btnReboot.draw(self.screen)
        self.btnFan.draw(self.screen)

        # Place temperatures texts
        text_pos = self.buttonHeight * 2 + 15
        text_gap = (self.buttonHeight * 2) / 8
        lbl_hotend_temp = self.fntText.render(u'Hot end:', 1, (220, 0, 0))
        self.screen.blit(lbl_hotend_temp, (self.leftPadding + self.buttonWidth + self.buttonSpace, text_pos))
        text_pos += text_gap + (2 if self.enable_graph else 0)
        lbl_hotend_temp = self.fntText.render(u'{0:.1f}\N{DEGREE SIGN}C ({1:.1f}\N{DEGREE SIGN}C)'.format(self.hotend_temp, self.hotend_temp_target), 1, (220, 0, 0))
        self.screen.blit(lbl_hotend_temp, (self.leftPadding + self.buttonWidth + self.buttonSpace, text_pos))
        
        text_pos += text_gap * 1.5
        lbl_bed_temp = self.fntText.render(u'Bed:', 1, (66, 100, 255))
        self.screen.blit(lbl_bed_temp, (self.leftPadding + self.buttonWidth + self.buttonSpace, text_pos))
        text_pos += text_gap + (2 if self.enable_graph else 0)
        lbl_bed_temp = self.fntText.render(u'{0:.1f}\N{DEGREE SIGN}C ({1:.1f}\N{DEGREE SIGN}C)'.format(self.bed_temp, self.bed_temp_target), 1, (66, 100, 255))
        self.screen.blit(lbl_bed_temp, (self.leftPadding + self.buttonWidth + self.buttonSpace, text_pos))

        # Place time left and compeltetion texts
        if self.JobLoaded is False or self.PrintTimeLeft is None or self.Completion is None:
            self.Completion = 0
            self.PrintTimeLeft = 0;

        text_pos += text_gap * 2
        lbl_print_time_left = self.fntText.render("Time left: {0}".format(datetime.timedelta(seconds = self.PrintTimeLeft)), 1, (200, 200, 200))
        self.screen.blit(lbl_print_time_left, (self.leftPadding + self.buttonWidth + self.buttonSpace, text_pos))

        text_pos += text_gap * 1.5
        lbl_completion = self.fntText.render("Completion: {0:.1f}%".format(self.Completion), 1, (200, 200, 200))
        self.screen.blit(lbl_completion, (self.leftPadding + self.buttonWidth + self.buttonSpace, text_pos))

        # ************************
        #   Temperature Graphing
        # ************************
        
        if self.enable_graph:
            # Graph area
            pygame.draw.rect(self.screen, (255, 255, 255), (self.graph_area_left, self.graph_area_top, self.graph_area_width, self.graph_area_height))

            # Graph axes
            # X, temp
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left, self.graph_area_top], [self.graph_area_left, self.graph_area_top + self.graph_area_height], 2)

            # X-axis divisions
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 5], [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 5], 2) # 0
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 4], [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 4], 2) # 50
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 3], [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 3], 2) # 100
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 2], [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 2], 2) # 150
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 1], [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 1], 2) # 200
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left - 3, self.graph_area_top + (self.graph_area_height / 5) * 0], [self.graph_area_left, self.graph_area_top + (self.graph_area_height / 5) * 0], 2) # 250

            # X-axis scale
            lbl0 = self.fntTextSmall.render("0", 1, (200, 200, 200))
            self.screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 5))
            lbl0 = self.fntTextSmall.render("50", 1, (200, 200, 200))
            self.screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 4))
            lbl0 = self.fntTextSmall.render("100", 1, (200, 200, 200))
            self.screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 3))
            lbl0 = self.fntTextSmall.render("150", 1, (200, 200, 200))
            self.screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 2))
            lbl0 = self.fntTextSmall.render("200", 1, (200, 200, 200))
            self.screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 1))
            lbl0 = self.fntTextSmall.render("250", 1, (200, 200, 200))
            self.screen.blit(lbl0, (self.graph_area_left - 26, self.graph_area_top - 6 + (self.graph_area_height / 5) * 0))

            # X-axis divisions, grey lines
            pygame.draw.line(self.screen, (200, 200, 200), [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 4], [self.graph_area_left + self.graph_area_width - 2, self.graph_area_top + (self.graph_area_height / 5) * 4], 1) # 50
            pygame.draw.line(self.screen, (200, 200, 200), [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 3], [self.graph_area_left + self.graph_area_width - 2, self.graph_area_top + (self.graph_area_height / 5) * 3], 1) # 100
            pygame.draw.line(self.screen, (200, 200, 200), [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 2], [self.graph_area_left + self.graph_area_width - 2, self.graph_area_top + (self.graph_area_height / 5) * 2], 1) # 150
            pygame.draw.line(self.screen, (200, 200, 200), [self.graph_area_left + 2, self.graph_area_top + (self.graph_area_height / 5) * 1], [self.graph_area_left + self.graph_area_width - 2, self.graph_area_top + (self.graph_area_height / 5) * 1], 1) # 200

            # Y, time, 2 seconds per pixel
            pygame.draw.line(self.screen, (0, 0, 0), [self.graph_area_left, self.graph_area_top + self.graph_area_height], [self.graph_area_left + self.graph_area_width, self.graph_area_top + self.graph_area_height], 2)

            # Scaling factor
            g_scale = self.graph_area_height / 250.0

            # Print temperatures for hot end
            i = 0
            for t in self.HotEndTempList:
                x = self.graph_area_left + i
                y = self.graph_area_top + self.graph_area_height - int(t * g_scale)
                pygame.draw.line(self.screen, (220, 0, 0), [x, y], [x + 1, y], 2)
                i += 1

            # Print temperatures for bed
            i = 0
            for t in self.BedTempList:
                x = self.graph_area_left + i
                y = self.graph_area_top + self.graph_area_height - int(t * g_scale)
                pygame.draw.line(self.screen, (0, 0, 220), [x, y], [x + 1, y], 2)
                i += 1

            # Draw target temperatures
            # Hot end
            pygame.draw.line(self.screen, (180, 40, 40), [self.graph_area_left, self.graph_area_top + self.graph_area_height - (self.hotend_temp_target * g_scale)], [self.graph_area_left + self.graph_area_width, self.graph_area_top + self.graph_area_height - (self.hotend_temp_target * g_scale)], 1)
            # Bed
            pygame.draw.line(self.screen, (40, 40, 180), [self.graph_area_left, self.graph_area_top + self.graph_area_height - (self.bed_temp_target * g_scale)], [self.graph_area_left + self.graph_area_width, self.graph_area_top + self.graph_area_height - (self.bed_temp_target * g_scale)], 1)

        # update screen
        pygame.display.update()

    def _home_xy(self):
        print "Home XY"
        data = { "command": "home", "axes": ["x", "y"] }
        self._sendAPICommand(self.apiurl_printhead, data)
        return

    def _home_z(self):
        print "Home Z"
        data = { "command": "home", "axes": ["z"] }
        self._sendAPICommand(self.apiurl_printhead, data)
        return

    def _z_up(self):
        print "Z up +" + str(self.z_up_value)
        data = { "command": "jog", "x": 0, "y": 0, "z": self.z_up_value }
        self._sendAPICommand(self.apiurl_printhead, data)
        return

    def _heat_bed(self):
        # is the bed already hot, in that case turn it off
        if self.HotBed:
            print "Turning bed off"
            data = { "command": "target", "target": 0 }
        else:
            print "Heating bed - " + str(self.hotbed_temp) + " degree"
            data = { "command": "target", "target": self.hotbed_temp }

        self._sendAPICommand(self.apiurl_bed, data)
        return

    def _heat_hotend(self):
        # is the bed already hot, in that case turn it off
        if self.HotHotEnd:
            print "Turning hotend off"
            data = { "command": "target", "targets": { "tool0": 0   } }
        else:
            print "Heating hotend - " + str(self.hotend_temp) + " degree"
            data = { "command": "target", "targets": { "tool0": self.hotend_temp } }

        self._sendAPICommand(self.apiurl_tool, data)
        return

    def _start_print(self):
        # here we should display a yes/no box somehow
        print "Start print"
        data = { "command": "start" }
        self._sendAPICommand(self.apiurl_job, data)
        return

    def _abort_print(self):
        # here we should display a yes/no box somehow
        print "Abort print"
        data = { "command": "cancel" }
        self._sendAPICommand(self.apiurl_job, data)
        return

    # Pause or resume print
    def _pause_print(self):
        print "Pause print"
        data = { "command": "pause" }
        self._sendAPICommand(self.apiurl_job, data)
        return

    # Reboot system
    def _reboot(self):
        if platform.system() == 'Linux':
            os.system("reboot")
        else:
            pygame.image.save(self.screen, "screenshot.jpg")

        self.done = True
        print "reboot"
        return

    # Turn on or off fan
    def _fan(self):
        if self.FanSpinning:
            print "Turning fan off"
            data = { "commands": ["M107"], "parameters": {} }
            self.FanSpinning = False
        else:
            print "Turning fan on"
            data = { "commands": ["M106 S255"], "parameters": {} }
            self.FanSpinning = True

        self._sendAPICommand(self.apiurl_command, data)
        return

    # Connect / disconnect
    def _connect(self):
        if self.connected:
            print "Disconnecting"
            self.connected = False
        else:
            print "Connecting"
            self.connected = True

        return

    # Send API-data to OctoPrint
    def _sendAPICommand(self, url, data):
        if self.connected:
            try:
                headers = {'content-type': 'application/json', 'X-Api-Key': self.apikey}
                r = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError as e:
                print "Connection Error ({0}): {1}".format(e.errno, e.strerror)


if __name__ == '__main__':
    opp = OctoPiPanel("OctoPiPanel!")
    opp.Start()
