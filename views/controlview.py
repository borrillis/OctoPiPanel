from views.panelview import PanelView


class ControlView(PanelView):

    def __init__(self, config, bus):
        PanelView.__init__(self, config, bus)