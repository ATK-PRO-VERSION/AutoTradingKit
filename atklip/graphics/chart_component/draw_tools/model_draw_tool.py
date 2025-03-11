from dataclasses import dataclass

from PySide6.QtCore import QPointF


@dataclass
class Line:
    text:str
    pos: list
    chart_pos: QPointF
    item: object
    color: tuple|str
    brush: tuple|str
    show: bool