from atklip.graphics.pyqtgraph import CrosshairROI


class Crosshair(CrosshairROI):
    def __init__(self, pos,size, **kwargs):
        super().__init__(pos,size, **kwargs)
        