import os
import pygbutton
from views.panelview import PanelView


class ControlView(PanelView):

    def __init__(self, config, client):
        PanelView.__init__(self, config, "Control")

        self.client = client

        self.jog_amount = 10

        loffset = ( self.config.width - 310 ) / 2
        toffset = ((self.config.height - self.config.statusbarheight  -150 ) / 2 ) - 40

        self.btn_left = pygbutton.PygButton((loffset + 2, toffset + 92, 50, 50), normal=self.image_path('assets/control-arrow-left.png'))
        self.btn_right = pygbutton.PygButton((loffset + 102, toffset + 92, 50, 50), normal=self.image_path('assets/control-arrow-right.png'))
        self.btn_up = pygbutton.PygButton((loffset + 52, toffset + 42, 50, 50), normal=self.image_path('assets/control-arrow-up.png'))
        self.btn_down = pygbutton.PygButton((loffset + 52, toffset + 142, 50, 50), normal=self.image_path('assets/control-arrow-down.png'))
        self.btn_z_up = pygbutton.PygButton((loffset + 180, toffset + 42, 50, 50), normal=self.image_path('assets/control-arrow-up.png'))
        self.btn_z_down = pygbutton.PygButton((loffset + 180, toffset + 142, 50, 50), normal=self.image_path('assets/control-arrow-down.png'))

        self.btn_x_home = pygbutton.PygButton((loffset + 260, toffset + 42, 50, 50), normal=self.image_path('assets/home-x.png'))
        self.btn_y_home = pygbutton.PygButton((loffset + 260, toffset + 92, 50, 50), normal=self.image_path('assets/home-y.png'))
        self.btn_z_home = pygbutton.PygButton((loffset + 260, toffset + 142, 50, 50), normal=self.image_path('assets/home-z.png'))

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

    def draw(self, screen, firstframe):
        PanelView.draw(self, screen, firstframe)

        self.btn_left.draw(screen)
        self.btn_right.draw(screen)
        self.btn_up.draw(screen)
        self.btn_down.draw(screen)
        self.btn_z_up.draw(screen)
        self.btn_z_down.draw(screen)
        self.btn_x_home.draw(screen)
        self.btn_y_home.draw(screen)
        self.btn_z_home.draw(screen)