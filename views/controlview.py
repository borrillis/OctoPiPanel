import os
import pygbutton
from views.panelview import PanelView


class ControlView(PanelView):

    def __init__(self, config, bus, client):
        PanelView.__init__(self, config, bus)

        self.client = client

        self.jog_amount = 10

        self.btn_left = pygbutton.PygButton((2, 92, 50, 50), normal=self.image_path('assets/control-arrow-left.png'))
        self.btn_right = pygbutton.PygButton((102, 92, 50, 50), normal=self.image_path('assets/control-arrow-right.png'))
        self.btn_up = pygbutton.PygButton((52, 42, 50, 50), normal=self.image_path('assets/control-arrow-up.png'))
        self.btn_down = pygbutton.PygButton((52, 142, 50, 50), normal=self.image_path('assets/control-arrow-down.png'))
        self.btn_z_up = pygbutton.PygButton((180, 42, 50, 50), normal=self.image_path('assets/control-arrow-up.png'))
        self.btn_z_down = pygbutton.PygButton((180, 142, 50, 50), normal=self.image_path('assets/control-arrow-down.png'))

        self.btn_x_home = pygbutton.PygButton((260, 42, 50, 50), normal=self.image_path('assets/home-x.png'))
        self.btn_y_home = pygbutton.PygButton((260, 92, 50, 50), normal=self.image_path('assets/home-y.png'))
        self.btn_z_home = pygbutton.PygButton((260, 142, 50, 50), normal=self.image_path('assets/home-z.png'))

        self.client = client

    def image_path(self, image):
        return os.path.join(self.config.script_directory, image)

    def handle_event(self, event):
        PanelView.handle_event(self, event)

        if 'click' in self.btn_left.handleEvent(event):
            self.client.jog_axis(x=-self.jog_amount)

        if 'click' in self.btn_right.handleEvent(event):
            self.client.jog_axis(x=self.jog_amount)

        if 'click' in self.btn_up.handleEvent(event):
            self.client.jog_axis(y=-self.jog_amount)

        if 'click' in self.btn_down.handleEvent(event):
            self.client.jog_axis(y=self.jog_amount)

        if 'click' in self.btn_z_up.handleEvent(event):
            self.client.jog_axis(z=self.jog_amount)

        if 'click' in self.btn_z_down.handleEvent(event):
            self.client.jog_axis(z=-self.jog_amount)

        if 'click' in self.btn_x_home.handleEvent(event):
            self.client.home_x()

        if 'click' in self.btn_y_home.handleEvent(event):
            self.client.home_y()

        if 'click' in self.btn_z_home.handleEvent(event):
            self.client.home_z()

    def draw(self, screen):
        PanelView.draw(self, screen)

        self.btn_left.draw(screen)
        self.btn_right.draw(screen)
        self.btn_up.draw(screen)
        self.btn_down.draw(screen)
        self.btn_z_up.draw(screen)
        self.btn_z_down.draw(screen)
        self.btn_x_home.draw(screen)
        self.btn_y_home.draw(screen)
        self.btn_z_home.draw(screen)