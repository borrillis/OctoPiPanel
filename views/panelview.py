import pygame
import os

class PanelView():
    def __init__(self, config,  title=''):
    	self.title = title
        self.config = config
        self.PanelMenuText = pygame.font.Font(os.path.join(self.config.script_directory, "assets/Roboto-Regular.ttf"), 16)
        
        
    def draw(self, screen, firstframe):
		if self.title:
			title_lbl = self.PanelMenuText.render(self.title, 1, (255, 255, 255))
			left = (self.config.width - title_lbl.get_width())/2
			down = (self.config.titlebarheight / 2 ) - (title_lbl.get_height() / 2 )
			#print dir(title_lbl)
			screen.blit(title_lbl, (left, down))
 
    def handle_event(self, event):
        pass