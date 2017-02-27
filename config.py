import os
import pygame
from ConfigParser import RawConfigParser

class OctoPiPanelConfig:

    @staticmethod
    def load_from_file():
        config = OctoPiPanelConfig()

        cfg = RawConfigParser()
        config.script_directory = os.path.dirname(os.path.realpath(__file__))
        settings_file_path = os.path.join(config.script_directory, "OctoPiPanel.cfg")
        cfg.readfp(open(settings_file_path, "r"))

        config.api_baseurl = cfg.get('settings', 'baseurl')
        config.apikey = cfg.get('settings', 'apikey')
        config.updatetime = cfg.getint('settings', 'updatetime')
        config.backlightofftime = cfg.getint('settings', 'backlightofftime')
        config.statusbarheight = 40
        config.titlebarheight = 40

        config.window_flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        
        if cfg.has_option('settings', 'fullscreen'):
            config.fullscreen = cfg.getboolean('settings', 'fullscreen')
            if config.fullscreen:
                config.window_flags |= pygame.FULLSCREEN | pygame.NOFRAME

        if cfg.has_option('settings', 'showmouse'):
            config.showmouse = cfg.getboolean('settings', 'showmouse')
        else:
            config.showmouse = True
            
        if cfg.has_option('settings', 'width'):
            config.width = cfg.getint('settings', 'width')
        elif cfg.has_option('settings', 'window_width'):
            config.width = cfg.getint('settings', 'width')
        else:
            config.width = 320

        if cfg.has_option('settings', 'height'):
            config.height = cfg.getint('settings', 'height')
        elif cfg.has_option('settings', 'window_height'):
            config.height = cfg.getint('settings', 'height')
        else:
            config.height = 240

        if cfg.has_option('settings', 'caption'):
            config.caption = cfg.get('settings', 'caption')
        else:
            config.caption = "OctoPiPanel"

        return config

