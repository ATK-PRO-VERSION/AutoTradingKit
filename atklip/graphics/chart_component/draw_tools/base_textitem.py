from atklip.graphics.pyqtgraph import TextItem
from atklip.graphics.pyqtgraph.Point import Point

class BaseTextItem(TextItem):
    def __init__(self, text='', color=(200,200,200), html=None, anchor=(0,0),
                 border=None, fill=None, angle=0, rotateAxis=None, ensureInBounds=False):
        super().__init__(text=text, color=color, html=html, anchor=anchor,
                 border=border, fill=fill, angle=angle, rotateAxis=rotateAxis, ensureInBounds=ensureInBounds)
    
    def updateTextPos(self):
        pass


    def updatePos(self,pointf):
        # update text position to obey anchor
        r = self.textItem.boundingRect()
        tl = self.textItem.mapToParent(r.topLeft())
        br = self.textItem.mapToParent(r.bottomRight())
        offset = (br - tl) * self.anchor

        mapFromParent = self.mapFromParent(pointf)
        _x = -offset.x() + mapFromParent.x()
        _y = mapFromParent.y()-r.height()/2
        pos = Point(_x,_y)
        self.textItem.setPos(pos)
